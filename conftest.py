import os
import json
import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://example.quantus.co.kr")
AUTH_STATE_PATH = Path(__file__).parent / "auth_state.json"


@pytest.fixture(scope="session")
def browser():
    """세션 단위 브라우저 인스턴스"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture(scope="session")
def auth_context(browser: Browser):
    """저장된 인증 세션을 사용하는 브라우저 컨텍스트"""
    if not AUTH_STATE_PATH.exists():
        pytest.skip("auth_state.json이 없습니다. 먼저 python save_auth.py를 실행하세요.")

    context = browser.new_context(storage_state=str(AUTH_STATE_PATH))
    yield context
    context.close()


@pytest.fixture
def auth_page(auth_context: BrowserContext):
    """인증된 상태의 페이지"""
    page = auth_context.new_page()
    page.goto(BASE_URL, wait_until="load")
    yield page
    page.close()


@pytest.fixture
def guest_page(browser: Browser):
    """비로그인 상태의 페이지 (게스트)"""
    context = browser.new_context()
    page = context.new_page()
    page.goto(BASE_URL, wait_until="load")
    yield page
    page.close()
    context.close()


def pytest_configure(config):
    """결과 디렉토리 자동 생성"""
    Path("chat_results").mkdir(exist_ok=True)
    Path("evaluation_results").mkdir(exist_ok=True)
