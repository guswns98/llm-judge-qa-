"""공통 페이지 액션을 제공하는 베이스 클래스"""

from playwright.sync_api import Page


class BasePage:
    """모든 Page Object의 부모 클래스"""

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    def navigate(self, path: str = "/"):
        """지정 경로로 이동"""
        url = f"{self.base_url}{path}"
        self.page.goto(url, wait_until="load")
        return self

    def search_stock(self, keyword: str):
        """종목 검색"""
        search_input = self.page.locator("input[placeholder*='검색'], input[placeholder*='종목']")
        search_input.fill(keyword)
        search_input.press("Enter")
        self.page.wait_for_load_state("load")
        return self

    def wait_for_element(self, selector: str, timeout: int = 10000):
        """특정 요소가 나타날 때까지 대기"""
        self.page.wait_for_selector(selector, timeout=timeout)
        return self

    def get_text(self, selector: str) -> str:
        """요소의 텍스트 반환"""
        element = self.page.locator(selector)
        return element.inner_text()

    def click(self, selector: str):
        """요소 클릭"""
        self.page.locator(selector).click()
        return self

    @property
    def current_url(self) -> str:
        return self.page.url
