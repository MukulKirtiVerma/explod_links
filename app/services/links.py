import json
import logging
import math
import random
import time

from app.config import LINKS_FILE

try:
    import pyautogui
    _HAS_PYAUTOGUI = True
    try:
        # pyautogui loads AppKit, which makes macOS show a Python rocket icon in the Dock; hide it
        import AppKit
        AppKit.NSApplication.sharedApplication().setActivationPolicy_(
            AppKit.NSApplicationActivationPolicyProhibited
        )
    except Exception:
        pass
except Exception:
    _HAS_PYAUTOGUI = False

log = logging.getLogger(__name__)


def _human_move(x0: float, y0: float, x1: float, y1: float) -> None:
    """Move along a curved path with ease-in/out speed and slight hand jitter."""
    dist = math.hypot(x1 - x0, y1 - y0)
    if dist < 1:
        return

    # Two random control points bend the path sideways (cubic Bezier)
    nx, ny = -(y1 - y0) / dist, (x1 - x0) / dist  # unit normal to the straight line
    bend = dist * random.uniform(0.1, 0.35) * random.choice([-1, 1])
    c1 = (x0 + (x1 - x0) * random.uniform(0.2, 0.4) + nx * bend * random.uniform(0.5, 1.0),
          y0 + (y1 - y0) * random.uniform(0.2, 0.4) + ny * bend * random.uniform(0.5, 1.0))
    c2 = (x0 + (x1 - x0) * random.uniform(0.6, 0.8) + nx * bend * random.uniform(0.3, 0.8),
          y0 + (y1 - y0) * random.uniform(0.6, 0.8) + ny * bend * random.uniform(0.3, 0.8))

    # Longer moves take longer, but not linearly (roughly Fitts' law)
    duration = random.uniform(0.15, 0.3) + math.log2(1 + dist / 40) * random.uniform(0.06, 0.1)
    steps = max(10, int(duration * 60))  # ~60 updates per second

    for i in range(1, steps + 1):
        t = i / steps
        t = t * t * (3 - 2 * t)  # smoothstep: slow start, fast middle, slow stop
        u = 1 - t
        x = u**3 * x0 + 3 * u**2 * t * c1[0] + 3 * u * t**2 * c2[0] + t**3 * x1
        y = u**3 * y0 + 3 * u**2 * t * c1[1] + 3 * u * t**2 * c2[1] + t**3 * y1
        if i < steps:  # tiny tremor, but land exactly on target
            x += random.gauss(0, 0.6)
            y += random.gauss(0, 0.6)
        pyautogui.moveTo(x, y, _pause=False)
        time.sleep(duration / steps * random.uniform(0.7, 1.3))

    # Sometimes overshoot slightly and correct back
    if dist > 80 and random.random() < 0.3:
        ox, oy = x1 + random.uniform(-8, 8), y1 + random.uniform(-8, 8)
        pyautogui.moveTo(ox, oy, _pause=False)
        time.sleep(random.uniform(0.03, 0.08))
        pyautogui.moveTo(x1, y1, duration=random.uniform(0.08, 0.15), _pause=False)


def random_activity(min_sec: float = 0.5, max_sec: float = 2.0) -> None:
    """Nudge the mouse and scroll a bit for a random duration.

    On macOS the process running the server (Terminal / PyCharm / VS Code)
    needs Accessibility permission, otherwise events are silently dropped.
    """
    if not _HAS_PYAUTOGUI:
        log.warning("pyautogui not installed; skipping random activity")
        return

    try:
        pyautogui.FAILSAFE = False  # don't abort if cursor hits a corner
        pyautogui.PAUSE = 0         # we control timing ourselves

        deadline = time.monotonic() + random.uniform(min_sec, max_sec)
        w, h = pyautogui.size()
        margin = 50

        while time.monotonic() < deadline:
            # Small move, clamped to the screen so the cursor doesn't drift into a corner
            x, y = pyautogui.position()
            nx = min(max(x + random.randint(-250, 250), margin), w - margin)
            ny = min(max(y + random.randint(-200, 200), margin), h - margin)
            _human_move(x, y, nx, ny)

            # Occasional scroll, as a few small wheel ticks like a real finger
            if random.random() < 0.6:
                direction = -1 if random.random() < 0.75 else 1  # mostly read downwards
                for _ in range(random.randint(2, 6)):
                    pyautogui.scroll(direction * random.randint(2, 5), _pause=False)
                    time.sleep(random.uniform(0.03, 0.09))

            # Pause like someone reading
            time.sleep(random.uniform(0.2, 0.8))
    except Exception:
        # Never let cosmetic activity break link loading, but don't hide it either
        log.exception("random activity failed")


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