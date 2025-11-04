"""
로깅 설정 모듈.

주요 기능:
- Structured JSON 로깅 (운영 환경)
- 컬러 콘솔 로깅 (개발 환경)
- 선택적 Sentry 연동 (오류 추적)
- 환경별 로그 레벨 설정

사용 예:
    from logging_config import setup_logging, get_logger
    
    setup_logging()
    logger = get_logger(__name__)
    logger.info("서버 시작", extra={"port": 8000})
"""

import logging
import sys
from typing import Optional
import os

# Sentry 선택적 import
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False


class JSONFormatter(logging.Formatter):
    """JSON 형식 로그 포매터 (운영 환경용)."""
    
    def format(self, record: logging.LogRecord) -> str:
        """로그 레코드를 JSON 문자열로 변환합니다."""
        import json
        from datetime import datetime
        
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # 예외 정보 포함
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # 추가 컨텍스트 (extra 필드)
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """컬러 콘솔 로그 포매터 (개발 환경용)."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # 청록색
        'INFO': '\033[32m',      # 녹색
        'WARNING': '\033[33m',   # 노란색
        'ERROR': '\033[31m',     # 빨간색
        'CRITICAL': '\033[35m',  # 자주색
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """컬러를 적용한 로그 메시지 생성."""
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    level: Optional[str] = None,
    json_logs: bool = False,
    sentry_dsn: Optional[str] = None,
) -> None:
    """로깅 시스템을 설정합니다.
    
    Args:
        level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
               기본값은 환경변수 LOG_LEVEL 또는 INFO
        json_logs: True이면 JSON 형식, False이면 컬러 콘솔 (기본값: False)
                   환경변수 JSON_LOGS=1로도 설정 가능
        sentry_dsn: Sentry DSN (환경변수 SENTRY_DSN으로도 설정 가능)
    """
    # 환경변수에서 설정 읽기
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    if not json_logs:
        json_logs = os.getenv("JSON_LOGS", "0") == "1"
    
    if sentry_dsn is None:
        sentry_dsn = os.getenv("SENTRY_DSN")
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level, logging.INFO))
    
    # 기존 핸들러 제거
    root_logger.handlers.clear()
    
    # 콘솔 핸들러 추가
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level, logging.INFO))
    
    if json_logs:
        # JSON 형식 (운영 환경)
        formatter = JSONFormatter()
    else:
        # 컬러 콘솔 (개발 환경)
        formatter = ColoredFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Sentry 연동 (선택적)
    if sentry_dsn and SENTRY_AVAILABLE:
        sentry_sdk.init(
            dsn=sentry_dsn,
            traces_sample_rate=0.1,  # 10% 트레이스 샘플링 (비용 절감)
            profiles_sample_rate=0.1,  # 10% 프로파일 샘플링
            integrations=[
                FastApiIntegration(transaction_style="url"),
                SqlalchemyIntegration(),
            ],
            environment=os.getenv("ENVIRONMENT", "development"),
            # 민감 정보 필터링
            before_send=_filter_sensitive_data,
        )
        root_logger.info("Sentry 오류 추적 활성화", extra={"dsn": sentry_dsn[:20] + "..."})
    elif sentry_dsn and not SENTRY_AVAILABLE:
        root_logger.warning(
            "SENTRY_DSN이 설정되었으나 sentry-sdk가 설치되지 않았습니다. "
            "pip install sentry-sdk로 설치하세요."
        )
    
    # 외부 라이브러리 로그 레벨 조정 (노이즈 감소)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    root_logger.info(f"로깅 시스템 초기화 완료 (레벨: {level}, JSON: {json_logs})")


def _filter_sensitive_data(event: dict, hint: dict) -> Optional[dict]:
    """Sentry 이벤트에서 민감 정보를 필터링합니다.
    
    Args:
        event: Sentry 이벤트 데이터
        hint: 추가 컨텍스트
    
    Returns:
        필터링된 이벤트 또는 None (전송 취소)
    """
    # 예시: Authorization 헤더, 비밀번호 등 필터링
    if "request" in event and "headers" in event["request"]:
        headers = event["request"]["headers"]
        if "Authorization" in headers:
            headers["Authorization"] = "[FILTERED]"
        if "Cookie" in headers:
            headers["Cookie"] = "[FILTERED]"
    
    return event


def get_logger(name: str) -> logging.Logger:
    """모듈별 로거를 가져옵니다.
    
    Args:
        name: 로거 이름 (일반적으로 __name__ 사용)
    
    Returns:
        설정된 로거 인스턴스
    """
    return logging.getLogger(name)


# 테스트용 (직접 실행 시)
if __name__ == "__main__":
    setup_logging(level="DEBUG", json_logs=False)
    logger = get_logger(__name__)
    
    logger.debug("디버그 메시지")
    logger.info("정보 메시지", extra={"user_id": 123})
    logger.warning("경고 메시지")
    logger.error("오류 메시지")
    
    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("예외 발생")
