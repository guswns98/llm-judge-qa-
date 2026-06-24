"""
최초 1회 수동 로그인 후 세션을 auth_state.json으로 저장하는 스크립트.

사용법:
    python save_auth.py

브라우저가 열리면 수동으로 Google 로그인을 완료한 뒤,
터미널에서 Enter를 눌러 세션을 저장합니다.
"""

import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://example.quantus.co.kr")
AUTH_STATE_PATH = Path(__file__).parent / "auth_state.json"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        page.goto(BASE_URL, wait_until="load")
        print(f"\n[INFO] 브라우저에서 로그인을 완료하세요: {BASE_URL}")
        input("[INPUT] 로그인 완료 후 Enter를 누르세요...")

        # 로그인 상태 확인 (예: 프로필 요소 존재 여부)
        page.wait_for_timeout(2000)

        context.storage_state(path=str(AUTH_STATE_PATH))
        print(f"[SUCCESS] 인증 세션이 저장되었습니다: {AUTH_STATE_PATH}")

        browser.close()


if __name__ == "__main__":
    main()
