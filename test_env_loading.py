"""환경 변수 로드 테스트"""
import sys
sys.path.insert(0, r"C:\GitHub\AI-killer\Back")

print("=" * 60)
print("환경 변수 로드 테스트")
print("=" * 60)

from Web.config import settings

print(f"\n✅ Settings 로드 성공!")
print(f"\n주요 환경 변수:")
print(f"- JWT_SECRET_KEY: {settings.JWT_SECRET_KEY[:10]}..." if settings.JWT_SECRET_KEY else "- JWT_SECRET_KEY: 없음")
print(f"- GEMINI_API_KEY: {settings.GEMINI_API_KEY[:10]}..." if settings.GEMINI_API_KEY else "- GEMINI_API_KEY: 없음")
print(f"- SERPER_API_KEY: {settings.SERPER_API_KEY[:10] if settings.SERPER_API_KEY else '없음'}...")
print(f"- OPENAI_API_KEY: {settings.OPENAI_API_KEY[:10] if settings.OPENAI_API_KEY else '없음'}...")

print(f"\n.env 파일 경로:")
from pathlib import Path
env_path = Path(__file__).parent / "Back" / "Web" / "config.py"
config_dir = env_path.parent
expected_env = config_dir.parent.parent / ".env"
print(f"- 예상 경로: {expected_env}")
print(f"- 존재 여부: {expected_env.exists()}")

# 실제 config.py의 env_file 경로 확인
import inspect
config_file = inspect.getfile(settings.__class__)
print(f"\n- Config 파일 위치: {config_file}")
env_file_path = Path(config_file).parent.parent.parent / ".env"
print(f"- 실제 .env 경로: {env_file_path}")
print(f"- .env 존재: {env_file_path.exists()}")

if env_file_path.exists():
    # SERPER_API_KEY 값 직접 읽기
    with open(env_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('SERPER_API_KEY='):
                key = line.split('=', 1)[1].strip()
                print(f"\n.env 파일의 SERPER_API_KEY: {key[:10]}...")
                print(f"Settings의 SERPER_API_KEY: {settings.SERPER_API_KEY[:10] if settings.SERPER_API_KEY else '없음'}...")
                print(f"일치 여부: {key == settings.SERPER_API_KEY}")
                break
