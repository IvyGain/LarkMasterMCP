"""
Lark Bot Server - Webhookでメッセージを受信してMCPツールを実行

Larkチャットで@メンションされたメッセージを処理し、
自動的に適切なアクションを実行して返信します。
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import time
from typing import Any, Dict, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .lark_client import LarkClient
from .smart_builder import SmartBitableBuilder, DocumentationGenerator
from .message_handler import MessageHandler, MessageParser

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LarkBotServer:
    """
    Lark Bot Webhook Server

    Larkからのイベント（メッセージ受信など）を処理し、
    MCPツールを実行して返信を送信します。
    """

    def __init__(
        self,
        app_id: str,
        app_secret: str,
        verification_token: Optional[str] = None,
        encrypt_key: Optional[str] = None
    ):
        self.app_id = app_id
        self.app_secret = app_secret
        self.verification_token = verification_token
        self.encrypt_key = encrypt_key

        # Lark Client
        self.lark_client = LarkClient(app_id, app_secret)

        # Smart components
        self.smart_builder = SmartBitableBuilder(self.lark_client)
        self.doc_generator = DocumentationGenerator(self.lark_client)
        self.message_handler = MessageHandler(self.lark_client, self.smart_builder)

        # 処理済みメッセージIDを追跡（重複防止）
        self.processed_messages: Dict[str, float] = {}

        logger.info("LarkBotServer initialized")

    def _clean_old_messages(self):
        """古い処理済みメッセージIDを削除（メモリ節約）"""
        current_time = time.time()
        # 5分以上前のメッセージIDを削除
        self.processed_messages = {
            msg_id: timestamp
            for msg_id, timestamp in self.processed_messages.items()
            if current_time - timestamp < 300
        }

    def _is_duplicate(self, message_id: str) -> bool:
        """重複メッセージかどうかを確認"""
        self._clean_old_messages()

        if message_id in self.processed_messages:
            return True

        self.processed_messages[message_id] = time.time()
        return False

    def _extract_text_from_content(self, content: str) -> str:
        """メッセージコンテンツからテキストを抽出"""
        try:
            content_json = json.loads(content)
            text = content_json.get("text", "")
        except (json.JSONDecodeError, TypeError):
            text = content if isinstance(content, str) else ""

        # @メンションを除去
        text = re.sub(r'@_user_\d+', '', text)
        text = re.sub(r'@\S+', '', text)
        text = text.strip()

        return text

    async def handle_url_verification(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """URL検証チャレンジを処理"""
        challenge = data.get("challenge", "")
        logger.info(f"URL verification challenge received")
        return {"challenge": challenge}

    async def handle_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """イベントを処理"""
        # イベントタイプを取得
        schema = event_data.get("schema", "")
        header = event_data.get("header", {})
        event_type = header.get("event_type", "")

        logger.info(f"Received event: {event_type}")

        # URL検証
        if event_data.get("type") == "url_verification":
            return await self.handle_url_verification(event_data)

        # メッセージ受信イベント
        if event_type == "im.message.receive_v1":
            return await self.handle_message_event(event_data)

        # Bot追加イベント
        if event_type == "im.chat.member.bot.added_v1":
            return await self.handle_bot_added(event_data)

        # その他のイベント
        logger.info(f"Unhandled event type: {event_type}")
        return {"status": "ignored", "event_type": event_type}

    async def handle_message_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """メッセージ受信イベントを処理"""
        event = event_data.get("event", {})
        message = event.get("message", {})
        sender = event.get("sender", {})

        # メッセージID
        message_id = message.get("message_id", "")

        # 重複チェック
        if self._is_duplicate(message_id):
            logger.info(f"Duplicate message ignored: {message_id}")
            return {"status": "duplicate"}

        # チャットID
        chat_id = message.get("chat_id", "")

        # 送信者情報
        sender_id = sender.get("sender_id", {}).get("user_id", "")
        sender_type = sender.get("sender_type", "")

        # Bot自身のメッセージは無視
        if sender_type == "app":
            return {"status": "ignored_self"}

        # メッセージタイプ
        message_type = message.get("message_type", "")

        # テキストメッセージのみ処理
        if message_type != "text":
            logger.info(f"Non-text message ignored: {message_type}")
            return {"status": "ignored_non_text"}

        # メッセージ内容を取得
        content = message.get("content", "{}")
        text = self._extract_text_from_content(content)

        if not text:
            return {"status": "empty_message"}

        logger.info(f"Processing message from {sender_id}: {text[:50]}...")

        try:
            # メッセージを処理
            result = await self.message_handler.handle_message(text)

            # 返信を送信
            await self.lark_client.send_message(
                chat_id=chat_id,
                message=result.message,
                message_type="text"
            )

            logger.info(f"Reply sent to {chat_id}")

            return {
                "status": "processed",
                "command_type": result.command_type.value,
                "success": result.success
            }

        except Exception as e:
            logger.error(f"Error processing message: {e}")

            # エラー返信
            try:
                await self.lark_client.send_message(
                    chat_id=chat_id,
                    message=f"エラーが発生しました: {str(e)}\n\n「ヘルプ」と入力すると使い方を確認できます。",
                    message_type="text"
                )
            except Exception as reply_error:
                logger.error(f"Error sending error reply: {reply_error}")

            return {"status": "error", "error": str(e)}

    async def handle_bot_added(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Botがチャットに追加されたイベントを処理"""
        event = event_data.get("event", {})
        chat_id = event.get("chat_id", "")

        logger.info(f"Bot added to chat: {chat_id}")

        # ウェルカムメッセージを送信
        welcome_message = """
🤖 **LarkMasterMCP Bot** がチャットに参加しました！

私に@メンションして話しかけると、以下のことができます：

📊 **Bitable作成**
「顧客管理テーブルを作成して」
「プロジェクト管理用のベースを作って」

📚 **Wiki/ドキュメント**
「Wikiスペースを作成」
「ドキュメントを作成」

✅ **タスク**
「タスクを追加: レビュー依頼」

💡 **ヘルプ**
「ヘルプ」と入力すると詳しい使い方が見れます！

さっそく試してみてください！
"""

        try:
            await self.lark_client.send_message(
                chat_id=chat_id,
                message=welcome_message,
                message_type="text"
            )
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")

        return {"status": "welcomed", "chat_id": chat_id}


def create_bot_app() -> FastAPI:
    """FastAPI Bot アプリケーションを作成"""

    app_id = os.environ.get("LARK_APP_ID", "")
    app_secret = os.environ.get("LARK_APP_SECRET", "")
    verification_token = os.environ.get("LARK_VERIFICATION_TOKEN", "")
    encrypt_key = os.environ.get("LARK_ENCRYPT_KEY", "")

    if not app_id or not app_secret:
        logger.warning("LARK_APP_ID or LARK_APP_SECRET not set")

    bot_server = LarkBotServer(
        app_id=app_id,
        app_secret=app_secret,
        verification_token=verification_token,
        encrypt_key=encrypt_key
    ) if app_id and app_secret else None

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("🤖 LarkMasterMCP Bot Server starting...")
        yield
        logger.info("👋 LarkMasterMCP Bot Server shutting down...")

    app = FastAPI(
        title="LarkMasterMCP Bot Server",
        description="Larkチャットで@メンションで操作できるBot",
        version="0.2.0",
        lifespan=lifespan
    )

    # CORS設定
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "name": "LarkMasterMCP Bot Server",
            "version": "0.2.0",
            "status": "running",
            "webhook_endpoint": "/webhook/event"
        }

    @app.get("/health")
    async def health():
        """Health check"""
        return {"status": "healthy"}

    @app.post("/webhook/event")
    async def webhook_event(request: Request):
        """
        Lark Webhook イベント受信エンドポイント

        Lark Open Platformで以下のURLを設定:
        https://your-server.com/webhook/event
        """
        if not bot_server:
            raise HTTPException(status_code=503, detail="Bot server not configured")

        try:
            body = await request.json()
            logger.debug(f"Webhook received: {json.dumps(body, ensure_ascii=False)[:200]}")

            # URL検証（初回設定時）
            if body.get("type") == "url_verification":
                challenge = body.get("challenge", "")
                return JSONResponse(content={"challenge": challenge})

            # イベント処理
            result = await bot_server.handle_event(body)
            return JSONResponse(content=result)

        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON")
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/webhook/card")
    async def webhook_card(request: Request):
        """カードアクションのWebhook（将来の拡張用）"""
        body = await request.json()
        logger.info(f"Card action received: {body}")
        return {"status": "ok"}

    return app


def run_bot_server(host: str = "0.0.0.0", port: int = 8001):
    """Bot サーバーを起動"""
    app = create_bot_app()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_bot_server()
