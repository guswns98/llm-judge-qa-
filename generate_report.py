"""
evaluation_results/*.json 파일을 읽어 HTML 리포트를 생성하는 스크립트.

사용법:
    python generate_report.py
"""

import json
from pathlib import Path

EVAL_DIR = Path("evaluation_results")
REPORT_PATH = EVAL_DIR / "report.html"


def load_results() -> list[dict]:
    """개별 평가 JSON 파일들을 로드"""
    results = []
    for filepath in sorted(EVAL_DIR.glob("eval_*.json")):
        with open(filepath, "r", encoding="utf-8") as f:
            results.append(json.load(f))
    return results


def generate_html(results: list[dict]) -> str:
    """평가 결과를 HTML 리포트로 변환"""
    valid_scores = [r["score"] for r in results if r["score"] > 0]
    avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
    total = len(results)
    distribution = {s: len([r for r in results if r["score"] == s]) for s in range(1, 6)}

    # 점수별 색상
    def score_color(score):
        colors = {5: "#22c55e", 4: "#84cc16", 3: "#eab308", 2: "#f97316", 1: "#ef4444", 0: "#9ca3af"}
        return colors.get(score, "#9ca3af")

    # 점수별 바 너비 (최대 기준)
    max_count = max(distribution.values()) if distribution.values() else 1

    rows = ""
    for r in results:
        color = score_color(r["score"])
        rows += f"""
        <tr>
            <td style="text-align:center">{r['index']}</td>
            <td>{r['question']}</td>
            <td style="max-width:400px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;"
                title="{r['response'][:200].replace('"', '&quot;')}">{r['response'][:100]}</td>
            <td style="text-align:center">
                <span style="background:{color}; color:white; padding:2px 10px; border-radius:12px; font-weight:bold;">
                    {r['score']}
                </span>
            </td>
            <td style="font-size:0.85em; color:#555;">{r['evaluation'][:150]}</td>
        </tr>"""

    dist_bars = ""
    for score in range(5, 0, -1):
        count = distribution.get(score, 0)
        pct = (count / total * 100) if total > 0 else 0
        bar_width = (count / max_count * 100) if max_count > 0 else 0
        dist_bars += f"""
        <div style="display:flex; align-items:center; margin:4px 0;">
            <span style="width:30px; font-weight:bold; color:{score_color(score)}">{score}점</span>
            <div style="flex:1; background:#f3f4f6; border-radius:4px; margin:0 8px; height:20px;">
                <div style="width:{bar_width}%; background:{score_color(score)}; height:100%; border-radius:4px;
                     display:flex; align-items:center; justify-content:flex-end; padding-right:6px;
                     color:white; font-size:0.75em; font-weight:bold; min-width:fit-content;">
                    {count}
                </div>
            </div>
            <span style="width:50px; font-size:0.85em; color:#888;">{pct:.1f}%</span>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quantus 챗봇 응답 품질 리포트</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
               background: #f8fafc; color: #1e293b; padding: 24px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ font-size: 1.8em; margin-bottom: 8px; }}
        .subtitle {{ color: #64748b; margin-bottom: 24px; }}
        .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                  gap: 16px; margin-bottom: 24px; }}
        .card {{ background: white; border-radius: 12px; padding: 20px;
                 box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .card-label {{ font-size: 0.85em; color: #64748b; margin-bottom: 4px; }}
        .card-value {{ font-size: 1.8em; font-weight: 700; }}
        .section {{ background: white; border-radius: 12px; padding: 20px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 24px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ background: #f1f5f9; padding: 10px 12px; text-align: left;
              font-size: 0.85em; color: #475569; border-bottom: 2px solid #e2e8f0; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #f1f5f9; font-size: 0.9em; }}
        tr:hover {{ background: #f8fafc; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Quantus 챗봇 응답 품질 리포트</h1>
        <p class="subtitle">LLM-as-a-Judge 자동 평가 결과 (Ollama {OLLAMA_MODEL})</p>

        <div class="cards">
            <div class="card">
                <div class="card-label">총 질문 수</div>
                <div class="card-value">{total}</div>
            </div>
            <div class="card">
                <div class="card-label">평균 점수</div>
                <div class="card-value" style="color:{score_color(round(avg_score))}">{avg_score:.2f}</div>
            </div>
            <div class="card">
                <div class="card-label">평가 완료</div>
                <div class="card-value">{len(valid_scores)}</div>
            </div>
            <div class="card">
                <div class="card-label">4점 이상 비율</div>
                <div class="card-value">{((distribution.get(4, 0) + distribution.get(5, 0)) / total * 100) if total else 0:.1f}%</div>
            </div>
        </div>

        <div class="section">
            <h2 style="margin-bottom:12px;">점수 분포</h2>
            {dist_bars}
        </div>

        <div class="section">
            <h2 style="margin-bottom:12px;">상세 평가 결과</h2>
            <div style="overflow-x:auto;">
                <table>
                    <thead>
                        <tr>
                            <th style="width:50px">#</th>
                            <th style="width:200px">질문</th>
                            <th style="width:300px">챗봇 응답</th>
                            <th style="width:60px">점수</th>
                            <th>평가 근거</th>
                        </tr>
                    </thead>
                    <tbody>{rows}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>"""
    return html


def main():
    results = load_results()
    if not results:
        print("[ERROR] evaluation_results/ 디렉토리에 eval_*.json 파일이 없습니다.")
        print("        먼저 pytest tests/test_chatbot_learn.py를 실행하세요.")
        return

    html = generate_html(results)
    REPORT_PATH.write_text(html, encoding="utf-8")
    print(f"[SUCCESS] 리포트 생성 완료: {REPORT_PATH}")
    print(f"          총 {len(results)}개 평가 결과 포함")


OLLAMA_MODEL = "qwen2.5:3b"  # 리포트 표시용

if __name__ == "__main__":
    main()
