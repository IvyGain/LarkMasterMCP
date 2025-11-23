# Lark Bot セットアップガイド

LarkMasterMCP BotをLarkチャットで@メンションして使えるようにする設定手順です。

---

## 概要

```
ユーザー                    サーバー                    Lark API
   │                          │                          │
   │  @LarkMCP 顧客管理作成    │                          │
   │─────────────────────────>│                          │
   │                          │  Webhook受信              │
   │                          │─────────────────────────>│
   │                          │                          │
   │                          │  MCPツール実行            │
   │                          │  (smart_build_bitable)   │
   │                          │                          │
   │                          │  Bitable作成              │
   │                          │─────────────────────────>│
   │                          │                          │
   │                          │  返信メッセージ送信       │
   │                          │─────────────────────────>│
   │                          │                          │
   │  ✅ Bitable作成完了！     │                          │
   │<─────────────────────────│                          │
```

---

## 手順

### 1. サーバーをデプロイ

まず、LarkMasterMCPサーバーを公開URLでアクセスできる場所にデプロイします。

**ローカル（ngrok使用）:**
```bash
# サーバー起動
lark-mcp-server

# 別ターミナルでngrok
ngrok http 8000
# → https://xxxx.ngrok.io が公開URL
```

**Railway:**
```bash
railway up
# 自動でURLが発行される
```

**Render/Fly.io:**
デプロイ後に発行されるURLを使用

### 2. Lark Open Platformでアプリを設定

#### 2.1 アプリを作成（既存の場合はスキップ）

1. [Lark Open Platform](https://open.larksuite.com/app) にアクセス
2. 「Create App」→「Custom App」
3. アプリ名: `LarkMCP`（任意）

#### 2.2 Bot機能を有効化

1. アプリ設定画面で「Add Capabilities」
2. 「Bot」を選択して追加

#### 2.3 権限を設定

「Permissions & Scopes」で以下を追加:

**必須:**
- `im:message` - メッセージの読み取り
- `im:message:send_as_bot` - Botとしてメッセージ送信
- `im:chat:readonly` - チャット情報読み取り

**Bitable操作用:**
- `bitable:app` - Bitable作成・操作

**Wiki操作用:**
- `wiki:wiki` - Wiki作成・操作

**ドキュメント操作用:**
- `docs:doc` - ドキュメント作成・操作

#### 2.4 Event Subscriptionを設定

1. 「Event Subscriptions」に移動
2. 「Request URL」に以下を入力:
   ```
   https://your-server.com/webhook/event
   ```
   例: `https://xxxx.ngrok.io/webhook/event`

3. URL検証が自動で実行されます（サーバーが起動している必要あり）

4. 「Add Events」で以下を追加:
   - `im.message.receive_v1` - メッセージ受信
   - `im.chat.member.bot.added_v1` - Bot追加（ウェルカムメッセージ用）

#### 2.5 アプリを公開

1. 「App Release」に移動
2. 「Create Version」
3. 「Submit」で公開

---

### 3. Botをチャットに追加

#### 方法A: チャット設定から追加
1. Larkでチャットを開く
2. 右上の「...」→「設定」
3. 「Bot」→「追加」
4. 作成したBotを選択

#### 方法B: グループ作成時に追加
1. 新規グループ作成
2. メンバー追加画面でBotを検索して追加

#### 方法C: 1対1チャット
1. 「新規チャット」
2. Botを検索して開始

---

### 4. 使ってみる

チャットでBotに@メンションして話しかけます:

```
@LarkMCP 顧客管理テーブルを作成して
```

Botが自動で:
1. メッセージを解析
2. 適切なMCPツールを実行
3. 結果を返信

---

## 使用例

### Bitable作成
```
@LarkMCP 顧客管理テーブルを作成して
```
→ 顧客管理用のBitableが自動作成される

### プロジェクト管理
```
@LarkMCP プロジェクト管理用のベースを作って
```
→ タスク管理用のBitableが作成される

### Wiki作成
```
@LarkMCP Wikiスペースを作成
```
→ ナレッジベースが作成される

### ヘルプ
```
@LarkMCP ヘルプ
```
→ 使い方が表示される

---

## トラブルシューティング

### Botが反応しない

1. **サーバーが起動しているか確認**
   ```bash
   curl https://your-server.com/health
   ```

2. **Webhook URLが正しいか確認**
   - Lark Open Platform → Event Subscriptions
   - Request URLが正しいか確認

3. **権限が付与されているか確認**
   - `im:message` 権限が必要

4. **アプリが公開されているか確認**
   - App Releaseでバージョンが公開済みか確認

### 「Permission denied」エラー

- 必要な権限がアプリに付与されていない
- アプリを再公開する必要がある場合あり

### Webhook URLの検証に失敗

1. サーバーが起動しているか確認
2. URLが正しいか確認（末尾に`/webhook/event`）
3. サーバーログを確認

---

## 環境変数

サーバーに以下を設定:

```env
LARK_APP_ID=cli_xxxxx
LARK_APP_SECRET=xxxxx
```

オプション（Webhook検証用）:
```env
LARK_VERIFICATION_TOKEN=xxxxx
LARK_ENCRYPT_KEY=xxxxx
```

---

## API仕様

### Webhookエンドポイント

**URL:** `POST /webhook/event`

**URL検証リクエスト:**
```json
{
  "type": "url_verification",
  "challenge": "xxx"
}
```

**レスポンス:**
```json
{
  "challenge": "xxx"
}
```

**メッセージイベント:**
```json
{
  "header": {
    "event_type": "im.message.receive_v1"
  },
  "event": {
    "message": {
      "message_id": "xxx",
      "chat_id": "xxx",
      "message_type": "text",
      "content": "{\"text\": \"@_user_1 顧客管理作成\"}"
    },
    "sender": {
      "sender_type": "user"
    }
  }
}
```

---

## 関連ドキュメント

- [README.md](../README.md) - プロジェクト概要
- [SETUP_GUIDE.md](./SETUP_GUIDE.md) - 基本セットアップ
- [SMART_TOOLS_GUIDE.md](./SMART_TOOLS_GUIDE.md) - スマートツール詳細
- [Lark Bot開発ガイド](https://open.larksuite.com/document/home/develop-a-bot)
