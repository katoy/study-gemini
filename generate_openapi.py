import json
import sys
import os

# プロジェクトのルートディレクトリをPythonの検索パスに追加
sys.path.insert(0, os.path.abspath("."))

from server.server import app  # server.pyからFastAPIアプリをインポート

# OpenAPIスキーマを生成
openapi_schema = app.openapi()

# JSONファイルとして保存
# `server/apidoc` ディレクトリが確実に存在するように
os.makedirs("server/apidoc", exist_ok=True)
output_path = "server/apidoc/openapi.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(openapi_schema, f, ensure_ascii=False, indent=2)

print(f"OpenAPI schema generated successfully to {output_path}")
