"""
간단한 사용자 추가 스크립트 (bcrypt 72바이트 제한 처리)
"""
import sqlite3
import bcrypt

# 데이터베이스 연결
conn = sqlite3.connect('Back/test.db')
cursor = conn.cursor()

print("=== 사용자 추가 ===")
username = input("사용자명: ")
email = input("이메일: ")
password = input("비밀번호: ")
is_admin = input("관리자 권한? (y/n): ").lower() == 'y'

# 중복 체크
cursor.execute("SELECT * FROM user WHERE username = ?", (username,))
if cursor.fetchone():
    print(f"❌ 사용자명 '{username}'은 이미 존재합니다.")
    conn.close()
    exit()

cursor.execute("SELECT * FROM user WHERE email = ?", (email,))
if cursor.fetchone():
    print(f"❌ 이메일 '{email}'은 이미 등록되어 있습니다.")
    conn.close()
    exit()

# 비밀번호 해시 (72바이트로 제한)
password_bytes = password.encode('utf-8')[:72]
hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

# 사용자 추가
cursor.execute("""
    INSERT INTO user (username, email, hashed_password, is_admin, kakao_id)
    VALUES (?, ?, ?, ?, NULL)
""", (username, email, hashed.decode('utf-8'), 1 if is_admin else 0))

conn.commit()
user_id = cursor.lastrowid

print(f"\n✅ 사용자가 추가되었습니다!")
print(f"   ID: {user_id}")
print(f"   사용자명: {username}")
print(f"   이메일: {email}")
print(f"   관리자: {is_admin}")

# 모든 사용자 조회
print("\n=== 전체 사용자 목록 ===")
cursor.execute("SELECT id, username, email, is_admin FROM user")
for row in cursor.fetchall():
    print(f"ID:{row[0]:3d} | {row[1]:20s} | {row[2]:30s} | 관리자:{bool(row[3])}")

conn.close()
