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


# OpenAI 클라이언트 지연 초기화 (API 키 없으면 서버는 정상 기동, 호출 시에만 필요)
_client: Optional[AsyncOpenAI] = None

def get_client() -> AsyncOpenAI:
    """OPENAI_API_KEY가 있을 때만 클라이언트를 초기화하여 반환합니다.

    Raises:
        ValueError: OPENAI_API_KEY 미설정 시
    """
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY 환경변수가 설정되지 않았습니다. .env 파일에 OPENAI_API_KEY를 추가하세요."
            )
        _client = AsyncOpenAI(
            api_key=api_key,
            timeout=httpx.Timeout(30.0, connect=5.0),  # 전체 30초, 연결 5초 타임아웃
            max_retries=3,  # 자동 재시도 3회 (OpenAI SDK 내장)
        )
    return _client


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
    try:
        client = get_client()
    except ValueError as e:
        # 키가 없을 때는 명시적으로 안내
        raise ValueError(
            "OPENAI_API_KEY 환경변수가 설정되지 않았습니다. .env 파일에 OPENAI_API_KEY를 추가하세요."
        ) from e
    
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
    try:
        client = get_client()
    except ValueError as e:
        raise ValueError(
            "OPENAI_API_KEY 환경변수가 설정되지 않았습니다. .env 파일에 OPENAI_API_KEY를 추가하세요."
        ) from e
    
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


async def generate_ai_abstracts(
    title: Optional[str] = None,
    n: int = 3,
    *,
    prompt: Optional[str] = None,
    num_samples: Optional[int] = None,
) -> List[str]:
    """AI가 생성한 비교용 초록 샘플들을 반환합니다.

    analysis.py 호환을 위해 title/prompt, n/num_samples 모두 지원합니다.
    OPENAI_API_KEY가 없을 경우, 간단한 더미 샘플을 반환하여 서버가 정상 동작하도록 합니다.

    Args:
        title: 주제/제목 텍스트
        n: 생성 개수
        prompt: (대안) 프롬프트 텍스트
        num_samples: (대안) 생성 개수

    Returns:
        생성된 초록 문자열 리스트
    """
    content = prompt or title or "입력 텍스트"
    count = num_samples or n or 3

    # 키가 없으면 더미 샘플을 반환 (OpenAI 호출 생략)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return [
            f"[샘플 1] {content[:50]} ... 에 대한 AI 초록 예시",
            f"[샘플 2] {content[:50]} ... 관련 요약 샘플",
            f"[샘플 3] {content[:50]} ... 비교용 텍스트",
        ][:count]

    # 키가 있으면 실제 OpenAI 호출
    combined_prompt = f"다음 내용의 텍스트와 유사한 한국어 초록을 200자 내외로 작성해주세요: {content}"
    return await generate_multiple_completions(
        prompt=combined_prompt,
        n=count,
        max_tokens=200,
        temperature=0.8,
        system_message="당신은 한국어 논문 초록을 작성하는 전문 AI입니다.",
    )
