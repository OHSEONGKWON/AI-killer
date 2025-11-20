import google.generativeai as genai
import json
import sys

# ==========================================
# 1. API 키 설정 (여기에 발급받은 키를 넣으세요)
# ==========================================
# 주의: "AIza..." 로 시작하는 키 전체를 따옴표 안에 넣어야 합니다.
API_KEY = "여기에_발급받은_API_키를_넣으세요"

# API 키가 입력되지 않았을 경우를 대비한 안전장치
if API_KEY.startswith("여기에"):
    print("❌ 오류: API 키가 설정되지 않았습니다.")
    print("코드의 9번째 줄 'API_KEY' 변수에 구글 AI Studio에서 발급받은 키를 입력해주세요.")
    sys.exit()

try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    print(f"❌ API 키 설정 중 오류 발생: {e}")
    sys.exit()


# ==========================================
# 2. 시스템 프롬프트 (설명 누락 방지 강화 버전)
# ==========================================
SYSTEM_PROMPT = """
당신은 아주 꼼꼼한 한국어 교정 및 윤문 전문가입니다.
사용자의 텍스트를 분석하여 결과를 JSON으로 반환하세요.

## 🚨 핵심 원칙 (Strict Rules)
1. **모든 변경 사항 기록 필수:** 텍스트가 단 한 글자라도 수정되었다면, 그 내용은 **반드시** `diff_explanation` 리스트에 포함되어야 합니다.
2. **맞춤법/오타 최우선:** '되야 -> 되어야', '할께 -> 할게' 같은 기본적인 맞춤법 수정은 설명에서 절대 누락하지 마세요.
3. **이유 명시:** 왜 수정했는지 구체적인 문법적 이유나 스타일 개선 이유를 적으세요.

## 수행 작업
1. **기본 교정 (Correction):** 맞춤법, 띄어쓰기, 오타를 완벽하게 수정합니다.
2. **윤문 (Refinement):** 어색한 표현, 번역투, 중복된 단어를 다듬어 자연스럽게 만듭니다.
3. **평가:** 문법 정확도와 자연스러움을 점수로 매깁니다.

## 출력 형식 (JSON Only)
반드시 아래 JSON 스키마만 출력하세요.

{
  "original_text": "사용자 원문",
  "corrected_text": "맞춤법과 오타가 수정된 1차 교정 텍스트",
  "refined_text": "문체가 다듬어진 최종 윤문 텍스트",
  "diff_explanation": [
    {
      "original": "되야",
      "changed": "되어야",
      "reason": "맞춤법 오류 ('되-' 뒤에 어미 '-어'가 와서 '되어' 또는 '돼'가 되어야 함)"
    },
    {
      "original": "뭐가",
      "changed": "무엇이",
      "reason": "문어체에 맞는 격식 있는 표현으로 변경"
    }
  ],
  "nuance_feedback": "글의 느낌 및 뉘앙스 분석",
  "vocabulary_suggestions": [
    { "word": "원문 단어", "suggestion": "추천 단어", "reason": "이유" }
  ],
  "score": {
    "grammar": 0~100,
    "naturalness": 0~100
  }
}
"""

# ==========================================
# 3. 분석 함수 정의
# ==========================================
def analyze_text_with_gemini(user_text):
    """Gemini API를 호출하여 텍스트를 분석하고 JSON으로 반환"""
    
    # 모델 설정 (JSON 출력 강제)
    generation_config = {
        "temperature": 0.1, # 정확한 교정을 위해 온도를 낮춤
        "top_p": 0.95,
        "max_output_tokens": 2048,
        "response_mime_type": "application/json", 
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", # 빠르고 저렴한 모델
        generation_config=generation_config,
        system_instruction=SYSTEM_PROMPT
    )

    user_input = f"""
    ## 입력 텍스트
    {user_text}
    """

    try:
        response = model.generate_content(user_input)
        return json.loads(response.text) # JSON 파싱
    except Exception as e:
        return {"error": str(e)}

# ==========================================
# 4. 메인 실행 블록
# ==========================================
if __name__ == "__main__":
    print("\n" + "="*40)
    print("✍️  Gemini AI 문법/윤문 검사기 (강화판)")
    print("="*40)
    
    while True:
        try:
            # 사용자 입력 받기 (목적 입력 삭제됨)
            print("\n[입력] 교정할 문장을 입력하세요 (종료: q):")
            user_text = input(">> ")
            
            if user_text.lower() in ['q', 'quit', 'exit', '종료']:
                print("프로그램을 종료합니다.")
                break
                
            if not user_text.strip():
                print("⚠️ 내용을 입력해주세요.")
                continue

            print("\n🔍 AI가 분석 중입니다... 잠시만 기다려주세요.\n")
            
            # API 호출
            result = analyze_text_with_gemini(user_text)

            # 결과 출력 로직
            if "error" in result:
                print(f"❌ 에러 발생: {result['error']}")
                print("API 키가 올바른지, 인터넷이 연결되어 있는지 확인해주세요.")
            else:
                print("-" * 50)
                print(f"📝 [원문]: {result.get('original_text', '')}")
                print(f"✅ [교정]: {result.get('corrected_text', '')}")
                print(f"✨ [윤문]: {result.get('refined_text', '')}")
                print("-" * 50)
                
                scores = result.get('score', {})
                print(f"📊 [점수]: 문법 {scores.get('grammar', 0)}점 / 자연스러움 {scores.get('naturalness', 0)}점")
                print(f"💡 [뉘앙스]: {result.get('nuance_feedback', '')}")
                print("-" * 50)
                
                diffs = result.get('diff_explanation', [])
                if diffs:
                    print("🔧 [수정 내역 상세]")
                    for diff in diffs:
                        print(f" • '{diff.get('original')}' → '{diff.get('changed')}'")
                        print(f"   └ 이유: {diff.get('reason')}")
                else:
                    print("🔧 수정할 내용이 없습니다. (완벽한 문장입니다!)")
                
                vocabs = result.get('vocabulary_suggestions', [])
                if vocabs:
                    print("\n📚 [어휘 추천]")
                    for voc in vocabs:
                        print(f" • {voc.get('word')} → {voc.get('suggestion')} ({voc.get('reason')})")
                print("-" * 50)
                
        except KeyboardInterrupt:
            print("\n프로그램을 종료합니다.")
            break