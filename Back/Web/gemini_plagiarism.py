# -*- coding: utf-8 -*-
"""
Gemini API를 활용한 지능형 표절 탐지 모듈
원본 출처를 자동으로 추적하고 표절 여부를 분석합니다.

⚠️ 중요 제한사항:
- Gemini는 실시간 인터넷 검색을 하지 않습니다
- 학습 데이터(~2024년) 내에서만 출처를 찾을 수 있습니다
- 최신 콘텐츠나 비공개 자료는 탐지하지 못합니다
- 실제 표절 검증 시스템으로 사용하려면 Google Custom Search API 등과 결합 필요
"""
import logging
import json
import re
import google.generativeai as genai
from typing import Dict, List, Optional
from .config import settings

logging.getLogger("google.generativeai").setLevel(logging.ERROR)

# 시스템 프롬프트
SYSTEM_PROMPT = """
당신은 '지능형 표절 수사관'입니다.
사용자가 입력한 텍스트(`draft_text`)를 분석하여, 당신의 방대한 지식 데이터베이스 내에서 이 글의 **원본(Original Source)**으로 추정되는 내용을 찾아내세요.

## ⚠️ 중요 지침
- **확실한 증거가 있을 때만** 출처를 명시하세요
- **추측이나 가능성만으로** 구체적인 논문명/기사명을 언급하지 마세요
- 원본을 찾지 못했다면 솔직하게 "출처를 특정할 수 없음" 또는 "창작물로 보임"이라고 답하세요
- 존재하지 않는 출처를 만들어내지 마세요

## 수행 절차 (Step-by-Step)
1. **출처 탐색:** 입력된 텍스트의 문체, 내용, 팩트를 분석하여 원본이 무엇인지 추론합니다.
   - 명확히 알려진 저작물(위키백과, 유명 뉴스, 교과서 등)과 일치하는지 확인
   - 단순히 비슷한 주제가 아니라 **문장 구조와 표현이 실제로 일치**하는지 검증
2. **비교 분석:** 찾아낸 '원본'과 사용자의 '초안'을 비교하여 표절 여부를 판단합니다.
3. **신중한 판단:** 
   - 확실하지 않으면 `original_found: false`, `suspected_source: "출처를 특정할 수 없음"`으로 설정
   - 일반적인 주제나 흔한 표현은 표절로 판단하지 않음
   - 구체적인 출처명은 **100% 확신할 때만** 제시

## 출력 형식 (JSON Format Only)
반드시 아래 JSON 스키마를 따르세요.

{
  "suspected_source": "확실한 출처만 명시 (예: '위키백과 - 이순신 항목', '조선일보 2024.3.15 기사') 또는 '출처를 특정할 수 없음' / '창작물로 보임'",
  "source_url": "출처의 URL (예: 'https://ko.wikipedia.org/wiki/이순신', 'https://www.chosun.com/...'). 없으면 null",
  "original_found": true | false,
  "overall_similarity_score": 0~100,
  "highlight_segments": [
    {
      "target_text": "draft_text 내에서 하이라이트 할 텍스트",
      "type": "EXACT" | "SUSPICIOUS",
      "reason": "구체적인 분석 근거 (예: '위키백과 내용과 문장 구조 90% 일치', '일반적인 상식 수준의 내용')"
    }
  ]
}
"""

# Gemini 모델 초기화 (지연 로딩)
_plagiarism_model = None

def get_plagiarism_model():
    """표절 탐지용 Gemini 모델 로드 (지연 로딩)"""
    global _plagiarism_model
    
    if _plagiarism_model is None:
        # API 키 검증
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY가 설정되지 않았습니다.")
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        try:
            generation_config = {
                "temperature": 0.1,
                "response_mime_type": "application/json",
            }
            
            # 안전 설정 (표절 검사 텍스트가 필터에 걸리지 않도록)
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            
            _plagiarism_model = genai.GenerativeModel(
                model_name="gemini-2.5-pro",
                generation_config=generation_config,
                safety_settings=safety_settings,
                system_instruction=SYSTEM_PROMPT
            )
            
            logging.info("Gemini 표절 탐지 모델 로드 완료")
        except Exception as e:
            logging.error(f"Gemini 표절 탐지 모델 로드 실패: {e}")
            raise RuntimeError("Gemini 표절 탐지 모델을 로드할 수 없습니다.")
    
    return _plagiarism_model


def verify_url(url: Optional[str]) -> Optional[str]:
    """
    URL이 유효한 형식인지 검증합니다.
    실제 접속 가능 여부는 확인하지 않습니다 (성능 이유).
    
    Args:
        url: 검증할 URL
    
    Returns:
        유효한 URL 또는 None
    """
    if not url:
        return None
    
    # 기본 URL 형식 검증
    url_pattern = re.compile(
        r'^https?://'
        r'(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'
        r'(?:/[^\s]*)?$'
    )
    
    if url_pattern.match(url):
        return url
    else:
        logging.warning(f"유효하지 않은 URL 형식: {url}")
        return None


def detect_plagiarism(draft_text: str) -> Dict:
    """
    입력된 텍스트의 표절 여부를 AI가 자동으로 탐지합니다.
    
    ⚠️ 주의: Gemini는 학습 데이터 내에서만 출처를 찾습니다.
    실시간 웹 검색을 하지 않으므로 최신 콘텐츠는 탐지하지 못합니다.
    
    Args:
        draft_text: 검사할 텍스트
    
    Returns:
        {
            "suspected_source": str,        # 추정 출처
            "original_found": bool,          # 원본 발견 여부
            "overall_similarity_score": int, # 유사도 점수 (0~100)
            "highlight_segments": [          # 하이라이트 구간
                {
                    "target_text": str,
                    "type": "EXACT" | "SUSPICIOUS",
                    "reason": str
                }
            ]
        }
    """
    if not draft_text.strip():
        raise ValueError("검사할 텍스트가 비어있습니다.")
    
    model = get_plagiarism_model()
    
    user_input = f"""
    ## 분석 요청 텍스트 (Draft):
    {draft_text}
    """
    
    try:
        response = model.generate_content(user_input)
        
        # 안전 필터 체크
        if not response.candidates:
            logging.warning("Gemini API가 응답을 생성하지 못했습니다 (안전 필터)")
            return {
                "suspected_source": "분석 불가 (안전 필터)",
                "source_url": None,
                "original_found": False,
                "overall_similarity_score": 0,
                "highlight_segments": [],
                "error": "입력 텍스트가 안전 필터에 걸렸습니다."
            }
        
        candidate = response.candidates[0]
        if candidate.finish_reason != 1:  # 1 = STOP (정상 완료)
            finish_reasons = {0: "UNSPECIFIED", 1: "STOP", 2: "SAFETY", 3: "RECITATION", 4: "OTHER"}
            reason = finish_reasons.get(candidate.finish_reason, "UNKNOWN")
            logging.warning(f"Gemini API 비정상 종료: {reason}")
            return {
                "suspected_source": f"분석 불가 ({reason})",
                "source_url": None,
                "original_found": False,
                "overall_similarity_score": 0,
                "highlight_segments": [],
                "error": f"AI 응답이 비정상적으로 종료되었습니다: {reason}"
            }
        
        if not response.text:
            logging.warning("Gemini API 응답이 비어있습니다")
            return {
                "suspected_source": "분석 불가 (빈 응답)",
                "source_url": None,
                "original_found": False,
                "overall_similarity_score": 0,
                "highlight_segments": [],
                "error": "AI 응답이 비어있습니다."
            }
        
        result = json.loads(response.text)
        
        # 데이터 검증 및 기본값 설정
        if "suspected_source" not in result:
            result["suspected_source"] = "출처 불명"
        if "source_url" not in result:
            result["source_url"] = None
        if "original_found" not in result:
            result["original_found"] = False
        if "overall_similarity_score" not in result:
            result["overall_similarity_score"] = 0
        if "highlight_segments" not in result:
            result["highlight_segments"] = []
        
        # URL 검증 (Gemini가 잘못된 URL을 생성할 수 있음)
        if result.get("source_url"):
            verified_url = verify_url(result["source_url"])
            if not verified_url:
                logging.warning(f"Gemini가 유효하지 않은 URL을 반환: {result['source_url']}")
                result["source_url"] = None
        
        # 출처를 찾았지만 URL이 없는 경우 경고
        if result["original_found"] and not result["source_url"]:
            result["suspected_source"] += " (URL 미제공 - AI 학습 데이터 기반 추론)"
        
        return result
        
    except json.JSONDecodeError as e:
        logging.error(f"Gemini 응답 JSON 파싱 실패: {e}")
        return {
            "suspected_source": "분석 오류",
            "original_found": False,
            "overall_similarity_score": 0,
            "highlight_segments": [],
            "error": "AI 응답을 파싱할 수 없습니다."
        }
    except Exception as e:
        logging.error(f"표절 탐지 중 오류: {e}")
        return {
            "suspected_source": "분석 오류",
            "original_found": False,
            "overall_similarity_score": 0,
            "highlight_segments": [],
            "error": str(e)
        }


def format_highlight_text(draft_text: str, segments: List[Dict]) -> str:
    """
    하이라이트 구간을 HTML 형식으로 포맷팅합니다.
    
    Args:
        draft_text: 원본 텍스트
        segments: 하이라이트 구간 리스트
    
    Returns:
        HTML 형식의 하이라이트된 텍스트
    """
    highlighted_text = draft_text
    
    # EXACT는 빨강, SUSPICIOUS는 노랑
    for seg in segments:
        target = seg.get("target_text", "")
        type_ = seg.get("type", "SUSPICIOUS")
        
        if type_ == "EXACT":
            replacement = f'<mark class="exact">{target}</mark>'
        else:
            replacement = f'<mark class="suspicious">{target}</mark>'
        
        highlighted_text = highlighted_text.replace(target, replacement)
    
    return highlighted_text
