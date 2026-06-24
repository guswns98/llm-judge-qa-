"""로그인/로그아웃 관련 액션"""

from playwright.sync_api import Page
from pages.base_page import BasePage


class LoginPage(BasePage):
    """로그인 페이지 Page Object"""

    # Selectors
    LOGIN_BUTTON = "button:has-text('로그인'), a:has-text('로그인')"
    GOOGLE_LOGIN_BUTTON = "button:has-text('Google'), a:has-text('Google')"
    LOGOUT_BUTTON = "button:has-text('로그아웃')"
    PROFILE_ICON = "[data-testid='profile'], .profile-icon, .user-avatar"

    def click_login(self):
        """로그인 버튼 클릭"""
        self.page.locator(self.LOGIN_BUTTON).first.click()
        self.page.wait_for_load_state("load")
        return self

    def click_google_login(self):
        """Google 로그인 버튼 클릭"""
        self.page.locator(self.GOOGLE_LOGIN_BUTTON).first.click()
        self.page.wait_for_load_state("load")
        return self

    def login_with_google(self, email: str, password: str):
        """Google 계정으로 로그인 (팝업 핸들링)"""
        with self.page.expect_popup() as popup_info:
            self.click_google_login()

        popup = popup_info.value
        popup.fill("input[type='email']", email)
        popup.click("#identifierNext")
        popup.wait_for_selector("input[type='password']", state="visible")
        popup.fill("input[type='password']", password)
        popup.click("#passwordNext")
        popup.wait_for_close()

        self.page.wait_for_load_state("load")
        return self

    def logout(self):
        """로그아웃"""
        self.page.locator(self.PROFILE_ICON).first.click()
        self.page.locator(self.LOGOUT_BUTTON).first.click()
        self.page.wait_for_load_state("load")
        return self

    def is_logged_in(self) -> bool:
        """로그인 상태 확인"""
        try:
            self.page.wait_for_selector(self.PROFILE_ICON, timeout=5000)
            return True
        except Exception:
            return False
