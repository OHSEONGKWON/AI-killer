"""
커스텀 예외 클래스 정의.

역할:
- AI 서비스 관련 공통 예외 계층 구조
- 일관된 에러 처리를 위한 예외 타입 분류
"""

from typing import Optional


class AIServiceError(Exception):
    """AI 서비스 관련 공통 예외 베이스 클래스."""
    
    def __init__(self, message: str = "AI 서비스 오류가 발생했습니다.", detail: Optional[str] = None):
        self.message = message
        self.detail = detail
        super().__init__(self.message)


class SafetyBlockError(AIServiceError):
    """Gemini API SAFETY 차단 예외."""
    
    def __init__(self, message: str = "안전 정책에 의해 차단된 콘텐츠입니다.", detail: Optional[str] = None):
        super().__init__(message, detail)


class ModelLoadError(AIServiceError):
    """AI 모델 로딩 실패 예외."""
    
    def __init__(self, model_name: str, detail: Optional[str] = None):
        message = f"AI 모델 '{model_name}' 로딩에 실패했습니다."
        super().__init__(message, detail)


class APIKeyError(AIServiceError):
    """API 키 관련 예외."""
    
    def __init__(self, service: str = "AI 서비스"):
        message = f"{service} API 키가 설정되지 않았습니다."
        super().__init__(message)


class ResponseParsingError(AIServiceError):
    """AI 응답 파싱 실패 예외."""
    
    def __init__(self, message: str = "AI 응답을 파싱할 수 없습니다.", detail: Optional[str] = None):
        super().__init__(message, detail)


class QuotaExceededError(AIServiceError):
    """API 할당량 초과 예외."""
    
    def __init__(self, message: str = "일일 사용 한도를 초과했습니다.", detail: Optional[str] = None):
        super().__init__(message, detail)
