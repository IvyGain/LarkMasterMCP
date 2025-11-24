"""Remote MCP Server with SSE support for LarkMasterMCP."""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from .lark_client import LarkClient
from .tools import LARK_TOOLS
from .smart_builder import SmartBitableBuilder, DocumentationGenerator
from .message_handler import MessageHandler, MessageParser

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ToolCallRequest(BaseModel):
    """Tool call request model."""
    name: str
    arguments: Dict[str, Any] = {}


class LarkRemoteMCPServer:
    """Remote MCP Server with SSE and HTTP endpoints."""

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.lark_client = LarkClient(app_id, app_secret)

        # Initialize smart components
        self.smart_builder = SmartBitableBuilder(self.lark_client)
        self.doc_generator = DocumentationGenerator(self.lark_client)
        self.message_handler = MessageHandler(self.lark_client, self.smart_builder)
        self.message_parser = MessageParser()

        logger.info("Initialized LarkMasterMCP Remote Server with 108 tools")

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools."""
        return LARK_TOOLS

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return result."""
        logger.info(f"Executing tool: {name}")

        try:
            # Import the tool execution logic from server.py
            result = await self._execute_tool(name, arguments)
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Execute tool implementation."""

        # Messaging tools
        if name == "send_message":
            return await self.lark_client.send_message(
                chat_id=arguments["chat_id"],
                message=arguments["message"],
                message_type=arguments.get("message_type", "text")
            )

        elif name == "list_chats":
            return await self.lark_client.list_chats()

        elif name == "search_messages":
            return await self.lark_client.search_messages(
                query=arguments["query"],
                chat_id=arguments.get("chat_id")
            )

        # Bitable tools
        elif name == "create_bitable_app":
            return await self.lark_client.create_bitable_app(
                name=arguments["name"],
                folder_token=arguments.get("folder_token")
            )

        elif name == "create_bitable_table":
            return await self.lark_client.create_bitable_table(
                app_token=arguments["app_token"],
                name=arguments["name"],
                fields=arguments["fields"]
            )

        elif name == "batch_create_records":
            return await self.lark_client.batch_create_records(
                app_token=arguments["app_token"],
                table_id=arguments["table_id"],
                records=arguments["records"]
            )

        elif name == "get_bitable_records":
            return await self.lark_client.get_bitable_records(
                app_token=arguments["app_token"],
                table_id=arguments["table_id"],
                view_id=arguments.get("view_id"),
                filter=arguments.get("filter")
            )

        # Document tools
        elif name == "create_document":
            return await self.lark_client.create_document(
                title=arguments["title"],
                content=arguments.get("content", ""),
                folder_token=arguments.get("folder_token")
            )

        elif name == "search_documents":
            return await self.lark_client.search_documents(
                query=arguments["query"],
                doc_types=arguments.get("doc_types"),
                owner_ids=arguments.get("owner_ids"),
                chat_ids=arguments.get("chat_ids")
            )

        # Wiki tools
        elif name == "create_wiki_space":
            return await self.lark_client.create_wiki_space(
                name=arguments["name"],
                description=arguments.get("description", ""),
                members=arguments.get("members", [])
            )

        elif name == "create_wiki_page":
            return await self.lark_client.create_wiki_page(
                space_id=arguments["space_id"],
                title=arguments["title"],
                content=arguments.get("content", ""),
                parent_page_id=arguments.get("parent_page_id")
            )

        # Smart tools
        elif name == "smart_build_bitable":
            return await self.smart_builder.build_from_message(
                message=arguments["message"],
                name=arguments.get("name"),
                folder_token=arguments.get("folder_token")
            )

        elif name == "process_lark_message":
            cmd_result = await self.message_handler.handle_message(
                message=arguments["message"]
            )
            return {
                "success": cmd_result.success,
                "command_type": cmd_result.command_type.value,
                "message": cmd_result.message,
                "data": cmd_result.data
            }

        elif name == "generate_bitable_documentation":
            design = self.smart_builder.design_bitable(
                message=arguments["message"],
                name=arguments.get("name")
            )
            doc_content = self.doc_generator.generate_bitable_documentation(design)
            return {
                "documentation": doc_content,
                "design_name": design.name
            }

        elif name == "create_bitable_with_wiki":
            # 1. Build Bitable
            bitable_result = await self.smart_builder.build_from_message(
                message=arguments["message"],
                name=arguments.get("name"),
                folder_token=arguments.get("folder_token")
            )

            # 2. Create Wiki space
            wiki_name = arguments.get("name", "システムドキュメント")
            wiki_result = await self.lark_client.create_wiki_space(
                name=f"{wiki_name} Wiki",
                description=f"{wiki_name}のドキュメンテーション"
            )

            # 3. Generate documentation
            design = self.smart_builder.design_bitable(
                message=arguments["message"],
                name=arguments.get("name")
            )
            space_id = wiki_result.get("space", {}).get("space_id", "")
            if space_id:
                doc_result = await self.doc_generator.create_wiki_documentation(
                    design=design,
                    space_id=space_id
                )
            else:
                doc_result = {"error": "Failed to get wiki space_id"}

            return {
                "bitable": bitable_result,
                "wiki": wiki_result,
                "documentation": doc_result
            }

        elif name == "list_bitable_templates":
            templates_info = {}
            for name_key, template in self.smart_builder.TEMPLATES.items():
                templates_info[name_key] = {
                    "name": template["name"],
                    "description": template["description"],
                    "fields": [
                        {"name": f.name, "type": f.field_type.name}
                        for f in template["fields"]
                    ]
                }
            return {"templates": templates_info}

        elif name == "analyze_message_intent":
            parsed = self.message_parser.parse(arguments["message"])
            return {
                "command_type": parsed.command_type.value,
                "confidence": parsed.confidence,
                "parameters": parsed.parameters,
                "original_message": parsed.original_message
            }

        elif name == "get_lark_bot_help":
            help_result = await self.message_handler.handle_message("ヘルプ")
            return {
                "help_text": help_result.message,
                "templates": help_result.data.get("templates", []) if help_result.data else []
            }

        else:
            raise ValueError(f"Unknown or unimplemented tool: {name}")


def create_app() -> FastAPI:
    """Create FastAPI application."""

    app_id = os.environ.get("LARK_APP_ID", "")
    app_secret = os.environ.get("LARK_APP_SECRET", "")

    if not app_id or not app_secret:
        logger.warning("LARK_APP_ID or LARK_APP_SECRET not set")

    mcp_server = LarkRemoteMCPServer(app_id, app_secret) if app_id and app_secret else None

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("🚀 LarkMasterMCP Remote Server starting...")
        yield
        logger.info("👋 LarkMasterMCP Remote Server shutting down...")

    app = FastAPI(
        title="LarkMasterMCP Remote Server",
        description="自然言語でLarkを操作できるMCPサーバー | 108ツール",
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
        """Root endpoint."""
        return {
            "name": "LarkMasterMCP Remote Server",
            "version": "0.2.0",
            "tools": 108,
            "status": "running",
            "endpoints": {
                "tools": "/tools",
                "call": "/call",
                "sse": "/sse",
                "health": "/health"
            }
        }

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "tools_count": 108}

    @app.get("/tools")
    async def list_tools():
        """List all available tools."""
        if not mcp_server:
            raise HTTPException(status_code=503, detail="Server not configured")
        tools = await mcp_server.list_tools()
        return {"tools": tools, "count": len(tools)}

    @app.get("/tools/{tool_name}")
    async def get_tool(tool_name: str):
        """Get specific tool information."""
        if not mcp_server:
            raise HTTPException(status_code=503, detail="Server not configured")
        tools = await mcp_server.list_tools()
        for tool in tools:
            if tool["name"] == tool_name:
                return tool
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

    @app.post("/call")
    async def call_tool(request: ToolCallRequest):
        """Call a tool."""
        if not mcp_server:
            raise HTTPException(status_code=503, detail="Server not configured")
        result = await mcp_server.call_tool(request.name, request.arguments)
        return result

    @app.get("/sse")
    async def sse_endpoint(request: Request):
        """SSE endpoint for streaming responses."""

        async def event_generator():
            # Send initial connection event
            yield f"data: {json.dumps({'type': 'connected', 'server': 'LarkMasterMCP'})}\n\n"

            # Keep connection alive
            while True:
                if await request.is_disconnected():
                    break
                yield f"data: {json.dumps({'type': 'ping'})}\n\n"
                await asyncio.sleep(30)

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )

    @app.post("/sse/call")
    async def sse_call_tool(request: Request):
        """SSE endpoint for tool calls with streaming response."""
        if not mcp_server:
            raise HTTPException(status_code=503, detail="Server not configured")

        body = await request.json()
        tool_name = body.get("name")
        arguments = body.get("arguments", {})

        async def stream_response():
            yield f"data: {json.dumps({'type': 'start', 'tool': tool_name})}\n\n"

            try:
                result = await mcp_server.call_tool(tool_name, arguments)
                yield f"data: {json.dumps({'type': 'result', 'data': result})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

            yield f"data: {json.dumps({'type': 'end'})}\n\n"

        return StreamingResponse(
            stream_response(),
            media_type="text/event-stream"
        )

    # MCP Protocol endpoints
    @app.post("/mcp/list_tools")
    async def mcp_list_tools():
        """MCP Protocol: List tools."""
        if not mcp_server:
            raise HTTPException(status_code=503, detail="Server not configured")
        tools = await mcp_server.list_tools()
        return {
            "jsonrpc": "2.0",
            "result": {"tools": tools}
        }

    @app.post("/mcp/call_tool")
    async def mcp_call_tool(request: Request):
        """MCP Protocol: Call tool."""
        if not mcp_server:
            raise HTTPException(status_code=503, detail="Server not configured")

        body = await request.json()
        params = body.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        result = await mcp_server.call_tool(tool_name, arguments)

        return {
            "jsonrpc": "2.0",
            "result": {"content": [{"type": "text", "text": json.dumps(result)}]}
        }

    # ===== Lark Bot Webhook Endpoints =====
    # 処理済みメッセージID追跡（重複防止）
    import time
    import re
    processed_messages: Dict[str, float] = {}

    def clean_old_messages():
        """古いメッセージIDを削除"""
        current_time = time.time()
        nonlocal processed_messages
        processed_messages = {
            msg_id: ts for msg_id, ts in processed_messages.items()
            if current_time - ts < 300
        }

    def extract_text(content: str) -> str:
        """メッセージからテキスト抽出"""
        try:
            content_json = json.loads(content)
            text = content_json.get("text", "")
        except (json.JSONDecodeError, TypeError):
            text = content if isinstance(content, str) else ""
        # @メンション除去
        text = re.sub(r'@_user_\d+', '', text)
        text = re.sub(r'@\S+', '', text)
        return text.strip()

    @app.post("/webhook/event")
    async def webhook_event(request: Request):
        """
        Lark Bot Webhook エンドポイント

        Lark Open Platformで設定するURL:
        https://your-server.com/webhook/event
        """
        if not mcp_server:
            raise HTTPException(status_code=503, detail="Server not configured")

        try:
            body = await request.json()
            logger.info(f"Webhook received: {json.dumps(body, ensure_ascii=False)[:100]}...")

            # URL検証（初回設定時）
            if body.get("type") == "url_verification":
                challenge = body.get("challenge", "")
                return JSONResponse(content={"challenge": challenge})

            # イベント処理
            header = body.get("header", {})
            event_type = header.get("event_type", "")
            event = body.get("event", {})

            # メッセージ受信イベント
            if event_type == "im.message.receive_v1":
                message = event.get("message", {})
                sender = event.get("sender", {})

                message_id = message.get("message_id", "")
                chat_id = message.get("chat_id", "")
                sender_type = sender.get("sender_type", "")

                # 重複・Bot自身のメッセージは無視
                clean_old_messages()
                if message_id in processed_messages or sender_type == "app":
                    return JSONResponse(content={"status": "ignored"})
                processed_messages[message_id] = time.time()

                # テキストメッセージのみ
                if message.get("message_type") != "text":
                    return JSONResponse(content={"status": "ignored_non_text"})

                content = message.get("content", "{}")
                text = extract_text(content)

                if not text:
                    return JSONResponse(content={"status": "empty"})

                logger.info(f"Processing: {text[:50]}...")

                user_id = sender.get("sender_id", {}).get("user_id", "")

                # 議事録リンクをチェック
                minute_result = await mcp_server.minutes_handler.handle_message_with_minute(
                    text=text,
                    chat_id=chat_id,
                    user_id=user_id
                )

                if minute_result.get("has_minute"):
                    # 議事録リンクが見つかった - インタラクティブカードを送信
                    card = minute_result.get("card")
                    if card:
                        await mcp_server.lark_client.send_interactive_message(
                            chat_id=chat_id,
                            card=card
                        )
                        return JSONResponse(content={
                            "status": "minute_detected",
                            "needs_confirmation": minute_result.get("needs_confirmation", False),
                            "needs_clarification": minute_result.get("needs_clarification", False)
                        })

                # 通常のメッセージ処理
                result = await mcp_server.message_handler.handle_message(text)

                # 返信送信
                await mcp_server.lark_client.send_message(
                    chat_id=chat_id,
                    message=result.message,
                    message_type="text"
                )

                return JSONResponse(content={
                    "status": "processed",
                    "command_type": result.command_type.value
                })

            # Bot追加イベント
            elif event_type == "im.chat.member.bot.added_v1":
                chat_id = event.get("chat_id", "")
                welcome = """🤖 **LarkMasterMCP Bot** が参加しました！

@メンションして話しかけてください：
• 「顧客管理テーブルを作成して」
• 「プロジェクト管理用のベースを作って」
• 「ヘルプ」で詳しい使い方"""

                await mcp_server.lark_client.send_message(
                    chat_id=chat_id,
                    message=welcome,
                    message_type="text"
                )
                return JSONResponse(content={"status": "welcomed"})

            # カードアクション（ボタンクリック）イベント
            elif event_type == "card.action.trigger":
                action = event.get("action", {})
                value_str = action.get("value", "{}")
                operator = event.get("operator", {})
                user_id = operator.get("user_id", "")

                try:
                    value = json.loads(value_str) if isinstance(value_str, str) else value_str
                except json.JSONDecodeError:
                    value = {}

                action_id = value.get("action_id", "")
                action_type_str = value.get("action_type", "")
                confirm = value.get("confirm")

                logger.info(f"Card action: action_id={action_id}, type={action_type_str}, confirm={confirm}")

                # ペンディングアクションを取得
                pending = mcp_server.minutes_handler.get_pending_action(action_id)
                if not pending:
                    return JSONResponse(content={"status": "action_expired"})

                chat_id = pending.chat_id

                # 確認フロー
                if confirm is True:
                    # 実行確認された - アクションを実行
                    result = await mcp_server.minutes_handler.execute_action(pending)
                    mcp_server.minutes_handler.remove_pending_action(action_id)

                    # 結果を送信
                    message = result.get("message", "処理が完了しました")
                    await mcp_server.lark_client.send_message(
                        chat_id=chat_id,
                        message=f"✅ {message}",
                        message_type="text"
                    )

                    return JSONResponse(content={"status": "executed", "result": result})

                elif confirm is False:
                    # キャンセルされた
                    mcp_server.minutes_handler.remove_pending_action(action_id)
                    await mcp_server.lark_client.send_message(
                        chat_id=chat_id,
                        message="❌ キャンセルしました",
                        message_type="text"
                    )
                    return JSONResponse(content={"status": "cancelled"})

                else:
                    # 初回ボタンクリック - 確認カードを表示
                    minute_data = await mcp_server.minutes_handler.get_minute_data(pending.minute_token)
                    if minute_data.get("success"):
                        analysis = mcp_server.minutes_handler.analyze_transcript(
                            minute_data.get("transcript", {})
                        )
                        confirm_card = mcp_server.minutes_handler.create_confirmation_card(
                            action_type=pending.action_type,
                            analysis=analysis,
                            action_id=action_id
                        )
                        await mcp_server.lark_client.send_interactive_message(
                            chat_id=chat_id,
                            card=confirm_card
                        )
                        return JSONResponse(content={"status": "confirmation_sent"})
                    else:
                        await mcp_server.lark_client.send_message(
                            chat_id=chat_id,
                            message=f"❌ 議事録の取得に失敗しました: {minute_data.get('error')}",
                            message_type="text"
                        )
                        return JSONResponse(content={"status": "error", "error": minute_data.get("error")})

            return JSONResponse(content={"status": "ignored", "event_type": event_type})

        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return JSONResponse(content={"status": "error", "error": str(e)})

    return app


def run_server(host: str = None, port: int = None):
    """Run the remote MCP server."""
    import os

    # Railway等のクラウド環境ではPORT環境変数を使用
    if host is None:
        host = os.getenv("HOST", "0.0.0.0")
    if port is None:
        port = int(os.getenv("PORT", "8000"))

    logger.info(f"Starting server on {host}:{port}")
    app = create_app()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
