"""
Base page object.

Every page object in this framework extends this class. Keeping shared
waits/navigation helpers here means individual page objects only need to
describe *their own* elements and actions - not re-implement plumbing.
"""

from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    def goto(self, path: str = "/"):
        self.page.goto(f"{self.base_url}{path}")

    def wait_for_test_id(self, test_id: str, timeout: int = 5000):
        locator = self.page.get_by_test_id(test_id)
        locator.wait_for(state="visible", timeout=timeout)
        return locator
