import subprocess

from app.config import CHROME_APP, CHROME_PROFILE


def open_in_chrome(urls: list[str]) -> None:
    # One new window in the given profile, one tab per URL.
    subprocess.run(
        ["open", "-na", CHROME_APP, "--args",
         f"--profile-directory={CHROME_PROFILE}", "--new-window", *urls],
        check=True,
    )
