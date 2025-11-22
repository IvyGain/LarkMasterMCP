# スマートツール使用ガイド

LarkMasterMCPの最も強力な機能である「スマートツール」の詳細な使い方を説明します。

---

## 概要

スマートツールは、自然言語からLarkの機能を自動的に実行する7つの高度なツールです。

| ツール名 | 機能 |
|---------|------|
| `smart_build_bitable` | 自然言語からBitableを自動構築 |
| `process_lark_message` | メッセージを解析して適切なツールを実行 |
| `generate_bitable_documentation` | Bitable設計のドキュメントを生成 |
| `create_bitable_with_wiki` | Bitable + Wiki同時作成 |
| `list_bitable_templates` | テンプレート一覧を表示 |
| `analyze_message_intent` | メッセージの意図を分析 |
| `get_lark_bot_help` | ヘルプ情報を表示 |

---

## 1. smart_build_bitable

### 説明
自然言語の説明からBitable（多次元テーブル）を自動的に設計・構築します。

### 使用例

```json
{
  "tool": "smart_build_bitable",
  "arguments": {
    "message": "顧客管理テーブルを作成して",
    "name": "CRM System"
  }
}
```

### パラメータ

| パラメータ | 必須 | 説明 |
|-----------|------|------|
| `message` | ✅ | 作りたいテーブルの説明 |
| `name` | ❌ | Bitable名（省略時は自動生成） |
| `folder_token` | ❌ | 作成先フォルダ |

### 対応テンプレート

以下のキーワードでテンプレートが自動選択されます：

| キーワード | テンプレート | 生成されるフィールド |
|-----------|-------------|---------------------|
| 顧客, クライアント, 営業, CRM | 顧客管理 | 会社名, 担当者名, メール, 電話, ステータス, 優先度, 担当営業, 次回アクション日, 備考 |
| プロジェクト, タスク, 進捗, TODO | プロジェクト管理 | タスク名, 説明, ステータス, 優先度, 担当者, 開始日, 期限, 進捗率, 添付ファイル |
| 在庫, 商品, 倉庫 | 在庫管理 | 商品名, SKU, カテゴリ, 在庫数, 発注点, 単価, 仕入先, 最終入荷日 |
| 売上, 販売, 収益 | 売上管理 | 取引日, 顧客名, 商品/サービス, 数量, 単価, 売上金額, 支払方法, ステータス |
| イベント, セミナー, 勉強会 | イベント管理 | イベント名, 説明, 開催日, 場所, 定員, 参加者数, ステータス, URL |
| 採用, 人事, 候補者, 面接 | 採用管理 | 候補者名, メール, 電話, 応募職種, 選考ステータス, 面接日, 評価, メモ |
| 問い合わせ, サポート, チケット | 問い合わせ管理 | 問い合わせ番号, タイトル, 内容, 顧客名, カテゴリ, 優先度, ステータス |
| 会議, ミーティング, 議事録 | 会議メモ | 会議タイトル, 開催日時, 参加者, 議事内容, 決定事項, 次回アクション |

### 戻り値の例

```json
{
  "success": true,
  "app": {
    "app_token": "bascnxxxxxxxx"
  },
  "tables": [...],
  "design": {
    "name": "顧客管理Base",
    "tables": [
      {
        "name": "顧客管理",
        "fields": [
          {"name": "会社名", "type": "TEXT"},
          {"name": "ステータス", "type": "SELECT"}
        ]
      }
    ]
  }
}
```

---

## 2. process_lark_message

### 説明
チャットメッセージを解析し、意図を判断して適切なMCPツールを自動実行します。

### 使用例

```json
{
  "tool": "process_lark_message",
  "arguments": {
    "message": "顧客管理システムを作って"
  }
}
```

### 対応コマンド

| メッセージ例 | 実行される処理 |
|-------------|--------------|
| 「顧客管理テーブルを作成して」 | Bitable作成 |
| 「プロジェクト管理のベースを作って」 | Bitable作成 |
| 「Wikiスペースを作成」 | Wiki作成 |
| 「ドキュメントを作成」 | ドキュメント作成 |
| 「タスクを追加: レビュー依頼」 | タスク作成 |
| 「〇〇を検索」 | 検索実行 |
| 「ヘルプ」 | ヘルプ表示 |

### 戻り値

```json
{
  "success": true,
  "command_type": "create_bitable",
  "message": "✅ Bitableを作成しました！\n\n**Base名:** 顧客管理Base\n**URL:** https://...",
  "data": {...}
}
```

---

## 3. generate_bitable_documentation

### 説明
Bitable設計のドキュメントをMarkdown形式で生成します。

### 使用例

```json
{
  "tool": "generate_bitable_documentation",
  "arguments": {
    "message": "顧客管理",
    "name": "CRM"
  }
}
```

### 生成されるドキュメント例

```markdown
# CRM

顧客情報を管理するテーブル

---

# 顧客管理

顧客情報を管理するテーブル

## フィールド一覧

| フィールド名 | タイプ | 説明 |
|------------|--------|------|
| 会社名 | TEXT |  |
| ステータス | SELECT | (選択肢: リード, 商談中, 契約済み, 休眠) |

---

## 使い方

1. 各テーブルにデータを入力してください
2. ビューを切り替えて様々な角度からデータを確認できます
3. フィルターや並び替えで必要な情報を絞り込めます
```

---

## 4. create_bitable_with_wiki

### 説明
Bitableを作成し、同時にWikiスペースとドキュメントも自動生成する複合ツールです。

### 使用例

```json
{
  "tool": "create_bitable_with_wiki",
  "arguments": {
    "message": "プロジェクト管理システム",
    "name": "Project Management"
  }
}
```

### 実行される処理

1. **Bitable作成**: 指定されたシステムのBitableを構築
2. **Wikiスペース作成**: `{name} Wiki` という名前のスペースを作成
3. **ドキュメント生成**: システムのマニュアルを自動生成してWikiに公開

### 戻り値

```json
{
  "bitable": {
    "success": true,
    "app": {...}
  },
  "wiki": {
    "space": {
      "space_id": "xxxxxxxx"
    }
  },
  "documentation": {...}
}
```

---

## 5. list_bitable_templates

### 説明
利用可能なBitableテンプレートの一覧とその構造を表示します。

### 使用例

```json
{
  "tool": "list_bitable_templates",
  "arguments": {}
}
```

### 戻り値

```json
{
  "templates": {
    "顧客管理": {
      "name": "顧客管理",
      "description": "顧客情報を管理するテーブル",
      "fields": [
        {"name": "会社名", "type": "TEXT"},
        {"name": "担当者名", "type": "TEXT"},
        {"name": "ステータス", "type": "SELECT"}
      ]
    },
    "プロジェクト管理": {...},
    "在庫管理": {...}
  }
}
```

---

## 6. analyze_message_intent

### 説明
メッセージを解析して、どのコマンドとして認識されるかを返します（実行はしません）。

### 使用例

```json
{
  "tool": "analyze_message_intent",
  "arguments": {
    "message": "顧客管理テーブルを作成して"
  }
}
```

### 戻り値

```json
{
  "command_type": "create_bitable",
  "confidence": 0.7,
  "parameters": {
    "raw_message": "顧客管理テーブルを作成して"
  },
  "original_message": "顧客管理テーブルを作成して"
}
```

### 信頼度（confidence）の解釈

| 値 | 意味 |
|----|------|
| 0.7以上 | 高確度で意図を認識 |
| 0.3-0.7 | 中程度の確度 |
| 0.3未満 | 認識困難、ヘルプを提示 |

---

## 7. get_lark_bot_help

### 説明
LarkMasterMCP Botの機能一覧とヘルプ情報を表示します。

### 使用例

```json
{
  "tool": "get_lark_bot_help",
  "arguments": {}
}
```

### 戻り値

```json
{
  "help_text": "🤖 **Lark Master MCP Bot** へようこそ！\n\n以下のことができます：\n\n📊 **Bitable (多次元テーブル)**\n• 「顧客管理テーブルを作成して」\n...",
  "templates": [
    "顧客管理",
    "プロジェクト管理",
    "在庫管理",
    "売上管理",
    "イベント管理",
    "採用管理",
    "問い合わせ管理",
    "会議メモ"
  ]
}
```

---

## 実践的な使用シナリオ

### シナリオ1: CRMシステムの構築

```
ユーザー: 「営業チーム用のCRMシステムを作成して、Wikiにマニュアルも作って」

AIが実行:
1. create_bitable_with_wiki(message="顧客管理システム", name="Sales CRM")
   → Bitable + Wiki + ドキュメント自動生成

結果:
- 顧客管理Bitableが作成される
- Wiki スペース「Sales CRM Wiki」が作成される
- 使い方マニュアルが自動生成される
```

### シナリオ2: チャットボット対応

```
ユーザーがLarkチャットで: 「プロジェクト管理のテーブル作って」

AIが実行:
1. process_lark_message(message="プロジェクト管理のテーブル作って")
   → 自動で smart_build_bitable が実行される

結果:
- プロジェクト管理Bitableが自動作成
- チャットに作成結果が返信される
```

### シナリオ3: テンプレートの確認と選択

```
ユーザー: 「どんなテンプレートがある？」

AIが実行:
1. list_bitable_templates()

結果:
- 8種類のテンプレート一覧が表示
- 各テンプレートのフィールド構成を確認可能
```

---

## 拡張方法

### カスタムテンプレートの追加

`smart_builder.py` の `TEMPLATES` ディクショナリに追加:

```python
TEMPLATES = {
    ...
    "新しいテンプレート": {
        "name": "新しいテンプレート",
        "description": "説明",
        "fields": [
            FieldDefinition("フィールド1", FieldType.TEXT),
            FieldDefinition("フィールド2", FieldType.SELECT, options=["A", "B", "C"]),
        ]
    }
}
```

### キーワードマッピングの追加

`KEYWORD_TEMPLATE_MAP` に追加:

```python
KEYWORD_TEMPLATE_MAP = {
    ...
    "新しいキーワード": "新しいテンプレート",
}
```

---

## 注意事項

1. **API権限**: Bitable作成には `bitable:app` 権限が必要
2. **レート制限**: Lark APIには呼び出し制限があります
3. **テナントトークン**: 現在はテナントアクセストークンのみサポート

---

## 関連ドキュメント

- [README.md](../README.md) - プロジェクト概要
- [SETUP_GUIDE.md](./SETUP_GUIDE.md) - セットアップ手順
- [Lark Open Platform](https://open.larksuite.com/document) - 公式ドキュメント
