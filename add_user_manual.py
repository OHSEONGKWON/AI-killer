"""
데이터베이스에 수동으로 사용자를 추가하는 스크립트
"""
import asyncio
from sqlmodel import select, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from Back.Web.database import engine
from Back.Web.models import User
from Back.Web.security import get_password_hash


async def init_db():
    """데이터베이스 테이블 생성"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def add_user_manual():
    """수동으로 사용자 추가"""
    # 데이터베이스 초기화
    await init_db()
    
    # 사용자 정보 입력
    username = input("사용자명을 입력하세요: ")
    email = input("이메일을 입력하세요: ")
    password = input("비밀번호를 입력하세요: ")
    is_admin_input = input("관리자 권한을 부여하시겠습니까? (y/n): ")
    is_admin = is_admin_input.lower() == 'y'
    
    # 비밀번호 해시화
    hashed_password = get_password_hash(password)
    
    # 데이터베이스에 추가
    async with AsyncSession(engine) as session:
        # 중복 체크
        existing_user = await session.execute(
            select(User).where(User.username == username)
        )
        if existing_user.scalars().first():
            print(f"❌ 사용자명 '{username}'은 이미 존재합니다.")
            return
        
        existing_email = await session.execute(
            select(User).where(User.email == email)
        )
        if existing_email.scalars().first():
            print(f"❌ 이메일 '{email}'은 이미 등록되어 있습니다.")
            return
        
        # 사용자 생성
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_admin=is_admin,
            kakao_id=None
        )
        
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        
        print(f"\n✅ 사용자가 성공적으로 추가되었습니다!")
        print(f"   - ID: {new_user.id}")
        print(f"   - 사용자명: {new_user.username}")
        print(f"   - 이메일: {new_user.email}")
        print(f"   - 관리자: {new_user.is_admin}")


async def list_all_users():
    """모든 사용자 목록 조회"""
    await init_db()
    
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        if not users:
            print("등록된 사용자가 없습니다.")
            return
        
        print(f"\n📋 등록된 사용자 목록 (총 {len(users)}명)")
        print("=" * 80)
        for user in users:
            print(f"ID: {user.id:3d} | 사용자명: {user.username:20s} | 이메일: {user.email:30s} | 관리자: {user.is_admin}")


async def delete_user_manual():
    """수동으로 사용자 삭제"""
    await init_db()
    
    user_id = int(input("삭제할 사용자 ID를 입력하세요: "))
    
    async with AsyncSession(engine) as session:
        user = await session.get(User, user_id)
        
        if not user:
            print(f"❌ ID {user_id}인 사용자를 찾을 수 없습니다.")
            return
        
        print(f"\n삭제할 사용자 정보:")
        print(f"   - 사용자명: {user.username}")
        print(f"   - 이메일: {user.email}")
        
        confirm = input("\n정말 삭제하시겠습니까? (y/n): ")
        if confirm.lower() != 'y':
            print("삭제가 취소되었습니다.")
            return
        
        await session.delete(user)
        await session.commit()
        
        print(f"✅ 사용자가 삭제되었습니다.")


async def main():
    """메인 메뉴"""
    while True:
        print("\n" + "=" * 50)
        print("데이터베이스 관리 메뉴")
        print("=" * 50)
        print("1. 사용자 추가")
        print("2. 사용자 목록 조회")
        print("3. 사용자 삭제")
        print("4. 종료")
        print("=" * 50)
        
        choice = input("메뉴를 선택하세요 (1-4): ")
        
        if choice == '1':
            await add_user_manual()
        elif choice == '2':
            await list_all_users()
        elif choice == '3':
            await delete_user_manual()
        elif choice == '4':
            print("프로그램을 종료합니다.")
            break
        else:
            print("❌ 잘못된 입력입니다.")


if __name__ == "__main__":
    asyncio.run(main())
