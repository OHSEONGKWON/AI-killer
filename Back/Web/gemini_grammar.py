"""
Gemini API 기반 한국어 문법 검사 및 윤문 모듈.

주요 기능:
- 맞춤법/오타 교정 (corrected_text)
- 문체 개선 (refined_text)
- 수정 내역 상세 설명 (diff_explanation)
- 문법 점수 및 자연스러움 평가 (score)
- 어휘 추천 (vocabulary_suggestions)
"""

import google.generativeai as genai
import json
from typing import Dict, Any
from .config import settings


# ==========================================
# 시스템 프롬프트 (설명 누락 방지 강화 버전)
# ==========================================
SYSTEM_PROMPT = """
You are an expert Korean grammar checker and writing improvement assistant.

YOUR TASK:
1. Carefully examine every word and phrase in the Korean text
2. Find ALL grammar errors, spelling mistakes, spacing issues, and awkward expressions
3. Provide TWO versions:
   - corrected_text: Fix only spelling/grammar errors (맞춤법, 띄어쓰기, 문법 오류만 수정)
   - refined_text: Also improve style and naturalness (문체까지 개선)
4. Document EVERY change you make in diff_explanation
5. Score the original text's grammar (0-100) and naturalness (0-100)

IMPORTANT RULES:
- Even small corrections like "되야→되어야", "할께→할게", "안되→안 돼" must be explained
- If there are NO errors, still provide the same text and explain it's perfect
- Be thorough - missing corrections is worse than over-correcting
- Respond ONLY with valid JSON

OUTPUT FORMAT:
{
  "original_text": "exact copy of user input",
  "corrected_text": "text with grammar/spelling fixed",
  "refined_text": "text with improved style",
  "diff_explanation": [
    {"original": "틀린부분", "changed": "고친부분", "reason": "자세한 설명"}
  ],
  "nuance_feedback": "detailed analysis in Korean",
  "vocabulary_suggestions": [
    {"word": "원래단어", "suggestion": "더나은단어", "reason": "이유"}
  ],
  "score": {"grammar": 85, "naturalness": 90}
}
"""


# ==========================================
# 모델 lazy loading
# ==========================================
_grammar_model = None


def get_grammar_model():
    """Gemini 문법 검사 모델을 반환합니다 (싱글톤 패턴)."""
    global _grammar_model
    if _grammar_model is None:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        generation_config = {
            "temperature": 0.1,  # 정확한 교정을 위해 온도를 낮춤
            "top_p": 0.95,
            "max_output_tokens": 2048,
            "response_mime_type": "application/json",
        }
        
        # 안전 설정 (문법 검사 텍스트가 필터에 걸리지 않도록)
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        _grammar_model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config=generation_config,
            safety_settings=safety_settings,
            system_instruction=SYSTEM_PROMPT
        )
    
    return _grammar_model


# ==========================================
# 분석 함수
# ==========================================
def check_grammar(text: str) -> Dict[str, Any]:
    """
    Gemini API를 호출하여 텍스트를 분석하고 JSON으로 반환합니다.
    
    Args:
        text: 검사할 텍스트
    
    Returns:
        Dict containing:
        - original_text: 원문
        - corrected_text: 맞춤법 교정된 텍스트
        - refined_text: 윤문된 최종 텍스트
        - diff_explanation: 수정 내역 리스트
        - nuance_feedback: 뉘앙스 분석
        - vocabulary_suggestions: 어휘 추천 리스트
        - score: 문법/자연스러움 점수
    """
    model = get_grammar_model()
    
    # 명확한 지시사항과 함께 텍스트 전달
    user_input = f"""Analyze this Korean text for grammar errors, spelling mistakes, and style improvements:

{text}

Find ALL errors and improvements. Be thorough."""
    
    try:
        response = model.generate_content(
            user_input,
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
        )
        
        # 안전 필터 체크
        if not response.candidates:
            # 폴백: 기본 응답 반환
            return {
                "original_text": text,
                "corrected_text": text,
                "refined_text": text,
                "diff_explanation": [],
                "nuance_feedback": "텍스트를 분석할 수 없습니다. 안전 필터에 의해 차단되었을 수 있습니다.",
                "vocabulary_suggestions": [],
                "score": {"grammar": 0, "naturalness": 0}
            }
        
        candidate = response.candidates[0]
        if candidate.finish_reason != 1:  # 1 = STOP (정상 완료)
            # 폴백: 기본 응답 반환
            finish_reasons = {0: "UNSPECIFIED", 1: "STOP", 2: "SAFETY", 3: "RECITATION", 4: "OTHER"}
            reason = finish_reasons.get(candidate.finish_reason, "UNKNOWN")
            return {
                "original_text": text,
                "corrected_text": text,
                "refined_text": text,
                "diff_explanation": [],
                "nuance_feedback": f"AI 분석이 차단되었습니다 (이유: {reason}). 다른 텍스트로 시도해주세요.",
                "vocabulary_suggestions": [],
                "score": {"grammar": 0, "naturalness": 0}
            }
        
        if not response.text:
            raise RuntimeError("Gemini API 응답이 비어있습니다.")
        
        result = json.loads(response.text)
        
        # 필수 필드 검증 및 기본값 설정
        result.setdefault("original_text", text)
        result.setdefault("corrected_text", text)
        result.setdefault("refined_text", text)
        result.setdefault("diff_explanation", [])
        result.setdefault("nuance_feedback", "")
        result.setdefault("vocabulary_suggestions", [])
        result.setdefault("score", {"grammar": 0, "naturalness": 0})
        
        return result
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini 응답을 JSON으로 파싱할 수 없습니다: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"문법 검사 중 오류 발생: {str(e)}")
