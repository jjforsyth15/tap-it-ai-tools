from collections.abc import Awaitable, Callable
from tapit_ai.environment import require_env
from tapit_ai.testing.browser import TapItBrowser
from tapit_ai.testing.models import TestStatus, TestResult


async def test_login() -> TestResult:
    browser = TapItBrowser()

    try:
        environment = require_env(
            "TAPIT_BASE_URL",
            "TAPIT_TEST_EMAIL",
            "TAPIT_TEST_PASSWORD",
        )
        base_url = environment["TAPIT_BASE_URL"]
        email = environment["TAPIT_TEST_EMAIL"]
        password = environment["TAPIT_TEST_PASSWORD"]

        await browser.start()
        await browser.navigate(f"{base_url}/login")
        
        page = browser.page
        
        if not page:
            raise RuntimeError("Browser page was not initialized.")
        
        await page.screenshot(path="login_debug.png", full_page=True)
        
        await page.get_by_label("Email").fill(email)
        await page.get_by_label("Password").fill(password)
        await page.get_by_role("button", name="Log in", exact=True).click()
        await page.wait_for_url("**/dashboard")
        await page.get_by_role("heading", name="Dashboard").wait_for()
        
        return TestResult(
            scenario="Authentication - Login",
            status=TestStatus.PASSED,
            summary="Test user successfully logged into TapIt.",
            details=[f"Final URL: {page.url}"],
        )
        
    except Exception as e:
        return TestResult(
            scenario="Authentication - Login",
            status=TestStatus.FAILED,
            summary="Test user failed to log into TapIt.",
            details=[str(e)],
        )
        
    finally:
        await browser.stop()


SCENARIOS: list[Callable[[], Awaitable[TestResult]]] = [
    test_login,
]
