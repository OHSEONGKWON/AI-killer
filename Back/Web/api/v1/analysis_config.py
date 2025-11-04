"""
분석 설정 관리 API (Analysis Configuration Management).

관리자 전용 엔드포인트로, 텍스트 유형별 AI 분석 가중치를 관리합니다.

주요 기능:
- 텍스트 유형별 가중치 설정 조회/생성/수정/삭제
- 기본 프리셋 제공 (논문, 에세이, 블로그)
- 가중치 합계 검증 (권장: 1.0)
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from ...dependencies import get_db, get_current_admin_user
from ... import models, crud

router = APIRouter()


@router.get(
    "/admin/analysis-configs",
    response_model=List[models.AnalysisConfigResponse],
    summary="모든 분석 설정 조회"
)
async def get_all_configs(
    db=Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user)
):
    """모든 텍스트 유형의 분석 설정을 조회합니다.
    
    Returns:
        전체 분석 설정 목록
    """
    configs = await crud.get_all_analysis_configs(db)
    return configs


@router.get(
    "/admin/analysis-configs/{text_type}",
    response_model=models.AnalysisConfigResponse,
    summary="특정 유형 분석 설정 조회"
)
async def get_config(
    text_type: str,
    db=Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user)
):
    """특정 텍스트 유형의 분석 설정을 조회합니다.
    
    Args:
        text_type: 텍스트 유형 (paper, essay, blog, etc.)
    
    Returns:
        해당 유형의 분석 설정
    """
    config = await crud.get_analysis_config(db, text_type=text_type)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"텍스트 유형 '{text_type}'에 대한 설정을 찾을 수 없습니다."
        )
    return config


@router.post(
    "/admin/analysis-configs",
    response_model=models.AnalysisConfigResponse,
    status_code=status.HTTP_201_CREATED,
    summary="새 분석 설정 생성"
)
async def create_config(
    config: models.AnalysisConfigCreate,
    db=Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user)
):
    """새로운 텍스트 유형의 분석 설정을 생성합니다.
    
    Args:
        config: 생성할 설정 (text_type, 가중치 등)
    
    Returns:
        생성된 분석 설정
    
    Raises:
        400: 가중치 합계가 1.0이 아닐 때 (경고)
        409: 이미 존재하는 text_type일 때
    """
    # 중복 체크
    existing = await crud.get_analysis_config(db, text_type=config.text_type)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"텍스트 유형 '{config.text_type}'에 대한 설정이 이미 존재합니다."
        )
    
    # 가중치 합계 검증 (경고만, 차단하지는 않음)
    weight_sum = (config.sbert_weight + config.kobert_weight + 
                  config.perplexity_weight + config.burstiness_weight)
    if abs(weight_sum - 1.0) > 0.01:
        # 경고 로그만 출력 (실제로는 logger 사용)
        print(f"⚠️ 경고: 가중치 합계가 {weight_sum:.2f}입니다. 1.0을 권장합니다.")
    
    # 생성
    new_config = await crud.create_analysis_config(db, config=config)
    return new_config


@router.put(
    "/admin/analysis-configs/{text_type}",
    response_model=models.AnalysisConfigResponse,
    summary="분석 설정 수정"
)
async def update_config(
    text_type: str,
    config_update: models.AnalysisConfigUpdate,
    db=Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user)
):
    """기존 분석 설정을 수정합니다.
    
    Args:
        text_type: 텍스트 유형
        config_update: 수정할 필드 (부분 업데이트 가능)
    
    Returns:
        수정된 분석 설정
    """
    updated_config = await crud.update_analysis_config(db, text_type=text_type, config_update=config_update)
    if not updated_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"텍스트 유형 '{text_type}'에 대한 설정을 찾을 수 없습니다."
        )
    
    # 수정 후 가중치 합계 검증
    weight_sum = (updated_config.sbert_weight + updated_config.kobert_weight + 
                  updated_config.perplexity_weight + updated_config.burstiness_weight)
    if abs(weight_sum - 1.0) > 0.01:
        print(f"⚠️ 경고: 수정 후 가중치 합계가 {weight_sum:.2f}입니다.")
    
    return updated_config


@router.delete(
    "/admin/analysis-configs/{text_type}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="분석 설정 삭제"
)
async def delete_config(
    text_type: str,
    db=Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user)
):
    """분석 설정을 삭제합니다.
    
    Args:
        text_type: 삭제할 텍스트 유형
    """
    success = await crud.delete_analysis_config(db, text_type=text_type)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"텍스트 유형 '{text_type}'에 대한 설정을 찾을 수 없습니다."
        )
    return None


@router.post(
    "/admin/analysis-configs/init-defaults",
    status_code=status.HTTP_201_CREATED,
    summary="기본 프리셋 초기화"
)
async def initialize_default_configs(
    db=Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user)
):
    """기본 분석 설정 프리셋(논문, 에세이, 블로그)을 생성합니다.
    
    이미 존재하는 설정은 건너뜁니다.
    
    Returns:
        생성된 설정 목록
    """
    default_configs = [
        models.AnalysisConfigCreate(
            text_type="paper",
            description="학술 논문용 설정 (형식성과 정확도 중시)",
            sbert_weight=0.20,
            kobert_weight=0.40,  # 논문은 KoBERT 가중치 높게
            perplexity_weight=0.25,
            burstiness_weight=0.15,
            is_active=True,
            is_default=True  # 기본 설정
        ),
        models.AnalysisConfigCreate(
            text_type="essay",
            description="에세이용 설정 (창의성과 다양성 중시)",
            sbert_weight=0.25,
            kobert_weight=0.30,
            perplexity_weight=0.20,
            burstiness_weight=0.25,  # 에세이는 Burstiness 가중치 높게
            is_active=True,
            is_default=False
        ),
        models.AnalysisConfigCreate(
            text_type="blog",
            description="블로그/SNS용 설정 (자연스러움 중시)",
            sbert_weight=0.30,  # 블로그는 SBERT 가중치 높게
            kobert_weight=0.25,
            perplexity_weight=0.20,
            burstiness_weight=0.25,
            is_active=True,
            is_default=False
        ),
    ]
    
    created_configs = []
    for config in default_configs:
        # 이미 존재하는지 확인
        existing = await crud.get_analysis_config(db, text_type=config.text_type)
        if not existing:
            new_config = await crud.create_analysis_config(db, config=config)
            created_configs.append(new_config)
    
    return {
        "message": f"{len(created_configs)}개의 기본 설정이 생성되었습니다.",
        "created": [c.text_type for c in created_configs]
    }
