from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Any


def _safe_filename(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name[:80] if name else "paper"


def save_report(report: Dict[str, Any], output_dir: str | Path) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    title = report.get("metadata", {}).get("title") or "paper"
    filename = _safe_filename(title) + ".json"
    path = output_dir / filename

    with path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return path
