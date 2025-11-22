"""Smart Bitable Builder - メッセージから自動でBitableを構築するエンジン"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class FieldType(Enum):
    """Bitableフィールドタイプ"""
    TEXT = 1          # テキスト
    NUMBER = 2        # 数値
    SELECT = 3        # 単一選択
    MULTISELECT = 4   # 複数選択
    DATE = 5          # 日付
    CHECKBOX = 7      # チェックボックス
    PERSON = 11       # 担当者
    PHONE = 13        # 電話番号
    URL = 15          # URL
    ATTACHMENT = 17   # 添付ファイル
    LINK = 18         # 関連レコード
    FORMULA = 20      # 数式
    CREATED_TIME = 1001  # 作成日時
    MODIFIED_TIME = 1002  # 更新日時
    CREATED_BY = 1003    # 作成者
    MODIFIED_BY = 1004   # 更新者
    AUTO_NUMBER = 1005   # 自動採番


@dataclass
class FieldDefinition:
    """フィールド定義"""
    name: str
    field_type: FieldType
    description: str = ""
    options: List[str] = field(default_factory=list)
    required: bool = False

    def to_api_format(self) -> Dict[str, Any]:
        """Lark API形式に変換"""
        result = {
            "field_name": self.name,
            "type": self.field_type.value
        }

        # 選択肢フィールドの場合
        if self.field_type in [FieldType.SELECT, FieldType.MULTISELECT] and self.options:
            result["property"] = {
                "options": [{"name": opt} for opt in self.options]
            }

        return result


@dataclass
class TableDefinition:
    """テーブル定義"""
    name: str
    description: str = ""
    fields: List[FieldDefinition] = field(default_factory=list)

    def to_api_format(self) -> Dict[str, Any]:
        """Lark API形式に変換"""
        return {
            "name": self.name,
            "fields": [f.to_api_format() for f in self.fields]
        }


@dataclass
class BitableDesign:
    """Bitable全体設計"""
    name: str
    description: str = ""
    tables: List[TableDefinition] = field(default_factory=list)


class SmartBitableBuilder:
    """
    スマートBitable構築エンジン

    メッセージや指示から自動的に最適なBitable構造を設計・構築する
    """

    # よく使われるテーブルテンプレート
    TEMPLATES = {
        "顧客管理": {
            "name": "顧客管理",
            "description": "顧客情報を管理するテーブル",
            "fields": [
                FieldDefinition("会社名", FieldType.TEXT, required=True),
                FieldDefinition("担当者名", FieldType.TEXT),
                FieldDefinition("メールアドレス", FieldType.TEXT),
                FieldDefinition("電話番号", FieldType.PHONE),
                FieldDefinition("ステータス", FieldType.SELECT, options=["リード", "商談中", "契約済み", "休眠"]),
                FieldDefinition("優先度", FieldType.SELECT, options=["高", "中", "低"]),
                FieldDefinition("担当営業", FieldType.PERSON),
                FieldDefinition("次回アクション日", FieldType.DATE),
                FieldDefinition("備考", FieldType.TEXT),
                FieldDefinition("作成日", FieldType.CREATED_TIME),
            ]
        },
        "プロジェクト管理": {
            "name": "プロジェクト管理",
            "description": "プロジェクトとタスクを管理",
            "fields": [
                FieldDefinition("タスク名", FieldType.TEXT, required=True),
                FieldDefinition("説明", FieldType.TEXT),
                FieldDefinition("ステータス", FieldType.SELECT, options=["未着手", "進行中", "レビュー中", "完了", "保留"]),
                FieldDefinition("優先度", FieldType.SELECT, options=["緊急", "高", "中", "低"]),
                FieldDefinition("担当者", FieldType.PERSON),
                FieldDefinition("開始日", FieldType.DATE),
                FieldDefinition("期限", FieldType.DATE),
                FieldDefinition("進捗率", FieldType.NUMBER),
                FieldDefinition("添付ファイル", FieldType.ATTACHMENT),
                FieldDefinition("作成日", FieldType.CREATED_TIME),
            ]
        },
        "在庫管理": {
            "name": "在庫管理",
            "description": "商品在庫を管理",
            "fields": [
                FieldDefinition("商品名", FieldType.TEXT, required=True),
                FieldDefinition("SKU", FieldType.TEXT),
                FieldDefinition("カテゴリ", FieldType.SELECT, options=["電子機器", "衣類", "食品", "日用品", "その他"]),
                FieldDefinition("在庫数", FieldType.NUMBER),
                FieldDefinition("発注点", FieldType.NUMBER),
                FieldDefinition("単価", FieldType.NUMBER),
                FieldDefinition("仕入先", FieldType.TEXT),
                FieldDefinition("最終入荷日", FieldType.DATE),
                FieldDefinition("備考", FieldType.TEXT),
            ]
        },
        "売上管理": {
            "name": "売上管理",
            "description": "売上データを管理",
            "fields": [
                FieldDefinition("取引日", FieldType.DATE, required=True),
                FieldDefinition("顧客名", FieldType.TEXT),
                FieldDefinition("商品/サービス", FieldType.TEXT),
                FieldDefinition("数量", FieldType.NUMBER),
                FieldDefinition("単価", FieldType.NUMBER),
                FieldDefinition("売上金額", FieldType.NUMBER),
                FieldDefinition("支払方法", FieldType.SELECT, options=["現金", "クレジット", "銀行振込", "その他"]),
                FieldDefinition("ステータス", FieldType.SELECT, options=["未入金", "入金済み", "キャンセル"]),
                FieldDefinition("担当者", FieldType.PERSON),
            ]
        },
        "イベント管理": {
            "name": "イベント管理",
            "description": "イベントやセミナーを管理",
            "fields": [
                FieldDefinition("イベント名", FieldType.TEXT, required=True),
                FieldDefinition("説明", FieldType.TEXT),
                FieldDefinition("開催日", FieldType.DATE),
                FieldDefinition("場所", FieldType.TEXT),
                FieldDefinition("定員", FieldType.NUMBER),
                FieldDefinition("参加者数", FieldType.NUMBER),
                FieldDefinition("ステータス", FieldType.SELECT, options=["企画中", "募集中", "満席", "開催済み", "中止"]),
                FieldDefinition("担当者", FieldType.PERSON),
                FieldDefinition("URL", FieldType.URL),
            ]
        },
        "採用管理": {
            "name": "採用管理",
            "description": "採用候補者を管理",
            "fields": [
                FieldDefinition("候補者名", FieldType.TEXT, required=True),
                FieldDefinition("メールアドレス", FieldType.TEXT),
                FieldDefinition("電話番号", FieldType.PHONE),
                FieldDefinition("応募職種", FieldType.SELECT, options=["エンジニア", "デザイナー", "営業", "マーケティング", "その他"]),
                FieldDefinition("選考ステータス", FieldType.SELECT, options=["書類選考", "一次面接", "二次面接", "最終面接", "内定", "不採用", "辞退"]),
                FieldDefinition("面接日", FieldType.DATE),
                FieldDefinition("担当者", FieldType.PERSON),
                FieldDefinition("履歴書", FieldType.ATTACHMENT),
                FieldDefinition("評価", FieldType.SELECT, options=["A", "B", "C", "D"]),
                FieldDefinition("メモ", FieldType.TEXT),
            ]
        },
        "問い合わせ管理": {
            "name": "問い合わせ管理",
            "description": "カスタマーサポート問い合わせを管理",
            "fields": [
                FieldDefinition("問い合わせ番号", FieldType.AUTO_NUMBER),
                FieldDefinition("タイトル", FieldType.TEXT, required=True),
                FieldDefinition("内容", FieldType.TEXT),
                FieldDefinition("顧客名", FieldType.TEXT),
                FieldDefinition("メールアドレス", FieldType.TEXT),
                FieldDefinition("カテゴリ", FieldType.SELECT, options=["製品", "サービス", "請求", "技術", "その他"]),
                FieldDefinition("優先度", FieldType.SELECT, options=["緊急", "高", "中", "低"]),
                FieldDefinition("ステータス", FieldType.SELECT, options=["新規", "対応中", "保留", "解決済み", "クローズ"]),
                FieldDefinition("担当者", FieldType.PERSON),
                FieldDefinition("受付日", FieldType.CREATED_TIME),
            ]
        },
        "会議メモ": {
            "name": "会議メモ",
            "description": "会議の記録を管理",
            "fields": [
                FieldDefinition("会議タイトル", FieldType.TEXT, required=True),
                FieldDefinition("開催日時", FieldType.DATE),
                FieldDefinition("参加者", FieldType.PERSON),
                FieldDefinition("議事内容", FieldType.TEXT),
                FieldDefinition("決定事項", FieldType.TEXT),
                FieldDefinition("次回アクション", FieldType.TEXT),
                FieldDefinition("添付ファイル", FieldType.ATTACHMENT),
                FieldDefinition("作成者", FieldType.CREATED_BY),
            ]
        },
    }

    # キーワードとテンプレートのマッピング
    KEYWORD_TEMPLATE_MAP = {
        "顧客": "顧客管理",
        "クライアント": "顧客管理",
        "お客様": "顧客管理",
        "営業": "顧客管理",
        "CRM": "顧客管理",
        "プロジェクト": "プロジェクト管理",
        "タスク": "プロジェクト管理",
        "進捗": "プロジェクト管理",
        "TODO": "プロジェクト管理",
        "在庫": "在庫管理",
        "商品": "在庫管理",
        "倉庫": "在庫管理",
        "売上": "売上管理",
        "販売": "売上管理",
        "収益": "売上管理",
        "イベント": "イベント管理",
        "セミナー": "イベント管理",
        "勉強会": "イベント管理",
        "採用": "採用管理",
        "人事": "採用管理",
        "候補者": "採用管理",
        "面接": "採用管理",
        "問い合わせ": "問い合わせ管理",
        "サポート": "問い合わせ管理",
        "チケット": "問い合わせ管理",
        "会議": "会議メモ",
        "ミーティング": "会議メモ",
        "議事録": "会議メモ",
    }

    # フィールドタイプ推定用キーワード
    FIELD_TYPE_KEYWORDS = {
        FieldType.DATE: ["日", "日付", "日時", "date", "開始", "終了", "期限", "締切"],
        FieldType.NUMBER: ["数", "金額", "価格", "数量", "個数", "率", "count", "amount"],
        FieldType.PHONE: ["電話", "tel", "phone", "携帯"],
        FieldType.URL: ["url", "リンク", "link", "ホームページ", "ウェブ"],
        FieldType.PERSON: ["担当", "責任者", "person", "メンバー", "作成者"],
        FieldType.CHECKBOX: ["フラグ", "flag", "有無", "チェック"],
        FieldType.ATTACHMENT: ["添付", "ファイル", "画像", "資料", "attachment"],
        FieldType.SELECT: ["ステータス", "状態", "種類", "カテゴリ", "優先度", "タイプ"],
    }

    def __init__(self, lark_client):
        """
        Args:
            lark_client: LarkClientインスタンス
        """
        self.lark_client = lark_client

    def analyze_intent(self, message: str) -> Tuple[str, Optional[str]]:
        """
        メッセージから意図を分析

        Args:
            message: ユーザーメッセージ

        Returns:
            (intent, template_name): 意図とテンプレート名
        """
        message_lower = message.lower()

        # テンプレートマッチング
        for keyword, template in self.KEYWORD_TEMPLATE_MAP.items():
            if keyword.lower() in message_lower:
                return "create_from_template", template

        # カスタム作成の検出
        if any(word in message_lower for word in ["作成", "作って", "作りたい", "新規", "create"]):
            return "create_custom", None

        return "unknown", None

    def extract_fields_from_text(self, text: str) -> List[FieldDefinition]:
        """
        テキストからフィールド定義を抽出

        Args:
            text: 解析するテキスト

        Returns:
            抽出されたフィールド定義のリスト
        """
        fields = []

        # 箇条書きやカンマ区切りのパターンを検出
        patterns = [
            r'[-・•]\s*(.+)',  # 箇条書き
            r'(\d+)[.．)）]\s*(.+)',  # 番号付きリスト
        ]

        extracted_items = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    extracted_items.append(match[-1].strip())
                else:
                    extracted_items.append(match.strip())

        # カンマ/読点区切り
        if not extracted_items:
            extracted_items = re.split(r'[,、，]', text)

        for item in extracted_items:
            item = item.strip()
            if not item or len(item) > 50:  # 長すぎるものはスキップ
                continue

            field_type = self._infer_field_type(item)
            fields.append(FieldDefinition(
                name=item,
                field_type=field_type
            ))

        return fields

    def _infer_field_type(self, field_name: str) -> FieldType:
        """
        フィールド名からタイプを推定

        Args:
            field_name: フィールド名

        Returns:
            推定されたフィールドタイプ
        """
        field_name_lower = field_name.lower()

        for field_type, keywords in self.FIELD_TYPE_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in field_name_lower:
                    return field_type

        return FieldType.TEXT  # デフォルトはテキスト

    def generate_select_options(self, field_name: str) -> List[str]:
        """
        フィールド名から選択肢を生成

        Args:
            field_name: フィールド名

        Returns:
            選択肢のリスト
        """
        field_name_lower = field_name.lower()

        # 一般的な選択肢パターン
        if any(word in field_name_lower for word in ["ステータス", "状態"]):
            return ["未着手", "進行中", "完了", "保留"]
        elif any(word in field_name_lower for word in ["優先度", "優先"]):
            return ["高", "中", "低"]
        elif any(word in field_name_lower for word in ["カテゴリ", "種類", "分類"]):
            return ["カテゴリA", "カテゴリB", "カテゴリC", "その他"]

        return []

    def design_bitable(
        self,
        message: str,
        name: Optional[str] = None
    ) -> BitableDesign:
        """
        メッセージからBitable設計を生成

        Args:
            message: ユーザーメッセージ
            name: Base名（指定がなければ自動生成）

        Returns:
            Bitable設計
        """
        intent, template_name = self.analyze_intent(message)

        if intent == "create_from_template" and template_name:
            # テンプレートベースで設計
            template = self.TEMPLATES[template_name]
            table = TableDefinition(
                name=template["name"],
                description=template["description"],
                fields=template["fields"]
            )

            base_name = name or f"{template_name}Base"
            return BitableDesign(
                name=base_name,
                description=f"{template_name}用のBitable",
                tables=[table]
            )

        else:
            # カスタム設計
            fields = self.extract_fields_from_text(message)

            # 最低限のフィールドを確保
            if not fields:
                fields = [
                    FieldDefinition("タイトル", FieldType.TEXT, required=True),
                    FieldDefinition("説明", FieldType.TEXT),
                    FieldDefinition("ステータス", FieldType.SELECT, options=["未着手", "進行中", "完了"]),
                    FieldDefinition("作成日", FieldType.CREATED_TIME),
                ]

            # 選択肢の自動生成
            for field in fields:
                if field.field_type == FieldType.SELECT and not field.options:
                    field.options = self.generate_select_options(field.name)

            table = TableDefinition(
                name=name or "メインテーブル",
                description="自動生成されたテーブル",
                fields=fields
            )

            base_name = name or "新規Base"
            return BitableDesign(
                name=base_name,
                description="自動生成されたBitable",
                tables=[table]
            )

    async def build_bitable(
        self,
        design: BitableDesign,
        folder_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        設計からBitableを実際に構築

        Args:
            design: Bitable設計
            folder_token: 作成先フォルダ

        Returns:
            作成結果
        """
        results = {
            "app": None,
            "tables": [],
            "success": False,
            "error": None
        }

        try:
            # 1. Bitable App作成
            app_result = await self.lark_client.create_bitable_app(
                name=design.name,
                folder_token=folder_token
            )
            results["app"] = app_result
            app_token = app_result.get("app", {}).get("app_token")

            if not app_token:
                raise Exception("Failed to get app_token")

            # 2. テーブル作成
            for table_def in design.tables:
                table_result = await self.lark_client.create_bitable_table(
                    app_token=app_token,
                    name=table_def.name,
                    fields=[f.to_api_format() for f in table_def.fields]
                )
                results["tables"].append(table_result)

            results["success"] = True
            logger.info(f"Successfully built Bitable: {design.name}")

        except Exception as e:
            results["error"] = str(e)
            logger.error(f"Failed to build Bitable: {e}")

        return results

    async def build_from_message(
        self,
        message: str,
        name: Optional[str] = None,
        folder_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        メッセージから直接Bitableを構築

        Args:
            message: ユーザーメッセージ
            name: Base名
            folder_token: 作成先フォルダ

        Returns:
            作成結果（設計情報含む）
        """
        # 設計生成
        design = self.design_bitable(message, name)

        # 構築
        result = await self.build_bitable(design, folder_token)
        result["design"] = {
            "name": design.name,
            "description": design.description,
            "tables": [
                {
                    "name": t.name,
                    "fields": [{"name": f.name, "type": f.field_type.name} for f in t.fields]
                }
                for t in design.tables
            ]
        }

        return result


class DocumentationGenerator:
    """
    Bitable構造からドキュメントを自動生成
    """

    def __init__(self, lark_client):
        self.lark_client = lark_client

    def generate_table_documentation(self, table_def: TableDefinition) -> str:
        """
        テーブル定義からMarkdown形式のドキュメントを生成
        """
        doc = f"# {table_def.name}\n\n"
        doc += f"{table_def.description}\n\n"
        doc += "## フィールド一覧\n\n"
        doc += "| フィールド名 | タイプ | 説明 |\n"
        doc += "|------------|--------|------|\n"

        for field in table_def.fields:
            type_name = field.field_type.name
            options_str = ""
            if field.options:
                options_str = f" (選択肢: {', '.join(field.options)})"
            doc += f"| {field.name} | {type_name} | {field.description}{options_str} |\n"

        return doc

    def generate_bitable_documentation(self, design: BitableDesign) -> str:
        """
        Bitable全体のドキュメントを生成
        """
        doc = f"# {design.name}\n\n"
        doc += f"{design.description}\n\n"
        doc += "---\n\n"

        for table in design.tables:
            doc += self.generate_table_documentation(table)
            doc += "\n---\n\n"

        doc += "## 使い方\n\n"
        doc += "1. 各テーブルにデータを入力してください\n"
        doc += "2. ビューを切り替えて様々な角度からデータを確認できます\n"
        doc += "3. フィルターや並び替えで必要な情報を絞り込めます\n"

        return doc

    async def create_wiki_documentation(
        self,
        design: BitableDesign,
        space_id: str,
        parent_page_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Wikiにドキュメントを作成
        """
        doc_content = self.generate_bitable_documentation(design)

        result = await self.lark_client.create_wiki_page(
            space_id=space_id,
            title=f"{design.name} マニュアル",
            content=doc_content,
            parent_page_id=parent_page_id
        )

        return result
