"""
글쓰기 어시스턴트 라우터.

주요 기능:
- 사용자의 글을 분석하여 더 인간적이고 창의적으로 개선할 수 있는 제안 제공
- 문장별 개선안과 개선 이유 제시
- 전체적인 창의성/인간성 점수 평가

개선 영역:
- creativity: 창의성 향상 (독특한 표현, 비유 추가)
- tone: 어조 개선 (더 친근하게, 개성있게)
- clarity: 명료성 향상 (불필요한 수식어 제거, 간결화)
"""

import re
from typing import List
from fastapi import APIRouter

from ... import models

router = APIRouter()


def analyze_creativity(text: str) -> float:
    """텍스트의 창의성 점수를 계산 (0~100).
    
    평가 요소:
    - 비유/은유 사용
    - 독특한 표현
    - 형식적 표현 비율 (낮을수록 좋음)
    """
    score = 70.0  # 기본 점수
    
    # 형식적 표현이 많으면 감점
    formal_patterns = [r"~할 수 있습니다", r"~하는 것이 중요합니다", r"결론적으로"]
    formal_count = sum(len(re.findall(p, text)) for p in formal_patterns)
    score -= formal_count * 5
    
    # 비유적 표현이 있으면 가점
    metaphor_patterns = [r"마치", r"~처럼", r"~같은", r"~듯"]
    metaphor_count = sum(len(re.findall(p, text)) for p in metaphor_patterns)
    score += metaphor_count * 3
    
    # 감정 표현이 있으면 가점
    emotion_patterns = [r"!", r"정말", r"너무", r"과연"]
    emotion_count = sum(len(re.findall(p, text)) for p in emotion_patterns)
    score += emotion_count * 2
    
    return max(0.0, min(100.0, score))


def generate_improvement_suggestions(
    text: str, 
    focus: str
) -> List[models.ImprovementSuggestion]:
    """텍스트 개선 제안 생성.
    
    Args:
        text: 분석할 텍스트
        focus: 개선 초점 ("creativity", "tone", "clarity", "all")
    """
    suggestions = []
    
    # 형식적 표현 개선 (창의성)
    if focus in ["creativity", "all"]:
        formal_replacements = [
            (r"중요한 점은", "핵심은", "더 직관적인 표현으로 바꾸면 읽기 편해요"),
            (r"~할 수 있습니다", "~할 수 있어요", "친근한 어조로 개성을 더해보세요"),
            (r"결론적으로", "결국", "간결한 전환어로 자연스러움을 높여요"),
        ]
        
        for pattern, replacement, explanation in formal_replacements:
            for match in re.finditer(pattern, text):
                original = match.group()
                improved = re.sub(pattern, replacement, original)
                suggestions.append(models.ImprovementSuggestion(
                    original_text=original,
                    improved_text=improved,
                    improvement_type="creativity",
                    explanation=explanation
                ))
    
    # 어조 개선
    if focus in ["tone", "all"]:
        tone_patterns = [
            (r"~입니다", "~이에요", "더 친근한 어조로 독자와 가까워져요"),
            (r"~하는 것이", "~하기", "간결하고 자연스러운 표현이 좋아요"),
        ]
        
        for pattern, replacement, explanation in tone_patterns:
            for match in re.finditer(pattern, text):
                original = match.group()
                improved = re.sub(pattern, replacement, original)
                suggestions.append(models.ImprovementSuggestion(
                    original_text=original,
                    improved_text=improved,
                    improvement_type="tone",
                    explanation=explanation
                ))
    
    # 명료성 개선
    if focus in ["clarity", "all"]:
        # 중복 수식어 탐지 (예: "매우 아주")
        if re.search(r"(매우|정말|너무|아주)\s+(매우|정말|너무|아주)", text):
            suggestions.append(models.ImprovementSuggestion(
                original_text="매우 정말 좋은",
                improved_text="정말 좋은",
                improvement_type="clarity",
                explanation="중복 강조어를 제거하면 더 명확해져요"
            ))
    
    return suggestions


@router.post("/assistant/improve", response_model=models.AssistantResponse, summary="글쓰기 개선 제안")
async def improve_writing(request: models.AssistantRequest):
    """사용자의 글을 분석하여 더 인간적이고 창의적으로 개선할 수 있는 제안을 제공합니다.
    
    처리 순서:
    1) 텍스트의 창의성/인간성 점수 평가
    2) 개선 초점에 따라 맞춤 제안 생성
    3) 각 제안에 대한 구체적인 개선안과 이유 제시
    
    Args:
        content: 분석할 텍스트
        improvement_focus: 개선 초점 ("creativity", "tone", "clarity", "all")
    
    Returns:
        suggestions: 개선 제안 목록
        overall_score: 현재 글의 창의성/인간성 점수 (0~100)
    """
    # 창의성 점수 계산
    creativity_score = analyze_creativity(request.content)
    
    # 개선 제안 생성
    suggestions = generate_improvement_suggestions(
        request.content,
        request.improvement_focus or "all"
    )
    
    return models.AssistantResponse(
        suggestions=suggestions,
        overall_score=round(creativity_score, 2)
    )


@router.post("/assistant/rewrite", summary="문장 리라이팅")
async def rewrite_sentence(content: str, style: str = "creative"):
    """특정 문장을 더 창의적이거나 자연스럽게 다시 작성합니다.
    
    Args:
        content: 다시 쓸 문장
        style: 리라이팅 스타일 ("creative", "casual", "formal")
    
    Returns:
        rewritten: 다시 작성된 문장
        explanation: 어떻게 개선되었는지 설명
    """
    # 임시 구현: 실제로는 LLM API 호출
    rewritten = content.replace("~입니다", "~이에요").replace("중요한", "핵심적인")
    
    return {
        "original": content,
        "rewritten": rewritten,
        "style": style,
        "explanation": f"{style} 스타일로 더 자연스럽게 다시 작성했어요"
    }
