import subprocess
import time

from app.config import CHROME_APP, CHROME_PROFILE

# Runs inside a YouTube tab: click the first real video on the home feed,
# skipping ads, sponsored items, Shorts and Mix playlists. Returns what it did.
_FIRST_VIDEO_JS = r"""
(() => {
  if (location.pathname.startsWith('/watch')) return 'already-watching';
  const AD = 'ytd-ad-slot-renderer, ytd-in-feed-ad-layout-renderer, ytd-promoted-video-renderer,'
           + 'ytd-display-ad-renderer, ytd-promoted-sparkles-web-renderer, ytd-rich-section-renderer,'
           + 'ytd-reel-shelf-renderer, [is-ad], .ytd-ad-slot-renderer';
  const links = document.querySelectorAll('ytd-browse a[href*="/watch?v="]');
  for (const a of links) {
    if (a.closest(AD)) continue;
    if (/[?&]list=/.test(a.getAttribute('href'))) continue;  // skip Mix / playlist cards
    const item = a.closest('ytd-rich-item-renderer, ytd-video-renderer, yt-lockup-view-model') || a;
    if (/\b(Sponsored|Ad)\b/.test(item.querySelector('#badges, .badge, [class*=badge]')?.innerText || '')) continue;
    if (!item.getBoundingClientRect().height) continue;  // hidden / not rendered
    a.click();
    return 'clicked ' + a.getAttribute('href');
  }
  return 'none';
})()
"""


def open_in_chrome(urls: list[str]) -> None:
    # One new window in the given profile, one tab per URL.
    subprocess.run(
        ["open", "-na", CHROME_APP, "--args",
         f"--profile-directory={CHROME_PROFILE}", "--new-window", *urls],
        check=True,
    )


def _osascript(script: str, *args: str) -> str:
    # Timeout so a pending macOS permission prompt can't hang the request forever
    try:
        result = subprocess.run(
            ["osascript", "-e", script, *args], capture_output=True, text=True, timeout=60
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            "osascript timed out - check for a macOS prompt asking to let PyCharm control Google Chrome"
        )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()


def wait_for_tabs(count: int, timeout: float = 30.0) -> int | None:
    """Wait until the front Chrome window has `count` loaded tabs; return its window id."""
    script = f'''
        tell application "{CHROME_APP}"
            if (count of windows) is 0 then return "0 0 true"
            set w to front window
            set busy to false
            repeat with t in tabs of w
                if loading of t then set busy to true
            end repeat
            return ((id of w) as text) & " " & ((count of tabs of w) as text) & " " & (busy as text)
        end tell'''
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        window_id, tabs, busy = _osascript(script).split()
        if int(tabs) >= count and busy == "false":
            return int(window_id)
        time.sleep(0.5)
    return None


def open_first_video(window_id: int, timeout: float = 20.0) -> list[str]:
    """In every tab of the window, click the first non-ad video. Returns one result per tab.

    Needs Chrome > View > Developer > "Allow JavaScript from Apple Events".
    """
    script = f'''
        on run argv
            tell application "{CHROME_APP}"
                set w to window id {window_id}
                set results to {{}}
                repeat with t in tabs of w
                    set end of results to (execute t javascript (item 1 of argv))
                end repeat
                set AppleScript's text item delimiters to linefeed
                return results as text
            end tell
        end run'''
    # The feed renders after page load, so retry while any tab found nothing yet.
    deadline = time.monotonic() + timeout
    while True:
        try:
            results = _osascript(script, _FIRST_VIDEO_JS).splitlines()
        except RuntimeError as e:
            if "JavaScript" in str(e):
                raise RuntimeError(
                    'Enable Chrome > View > Developer > "Allow JavaScript from Apple Events"'
                ) from e
            raise
        if "none" not in results or time.monotonic() > deadline:
            return results
        time.sleep(1.0)
