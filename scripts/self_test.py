import json
import os
import sys
from pathlib import Path

import chromadb

ROOT = Path(__file__).resolve().parents[2]


def check_env() -> tuple[bool, str]:
    api_key = os.getenv("API_KEY")
    if not api_key:
        return False, "API_KEY missing"
    return True, "API_KEY configured"


def check_chroma() -> tuple[bool, str]:
    db_path = ROOT / "chroma_db"
    try:
        client = chromadb.PersistentClient(path=str(db_path))
        names = [c.name for c in client.list_collections()]
        if "product_manager_knowledge" in names:
            return True, "collection product_manager_knowledge exists"
        return False, "collection product_manager_knowledge missing"
    except Exception as e:
        return False, f"chroma check failed: {e}"


def check_frontend_assets() -> tuple[bool, str]:
    app_html = ROOT / "frontend" / "app.html"
    if app_html.exists():
        return True, "frontend/app.html exists"
    return False, "frontend/app.html missing"


def main() -> int:
    checks = {
        "env": check_env(),
        "chroma": check_chroma(),
        "frontend": check_frontend_assets(),
    }
    payload = {
        "root": str(ROOT),
        "checks": {k: {"ok": ok, "message": msg} for k, (ok, msg) in checks.items()},
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if all(ok for ok, _ in checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
