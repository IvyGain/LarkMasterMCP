# LarkMasterMCP セットアップガイド

## 📋 目次
1. [前提条件](#前提条件)
2. [Larkアプリの作成](#larkアプリの作成)
3. [権限の設定](#権限の設定)
4. [インストール](#インストール)
5. [AIクライアント設定](#aiクライアント設定)
6. [動作確認](#動作確認)
7. [トラブルシューティング](#トラブルシューティング)

---

## 前提条件

- Python 3.8以上
- pip (Pythonパッケージマネージャー)
- Larkアカウント（管理者権限推奨）

---

## Larkアプリの作成

### 1. Lark Open Platformにアクセス

**国際版（Lark）:**
https://open.larksuite.com/app

**中国版（飛書/Feishu）:**
https://open.feishu.cn/app

### 2. 新規アプリを作成

1. 「Create App」または「创建应用」をクリック
2. 「Custom App」を選択
3. アプリ名を入力（例: "LarkMasterMCP"）
4. アプリの説明を入力
5. 「Create」をクリック

### 3. 認証情報を取得

1. 作成したアプリをクリック
2. 「Credentials & Basic Info」に移動
3. 以下をコピーして保存:
   - **App ID**: `cli_xxxxxxxxxx`
   - **App Secret**: `xxxxxxxxxxxxxxxxxx`

---

## 権限の設定

### 必要な権限一覧

アプリに以下の権限を追加してください:

#### メッセージング
- `im:message` - メッセージの送受信
- `im:message:send_as_bot` - Botとしてメッセージ送信
- `im:chat` - チャット情報の取得
- `im:chat:create` - チャットグループの作成

#### カレンダー
- `calendar:calendar` - カレンダーアクセス
- `calendar:calendar:readonly` - カレンダー読み取り

#### ドキュメント
- `docs:doc` - ドキュメント操作
- `drive:drive` - ドライブ操作

#### Bitable (多次元テーブル)
- `bitable:app` - Bitableアプリ操作
- `bitable:table` - テーブル操作

#### Wiki
- `wiki:wiki` - Wikiスペース操作

#### ユーザー情報
- `contact:user.base:readonly` - ユーザー基本情報読み取り
- `contact:department.base:readonly` - 部門情報読み取り

### 権限の追加方法

1. アプリ設定 → 「Permissions & Scopes」
2. 「Add Scopes」をクリック
3. 上記の権限を検索して追加
4. 「Save」をクリック

### アプリの公開

1. 「App Release」または「版本管理与发布」に移動
2. 「Create Version」をクリック
3. バージョン情報を入力
4. 「Submit for Review」で審査に提出
5. （内部アプリの場合は自動承認される場合があります）

---

## インストール

### 方法1: pipで直接インストール

```bash
# リポジトリをクローン
git clone https://github.com/IvyGain/LarkMasterMCP.git
cd LarkMasterMCP

# インストール
pip install -e .
```

### 方法2: 仮想環境を使用（推奨）

```bash
# リポジトリをクローン
git clone https://github.com/IvyGain/LarkMasterMCP.git
cd LarkMasterMCP

# 仮想環境を作成
python -m venv venv

# アクティベート
# macOS/Linux:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# インストール
pip install -e .
```

### 環境変数の設定

```bash
# .envファイルを作成
cp .env.example .env

# 編集
nano .env  # または任意のエディタで編集
```

`.env`ファイルの内容:
```
LARK_APP_ID=cli_xxxxxxxxxx
LARK_APP_SECRET=xxxxxxxxxxxxxxxxxx
```

---

## AIクライアント設定

### Claude Desktop

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "lark-master": {
      "command": "lark-mcp",
      "env": {
        "LARK_APP_ID": "cli_xxxxxxxxxx",
        "LARK_APP_SECRET": "xxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

### Cursor

`.cursor/mcp.json` をプロジェクトルートに作成:

```json
{
  "mcpServers": {
    "lark-master": {
      "command": "lark-mcp",
      "env": {
        "LARK_APP_ID": "cli_xxxxxxxxxx",
        "LARK_APP_SECRET": "xxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

### VS Code + Claude Code Extension

`.vscode/settings.json`:

```json
{
  "claude-code.mcpServers": {
    "lark-master": {
      "command": "lark-mcp",
      "env": {
        "LARK_APP_ID": "cli_xxxxxxxxxx",
        "LARK_APP_SECRET": "xxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

### 絶対パスを使用する場合

`lark-mcp` がPATHにない場合:

```json
{
  "mcpServers": {
    "lark-master": {
      "command": "/Users/yourname/LarkMasterMCP/venv/bin/lark-mcp",
      "env": {
        "LARK_APP_ID": "cli_xxxxxxxxxx",
        "LARK_APP_SECRET": "xxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

または Python経由:

```json
{
  "mcpServers": {
    "lark-master": {
      "command": "python",
      "args": ["-m", "lark_master_mcp.cli"],
      "cwd": "/Users/yourname/LarkMasterMCP",
      "env": {
        "LARK_APP_ID": "cli_xxxxxxxxxx",
        "LARK_APP_SECRET": "xxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

---

## 動作確認

### 1. コマンドラインでテスト

```bash
# MCPサーバーを起動
lark-mcp

# 正常に起動すると以下のようなログが表示:
# INFO:lark_master_mcp.server:Initializing LarkMasterMCP server with 108 tools
```

### 2. AIクライアントでテスト

Claude Desktopなどで以下のようなプロンプトを試す:

```
Larkで顧客管理テーブルを作成して
```

期待される結果:
- Bitableが自動で作成される
- 会社名、担当者名、メールアドレス等のフィールドが自動設定される

### 3. 利用可能なツールを確認

```
Larkで使えるツールを教えて
```

または `get_lark_bot_help` ツールを実行

---

## トラブルシューティング

### よくあるエラー

#### 1. "Failed to get access token"

**原因:** App IDまたはApp Secretが間違っている

**解決策:**
- `.env`ファイルの認証情報を確認
- Lark Open Platformで認証情報を再確認

#### 2. "Permission denied" エラー

**原因:** 必要な権限がアプリに付与されていない

**解決策:**
- Lark Open Platformで権限を追加
- アプリを再公開

#### 3. "lark-mcp: command not found"

**原因:** PATHが通っていない

**解決策:**
```bash
# pipでインストール場所を確認
pip show lark-master-mcp

# 絶対パスで実行
/path/to/venv/bin/lark-mcp

# またはPython経由
python -m lark_master_mcp.cli
```

#### 4. Bitableが作成されない

**原因:** `bitable:app` 権限がない

**解決策:**
- Lark Open Platformで `bitable:app` 権限を追加
- アプリを再公開

### ログの確認

詳細なログを有効にする:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### サポート

- [GitHub Issues](https://github.com/IvyGain/LarkMasterMCP/issues)
- [Lark Open Platform ドキュメント](https://open.larksuite.com/document)

---

## 次のステップ

セットアップが完了したら:

1. **Smart Tools を試す**: `smart_build_bitable` で自然言語からテーブル作成
2. **テンプレートを確認**: `list_bitable_templates` で利用可能なテンプレートを表示
3. **メッセージ処理**: `process_lark_message` でチャットbot機能をテスト

詳しい使い方は [README.md](../README.md) を参照してください。
