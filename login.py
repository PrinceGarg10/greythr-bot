"""
Grathr headless login — runs inside GitHub Actions.
Edit the selectors below if they don't match Grathr's actual HTML.
"""

import os
import sys
import logging
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
)
log = logging.getLogger(__name__)

# ── Config — update these to match Grathr's login page ───────────────────────
GRATHR_URL        = "https://www.grathr.com/login"
USERNAME_SELECTOR = 'input[name="email"]'
PASSWORD_SELECTOR = 'input[name="password"]'
SUBMIT_SELECTOR   = 'button[type="submit"]'
SUCCESS_URL_PART  = "/dashboard"

# ── Credentials come from GitHub Secrets ─────────────────────────────────────
USERNAME = os.environ.get("GRATHR_USERNAME", "")
PASSWORD = os.environ.get("GRATHR_PASSWORD", "")


def login() -> bool:
    if not USERNAME or not PASSWORD:
        log.error("GRATHR_USERNAME or GRATHR_PASSWORD secret is missing.")
        return False

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            log.info(f"Navigating to {GRATHR_URL} ...")
            page.goto(GRATHR_URL, timeout=30_000)

            page.fill(USERNAME_SELECTOR, USERNAME)
            page.fill(PASSWORD_SELECTOR, PASSWORD)
            page.click(SUBMIT_SELECTOR)

            page.wait_for_url(f"**{SUCCESS_URL_PART}**", timeout=15_000)
            log.info(f"Login successful! Landed on: {page.url}")
            return True

        except PlaywrightTimeout:
            log.error("Timed out — login page may have changed or credentials are wrong.")
            page.screenshot(path="login_error.png")
            return False

        except Exception as e:
            log.error(f"Unexpected error: {e}")
            page.screenshot(path="login_error.png")
            return False

        finally:
            browser.close()


if __name__ == "__main__":
    success = login()
    sys.exit(0 if success else 1)  # non-zero exit marks the Action as failed
