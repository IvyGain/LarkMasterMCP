# LarkMasterMCP Docker Image
# 自然言語でLarkを操作できるMCPサーバー

FROM python:3.11-slim

# メタデータ
LABEL maintainer="IvyGain"
LABEL description="LarkMasterMCP - 108ツールを持つ最も包括的なLark MCPサーバー"
LABEL version="0.2.0"

# 作業ディレクトリ
WORKDIR /app

# システム依存関係
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係をコピーしてインストール
COPY pyproject.toml .
COPY src/ ./src/

# パッケージインストール
RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir fastapi uvicorn

# ポート公開
EXPOSE 8000

# 環境変数（デフォルト値）
ENV LARK_APP_ID=""
ENV LARK_APP_SECRET=""
ENV PORT=8000
ENV HOST=0.0.0.0

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# 起動コマンド
CMD ["python", "-m", "lark_master_mcp.remote_server"]
