import json
import time

from fastapi import APIRouter, HTTPException

from app.config import CHROME_PROFILE, FOLLOWUP_URL
from app.services.chrome import open_first_video, open_in_chrome, wait_for_tabs
from app.services.links import load_links, random_activity

router = APIRouter(prefix="/api", tags=["api"])


@router.get("/links")
def get_links():
    try:
        links = load_links()
    except json.JSONDecodeError as e:
        raise HTTPException(400, f"url_links.json is not valid JSON: {e}")
    return {"count": len(links), "links": links}


@router.post("/open")
def open_links(dry_run: bool = False):
    links = get_links()["links"]
    if not links:
        raise HTTPException(400, "url_links.json has no URLs")

    tabs = [FOLLOWUP_URL] * len(links)  # one YouTube tab per URL in the JSON
    videos: list[str] = []
    if not dry_run:
        open_in_chrome(tabs)
        time.sleep(1.5)     # let the new Chrome window come to the front
        window_id = wait_for_tabs(len(tabs))
        if window_id is None:
            raise HTTPException(504, "Chrome tabs did not finish opening in time")
        try:
            videos = open_first_video(window_id)
        except RuntimeError as e:
            raise HTTPException(403, str(e))
        random_activity()   # 0.5–2s of mouse + scroll
    return {"profile": CHROME_PROFILE, "tabs_opened": len(tabs), "videos": videos, "dry_run": dry_run}
