import json

from app.config import LINKS_FILE


def load_links() -> list[str]:
    """Accepts ["url", ...], [{"url": "..."}, ...] or {"urls": [...]}."""
    if not LINKS_FILE.exists() or not LINKS_FILE.read_text().strip():
        return []
    data = json.loads(LINKS_FILE.read_text())
    if isinstance(data, dict):
        data = data.get("urls") or data.get("links") or []
    links = []
    for item in data:
        if isinstance(item, dict):
            item = item.get("url") or item.get("link")
        if item:
            links.append(str(item).strip())
    return links

