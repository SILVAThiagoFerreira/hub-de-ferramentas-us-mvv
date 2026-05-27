"""Sincronizacao do manifesto gerado com o HTML do front-end."""

from __future__ import annotations

import json
from pathlib import Path

from .exceptions import OutputError


MANIFEST_MARKER_START = "<!-- MANIFEST:START -->"
MANIFEST_MARKER_END = "<!-- MANIFEST:END -->"
MANIFEST_SCRIPT_ID = "initial-manifest"


def sync_manifest_snapshot(index_path: str | Path, manifest_path: str | Path) -> Path:
    index_file = Path(index_path)
    manifest_file = Path(manifest_path)

    if not index_file.exists():
        raise OutputError(f"Frontend HTML not found: {index_file}")
    if not manifest_file.exists():
        raise OutputError(f"Manifest not found for HTML sync: {manifest_file}")

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    snapshot = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"))
    script_block = (
        f'{MANIFEST_MARKER_START}\n'
        f'<script type="application/json" id="{MANIFEST_SCRIPT_ID}">{snapshot}</script>\n'
        f"{MANIFEST_MARKER_END}"
    )

    html = index_file.read_text(encoding="utf-8")
    start = html.find(MANIFEST_MARKER_START)
    end = html.find(MANIFEST_MARKER_END)

    if start == -1 or end == -1 or end < start:
        raise OutputError(
            f"Missing manifest markers in HTML file {index_file}. "
            "Expected <!-- MANIFEST:START --> and <!-- MANIFEST:END -->."
        )

    end += len(MANIFEST_MARKER_END)
    updated_html = html[:start] + script_block + html[end:]
    index_file.write_text(updated_html, encoding="utf-8")
    return index_file
