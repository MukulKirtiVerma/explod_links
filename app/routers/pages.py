from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import CHROME_PROFILE, CHROME_PROFILE_NAME, STATIC_DIR, TEMPLATES_DIR

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def static_url(request: Request, path: str) -> str:
    # Append the file's mtime so browsers refetch it after every edit.
    version = int((STATIC_DIR / path).stat().st_mtime)
    return f"{request.url_for('static', path=path)}?v={version}"


templates.env.globals["static_url"] = static_url


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"profile_name": CHROME_PROFILE_NAME, "profile_dir": CHROME_PROFILE},
    )
