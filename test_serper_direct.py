"""Serper API 직접 테스트"""
import requests
import sys
sys.path.insert(0, r"C:\GitHub\AI-killer\Back")

from Web.config import settings

print("=" * 60)
print("Serper API 직접 테스트")
print("=" * 60)

print(f"\nSERPER_API_KEY 설정 여부: {'있음' if settings.SERPER_API_KEY else '없음'}")
if settings.SERPER_API_KEY:
    print(f"API 키 (앞 10자): {settings.SERPER_API_KEY[:10]}...")

url = "https://google.serper.dev/search"
headers = {
    "X-API-KEY": settings.SERPER_API_KEY,
    "Content-Type": "application/json"
}
payload = {
    "q": "\"인공지능은 인간의 학습능력과 추론능력\"",
    "num": 3,
    "gl": "kr",
    "hl": "ko"
}

print(f"\n요청 URL: {url}")
print(f"검색 쿼리: {payload['q']}")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    print(f"\n상태 코드: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        results = data.get("organic", [])
        print(f"검색 결과 수: {len(results)}개\n")
        
        for i, result in enumerate(results[:3], 1):
            print(f"{i}. {result.get('title', 'N/A')}")
            print(f"   URL: {result.get('link', 'N/A')}")
            print(f"   요약: {result.get('snippet', 'N/A')[:100]}...")
            print()
    else:
        print(f"오류: {response.text}")
        
except Exception as e:
    print(f"❌ 예외 발생: {e}")
