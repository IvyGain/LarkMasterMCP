"""Minutes (議事録) handler for LarkMasterMCP.

This module handles:
- Parsing minute links from messages
- Extracting transcripts and analyzing content
- Generating action items and decisions from meetings
- Creating Bitable summaries from meeting minutes
- Interactive confirmation flow with buttons
"""

import json
import logging
import re
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .lark_client import LarkClient
    from .smart_builder import SmartBitableBuilder

logger = logging.getLogger(__name__)


class ActionType(Enum):
    """Types of actions that can be performed on minutes."""
    EXTRACT_TASKS = "extract_tasks"
    CREATE_SUMMARY_BITABLE = "create_summary_bitable"
    ARCHIVE_TO_WIKI = "archive_to_wiki"
    EXTRACT_DECISIONS = "extract_decisions"
    FULL_ANALYSIS = "full_analysis"


@dataclass
class PendingAction:
    """Represents a pending action waiting for user confirmation."""
    action_id: str
    action_type: ActionType
    minute_token: str
    chat_id: str
    user_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0


@dataclass
class MinuteAnalysis:
    """Analysis result from a meeting minute."""
    title: str
    duration_seconds: int
    participants: List[str]
    tasks: List[Dict[str, str]]  # {"assignee": "", "task": "", "deadline": ""}
    decisions: List[str]
    key_points: List[str]
    transcript_summary: str


class MinutesHandler:
    """Handler for Lark Minutes processing."""

    # Pattern to extract minute token from URLs
    MINUTE_URL_PATTERNS = [
        r'https?://[^/]+/minutes/([a-zA-Z0-9]+)',
        r'https?://[^/]+/mm/([a-zA-Z0-9]+)',
        r'minute[_\-]?token[=:]?\s*([a-zA-Z0-9]+)',
    ]

    # Pending actions storage (in production, use Redis or DB)
    _pending_actions: Dict[str, PendingAction] = {}

    def __init__(
        self,
        lark_client: "LarkClient",
        smart_builder: Optional["SmartBitableBuilder"] = None
    ):
        self.lark_client = lark_client
        self.smart_builder = smart_builder

    def extract_minute_token(self, text: str) -> Optional[str]:
        """Extract minute token from text containing a minute URL."""
        for pattern in self.MINUTE_URL_PATTERNS:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

    def detect_intent(self, text: str) -> Optional[ActionType]:
        """Detect what the user wants to do with the minutes."""
        text_lower = text.lower()

        # Task extraction keywords
        if any(kw in text_lower for kw in [
            'タスク', 'task', 'todo', 'アクション', 'action',
            'やること', '宿題', 'アサイン', 'assign'
        ]):
            return ActionType.EXTRACT_TASKS

        # Bitable/Table creation keywords
        if any(kw in text_lower for kw in [
            'テーブル', 'table', 'bitable', 'ベース', 'base',
            'まとめ', 'summary', 'データベース', 'database'
        ]):
            return ActionType.CREATE_SUMMARY_BITABLE

        # Wiki/Archive keywords
        if any(kw in text_lower for kw in [
            'wiki', 'アーカイブ', 'archive', '保存', 'save',
            'ドキュメント', 'document', '記録', 'record'
        ]):
            return ActionType.ARCHIVE_TO_WIKI

        # Decision extraction keywords
        if any(kw in text_lower for kw in [
            '決定', 'decision', '決まった', '結論', 'conclusion',
            '合意', 'agreement', '承認', 'approve'
        ]):
            return ActionType.EXTRACT_DECISIONS

        # Full analysis keywords
        if any(kw in text_lower for kw in [
            '分析', 'analyze', '解析', 'すべて', 'all', '全部',
            'フル', 'full', '完全'
        ]):
            return ActionType.FULL_ANALYSIS

        return None

    async def get_minute_data(self, minute_token: str) -> Dict[str, Any]:
        """Get minute metadata and transcript."""
        try:
            # Get metadata
            metadata = await self.lark_client.get_minute(minute_token)

            # Get transcript
            transcript = await self.lark_client.get_minute_transcript(minute_token)

            # Get statistics if available
            try:
                statistics = await self.lark_client.get_minute_statistics(minute_token)
            except Exception:
                statistics = {}

            return {
                "metadata": metadata.get("data", {}),
                "transcript": transcript.get("data", {}),
                "statistics": statistics.get("data", {}),
                "success": True
            }
        except Exception as e:
            logger.error(f"Failed to get minute data: {e}")
            return {"success": False, "error": str(e)}

    def analyze_transcript(self, transcript_data: Dict) -> MinuteAnalysis:
        """Analyze transcript to extract key information."""
        # Extract basic info
        paragraphs = transcript_data.get("paragraphs", [])

        full_text = ""
        participants = set()

        for para in paragraphs:
            speaker = para.get("speaker", {}).get("username", "Unknown")
            participants.add(speaker)
            sentences = para.get("sentences", [])
            for sentence in sentences:
                full_text += sentence.get("text", "") + " "

        # Simple keyword-based extraction (in production, use NLP/LLM)
        tasks = self._extract_tasks_from_text(full_text)
        decisions = self._extract_decisions_from_text(full_text)
        key_points = self._extract_key_points(full_text)

        return MinuteAnalysis(
            title=transcript_data.get("title", "無題の会議"),
            duration_seconds=transcript_data.get("duration", 0),
            participants=list(participants),
            tasks=tasks,
            decisions=decisions,
            key_points=key_points,
            transcript_summary=full_text[:500] + "..." if len(full_text) > 500 else full_text
        )

    def _extract_tasks_from_text(self, text: str) -> List[Dict[str, str]]:
        """Extract tasks from text using keyword patterns."""
        tasks = []
        # Japanese task patterns
        patterns = [
            r'([^。]+(?:してください|お願い|タスク|TODO|やる|確認する|対応する)[^。]*)',
            r'([^。]*(?:までに|期限|deadline)[^。]*)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:5]:  # Limit to 5 tasks per pattern
                tasks.append({
                    "task": match.strip()[:100],
                    "assignee": "",
                    "deadline": ""
                })

        return tasks[:10]  # Max 10 tasks

    def _extract_decisions_from_text(self, text: str) -> List[str]:
        """Extract decisions from text."""
        decisions = []
        patterns = [
            r'([^。]*(?:決定|決まり|合意|承認|確定)[^。]*)',
            r'([^。]*(?:ということで|に決定|で行く)[^。]*)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:5]:
                decisions.append(match.strip()[:150])

        return decisions[:5]

    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key discussion points."""
        # Split into sentences and find important ones
        sentences = re.split(r'[。.!?]', text)
        key_points = []

        importance_keywords = [
            '重要', '大事', 'ポイント', '注意', '課題', '問題',
            '提案', '検討', '必要', 'important', 'key', 'issue'
        ]

        for sentence in sentences:
            if any(kw in sentence.lower() for kw in importance_keywords):
                if len(sentence.strip()) > 10:
                    key_points.append(sentence.strip()[:150])

        return key_points[:5]

    def create_action_card(
        self,
        minute_token: str,
        chat_id: str,
        user_id: str,
        suggested_actions: List[ActionType],
        minute_title: str = ""
    ) -> Dict[str, Any]:
        """Create an interactive card with action buttons."""

        # Create pending actions for each suggestion
        action_buttons = []
        for action_type in suggested_actions:
            action_id = str(uuid.uuid4())[:8]

            # Store pending action
            import time
            self._pending_actions[action_id] = PendingAction(
                action_id=action_id,
                action_type=action_type,
                minute_token=minute_token,
                chat_id=chat_id,
                user_id=user_id,
                created_at=time.time()
            )

            # Button label
            labels = {
                ActionType.EXTRACT_TASKS: "📋 タスク抽出",
                ActionType.CREATE_SUMMARY_BITABLE: "📊 Bitable作成",
                ActionType.ARCHIVE_TO_WIKI: "📚 Wikiに保存",
                ActionType.EXTRACT_DECISIONS: "✅ 決定事項抽出",
                ActionType.FULL_ANALYSIS: "🔍 フル分析",
            }

            action_buttons.append({
                "tag": "button",
                "text": {
                    "tag": "plain_text",
                    "content": labels.get(action_type, action_type.value)
                },
                "type": "primary" if action_type == ActionType.FULL_ANALYSIS else "default",
                "value": json.dumps({
                    "action_id": action_id,
                    "action_type": action_type.value
                })
            })

        # Build card
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"📝 議事録を検出しました"
                },
                "template": "blue"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**{minute_title or '会議'}** の議事録リンクを検出しました。\n\nどの処理を実行しますか？"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "action",
                    "actions": action_buttons
                }
            ]
        }

        return card

    def create_confirmation_card(
        self,
        action_type: ActionType,
        analysis: MinuteAnalysis,
        action_id: str
    ) -> Dict[str, Any]:
        """Create a confirmation card showing what will be done."""

        descriptions = {
            ActionType.EXTRACT_TASKS: f"以下の **{len(analysis.tasks)}件のタスク** を抽出します",
            ActionType.CREATE_SUMMARY_BITABLE: "議事録サマリーのBitableを作成します",
            ActionType.ARCHIVE_TO_WIKI: "議事録をWikiページとして保存します",
            ActionType.EXTRACT_DECISIONS: f"以下の **{len(analysis.decisions)}件の決定事項** を抽出します",
            ActionType.FULL_ANALYSIS: "タスク抽出、決定事項、Bitable作成を一括で行います",
        }

        # Preview content based on action type
        preview_items = []
        if action_type in [ActionType.EXTRACT_TASKS, ActionType.FULL_ANALYSIS]:
            for task in analysis.tasks[:3]:
                preview_items.append(f"• {task['task'][:50]}...")
        elif action_type in [ActionType.EXTRACT_DECISIONS, ActionType.FULL_ANALYSIS]:
            for decision in analysis.decisions[:3]:
                preview_items.append(f"• {decision[:50]}...")

        preview_text = "\n".join(preview_items) if preview_items else "プレビューなし"

        card = {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": "⚡ 実行確認"},
                "template": "orange"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**会議:** {analysis.title}\n**参加者:** {', '.join(analysis.participants[:5])}\n\n{descriptions.get(action_type, '')}"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**プレビュー:**\n{preview_text}"
                    }
                },
                {"tag": "hr"},
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {"tag": "plain_text", "content": "✅ 実行する"},
                            "type": "primary",
                            "value": json.dumps({
                                "action_id": action_id,
                                "confirm": True
                            })
                        },
                        {
                            "tag": "button",
                            "text": {"tag": "plain_text", "content": "❌ キャンセル"},
                            "type": "danger",
                            "value": json.dumps({
                                "action_id": action_id,
                                "confirm": False
                            })
                        }
                    ]
                }
            ]
        }

        return card

    def create_clarification_card(
        self,
        minute_token: str,
        chat_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Create a card asking what the user wants to do."""

        # Store pending action for each option
        import time
        options = [
            ActionType.EXTRACT_TASKS,
            ActionType.CREATE_SUMMARY_BITABLE,
            ActionType.ARCHIVE_TO_WIKI,
            ActionType.FULL_ANALYSIS
        ]

        action_buttons = []
        for action_type in options:
            action_id = str(uuid.uuid4())[:8]
            self._pending_actions[action_id] = PendingAction(
                action_id=action_id,
                action_type=action_type,
                minute_token=minute_token,
                chat_id=chat_id,
                user_id=user_id,
                created_at=time.time()
            )

            labels = {
                ActionType.EXTRACT_TASKS: "📋 タスクを抽出",
                ActionType.CREATE_SUMMARY_BITABLE: "📊 サマリーテーブル作成",
                ActionType.ARCHIVE_TO_WIKI: "📚 Wikiに保存",
                ActionType.FULL_ANALYSIS: "🔍 すべて実行",
            }

            action_buttons.append({
                "tag": "button",
                "text": {"tag": "plain_text", "content": labels[action_type]},
                "type": "primary" if action_type == ActionType.FULL_ANALYSIS else "default",
                "value": json.dumps({"action_id": action_id, "action_type": action_type.value})
            })

        card = {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": "🤔 何をしますか？"},
                "template": "turquoise"
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": "議事録リンクを検出しました。\n\n以下から実行したい処理を選んでください："
                    }
                },
                {"tag": "hr"},
                {
                    "tag": "action",
                    "actions": action_buttons
                }
            ]
        }

        return card

    def get_pending_action(self, action_id: str) -> Optional[PendingAction]:
        """Get a pending action by ID."""
        return self._pending_actions.get(action_id)

    def remove_pending_action(self, action_id: str) -> None:
        """Remove a pending action."""
        self._pending_actions.pop(action_id, None)

    def cleanup_old_actions(self, max_age_seconds: int = 3600) -> None:
        """Remove pending actions older than max_age_seconds."""
        import time
        current_time = time.time()
        expired = [
            aid for aid, action in self._pending_actions.items()
            if current_time - action.created_at > max_age_seconds
        ]
        for aid in expired:
            del self._pending_actions[aid]

    async def execute_action(
        self,
        action: PendingAction,
        analysis: Optional[MinuteAnalysis] = None
    ) -> Dict[str, Any]:
        """Execute the confirmed action."""

        if analysis is None:
            # Get minute data first
            minute_data = await self.get_minute_data(action.minute_token)
            if not minute_data.get("success"):
                return {"success": False, "error": minute_data.get("error")}
            analysis = self.analyze_transcript(minute_data.get("transcript", {}))

        result = {"success": True, "action_type": action.action_type.value}

        if action.action_type == ActionType.EXTRACT_TASKS:
            result["tasks"] = analysis.tasks
            result["message"] = f"📋 {len(analysis.tasks)}件のタスクを抽出しました"

        elif action.action_type == ActionType.EXTRACT_DECISIONS:
            result["decisions"] = analysis.decisions
            result["message"] = f"✅ {len(analysis.decisions)}件の決定事項を抽出しました"

        elif action.action_type == ActionType.CREATE_SUMMARY_BITABLE:
            if self.smart_builder:
                try:
                    # Create meeting summary Bitable
                    bitable_result = await self._create_meeting_bitable(analysis)
                    result["bitable"] = bitable_result
                    result["message"] = f"📊 議事録サマリーBitableを作成しました"
                except Exception as e:
                    result["success"] = False
                    result["error"] = str(e)
            else:
                result["message"] = "📊 Bitable作成機能は現在利用できません"

        elif action.action_type == ActionType.ARCHIVE_TO_WIKI:
            try:
                wiki_result = await self._archive_to_wiki(analysis)
                result["wiki"] = wiki_result
                result["message"] = f"📚 Wikiに保存しました"
            except Exception as e:
                result["success"] = False
                result["error"] = str(e)

        elif action.action_type == ActionType.FULL_ANALYSIS:
            result["tasks"] = analysis.tasks
            result["decisions"] = analysis.decisions
            result["key_points"] = analysis.key_points
            result["summary"] = analysis.transcript_summary

            if self.smart_builder:
                try:
                    bitable_result = await self._create_meeting_bitable(analysis)
                    result["bitable"] = bitable_result
                except Exception as e:
                    result["bitable_error"] = str(e)

            result["message"] = f"🔍 フル分析完了: {len(analysis.tasks)}タスク, {len(analysis.decisions)}決定事項"

        return result

    async def _create_meeting_bitable(self, analysis: MinuteAnalysis) -> Dict[str, Any]:
        """Create a Bitable from meeting analysis."""
        if not self.smart_builder:
            return {"error": "SmartBuilder not available"}

        # Use the meeting memo template
        design = {
            "name": f"議事録: {analysis.title}",
            "tables": [
                {
                    "name": "会議情報",
                    "fields": [
                        {"name": "会議名", "type": "text"},
                        {"name": "参加者", "type": "text"},
                        {"name": "時間（分）", "type": "number"},
                        {"name": "サマリー", "type": "text"}
                    ]
                },
                {
                    "name": "タスク",
                    "fields": [
                        {"name": "タスク内容", "type": "text"},
                        {"name": "担当者", "type": "text"},
                        {"name": "期限", "type": "date"},
                        {"name": "ステータス", "type": "singleSelect"}
                    ]
                },
                {
                    "name": "決定事項",
                    "fields": [
                        {"name": "決定内容", "type": "text"},
                        {"name": "決定日", "type": "date"}
                    ]
                }
            ]
        }

        return await self.smart_builder.build_bitable(design)

    async def _archive_to_wiki(self, analysis: MinuteAnalysis) -> Dict[str, Any]:
        """Archive meeting minutes to Wiki."""
        content = f"""# {analysis.title}

## 会議情報
- **参加者**: {', '.join(analysis.participants)}
- **時間**: {analysis.duration_seconds // 60}分

## サマリー
{analysis.transcript_summary}

## タスク
"""
        for task in analysis.tasks:
            content += f"- [ ] {task['task']}\n"

        content += "\n## 決定事項\n"
        for decision in analysis.decisions:
            content += f"- {decision}\n"

        content += "\n## キーポイント\n"
        for point in analysis.key_points:
            content += f"- {point}\n"

        # Create wiki page
        try:
            result = await self.lark_client.create_wiki_page(
                space_id="",  # Will need to be configured
                title=f"議事録: {analysis.title}",
                content=content
            )
            return result
        except Exception as e:
            return {"error": str(e)}

    async def handle_message_with_minute(
        self,
        text: str,
        chat_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Handle a message that may contain a minute link.

        Returns:
            - If minute detected with clear intent: execute or show confirmation
            - If minute detected without clear intent: show clarification card
            - If no minute detected: return None
        """
        minute_token = self.extract_minute_token(text)
        if not minute_token:
            return {"has_minute": False}

        intent = self.detect_intent(text)

        if intent:
            # Clear intent detected - show action card with suggestion
            card = self.create_action_card(
                minute_token=minute_token,
                chat_id=chat_id,
                user_id=user_id,
                suggested_actions=[intent, ActionType.FULL_ANALYSIS],
                minute_title=""
            )
            return {
                "has_minute": True,
                "minute_token": minute_token,
                "intent": intent.value,
                "card": card,
                "needs_confirmation": True
            }
        else:
            # No clear intent - ask what to do
            card = self.create_clarification_card(
                minute_token=minute_token,
                chat_id=chat_id,
                user_id=user_id
            )
            return {
                "has_minute": True,
                "minute_token": minute_token,
                "intent": None,
                "card": card,
                "needs_clarification": True
            }
