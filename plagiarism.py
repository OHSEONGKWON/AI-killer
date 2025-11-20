import google.generativeai as genai
import json
import sys

# ==========================================
# 1. API 키 설정
# ==========================================
API_KEY = ""

if API_KEY.startswith("여기에"):
    print("❌ 오류: API 키가 설정되지 않았습니다.")
    sys.exit()

genai.configure(api_key=API_KEY)

# ==========================================
# 2. 시스템 프롬프트 (출처 자동 탐지 기능 추가)
# ==========================================
SYSTEM_PROMPT = """
당신은 '지능형 표절 수사관'입니다.
사용자가 입력한 텍스트(`draft_text`)를 분석하여, 당신의 방대한 지식 데이터베이스 내에서 이 글의 **원본(Original Source)**으로 추정되는 내용을 찾아내세요.

## 수행 절차 (Step-by-Step)
1. **출처 탐색:** 입력된 텍스트의 문체, 내용, 팩트를 분석하여 원본이 무엇인지(예: 위키백과, 뉴스 기사, 유명한 소설, 노래 가사 등) 추론하십시오.
2. **비교 분석:** 당신이 찾아낸 '원본'과 사용자의 '초안'을 비교하여 표절 여부를 판단하십시오.
3. **데이터 생성:** 원본의 출처 명(`suspected_source`)과 표절 하이라이팅 데이터를 JSON으로 반환하십시오.

## 출력 형식 (JSON Format Only)
반드시 아래 JSON 스키마를 따르세요.

{
  "suspected_source": "AI가 추정한 원본 출처 (예: '나무위키 - 이순신 문서', '2024년 00신문 기사', '창작물일 확률 높음')",
  "original_found": true | false,
  "overall_similarity_score": 0~100,
  "highlight_segments": [
    {
      "target_text": "draft_text 내에서 하이라이트 할 텍스트",
      "type": "EXACT" | "SUSPICIOUS",
      "reason": "구체적인 분석 (예: '위키백과 내용과 90% 일치함')"
    }
  ]
}
"""

# ==========================================
# 3. 함수 정의
# ==========================================
def auto_detect_plagiarism(draft_text):
    """초안만 입력받아 원본을 추적하고 분석"""
    
    generation_config = {
        "temperature": 0.1,
        "response_mime_type": "application/json",
    }

    model = genai.GenerativeModel(
        model_name="gemini-2.5-pro",
        generation_config=generation_config,
        system_instruction=SYSTEM_PROMPT
    )

    user_input = f"""
    ## 분석 요청 텍스트 (Draft):
    {draft_text}
    """

    try:
        response = model.generate_content(user_input)
        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e)}

def print_result(draft_text, result_json):
    """결과 시각화"""
    RED = "\033[41m\033[97m"
    YELLOW = "\033[43m\033[30m"
    RESET = "\033[0m"
    
    highlighted_text = draft_text
    segments = result_json.get("highlight_segments", [])
    
    # 하이라이팅 적용
    for seg in segments:
        target = seg["target_text"]
        type_ = seg["type"]
        color = RED if type_ == "EXACT" else YELLOW
        replacement = f"{color}{target}{RESET}"
        highlighted_text = highlighted_text.replace(target, replacement)

    print("\n" + "="*50)
    print(f"🕵️  AI 수사 결과")
    print("="*50)
    print(f"📂 추정 출처: {result_json.get('suspected_source', '알 수 없음')}")
    print(f"📊 표절 의심도: {result_json.get('overall_similarity_score', 0)}%")
    print("-" * 50)
    
    print("\n[🔍 시각화된 결과]\n")
    print(highlighted_text)
    print("\n" + "-" * 50)
    
    print("[💡 상세 분석]")
    for seg in segments:
        icon = "🔴" if seg['type'] == "EXACT" else "🟡"
        print(f"{icon} [{seg['type']}] : {seg['reason']}")

# ==========================================
# 4. 메인 실행
# ==========================================
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🕵️  AI 자동 표절 헌터 (원본 입력 불필요)")
    print("="*50)
    
    while True:
        d_text = input("\n📝 [검사할 글]을 입력하세요 (종료: q):\n>> ")
        
        if d_text.lower() in ['q', 'quit']:
            break
        if not d_text.strip():
            continue

        print("\n🔍 AI가 인터넷과 지식 베이스를 뒤지는 중입니다...\n")
        
        result = auto_detect_plagiarism(d_text)
        
        if "error" in result:
            print(f"❌ 에러: {result['error']}")
        else:
            print_result(d_text, result)