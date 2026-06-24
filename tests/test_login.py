"""로그인/로그아웃 기능 테스트"""

import os
import pytest
from dotenv import load_dotenv
from pages.login_page import LoginPage

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "https://example.quantus.co.kr")


class TestLogin:
    """로그인 관련 테스트 스위트"""

    def test_login_page_loads(self, guest_page):
        """로그인 페이지가 정상적으로 로드되는지 확인"""
        login = LoginPage(guest_page, BASE_URL)
        login.navigate("/")
        assert BASE_URL in login.current_url

    def test_login_button_visible(self, guest_page):
        """비로그인 상태에서 로그인 버튼이 표시되는지 확인"""
        login = LoginPage(guest_page, BASE_URL)
        login.navigate("/")
        login_btn = guest_page.locator(LoginPage.LOGIN_BUTTON).first
        assert login_btn.is_visible(), "로그인 버튼이 보이지 않습니다"

    def test_authenticated_session(self, auth_page):
        """저장된 세션으로 로그인 상태가 유지되는지 확인"""
        login = LoginPage(auth_page, BASE_URL)
        assert login.is_logged_in(), "인증 세션이 유효하지 않습니다"

    def test_logout(self, auth_page):
        """로그아웃이 정상 동작하는지 확인"""
        login = LoginPage(auth_page, BASE_URL)
        assert login.is_logged_in(), "로그아웃 테스트 전 로그인 상태여야 합니다"
        login.logout()
        assert not login.is_logged_in(), "로그아웃 후에도 로그인 상태입니다"
