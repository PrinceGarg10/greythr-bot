"""
Greythr Daily Attendance Bot — runs inside GitHub Actions.

Sign In flow (runs at 9:00 AM IST):
  1. Login        — fill credentials and submit
  2. Sign In      — click the Sign In button on the dashboard
  3. WFH + Submit — select Work from Home in the modal, click Sign In
  4. Verify       — confirm modal closed and Sign Out button is visible

Sign Out flow (runs at 6:30 PM IST):
  1. Login        — same login process
  2. Sign Out     — click the Sign Out button on the dashboard
  3. Confirm      — click Sign Out in the modal (no location needed)
  4. Verify       — confirm modal closed and Sign In button is visible again
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

# ── URLs ──────────────────────────────────────────────────────────────────────
LOGIN_URL = "https://l7i.greythr.com/uas/portal/auth/login"

# ── Credentials from GitHub Secrets ──────────────────────────────────────────
USERNAME = os.environ.get("GREYTHR_USERNAME", "")
PASSWORD = os.environ.get("GREYTHR_PASSWORD", "")

# ── Mode: "signin" or "signout" — passed via env var ACTION_MODE ──────────────
ACTION_MODE = os.environ.get("ACTION_MODE", "signin").lower()

# ── Work location to select in the sign-in modal ─────────────────────────────
WORK_LOCATION = "Work from Home"   # change to "Office" if needed


# ═════════════════════════════════════════════════════════════════════════════
# SHARED STEP
# ═════════════════════════════════════════════════════════════════════════════

def step_login(page) -> bool:
    """STEP 1 (shared) — Navigate to login page and authenticate."""
    log.info("── STEP 1: Login ──")
    try:
        page.goto(LOGIN_URL, timeout=30_000)
        page.wait_for_load_state("networkidle")

        page.fill('input[name="username"]', USERNAME)
        page.fill('input[name="password"]', PASSWORD)
        page.click('button[type="submit"]')

        page.wait_for_url("**/v3/portal/ess/home**", timeout=20_000)
        log.info(f"  ✅ Logged in. URL: {page.url}")
        return True

    except PlaywrightTimeout:
        log.error("  ❌ Login timed out — wrong credentials or page changed.")
        page.screenshot(path="step1_login_error.png")
        return False
    except Exception as e:
        log.error(f"  ❌ Login error: {e}")
        page.screenshot(path="step1_login_error.png")
        return False


# ═════════════════════════════════════════════════════════════════════════════
# SIGN IN FLOW
# ═════════════════════════════════════════════════════════════════════════════

def step_click_signin_button(page) -> bool:
    """STEP 2 (sign in) — Click the Sign In button on the dashboard."""
    log.info("── STEP 2: Click Sign In button on dashboard ──")
    try:
        page.wait_for_load_state("networkidle")

        signin_btn = page.locator(
            'gt-attendance-info button.btn-primary[name="primary"]'
        ).first
        signin_btn.wait_for(state="visible", timeout=15_000)
        signin_btn.click()

        page.wait_for_selector('gt-popup-modal[open]', timeout=10_000)
        log.info("  ✅ Clicked Sign In — modal is open.")
        return True

    except PlaywrightTimeout:
        log.error("  ❌ Sign In button not found or modal did not open.")
        page.screenshot(path="step2_signin_error.png")
        return False
    except Exception as e:
        log.error(f"  ❌ Error: {e}")
        page.screenshot(path="step2_signin_error.png")
        return False


def step_select_wfh_and_confirm(page) -> bool:
    """STEP 3 (sign in) — Select Work from Home and click Sign In in modal."""
    log.info(f"── STEP 3: Select '{WORK_LOCATION}' and confirm ──")
    try:
        dropdown_btn = page.locator(
            'gt-popup-modal[open] button.btn-primary[name="primary"]'
        ).first
        dropdown_btn.wait_for(state="visible", timeout=10_000)
        dropdown_btn.click()
        log.info("  Dropdown opened.")

        option = page.get_by_role("option", name=WORK_LOCATION)
        option.wait_for(state="visible", timeout=5_000)
        option.click()
        log.info(f"  ✅ Selected '{WORK_LOCATION}'.")

        modal_signin = page.locator(
            'gt-popup-modal[open] gt-button[shade="primary"]'
        ).first
        modal_signin.wait_for(state="visible", timeout=5_000)
        modal_signin.click()
        log.info("  ✅ Clicked Sign In in modal.")
        return True

    except PlaywrightTimeout:
        log.error("  ❌ Could not interact with modal.")
        page.screenshot(path="step3_modal_error.png")
        return False
    except Exception as e:
        log.error(f"  ❌ Modal error: {e}")
        page.screenshot(path="step3_modal_error.png")
        return False


def step_verify_signedin(page) -> bool:
    """STEP 4 (sign in) — Verify modal closed and Sign Out button is visible."""
    log.info("── STEP 4: Verify sign-in success ──")
    try:
        page.wait_for_selector('gt-popup-modal[open]', state="hidden", timeout=10_000)
        log.info("  ✅ Modal closed.")

        signout_btn = page.locator(
            'gt-attendance-info gt-button[shade="link"]'
        ).filter(has_text="Sign Out").first
        signout_btn.wait_for(state="visible", timeout=10_000)
        log.info("  ✅ Sign Out button visible — attendance marked successfully!")
        return True

    except PlaywrightTimeout:
        log.error("  ❌ Verification failed — Sign Out button not found.")
        page.screenshot(path="step4_verify_error.png")
        return False
    except Exception as e:
        log.error(f"  ❌ Verification error: {e}")
        page.screenshot(path="step4_verify_error.png")
        return False


# ═════════════════════════════════════════════════════════════════════════════
# SIGN OUT FLOW
# ═════════════════════════════════════════════════════════════════════════════

def step_click_signout_button(page) -> bool:
    """STEP 2 (sign out) — Click the Sign Out button on the dashboard."""
    log.info("── STEP 2: Click Sign Out button on dashboard ──")
    try:
        page.wait_for_load_state("networkidle")

        signout_btn = page.locator(
            'gt-attendance-info gt-button[shade="link"]'
        ).filter(has_text="Sign Out").first
        signout_btn.wait_for(state="visible", timeout=15_000)
        signout_btn.click()

        page.wait_for_selector('gt-popup-modal[open]', timeout=10_000)
        log.info("  ✅ Clicked Sign Out — modal is open.")
        return True

    except PlaywrightTimeout:
        log.error("  ❌ Sign Out button not found or modal did not open.")
        page.screenshot(path="step2_signout_error.png")
        return False
    except Exception as e:
        log.error(f"  ❌ Error: {e}")
        page.screenshot(path="step2_signout_error.png")
        return False


def step_confirm_signout(page) -> bool:
    """STEP 3 (sign out) — Click Sign Out in the modal (no location needed)."""
    log.info("── STEP 3: Confirm Sign Out in modal ──")
    try:
        modal_signout = page.locator(
            'gt-popup-modal[open] gt-button[shade="primary"]'
        ).first
        modal_signout.wait_for(state="visible", timeout=10_000)
        modal_signout.click()
        log.info("  ✅ Clicked Sign Out in modal.")
        return True

    except PlaywrightTimeout:
        log.error("  ❌ Sign Out button in modal not found.")
        page.screenshot(path="step3_signout_modal_error.png")
        return False
    except Exception as e:
        log.error(f"  ❌ Modal error: {e}")
        page.screenshot(path="step3_signout_modal_error.png")
        return False


def step_verify_signedout(page) -> bool:
    """STEP 4 (sign out) — Verify modal closed and Sign In button is visible again."""
    log.info("── STEP 4: Verify sign-out success ──")
    try:
        page.wait_for_selector('gt-popup-modal[open]', state="hidden", timeout=10_000)
        log.info("  ✅ Modal closed.")

        signin_btn = page.locator(
            'gt-attendance-info gt-button[shade="primary"]'
        ).first
        signin_btn.wait_for(state="visible", timeout=10_000)
        log.info("  ✅ Sign In button visible — signed out successfully!")
        return True

    except PlaywrightTimeout:
        log.error("  ❌ Verification failed — Sign In button not found after sign out.")
        page.screenshot(path="step4_signout_verify_error.png")
        return False
    except Exception as e:
        log.error(f"  ❌ Verification error: {e}")
        page.screenshot(path="step4_signout_verify_error.png")
        return False


# ═════════════════════════════════════════════════════════════════════════════
# Main runner
# ═════════════════════════════════════════════════════════════════════════════

def run() -> bool:
    if not USERNAME or not PASSWORD:
        log.error("GREYTHR_USERNAME or GREYTHR_PASSWORD secret is not set.")
        return False

    log.info(f"🚀 Starting Greythr bot in [{ACTION_MODE.upper()}] mode")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            if not step_login(page):
                return False

            if ACTION_MODE == "signin":
                if not step_click_signin_button(page):
                    return False
                if not step_select_wfh_and_confirm(page):
                    return False
                if not step_verify_signedin(page):
                    return False

            elif ACTION_MODE == "signout":
                if not step_click_signout_button(page):
                    return False
                if not step_confirm_signout(page):
                    return False
                if not step_verify_signedout(page):
                    return False

            else:
                log.error(f"Unknown ACTION_MODE '{ACTION_MODE}'. Use 'signin' or 'signout'.")
                return False

            log.info(f"🎉 [{ACTION_MODE.upper()}] completed successfully!")
            return True

        finally:
            browser.close()


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
