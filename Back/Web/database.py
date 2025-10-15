# database.py

from sqlmodel import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

# 데이터베이스 URL을 정의합니다. 
# "sqlite+aiosqlite:///./test.db"는 같은 디렉토리에 있는
# "test.db" 파일에 비동기 드라이버로 연결한다는 의미입니다.
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# 비동기 엔진을 생성합니다. 이것이 데이터베이스의 진입점입니다.
engine = create_async_engine(DATABASE_URL, echo=True)

# 비동기 세션 팩토리
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)