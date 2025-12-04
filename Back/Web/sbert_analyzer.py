"""
SBERT 코사인 유사도 분석 모듈.

역할:
- 입력 텍스트와 AI 생성 샘플들 간의 코사인 유사도 계산
- SBERT (Sentence-BERT) 임베딩 기반
- 싱글톤 패턴으로 모델 메모리 효율화
"""

import logging
from typing import List
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger(__name__)

# 전역 변수로 모델 지연 로드 (싱글톤 패턴)
_sbert_model = None


def get_sbert_model() -> SentenceTransformer:
    """
    SBERT 모델을 로드합니다 (싱글톤 패턴으로 메모리 절약).
    
    Returns:
        SentenceTransformer 모델 인스턴스
        
    Raises:
        RuntimeError: 모델 로드 실패 시
    """
    global _sbert_model
    
    if _sbert_model is None:
        try:
            model_name = "jhgan/ko-sroberta-multitask"
            _sbert_model = SentenceTransformer(model_name)
            logger.info(f"SBERT 모델 로드 완료: {model_name}")
        except Exception as e:
            logger.error(f"SBERT 모델 로드 실패: {e}")
            raise RuntimeError(f"SBERT 모델을 로드할 수 없습니다: {e}")
    
    return _sbert_model


def calculate_sbert_similarity(original_text: str, generated_samples: List[str]) -> float:
    """
    SBERT를 사용하여 원본 텍스트와 AI 생성 샘플들 간의 코사인 유사도를 계산합니다.
    
    Args:
        original_text: 분석할 원본 텍스트
        generated_samples: AI가 생성한 비교용 샘플 리스트
    
    Returns:
        코사인 유사도 점수 (0.0 ~ 1.0)
        높을수록 AI가 작성한 글과 유사함
        
    Raises:
        RuntimeError: 모델 로드 또는 임베딩 실패 시
    """
    if not original_text or not generated_samples:
        logger.warning("입력 텍스트가 비어있습니다")
        return 0.0
    
    try:
        model = get_sbert_model()
        
        # 원본 텍스트 임베딩
        original_embedding = model.encode(original_text, convert_to_tensor=True)
        
        # 생성 샘플들 임베딩
        sample_embeddings = model.encode(generated_samples, convert_to_tensor=True)
        
        # 코사인 유사도 계산 (벡터화)
        similarities = util.cos_sim(original_embedding, sample_embeddings)[0]
        
        # 평균 유사도 반환 (0~1 범위)
        avg_similarity = float(similarities.mean())
        
        logger.debug(f"SBERT 유사도 계산 완료: {avg_similarity:.3f}")
        
        return min(avg_similarity, 1.0)  # 1.0 이하로 클립
        
    except Exception as e:
        logger.error(f"SBERT 유사도 계산 중 오류: {e}")
        raise RuntimeError(f"SBERT 분석 실패: {e}")
