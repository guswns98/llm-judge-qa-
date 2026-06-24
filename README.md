# QA Quri - LLM 평가 자동화

Quantus 웹 서비스의 챗봇 응답 품질을 자동 평가하는 프로젝트입니다.  
Python + Playwright를 기반으로 150개의 질문을 자동 전송하고, **Ollama(로컬 LLM)**를 통해 응답의 관련성, 정확성, 완결성을 정량적으로 채점합니다.

## 프로젝트 구조

```
qa-quri-automation/
├── conftest.py                  # pytest fixtures (인증 컨텍스트, 페이지, 세션 검증)
├── save_auth.py                 # 최초 1회 수동 로그인 후 세션 저장 스크립트
├── generate_report.py           # evaluation_results/*.json → HTML 리포트 생성
├── .env                         # BASE_URL, Google 계정 정보 (커밋 금지)
├── auth_state.json              # 저장된 로그인 세션 (자동 생성)
├── pages/                       # Page Object Model 클래스
│   ├── base_page.py             # 공통 navigate, search_stock
│   ├── login_page.py            # 로그인/로그아웃 액션
│   └── chatbot_page.py          # 챗봇 응답 감지 및 저장
├── tests/
│   ├── test_login.py            # 로그인/로그아웃 테스트
│   ├── test_chatbot.py          # 챗봇 기본 테스트 (비로그인)
│   └── test_chatbot_learn.py    # 챗봇 150개 질문 + Ollama 품질 평가
├── chat_results/                # 챗봇 응답 저장 (자동 생성)
└── evaluation_results/          # Ollama 평가 결과 및 HTML 리포트
```

## 환경 설정 및 실행

### 1. 설치

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일에 실제 값 입력
```

### 3. 로그인 세션 저장 (최초 1회)

```bash
python save_auth.py
```

### 4. 테스트 실행

| 대상 | 실행 명령어 | 비고 |
|------|------------|------|
| 전체 테스트 | `pytest` | 전체 시나리오 실행 |
| 품질 평가 | `pytest tests/test_chatbot_learn.py -s --headed` | `--headed` 필수 |
| 화면 확인 | `pytest --headed` | 실행 과정을 브라우저로 확인 |

### 5. 리포트 생성

```bash
python generate_report.py
# → evaluation_results/report.html
```

## 챗봇 품질 평가 시스템 (LLM-as-a-Judge)

로컬 LLM인 **Ollama(qwen2.5:3b)**를 평가자로 활용하여 챗봇의 응답을 자동으로 채점합니다.

### 평가 기준 (Score Card)

| 점수 | 설명 |
|------|------|
| 5점 | 관련성·정확성·완결성 완벽, 구체적이고 유용한 정보 제공 |
| 4점 | 대부분 충족하나 설명이 다소 부족함 |
| 3점 | 관련성은 있으나 정확성 또는 완결성 중 하나가 미흡함 |
| 2점 | 관련은 있으나 답변이 불충분하거나 일부 오류가 있음 |
| 1점 | 질문과 무관하거나 에러 메시지만 반환함 |

### 평가 워크플로우

1. **데이터 수집**: 로그인 상태에서 150개 질문 순차 전송 및 응답 캡처
2. **병렬 평가**: Ollama가 백그라운드 스레드(`max_workers=2`)로 실시간 채점
3. **결과 저장**: `eval_NN.json` 개별 저장 후 `report.html` 통합 리포트 생성

## 주요 설계 원칙

- **POM (Page Object Model)**: 모든 셀렉터와 액션을 `pages/`에 캡슐화하여 유지보수성 극대화
- **Context Isolation**: 로그인 기반 테스트(`auth_context`)와 비로그인 테스트(`guest_page`)를 완전히 분리
- **Wait Strategy**: 실시간 WebSocket 통신 특성을 고려하여 `networkidle` 대신 `load` 상태 및 특정 요소 대기 전략 사용

## 기술 스택

- **Python 3.11+**
- **Playwright** - 브라우저 자동화
- **pytest** - 테스트 프레임워크
- **Ollama (qwen2.5:3b)** - 로컬 LLM 평가자
- **requests** - Ollama API 통신
