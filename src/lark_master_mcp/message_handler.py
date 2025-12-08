"""Message Handler - Larkメッセージを解析してMCPツールを実行"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CommandType(Enum):
    """コマンドタイプ"""
    CREATE_BITABLE = "create_bitable"
    CREATE_TABLE = "create_table"
    CREATE_WIKI = "create_wiki"
    CREATE_DOC = "create_doc"
    SEND_MESSAGE = "send_message"
    CREATE_TASK = "create_task"
    SEARCH = "search"
    HELP = "help"
    GREETING = "greeting"
    CONVERSATION = "conversation"
    UNKNOWN = "unknown"


@dataclass
class ParsedCommand:
    """解析されたコマンド"""
    command_type: CommandType
    parameters: Dict[str, Any]
    original_message: str
    confidence: float  # 0.0 - 1.0


@dataclass
class CommandResult:
    """コマンド実行結果"""
    success: bool
    data: Any
    message: str
    command_type: CommandType


class MessageParser:
    """
    Larkメッセージを解析してコマンドを抽出
    """

    # コマンドパターン定義
    COMMAND_PATTERNS = {
        CommandType.CREATE_BITABLE: [
            r"(?:ベース|base|bitable|多次元テーブル).*(?:作成|作って|作りたい|create)",
            r"(?:作成|作って|作りたい|create).*(?:ベース|base|bitable|多次元テーブル)",
            r"(?:顧客|プロジェクト|タスク|在庫|売上)(?:管理)?.*(?:テーブル|表)",
        ],
        CommandType.CREATE_TABLE: [
            r"テーブル.*(?:追加|作成|作って)",
            r"(?:追加|作成).*テーブル",
        ],
        CommandType.CREATE_WIKI: [
            r"(?:wiki|ウィキ|知識|ナレッジ).*(?:作成|作って|作りたい)",
            r"(?:作成|作って).*(?:wiki|ウィキ|知識ベース)",
            r"ドキュメント.*(?:整理|まとめ)",
        ],
        CommandType.CREATE_DOC: [
            r"(?:ドキュメント|文書|doc|マニュアル).*(?:作成|作って)",
            r"(?:作成|作って).*(?:ドキュメント|文書|doc)",
        ],
        CommandType.SEND_MESSAGE: [
            r"(?:メッセージ|通知).*(?:送|配信)",
            r"(?:伝えて|知らせて|連絡して)",
        ],
        CommandType.CREATE_TASK: [
            r"タスク.*(?:作成|追加|登録)",
            r"(?:作成|追加).*タスク",
            r"(?:TODO|やること).*(?:追加|登録)",
        ],
        CommandType.SEARCH: [
            r"(?:検索|探して|見つけて|search)",
            r"(?:どこ|どれ).*(?:ある|いる)",
        ],
        CommandType.HELP: [
            r"(?:ヘルプ|help|使い方|できること)",
            r"(?:教えて|何ができる)",
        ],
        CommandType.GREETING: [
            r"^(?:こんにちは|こんばんは|おはよう|ハロー|hello|hi|hey|やあ|おっす)",
            r"(?:テスト|test|聞こえ|返事|応答)",
            r"^(?:よろしく|はじめまして)",
        ],
    }

    # パラメータ抽出パターン
    PARAM_PATTERNS = {
        "name": [
            r"名前[はを:：]?\s*[「『]?([^」』\s]+)[」』]?",
            r"(?:という|って)名前",
            r"[「『]([^」』]+)[」』]",
        ],
        "fields": [
            r"フィールド[はを:：]?\s*(.+)",
            r"項目[はを:：]?\s*(.+)",
            r"カラム[はを:：]?\s*(.+)",
        ],
        "description": [
            r"説明[はを:：]?\s*(.+)",
            r"概要[はを:：]?\s*(.+)",
        ],
    }

    def __init__(self):
        self._compile_patterns()

    def _compile_patterns(self):
        """正規表現パターンをコンパイル"""
        self.compiled_patterns = {}
        for cmd_type, patterns in self.COMMAND_PATTERNS.items():
            self.compiled_patterns[cmd_type] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

    def parse(self, message: str) -> ParsedCommand:
        """
        メッセージを解析してコマンドを抽出

        Args:
            message: ユーザーメッセージ

        Returns:
            ParsedCommand
        """
        message = message.strip()

        # コマンドタイプの検出
        detected_type = CommandType.UNKNOWN
        max_confidence = 0.0

        for cmd_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(message):
                    # パターン一致数で信頼度計算
                    match_count = sum(1 for p in patterns if p.search(message))
                    confidence = min(0.5 + (match_count * 0.2), 1.0)

                    if confidence > max_confidence:
                        max_confidence = confidence
                        detected_type = cmd_type

        # パラメータ抽出
        params = self._extract_parameters(message, detected_type)

        return ParsedCommand(
            command_type=detected_type,
            parameters=params,
            original_message=message,
            confidence=max_confidence
        )

    def _extract_parameters(
        self,
        message: str,
        cmd_type: CommandType
    ) -> Dict[str, Any]:
        """
        メッセージからパラメータを抽出

        Args:
            message: メッセージ
            cmd_type: コマンドタイプ

        Returns:
            抽出されたパラメータ
        """
        params = {}

        # 名前の抽出
        for pattern in self.PARAM_PATTERNS["name"]:
            match = re.search(pattern, message)
            if match:
                params["name"] = match.group(1)
                break

        # フィールドの抽出（Bitable作成時）
        if cmd_type == CommandType.CREATE_BITABLE:
            for pattern in self.PARAM_PATTERNS["fields"]:
                match = re.search(pattern, message)
                if match:
                    fields_text = match.group(1)
                    # カンマや読点で分割
                    fields = re.split(r'[,、，]', fields_text)
                    params["fields"] = [f.strip() for f in fields if f.strip()]
                    break

        # 説明の抽出
        for pattern in self.PARAM_PATTERNS["description"]:
            match = re.search(pattern, message)
            if match:
                params["description"] = match.group(1)
                break

        # メッセージ全体も保持
        params["raw_message"] = message

        return params


class MessageHandler:
    """
    メッセージを処理してMCPツールを実行するハンドラ
    """

    def __init__(self, lark_client, smart_builder=None):
        """
        Args:
            lark_client: LarkClientインスタンス
            smart_builder: SmartBitableBuilderインスタンス（オプション）
        """
        self.lark_client = lark_client
        self.parser = MessageParser()

        # SmartBitableBuilderは遅延インポート
        if smart_builder:
            self.smart_builder = smart_builder
        else:
            from .smart_builder import SmartBitableBuilder
            self.smart_builder = SmartBitableBuilder(lark_client)

        # コマンドハンドラの登録
        self.handlers: Dict[CommandType, Callable] = {
            CommandType.CREATE_BITABLE: self._handle_create_bitable,
            CommandType.CREATE_TABLE: self._handle_create_table,
            CommandType.CREATE_WIKI: self._handle_create_wiki,
            CommandType.CREATE_DOC: self._handle_create_doc,
            CommandType.SEND_MESSAGE: self._handle_send_message,
            CommandType.CREATE_TASK: self._handle_create_task,
            CommandType.SEARCH: self._handle_search,
            CommandType.HELP: self._handle_help,
            CommandType.GREETING: self._handle_greeting,
            CommandType.CONVERSATION: self._handle_conversation,
        }

    async def handle_message(self, message: str) -> CommandResult:
        """
        メッセージを処理

        Args:
            message: ユーザーメッセージ

        Returns:
            CommandResult
        """
        # メッセージ解析
        parsed = self.parser.parse(message)
        logger.info(f"Parsed command: {parsed.command_type.value} (confidence: {parsed.confidence})")

        # 信頼度が低い場合は会話モードで応答
        if parsed.confidence < 0.3:
            parsed.command_type = CommandType.CONVERSATION
            return await self._handle_conversation(parsed)

        # ハンドラ実行
        handler = self.handlers.get(parsed.command_type)
        if handler:
            try:
                return await handler(parsed)
            except Exception as e:
                logger.error(f"Handler error: {e}")
                return CommandResult(
                    success=False,
                    data={"error": str(e)},
                    message=f"エラーが発生しました: {str(e)}",
                    command_type=parsed.command_type
                )
        else:
            return await self._handle_unknown(parsed)

    async def _handle_create_bitable(self, parsed: ParsedCommand) -> CommandResult:
        """Bitable作成処理"""
        name = parsed.parameters.get("name")
        message = parsed.original_message

        result = await self.smart_builder.build_from_message(
            message=message,
            name=name
        )

        if result.get("success"):
            app_info = result.get("app", {}).get("app", {})
            app_token = app_info.get("app_token", "")
            app_url = f"https://bytedance.feishu.cn/base/{app_token}" if app_token else ""

            design = result.get("design", {})
            tables_info = design.get("tables", [])

            response_msg = f"✅ Bitableを作成しました！\n\n"
            response_msg += f"**Base名:** {design.get('name', 'N/A')}\n"

            if app_url:
                response_msg += f"**URL:** {app_url}\n\n"

            if tables_info:
                response_msg += "**テーブル構成:**\n"
                for table in tables_info:
                    response_msg += f"\n📋 {table.get('name', 'テーブル')}\n"
                    for field in table.get('fields', []):
                        response_msg += f"  • {field.get('name')} ({field.get('type')})\n"

            return CommandResult(
                success=True,
                data=result,
                message=response_msg,
                command_type=CommandType.CREATE_BITABLE
            )
        else:
            return CommandResult(
                success=False,
                data=result,
                message=f"❌ Bitable作成に失敗しました: {result.get('error', '不明なエラー')}",
                command_type=CommandType.CREATE_BITABLE
            )

    async def _handle_create_table(self, parsed: ParsedCommand) -> CommandResult:
        """テーブル追加処理"""
        # 既存Bitableへのテーブル追加
        # app_tokenが必要なので、追加の対話が必要
        return CommandResult(
            success=False,
            data=None,
            message="テーブルを追加するには、対象のBitableのapp_tokenを指定してください。\n"
                   "例: 「app_token: xxx のベースにテーブルを追加して」",
            command_type=CommandType.CREATE_TABLE
        )

    async def _handle_create_wiki(self, parsed: ParsedCommand) -> CommandResult:
        """Wiki作成処理"""
        name = parsed.parameters.get("name", "ナレッジベース")
        description = parsed.parameters.get("description", "")

        try:
            result = await self.lark_client.create_wiki_space(
                name=name,
                description=description
            )

            space_id = result.get("space", {}).get("space_id", "")

            return CommandResult(
                success=True,
                data=result,
                message=f"✅ Wikiスペースを作成しました！\n\n"
                       f"**スペース名:** {name}\n"
                       f"**スペースID:** {space_id}",
                command_type=CommandType.CREATE_WIKI
            )
        except Exception as e:
            return CommandResult(
                success=False,
                data={"error": str(e)},
                message=f"❌ Wiki作成に失敗しました: {str(e)}",
                command_type=CommandType.CREATE_WIKI
            )

    async def _handle_create_doc(self, parsed: ParsedCommand) -> CommandResult:
        """ドキュメント作成処理"""
        title = parsed.parameters.get("name", "新規ドキュメント")
        content = parsed.parameters.get("description", "")

        try:
            result = await self.lark_client.create_document(
                title=title,
                content=content
            )

            doc_id = result.get("document", {}).get("document_id", "")

            return CommandResult(
                success=True,
                data=result,
                message=f"✅ ドキュメントを作成しました！\n\n"
                       f"**タイトル:** {title}\n"
                       f"**ドキュメントID:** {doc_id}",
                command_type=CommandType.CREATE_DOC
            )
        except Exception as e:
            return CommandResult(
                success=False,
                data={"error": str(e)},
                message=f"❌ ドキュメント作成に失敗しました: {str(e)}",
                command_type=CommandType.CREATE_DOC
            )

    async def _handle_send_message(self, parsed: ParsedCommand) -> CommandResult:
        """メッセージ送信処理"""
        return CommandResult(
            success=False,
            data=None,
            message="メッセージを送信するには、宛先（chat_id）と内容を指定してください。",
            command_type=CommandType.SEND_MESSAGE
        )

    async def _handle_create_task(self, parsed: ParsedCommand) -> CommandResult:
        """タスク作成処理"""
        title = parsed.parameters.get("name", "")
        description = parsed.parameters.get("description", "")

        if not title:
            # メッセージからタイトルを抽出試行
            title = parsed.original_message[:50] if len(parsed.original_message) > 50 else parsed.original_message

        try:
            result = await self.lark_client.create_task(
                title=title,
                description=description
            )

            task_id = result.get("task", {}).get("id", "")

            return CommandResult(
                success=True,
                data=result,
                message=f"✅ タスクを作成しました！\n\n"
                       f"**タイトル:** {title}\n"
                       f"**タスクID:** {task_id}",
                command_type=CommandType.CREATE_TASK
            )
        except Exception as e:
            return CommandResult(
                success=False,
                data={"error": str(e)},
                message=f"❌ タスク作成に失敗しました: {str(e)}",
                command_type=CommandType.CREATE_TASK
            )

    async def _handle_search(self, parsed: ParsedCommand) -> CommandResult:
        """検索処理"""
        query = parsed.parameters.get("raw_message", "")

        try:
            result = await self.lark_client.search_documents(query=query)

            docs = result.get("docs_entities", [])
            if docs:
                response_msg = f"🔍 検索結果: {len(docs)}件\n\n"
                for doc in docs[:5]:  # 最大5件表示
                    response_msg += f"• {doc.get('title', 'N/A')}\n"
            else:
                response_msg = "検索結果が見つかりませんでした。"

            return CommandResult(
                success=True,
                data=result,
                message=response_msg,
                command_type=CommandType.SEARCH
            )
        except Exception as e:
            return CommandResult(
                success=False,
                data={"error": str(e)},
                message=f"❌ 検索に失敗しました: {str(e)}",
                command_type=CommandType.SEARCH
            )

    async def _handle_help(self, parsed: ParsedCommand) -> CommandResult:
        """ヘルプ表示"""
        help_text = """
🤖 **Lark Master MCP Bot** へようこそ！

以下のことができます：

📊 **Bitable (多次元テーブル)**
• 「顧客管理テーブルを作成して」
• 「プロジェクト管理用のベースを作って」
• 「在庫管理システムを構築」

📚 **Wiki / ドキュメント**
• 「ナレッジベースを作成」
• 「プロジェクトWikiを作って」
• 「マニュアルを作成」

✅ **タスク**
• 「タスクを追加: レビュー依頼」
• 「TODO: 資料作成」

🔍 **検索**
• 「〇〇を検索」
• 「△△のドキュメントを探して」

💡 **テンプレート**
利用可能なテンプレート:
• 顧客管理
• プロジェクト管理
• 在庫管理
• 売上管理
• イベント管理
• 採用管理
• 問い合わせ管理
• 会議メモ
"""
        return CommandResult(
            success=True,
            data={"templates": [
                "顧客管理", "プロジェクト管理", "在庫管理", "売上管理",
                "イベント管理", "採用管理", "問い合わせ管理", "会議メモ"
            ]},
            message=help_text,
            command_type=CommandType.HELP
        )

    async def _handle_greeting(self, parsed: ParsedCommand) -> CommandResult:
        """挨拶・テスト応答"""
        message = parsed.original_message.lower()

        # テスト系のメッセージ
        if any(kw in message for kw in ['テスト', 'test', '聞こえ', '返事', '応答']):
            response = """📡 はい、聞こえています！

LarkMasterMCP Bot が正常に動作しています。

私にできることの例：
• 「顧客管理テーブルを作成して」→ Bitable自動作成
• 「プロジェクト管理用のベースを作って」→ テンプレートから作成
• 「Wikiスペースを作成」→ ナレッジベース作成
• 「ヘルプ」→ 詳しい使い方

何かお手伝いできることはありますか？"""
        else:
            # 通常の挨拶
            import random
            greetings = [
                "こんにちは！LarkMasterMCP Botです。何かお手伝いできることはありますか？",
                "はい！何でもお聞きください。Bitableの作成やドキュメント管理などお手伝いします。",
                "お呼びですか？「ヘルプ」で私にできることを確認できます！",
            ]
            response = random.choice(greetings)

        return CommandResult(
            success=True,
            data=None,
            message=response,
            command_type=CommandType.GREETING
        )

    async def _handle_conversation(self, parsed: ParsedCommand) -> CommandResult:
        """会話形式の応答 - どんなメッセージにも応答"""
        message = parsed.original_message

        # メッセージの内容に応じた応答を生成
        response = f"""💬 メッセージを受け取りました！

「{message[:50]}{'...' if len(message) > 50 else ''}」

私はLark操作の自動化が得意です。以下のようなことができます：

📊 **データ管理**
• 「顧客管理テーブルを作成」
• 「プロジェクト進捗管理のベースを作って」
• 「在庫管理システムを構築」

📚 **ドキュメント**
• 「Wikiスペースを作成」
• 「ドキュメントを作成」

✅ **タスク**
• 「タスクを追加: 〇〇」

具体的にやりたいことを教えていただければ、お手伝いします！
「ヘルプ」で詳しい使い方を確認できます。"""

        return CommandResult(
            success=True,
            data={"original_message": message},
            message=response,
            command_type=CommandType.CONVERSATION
        )

    async def _handle_unknown(self, parsed: ParsedCommand) -> CommandResult:
        """不明なコマンド処理 - 会話モードにフォールバック"""
        return await self._handle_conversation(parsed)


class BotEventHandler:
    """
    Lark Botイベントを処理するハンドラ

    Webhook経由でイベントを受信し、適切な処理を実行
    """

    def __init__(self, lark_client, message_handler: MessageHandler):
        self.lark_client = lark_client
        self.message_handler = message_handler

    async def handle_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        イベントを処理

        Args:
            event_data: イベントデータ

        Returns:
            処理結果
        """
        event_type = event_data.get("header", {}).get("event_type", "")

        if event_type == "im.message.receive_v1":
            return await self._handle_message_event(event_data)
        else:
            logger.info(f"Unhandled event type: {event_type}")
            return {"status": "ignored", "event_type": event_type}

    async def _handle_message_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        メッセージ受信イベントを処理
        """
        event = event_data.get("event", {})
        message = event.get("message", {})

        # メッセージ内容を取得
        content = message.get("content", "{}")
        try:
            content_json = json.loads(content)
            text = content_json.get("text", "")
        except json.JSONDecodeError:
            text = content

        # @メンションを除去
        text = re.sub(r'@\w+', '', text).strip()

        if not text:
            return {"status": "empty_message"}

        # メッセージ処理
        result = await self.message_handler.handle_message(text)

        # 返信を送信
        chat_id = message.get("chat_id", "")
        if chat_id:
            await self.lark_client.send_message(
                chat_id=chat_id,
                message=result.message
            )

        return {
            "status": "processed",
            "command_type": result.command_type.value,
            "success": result.success
        }
