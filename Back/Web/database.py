"""
데이터베이스 초기화 및 세션 팩토리.

주의:
- SQLModel과 aiosqlite 기반의 비동기 엔진을 사용합니다.
- 요청 단위 세션은 dependencies.get_db에서 관리합니다.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

# 데이터베이스 URL 정의
# DB 파일을 Back/Web/test.db에 고정
DB_PATH = os.path.join(os.path.dirname(__file__), "test.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# 비동기 엔진 생성 (echo=True는 SQL 로그 출력)
engine = create_async_engine(DATABASE_URL, echo=True)

# 비동기 세션 팩토리 (commit 후 객체 만료 비활성화)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)