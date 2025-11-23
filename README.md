# 🚀 LarkMasterMCP - スーパーLark MCP

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tools](https://img.shields.io/badge/Tools-108-purple.svg)](#利用可能なツール)

**自然言語でLarkを操作できる、最も包括的なMCPサーバー**

「顧客管理テーブルを作成して」と言うだけで、AIが自動的にBitableを設計・構築します。

---

## ✨ 特徴

| 機能 | 説明 |
|------|------|
| 🧠 **スマートBitable構築** | 自然言語からデータベースを自動設計・作成 |
| 📚 **自動ドキュメント生成** | 作成したシステムのWikiマニュアルを自動生成 |
| 🤖 **108個のツール** | Larkの全機能を網羅した最も包括的な実装 |
| 🎯 **8種類のテンプレート** | 顧客管理、プロジェクト管理、在庫管理など |
| 🔧 **簡単セットアップ** | App IDとSecretを設定するだけ |

---

## 📦 インストール

### 必要なもの
- Python 3.8以上
- Larkアプリの認証情報（[取得方法](#larkアプリの作成)）

### 手順

```bash
# 1. リポジトリをクローン
git clone https://github.com/IvyGain/LarkMasterMCP.git
cd LarkMasterMCP

# 2. インストール
pip install -e .

# 3. 環境設定
cp .env.example .env
```

### 環境変数の設定

`.env` ファイルを編集して、あなたのLarkアプリの認証情報を設定：

```env
LARK_APP_ID=cli_あなたのAppID
LARK_APP_SECRET=あなたのAppSecret
```

---

## 🔧 AIクライアントでの設定

### Claude Desktop

`~/Library/Application Support/Claude/claude_desktop_config.json` (Mac)
`%APPDATA%\Claude\claude_desktop_config.json` (Windows)

```json
{
  "mcpServers": {
    "lark-master": {
      "command": "lark-mcp",
      "env": {
        "LARK_APP_ID": "cli_あなたのAppID",
        "LARK_APP_SECRET": "あなたのAppSecret"
      }
    }
  }
}
```

### Cursor

`.cursor/mcp.json` をプロジェクトルートに作成：

```json
{
  "mcpServers": {
    "lark-master": {
      "command": "lark-mcp",
      "env": {
        "LARK_APP_ID": "cli_あなたのAppID",
        "LARK_APP_SECRET": "あなたのAppSecret"
      }
    }
  }
}
```

### VS Code (Claude Code Extension)

`.vscode/settings.json`:

```json
{
  "claude-code.mcpServers": {
    "lark-master": {
      "command": "lark-mcp",
      "env": {
        "LARK_APP_ID": "cli_あなたのAppID",
        "LARK_APP_SECRET": "あなたのAppSecret"
      }
    }
  }
}
```

---

## 🎮 使い方

### 起動

```bash
lark-mcp
```

### AIに話しかけるだけ

設定が完了したら、Claudeなどに以下のように話しかけるだけです：

```
「顧客管理テーブルを作成して」
「プロジェクト管理システムをWiki付きで作って」
「在庫管理用のデータベースを構築して」
```

AIが自動的に：
1. 適切なテーブル構造を設計
2. フィールドとタイプを選択
3. Bitableを作成
4. （オプション）Wikiドキュメントも生成

---

## 🧠 スマートツール

### smart_build_bitable
自然言語からBitableを自動構築

```
入力: 「顧客管理テーブルを作成して」

出力:
- 会社名（テキスト）
- 担当者名（テキスト）
- メールアドレス（テキスト）
- 電話番号（電話）
- ステータス（選択: リード, 商談中, 契約済み, 休眠）
- 優先度（選択: 高, 中, 低）
- 担当営業（担当者）
- 次回アクション日（日付）
- 備考（テキスト）
```

### process_lark_message
メッセージを解析して自動実行

| メッセージ | 実行される処理 |
|-----------|--------------|
| 「顧客管理テーブルを作成」 | Bitable作成 |
| 「Wikiスペースを作成」 | Wiki作成 |
| 「タスクを追加: 〇〇」 | タスク作成 |
| 「ヘルプ」 | ヘルプ表示 |

### create_bitable_with_wiki
Bitable + Wiki + ドキュメントを一括作成

```json
{
  "message": "プロジェクト管理システム",
  "name": "Project Manager"
}
```

→ Bitable作成 + Wikiスペース作成 + マニュアル自動生成

---

## 📋 利用可能なテンプレート

| テンプレート | 用途 | 主なフィールド |
|-------------|------|---------------|
| 顧客管理 | CRM、営業管理 | 会社名, 担当者, ステータス, 優先度 |
| プロジェクト管理 | タスク管理、進捗管理 | タスク名, ステータス, 担当者, 期限 |
| 在庫管理 | 商品・倉庫管理 | 商品名, SKU, 在庫数, 単価 |
| 売上管理 | 販売・収益管理 | 取引日, 顧客, 金額, 支払方法 |
| イベント管理 | セミナー・イベント | イベント名, 日時, 定員, 参加者数 |
| 採用管理 | 人事・採用 | 候補者, 職種, 選考ステータス, 評価 |
| 問い合わせ管理 | サポート・チケット | タイトル, カテゴリ, 優先度, ステータス |
| 会議メモ | 議事録管理 | 会議名, 参加者, 議事内容, 決定事項 |

---

## 🛠️ 全108ツール一覧

<details>
<summary>📨 メッセージング（16ツール）</summary>

| ツール | 機能 |
|-------|------|
| `send_message` | メッセージ送信 |
| `reply_message` | 返信 |
| `search_messages` | メッセージ検索 |
| `list_chats` | チャット一覧 |
| `create_chat_group` | グループ作成 |
| `get_chat_members` | メンバー取得 |
| `add_bot_to_chat` | Bot追加 |
| `create_poll` | 投票作成 |
| `add_message_reaction` | リアクション追加 |
| `delete_message_reaction` | リアクション削除 |
| `pin_message` | ピン留め |
| `unpin_message` | ピン解除 |
| `forward_message` | 転送 |
| `send_urgent_message` | 緊急メッセージ |
| `read_message` | 既読にする |
| `get_message_read_users` | 既読者取得 |

</details>

<details>
<summary>📅 カレンダー（12ツール）</summary>

| ツール | 機能 |
|-------|------|
| `create_calendar_event` | 予定作成 |
| `get_user_calendar` | 予定取得 |
| `create_meeting` | 会議作成 |
| `share_screen` | 画面共有 |
| `set_out_of_office` | 不在設定 |
| `list_free_busy` | 空き時間確認 |
| `create_calendar_reminder` | リマインダー |
| `create_recurring_event` | 繰り返し予定 |
| `book_meeting_room` | 会議室予約 |
| `search_meeting_rooms` | 会議室検索 |
| `accept_calendar_event` | 予定承諾 |
| `decline_calendar_event` | 予定辞退 |

</details>

<details>
<summary>📄 ドキュメント（17ツール）</summary>

| ツール | 機能 |
|-------|------|
| `create_document` | ドキュメント作成 |
| `upload_file` | ファイルアップロード |
| `create_drive_folder` | フォルダ作成 |
| `share_file` | ファイル共有 |
| `get_spreadsheet_data` | スプレッドシート読取 |
| `update_spreadsheet_data` | スプレッドシート更新 |
| `search_documents` | ドキュメント検索 |
| `import_document` | インポート |
| `export_document` | エクスポート |
| `get_document_content` | 内容取得 |
| `add_document_permission` | 権限追加 |
| `add_document_comment` | コメント追加 |
| `get_document_comments` | コメント取得 |
| `create_document_from_template` | テンプレートから作成 |
| `lock_document_section` | セクションロック |
| `unlock_document_section` | ロック解除 |
| `subscribe_document_changes` | 変更監視 |

</details>

<details>
<summary>📊 Bitable（12ツール）</summary>

| ツール | 機能 |
|-------|------|
| `create_bitable_app` | Base作成 |
| `create_bitable_table` | テーブル作成 |
| `create_bitable_view` | ビュー作成 |
| `add_bitable_field` | フィールド追加 |
| `update_bitable_field` | フィールド更新 |
| `get_bitable_fields` | フィールド取得 |
| `get_bitable_records` | レコード取得 |
| `batch_create_records` | 一括作成 |
| `batch_update_records` | 一括更新 |
| `delete_bitable_records` | レコード削除 |
| `search_bitable_records` | レコード検索 |
| `get_bitable_views` | ビュー一覧 |
| `update_bitable_view` | ビュー更新 |

</details>

<details>
<summary>✅ タスク・ワークフロー（12ツール）</summary>

| ツール | 機能 |
|-------|------|
| `create_task` | タスク作成 |
| `update_task_status` | ステータス更新 |
| `add_task_reminder` | リマインダー |
| `create_approval` | 承認申請 |
| `get_approval_status` | 承認状況確認 |
| `transfer_approval` | 承認転送 |
| `cancel_approval` | 承認キャンセル |
| `cc_approval` | CC追加 |
| `add_approval_comment` | コメント追加 |
| `rollback_approval` | 差し戻し |
| `create_workflow` | ワークフロー作成 |
| `execute_workflow` | ワークフロー実行 |

</details>

<details>
<summary>📚 その他（39ツール）</summary>

**Wiki（3ツール）**: `create_wiki_space`, `create_wiki_page`, `search_wiki`

**ビデオ会議（3ツール）**: `start_meeting_recording`, `stop_meeting_recording`, `get_meeting_recording`

**HR・組織（5ツール）**: `get_user_info`, `get_department_users`, `get_user_by_email_or_phone`, `create_leave_request`, `get_attendance_records`

**ヘルプデスク（4ツール）**: `create_helpdesk_ticket`, `get_helpdesk_ticket`, `update_helpdesk_ticket`, `list_helpdesk_tickets`

**ドライブ高度（4ツール）**: `create_file_version`, `get_file_versions`, `update_file_permission`, `get_file_permissions`

**Bot管理（3ツール）**: `create_bot_menu`, `update_bot_info`, `subscribe_events`

**管理・セキュリティ（3ツール）**: `get_app_usage_stats`, `get_audit_logs`, `manage_app_permissions`

**AI（2ツール）**: `create_ai_agent`, `chat_with_ai`

**OKR（2ツール）**: `create_okr`, `update_okr_progress`

**フォーム（2ツール）**: `create_form`, `get_form_responses`

**スマートツール（7ツール）**: `smart_build_bitable`, `process_lark_message`, `generate_bitable_documentation`, `create_bitable_with_wiki`, `list_bitable_templates`, `analyze_message_intent`, `get_lark_bot_help`

</details>

---

## 🔑 Larkアプリの作成

### 1. Lark Open Platformにアクセス

- **国際版**: https://open.larksuite.com/app
- **中国版（飛書）**: https://open.feishu.cn/app

### 2. アプリを作成

1. 「Create App」をクリック
2. 「Custom App」を選択
3. アプリ名と説明を入力
4. 作成完了

### 3. 認証情報を取得

1. 作成したアプリをクリック
2. 「Credentials & Basic Info」に移動
3. **App ID** と **App Secret** をコピー

### 4. 権限を設定

「Permissions & Scopes」で以下の権限を追加：

**必須権限:**
- `im:message` - メッセージング
- `bitable:app` - Bitable操作
- `docs:doc` - ドキュメント
- `wiki:wiki` - Wiki
- `contact:user.base:readonly` - ユーザー情報

### 5. アプリを公開

「App Release」からバージョンを作成し、公開

---

## 📁 プロジェクト構成

```
LarkMasterMCP/
├── src/lark_master_mcp/
│   ├── __init__.py          # パッケージ初期化
│   ├── server.py            # MCPサーバー本体
│   ├── lark_client.py       # Lark APIクライアント
│   ├── tools.py             # 108ツール定義
│   ├── cli.py               # コマンドラインインターフェース
│   ├── smart_builder.py     # スマートBitable構築エンジン
│   └── message_handler.py   # メッセージ解析・処理
├── docs/
│   ├── SETUP_GUIDE.md       # セットアップガイド
│   └── SMART_TOOLS_GUIDE.md # スマートツールガイド
├── .env.example             # 環境変数テンプレート
└── README.md                # このファイル
```

---

## 🌐 リモートMCPサーバー

### ローカルでリモートサーバー起動

```bash
# リモートサーバーを起動（HTTP/SSE対応）
lark-mcp-server

# または直接実行
python -m lark_master_mcp.remote_server
```

サーバーが `http://localhost:8000` で起動します。

### APIエンドポイント

| エンドポイント | 説明 |
|--------------|------|
| `GET /` | サーバー情報 |
| `GET /health` | ヘルスチェック |
| `GET /tools` | ツール一覧（108個） |
| `POST /call` | ツール実行 |
| `GET /sse` | SSEストリーム接続 |
| `POST /sse/call` | SSEでツール実行 |

### 使用例

```bash
# ヘルスチェック
curl http://localhost:8000/health

# ツール一覧
curl http://localhost:8000/tools

# ツール実行
curl -X POST http://localhost:8000/call \
  -H "Content-Type: application/json" \
  -d '{"name": "list_bitable_templates", "arguments": {}}'

# スマートBitable作成
curl -X POST http://localhost:8000/call \
  -H "Content-Type: application/json" \
  -d '{"name": "smart_build_bitable", "arguments": {"message": "顧客管理テーブルを作成"}}'
```

### Dockerでデプロイ

```bash
# ビルド
docker build -t lark-master-mcp .

# 起動
docker run -d -p 8000:8000 \
  -e LARK_APP_ID=cli_xxxxx \
  -e LARK_APP_SECRET=xxxxx \
  lark-master-mcp

# または docker-compose
docker-compose up -d
```

### クラウドにデプロイ

**Railway:**
```bash
# railway.jsonを使用
railway up
```

**Render:**
```bash
# render.yamlを使用してデプロイ
# 環境変数にLARK_APP_IDとLARK_APP_SECRETを設定
```

**Fly.io:**
```bash
fly launch
fly secrets set LARK_APP_ID=cli_xxxxx LARK_APP_SECRET=xxxxx
fly deploy
```

---

## 🤖 Lark Bot（@メンションで操作）

### Bot機能の概要

LarkチャットでBotに@メンションして話しかけると、自動的にMCPツールを実行して返信します。

```
@LarkMCP 顧客管理テーブルを作成して
```
↓
Botが自動でBitableを作成して結果を返信！

### Botのセットアップ

1. **サーバーをデプロイ**（上記参照）

2. **Lark Open Platformで設定**
   - Bot機能を有効化
   - Event Subscriptionを設定:
     ```
     https://your-server.com/webhook/event
     ```
   - 必要な権限を追加:
     - `im:message`
     - `im:message:send_as_bot`
     - `bitable:app`

3. **Botをチャットに追加**
   - チャット設定 → Bot → 追加

詳細は [BOT_SETUP_GUIDE.md](docs/BOT_SETUP_GUIDE.md) を参照

### 使用例

| メッセージ | 動作 |
|-----------|------|
| `@Bot 顧客管理テーブルを作成して` | 顧客管理Bitableを作成 |
| `@Bot プロジェクト管理のベース作って` | プロジェクト管理Bitableを作成 |
| `@Bot Wikiスペースを作成` | Wikiスペースを作成 |
| `@Bot ヘルプ` | 使い方を表示 |

---

## 🔒 セキュリティ

- 認証情報は環境変数で管理（コードに埋め込まない）
- OAuth 2.0 テナントアクセストークン使用
- すべての通信はHTTPS
- トークンは自動更新

---

## 🛠️ 開発者向け

```bash
# 開発用インストール
pip install -e ".[dev]"

# テスト実行
pytest

# コードフォーマット
black src/

# 型チェック
mypy src/

# リント
ruff src/
```

---

## 📞 サポート

- **Issues**: [GitHub Issues](https://github.com/IvyGain/LarkMasterMCP/issues)
- **Lark公式ドキュメント**: [open.larksuite.com](https://open.larksuite.com/document)

---

## 📜 ライセンス

MIT License - 自由に使用・改変・配布できます。

---

## 🙏 謝辞

- [Lark Open Platform](https://open.larksuite.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Anthropic Claude](https://claude.ai/)

---

## 📝 更新履歴

### v0.2.0 (2024-11)
- 🧠 スマートツール7個追加（合計108ツール）
- 📊 SmartBitableBuilder：自然言語からBitable自動構築
- 📝 MessageHandler：メッセージ解析・自動実行
- 📚 DocumentationGenerator：Wiki自動生成
- 📖 日本語ドキュメント整備

### v0.1.0
- 初回リリース
- 101個の基本ツール
- MCP基本機能

---

<div align="center">

**⭐ このプロジェクトが役に立ったら、スターをお願いします！ ⭐**

Made with ❤️ by [IvyGain](https://github.com/IvyGain)

</div>
