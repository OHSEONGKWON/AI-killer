"""
데이터베이스 초기화 및 세션 팩토리.

주의:
- SQLModel과 aiosqlite 기반의 비동기 엔진을 사용합니다.
- 요청 단위 세션은 dependencies.get_db에서 관리합니다.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 데이터베이스 URL 정의
# "sqlite+aiosqlite:///./test.db" → 현재 디렉토리의 test.db에 비동기 드라이버로 연결
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# 비동기 엔진 생성 (echo=True는 SQL 로그 출력)
engine = create_async_engine(DATABASE_URL, echo=True)

# 비동기 세션 팩토리 (commit 후 객체 만료 비활성화)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)