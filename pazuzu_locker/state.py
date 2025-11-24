from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

STATE_DIR = Path.home() / ".pazuzu-locker"
STATE_FILE = STATE_DIR / "last_run.json"


def save_summary(summary: Dict[str, Any]) -> Path:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    summary = {**summary, "saved_at": datetime.utcnow().isoformat()}
    STATE_FILE.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return STATE_FILE


def load_summary() -> Optional[Dict[str, Any]]:
    if not STATE_FILE.exists():
        return None
    content = STATE_FILE.read_text(encoding="utf-8")
    return json.loads(content)
