"""챗봇 기본 기능 테스트 (비로그인 상태)"""

import os
import pytest
from dotenv import load_dotenv
from pages.chatbot_page import ChatbotPage

load_dotenv()
BASE_URL = os.getenv("BASE_URL", "https://example.quantus.co.kr")


class TestChatbotGuest:
    """비로그인 상태에서의 챗봇 기본 테스트"""

    def test_chatbot_toggle_visible(self, guest_page):
        """챗봇 토글 버튼이 페이지에 표시되는지 확인"""
        chatbot = ChatbotPage(guest_page, BASE_URL)
        chatbot.navigate("/")
        toggle = guest_page.locator(ChatbotPage.CHATBOT_TOGGLE)
        assert toggle.is_visible(), "챗봇 토글 버튼이 보이지 않습니다"

    def test_chatbot_opens(self, guest_page):
        """챗봇 패널이 정상적으로 열리는지 확인"""
        chatbot = ChatbotPage(guest_page, BASE_URL)
        chatbot.navigate("/")
        chatbot.open_chatbot()
        chat_input = guest_page.locator(ChatbotPage.CHAT_INPUT).first
        assert chat_input.is_visible(), "챗봇 입력창이 보이지 않습니다"

    def test_chatbot_send_message(self, guest_page):
        """비로그인 상태에서 챗봇에 메시지를 보낼 수 있는지 확인"""
        chatbot = ChatbotPage(guest_page, BASE_URL)
        chatbot.navigate("/")
        chatbot.open_chatbot()

        response = chatbot.ask_and_get_response("안녕하세요")
        assert len(response) > 0, "챗봇 응답이 비어있습니다"

    def test_chatbot_response_relevance(self, guest_page):
        """챗봇이 주식 관련 질문에 관련된 응답을 하는지 기본 확인"""
        chatbot = ChatbotPage(guest_page, BASE_URL)
        chatbot.navigate("/")
        chatbot.open_chatbot()

        response = chatbot.ask_and_get_response("삼성전자 주가 알려줘")
        assert len(response) > 10, "응답이 너무 짧습니다"
