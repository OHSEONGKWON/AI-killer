"""
OpenAI API 호출 래퍼 모듈.

주요 기능:
- 재시도(retry) 로직으로 일시적 네트워크/API 오류 대응
- 타임아웃 설정으로 무한 대기 방지
- 구조화된 예외 처리 및 사용자 친화적 오류 메시지
- 비용 추적을 위한 토큰 사용량 로깅

사용 예:
    from openai_client import generate_text_completion
    
    result = await generate_text_completion(
        prompt="한국어 논문 초록을 작성해주세요",
        max_tokens=200
    )
"""

import asyncio
import os
from typing import List, Optional
import httpx
from openai import AsyncOpenAI, OpenAIError, APIError, APITimeoutError, RateLimitError, AuthenticationError


# OpenAI 클라이언트 초기화
# API 키는 환경변수에서 읽음 (config.py의 settings를 사용해도 됨)
client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=httpx.Timeout(30.0, connect=5.0),  # 전체 30초, 연결 5초 타임아웃
    max_retries=3,  # 자동 재시도 3회 (OpenAI SDK 내장)
)


async def generate_text_completion(
    prompt: str,
    model: str = "gpt-3.5-turbo",
    max_tokens: int = 200,
    temperature: float = 0.7,
    system_message: str = "당신은 한국어 논문 초록을 작성하는 전문 AI입니다.",
) -> str:
    """OpenAI Chat Completion API를 호출하여 텍스트를 생성합니다.
    
    Args:
        prompt: 사용자 프롬프트 (예: "다음 제목으로 초록을 작성해주세요: ...")
        model: 사용할 모델 (기본값: gpt-3.5-turbo)
        max_tokens: 생성할 최대 토큰 수 (기본값: 200)
        temperature: 창의성 정도 (0~2, 기본값: 0.7)
        system_message: 시스템 역할 메시지
    
    Returns:
        생성된 텍스트 (str)
    
    Raises:
        ValueError: API 키가 설정되지 않았을 때
        OpenAIError: OpenAI API 호출 실패 시
    """
    if not client.api_key:
        raise ValueError(
            "OPENAI_API_KEY 환경변수가 설정되지 않았습니다. "
            ".env 파일에 OPENAI_API_KEY를 추가하세요."
        )
    
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        # 토큰 사용량 로깅 (비용 추적에 유용)
        usage = response.usage
        print(f"[OpenAI] 토큰 사용: {usage.prompt_tokens} (입력) + {usage.completion_tokens} (출력) = {usage.total_tokens} (총)")
        
        return response.choices[0].message.content.strip()
    
    except AuthenticationError as e:
        # API 키 인증 실패
        raise ValueError(f"OpenAI API 인증 실패: {e}. API 키를 확인하세요.")
    
    except RateLimitError as e:
        # 요청 제한 초과 (무료 티어 또는 할당량 초과)
        raise OpenAIError(f"OpenAI API 요청 제한 초과: {e}. 잠시 후 다시 시도하세요.")
    
    except APITimeoutError as e:
        # 타임아웃 (30초 초과)
        raise OpenAIError(f"OpenAI API 타임아웃: {e}. 네트워크 상태를 확인하세요.")
    
    except APIError as e:
        # 기타 API 오류 (500, 503 등)
        raise OpenAIError(f"OpenAI API 서버 오류: {e}. 잠시 후 다시 시도하세요.")
    
    except OpenAIError as e:
        # 기타 OpenAI 관련 오류
        raise OpenAIError(f"OpenAI API 호출 실패: {e}")


async def generate_multiple_completions(
    prompt: str,
    n: int = 3,
    model: str = "gpt-3.5-turbo",
    max_tokens: int = 200,
    temperature: float = 0.7,
    system_message: str = "당신은 한국어 논문 초록을 작성하는 전문 AI입니다.",
) -> List[str]:
    """OpenAI API를 호출하여 여러 개의 텍스트를 생성합니다.
    
    Args:
        prompt: 사용자 프롬프트
        n: 생성할 텍스트 개수 (기본값: 3)
        model: 사용할 모델
        max_tokens: 생성할 최대 토큰 수
        temperature: 창의성 정도
        system_message: 시스템 역할 메시지
    
    Returns:
        생성된 텍스트 리스트 (List[str])
    
    Raises:
        ValueError: API 키가 설정되지 않았을 때
        OpenAIError: OpenAI API 호출 실패 시
    """
    if not client.api_key:
        raise ValueError(
            "OPENAI_API_KEY 환경변수가 설정되지 않았습니다. "
            ".env 파일에 OPENAI_API_KEY를 추가하세요."
        )
    
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            n=n,  # 한 번에 n개 생성
        )
        
        # 토큰 사용량 로깅
        usage = response.usage
        print(f"[OpenAI] 토큰 사용 (n={n}): {usage.prompt_tokens} (입력) + {usage.completion_tokens} (출력) = {usage.total_tokens} (총)")
        
        return [choice.message.content.strip() for choice in response.choices]
    
    except AuthenticationError as e:
        raise ValueError(f"OpenAI API 인증 실패: {e}. API 키를 확인하세요.")
    
    except RateLimitError as e:
        raise OpenAIError(f"OpenAI API 요청 제한 초과: {e}. 잠시 후 다시 시도하세요.")
    
    except APITimeoutError as e:
        raise OpenAIError(f"OpenAI API 타임아웃: {e}. 네트워크 상태를 확인하세요.")
    
    except APIError as e:
        raise OpenAIError(f"OpenAI API 서버 오류: {e}. 잠시 후 다시 시도하세요.")
    
    except OpenAIError as e:
        raise OpenAIError(f"OpenAI API 호출 실패: {e}")


async def generate_ai_abstracts(title: str, n: int = 3) -> List[str]:
    """논문 제목을 받아 AI가 생성한 초록 샘플들을 반환합니다.
    
    이 함수는 기존 analysis.py의 generate_ai_content를 대체합니다.
    
    Args:
        title: 논문 제목
        n: 생성할 초록 개수 (기본값: 3)
    
    Returns:
        생성된 초록 리스트 (List[str])
    
    Raises:
        ValueError: API 키가 설정되지 않았을 때
        OpenAIError: OpenAI API 호출 실패 시
    """
    prompt = f"다음 제목의 논문에 대한 초록을 200자 내외로 작성해주세요: {title}"
    
    return await generate_multiple_completions(
        prompt=prompt,
        n=n,
        max_tokens=200,
        temperature=0.8,  # 다양성을 위해 조금 높게 설정
        system_message="당신은 한국어 논문 초록을 작성하는 전문 AI입니다.",
    )
