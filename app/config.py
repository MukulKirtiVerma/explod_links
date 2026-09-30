from pathlib import Path

APP_DIR = Path(__file__).parent
BASE_DIR = APP_DIR.parent

LINKS_FILE = BASE_DIR / "url_links.json"
TEMPLATES_DIR = APP_DIR / "templates"
STATIC_DIR = APP_DIR / "static"

# "MUKUL KIRTI" (rahulsingh60verma@gmail.com) profile folder, from
# ~/Library/Application Support/Google/Chrome/Local State
CHROME_PROFILE = "Profile 10"
CHROME_PROFILE_NAME = "MUKUL KIRTI"
CHROME_APP = "Google Chrome"

HOST = "127.0.0.1"
PORT = 8001

