# -*- coding: utf-8 -*-
"""
Gemini API와 SBERT를 활용한 텍스트 유사도 분석 모듈
"""
import os
import logging
import asyncio
import google.generativeai as genai
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict, AsyncGenerator

from .config import settings
from .perplexity_kobert import calculate_perplexity

# 로그 최소화
logging.getLogger("absl").setLevel(logging.ERROR)
logging.getLogger("grpc").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)

# Gemini API 키 설정 (환경변수에서 가져오기)
if not settings.GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY가 설정되지 않았습니다. "
        ".env 파일에 GEMINI_API_KEY를 추가해주세요."
    )

genai.configure(api_key=settings.GEMINI_API_KEY)

# Gemini 모델 초기화
try:
    gemini_model = genai.GenerativeModel("gemini-2.0-flash")
except Exception as e:
    logging.warning(f"gemini-2.0-flash 로드 실패: {e}, gemini-pro로 재시도")
    try:
        gemini_model = genai.GenerativeModel("gemini-pro")
    except Exception as e_pro:
        logging.error(f"Gemini 모델 로드 실패: {e_pro}")
        gemini_model = None

# SBERT 모델 로드 (한국어)
sbert_model = None

def get_sbert_model():
    """SBERT 모델을 로드합니다 (지연 로딩)"""
    global sbert_model
    if sbert_model is None:
        try:
            sbert_model = SentenceTransformer('jhgan/ko-sroberta-multitask')
        except Exception as e:
            logging.error(f"SBERT 모델 로드 실패: {e}")
            raise RuntimeError("SBERT 모델을 로드할 수 없습니다.")
    return sbert_model


# Jaccard 제거: 이제 SBERT 코사인 유사도만 사용


async def generate_gemini_texts(topic: str, num_sentences: int = 20, char_limit: int = 200) -> List[str]:
    """
    Gemini API를 사용하여 주제에 대한 다양한 문장을 생성합니다.
    
    Args:
        topic: 생성할 문장의 주제
        num_sentences: 생성할 문장 수
        char_limit: 각 문장의 최대 길이
    
    Returns:
        생성된 문장 리스트
    """
    if gemini_model is None:
        raise RuntimeError("Gemini 모델이 초기화되지 않았습니다.")
    
    generated_texts = []
    
    for i in range(num_sentences):
        prompt = (
            f"주제: '{topic}'\n"
            "요청: 위 주제에 대해 약 200자 내외의 단락을 작성하세요.\n"
            "조건: 목록/개조식 금지, 이전 결과와 내용 중복 금지, 하나의 완결된 문단으로 작성.\n"
            f"표시: (항목 번호: {i+1})"
        )
        
        try:
            response = gemini_model.generate_content(prompt)
            text = getattr(response, 'text', '').strip()
            
            if not text and response.parts:
                text = " ".join(part.text for part in response.parts if hasattr(part, 'text')).strip()
            
            if text:
                # 200자 내외를 유지하기 위해 하드 컷 적용
                text = text[:char_limit]
                generated_texts.append(text)
            else:
                logging.warning(f"{i+1}번째 문장 생성 실패: 응답이 비어있습니다.")
                
        except Exception as e:
            logging.error(f"Gemini API 호출 중 오류: {e}")
            continue
    
    return generated_texts


async def calculate_similarity(
    user_text: str,
    topic: str,
    num_sentences: int = 20,
) -> Dict:
    """
    사용자 텍스트와 Gemini가 생성한 텍스트 간의 유사도 및 Perplexity를 계산합니다.
    
    Args:
        user_text: 비교 대상 사용자 텍스트
        topic: Gemini가 생성할 텍스트의 주제
        num_sentences: 생성할 문장 수 (기본 20)
    
    Returns:
        {
            "user_text": str,
            "topic": str,
            "generated_texts": List[str],
            "scores": List[Dict],  # 각 문장별 SBERT 점수
            "top_scores": List[Dict],  # 상위 3개 점수
            "final_score": float,  # 최종 평균 (0~1)
            "perplexity": float,  # 사용자 텍스트의 Perplexity
            "num_generated": int
        }
    """
    # Perplexity 계산 (사용자 텍스트에 대해)
    try:
        perplexity_score = await asyncio.to_thread(calculate_perplexity, user_text)
    except Exception as e:
        logging.warning(f"Perplexity 계산 실패: {e}")
        perplexity_score = None
    
    # Gemini로 텍스트 생성
    generated_texts = await generate_gemini_texts(topic, num_sentences)
    
    if not generated_texts:
        raise ValueError("Gemini로부터 생성된 텍스트가 없습니다.")
    
    # SBERT 모델 로드
    model = get_sbert_model()
    
    # 사용자 텍스트 인코딩
    emb_user = model.encode(user_text, convert_to_tensor=True)
    
    # 각 생성된 텍스트와 유사도 계산
    all_scores = []
    
    for idx, gen_text in enumerate(generated_texts, 1):
        try:
            # SBERT 코사인 유사도
            emb_gen = model.encode(gen_text, convert_to_tensor=True)
            semantic_sim = util.cos_sim(emb_user, emb_gen).item()
            final_score = semantic_sim  # SBERT 점수 그대로 사용
            
            all_scores.append({
                "idx": idx,
                "text": gen_text,
                "semantic_similarity": round(semantic_sim, 4),
                "score": round(final_score, 4)
            })
            
        except Exception as e:
            logging.error(f"문장 {idx} 유사도 계산 중 오류: {e}")
            continue
    
    if not all_scores:
        raise ValueError("유사도를 계산할 수 없습니다.")
    
    # 점수 기준 내림차순 정렬
    all_scores.sort(key=lambda x: x["score"], reverse=True)
    
    # Top-3 선택 및 평균 계산
    num_to_average = min(3, len(all_scores))
    top_scores = all_scores[:num_to_average]
    
    total_score = sum(item['score'] for item in top_scores)
    final_average_score = round(total_score / num_to_average, 4)
    
    # 확률(%) 계산
    final_probability = round(final_average_score * 100, 1)
    
    # 사용자 텍스트 문장 분할 및 하이라이팅
    user_sentences = [s.strip() + '.' for s in user_text.split('.') if s.strip()]
    highlighted_sentences = []
    
    for idx, sentence in enumerate(user_sentences, 1):
        if not sentence.strip():
            continue
            
        # 각 사용자 문장과 Top-3 생성 문장들의 유사도 계산
        emb_sentence = model.encode(sentence, convert_to_tensor=True)
        max_sim = 0.0
        best_match = None
        
        for top_item in top_scores:
            emb_top = model.encode(top_item['text'], convert_to_tensor=True)
            sim = util.cos_sim(emb_sentence, emb_top).item()
            if sim > max_sim:
                max_sim = sim
                best_match = top_item['idx']
        
        # 유사도에 따른 위험도 레벨
        if max_sim >= 0.7:
            risk_level = "high"
        elif max_sim >= 0.5:
            risk_level = "medium"
        elif max_sim >= 0.3:
            risk_level = "low"
        else:
            risk_level = "safe"
        
        highlighted_sentences.append({
            "sentence_idx": idx,
            "text": sentence,
            "similarity": round(max_sim, 4),
            "risk_level": risk_level,
            "matched_gen_idx": best_match
        })
    
    # AI 작성 가능성 판단
    if final_probability >= 80:
        ai_likelihood = "매우 높음"
        recommendation = "이 텍스트는 AI가 작성했을 가능성이 매우 높습니다. 재작성을 권장합니다."
    elif final_probability >= 60:
        ai_likelihood = "높음"
        recommendation = "AI 작성 가능성이 높습니다. 일부 문장을 수정하는 것을 권장합니다."
    elif final_probability >= 40:
        ai_likelihood = "보통"
        recommendation = "AI와 사람이 함께 작성했을 가능성이 있습니다. 의심스러운 부분을 확인하세요."
    else:
        ai_likelihood = "낮음"
        recommendation = "사람이 작성한 것으로 판단됩니다. 자연스러운 텍스트입니다."

    return {
        "user_text": user_text,
        "topic": topic,
        "generated_texts": generated_texts[:3],  # Top-3만 반환
        "scores": all_scores[:3],  # Top-3만 반환
        "top_scores": top_scores,
        "final_score": final_average_score,
        "final_probability": final_probability,
        "perplexity": perplexity_score,
        "num_generated": len(generated_texts),
        "highlighted_sentences": highlighted_sentences,
        "ai_likelihood": ai_likelihood,
        "recommendation": recommendation,
        "analysis": {
            "high_risk_sentences": sum(1 for s in highlighted_sentences if s['risk_level'] == 'high'),
            "medium_risk_sentences": sum(1 for s in highlighted_sentences if s['risk_level'] == 'medium'),
            "low_risk_sentences": sum(1 for s in highlighted_sentences if s['risk_level'] == 'low'),
            "safe_sentences": sum(1 for s in highlighted_sentences if s['risk_level'] == 'safe'),
            "total_sentences": len(highlighted_sentences)
        },
        "weights": {
            "semantic": 1.0
        }
    }


async def stream_similarity(
    user_text: str,
    topic: str,
    num_sentences: int = 20,
) -> AsyncGenerator[str, None]:
    """유사도 및 Perplexity 계산 결과를 SSE로 스트리밍 (진행률 제거, 최종 결과만 전송)

    이벤트 타입:
      - final: 최종 결과 (유사도 + Perplexity)
      - error: 오류 발생
    """
    try:
        # calculate_similarity 재사용 (내부적으로 perplexity 포함)
        result = await calculate_similarity(
            user_text=user_text,
            topic=topic,
            num_sentences=num_sentences
        )
        yield _sse_event({"type": "final", **result})
    except Exception as e:
        logging.error(f"스트리밍 중 오류: {e}")
        yield _sse_event({"type": "error", "message": str(e)})


def _sse_event(payload: Dict) -> str:
    import json
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
