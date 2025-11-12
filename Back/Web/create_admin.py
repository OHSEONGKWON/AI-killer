"""
관리자 계정 생성 스크립트.

실행 방법:
    cd Back/Web
    python -m create_admin

또는:
    cd Back
    python -m Web.create_admin

주의:
- 운영 환경에서는 반드시 강력한 비밀번호를 사용하세요!
- 이 스크립트는 개발 환경에서만 사용하세요.
"""

import asyncio
import sys
import os

# 상위 디렉터리를 sys.path에 추가
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from passlib.context import CryptContext

# Web 패키지에서 import
from Web.database import engine
from Web.models import User

# 비밀번호 해시 함수
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """비밀번호를 해시화합니다."""
    return pwd_context.hash(password)


async def create_admin(
    username: str = "admin",
    email: str = "admin@example.com",
    password: str = "admin123"
):
    """관리자 계정을 생성합니다.
    
    Args:
        username: 관리자 아이디 (기본값: admin)
        email: 관리자 이메일 (기본값: admin@example.com)
        password: 관리자 비밀번호 (기본값: admin123)
    """
    async with AsyncSession(engine) as session:
        # 기존 관리자 확인
        statement = select(User).where(User.username == username)
        result = await session.exec(statement)
        existing = result.first()
        
        if existing:
            print(f"⚠️  '{username}' 계정이 이미 존재합니다.")
            print(f"   - ID: {existing.id}")
            print(f"   - Email: {existing.email}")
            print(f"   - 관리자 권한: {existing.is_admin}")
            
            # 관리자 권한 업데이트
            if not existing.is_admin:
                existing.is_admin = True
                await session.commit()
                print(f"   ✅ 관리자 권한을 부여했습니다.")
            return
        
        # 관리자 생성
        admin = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            is_admin=True
        )
        session.add(admin)
        await session.commit()
        await session.refresh(admin)
        
        print("=" * 60)
        print("✅ 관리자 계정 생성 완료!")
        print("=" * 60)
        print(f"   Username: {admin.username}")
        print(f"   Email:    {admin.email}")
        print(f"   Password: {password}")
        print(f"   ID:       {admin.id}")
        print("=" * 60)
        print("⚠️  운영 환경에서는 반드시 비밀번호를 변경하세요!")
        print("=" * 60)


async def main():
    """메인 함수."""
    print("\n🔧 관리자 계정 생성 스크립트\n")
    
    # 사용자 정의 입력 받기 (선택 사항)
    import sys
    if len(sys.argv) > 1:
        username = sys.argv[1]
        email = sys.argv[2] if len(sys.argv) > 2 else f"{username}@example.com"
        password = sys.argv[3] if len(sys.argv) > 3 else "admin123"
        
        print(f"사용자 지정 정보로 생성:")
        print(f"  - Username: {username}")
        print(f"  - Email: {email}")
        print(f"  - Password: {password}\n")
        
        await create_admin(username, email, password)
    else:
        print("기본 관리자 계정 생성 (admin/admin123)")
        print("사용자 정의: python create_admin.py <username> <email> <password>\n")
        await create_admin()


if __name__ == "__main__":
    asyncio.run(main())
