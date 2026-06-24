"""챗봇 응답 감지 및 저장"""

import json
import time
from pathlib import Path
from playwright.sync_api import Page
from pages.base_page import BasePage


class ChatbotPage(BasePage):
    """챗봇 Page Object - 질문 전송, 응답 대기, 결과 저장"""

    # Selectors
    CHAT_INPUT = "textarea[placeholder*='질문'], input[placeholder*='질문'], textarea[placeholder*='메시지']"
    SEND_BUTTON = "button[aria-label*='전송'], button:has-text('전송'), button[type='submit']"
    CHAT_MESSAGES = ".chat-message, .message-content, [data-testid='chat-message']"
    BOT_MESSAGE = ".bot-message, .assistant-message, [data-role='assistant']"
    LOADING_INDICATOR = ".loading, .typing-indicator, [data-testid='loading']"
    CHATBOT_TOGGLE = "button[aria-label*='챗봇'], .chatbot-toggle, [data-testid='chatbot-button']"

    RESULTS_DIR = Path("chat_results")

    def open_chatbot(self):
        """챗봇 패널 열기"""
        toggle = self.page.locator(self.CHATBOT_TOGGLE)
        if toggle.is_visible():
            toggle.click()
            self.page.wait_for_timeout(1000)
        return self

    def send_question(self, question: str):
        """챗봇에 질문 전송"""
        input_field = self.page.locator(self.CHAT_INPUT).first
        input_field.fill(question)
        self.page.wait_for_timeout(300)

        send_btn = self.page.locator(self.SEND_BUTTON).first
        if send_btn.is_visible():
            send_btn.click()
        else:
            input_field.press("Enter")

        return self

    def wait_for_response(self, timeout: int = 60000) -> str:
        """챗봇 응답이 완료될 때까지 대기 후 마지막 응답 반환"""
        # 로딩 인디케이터가 나타날 때까지 잠시 대기
        self.page.wait_for_timeout(1000)

        # 로딩 인디케이터가 사라질 때까지 대기
        try:
            loading = self.page.locator(self.LOADING_INDICATOR)
            if loading.is_visible():
                loading.wait_for(state="hidden", timeout=timeout)
        except Exception:
            pass

        # 응답 안정화 대기 (스트리밍 응답 고려)
        self._wait_for_stable_response(timeout=timeout)

        # 마지막 봇 메시지 추출
        bot_messages = self.page.locator(self.BOT_MESSAGE)
        count = bot_messages.count()
        if count > 0:
            return bot_messages.nth(count - 1).inner_text()

        # fallback: 전체 메시지에서 마지막 추출
        all_messages = self.page.locator(self.CHAT_MESSAGES)
        count = all_messages.count()
        if count > 0:
            return all_messages.nth(count - 1).inner_text()

        return ""

    def _wait_for_stable_response(self, timeout: int = 60000, stable_duration: float = 2.0):
        """응답 텍스트가 더 이상 변하지 않을 때까지 대기 (스트리밍 대응)"""
        start_time = time.time()
        last_text = ""
        stable_start = None

        while (time.time() - start_time) * 1000 < timeout:
            bot_messages = self.page.locator(self.BOT_MESSAGE)
            count = bot_messages.count()
            current_text = bot_messages.nth(count - 1).inner_text() if count > 0 else ""

            if current_text and current_text == last_text:
                if stable_start is None:
                    stable_start = time.time()
                elif time.time() - stable_start >= stable_duration:
                    return
            else:
                stable_start = None
                last_text = current_text

            self.page.wait_for_timeout(500)

    def ask_and_get_response(self, question: str, timeout: int = 60000) -> str:
        """질문 전송 후 응답 반환 (편의 메서드)"""
        self.send_question(question)
        return self.wait_for_response(timeout=timeout)

    def save_result(self, index: int, question: str, response: str):
        """질문-응답 쌍을 JSON 파일로 저장"""
        self.RESULTS_DIR.mkdir(exist_ok=True)
        result = {
            "index": index,
            "question": question,
            "response": response,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        filepath = self.RESULTS_DIR / f"chat_{index:03d}.json"
        filepath.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        return filepath
