"""표절 검사 API 테스트 스크립트"""
import requests
import json

def test_plagiarism_check():
    url = "http://127.0.0.1:8001/api/v1/plagiarism/check"
    
    # 테스트 텍스트 (위키백과에서 실제로 가져온 문장)
    test_text = """
    인공지능은 인간의 학습능력과 추론능력, 지각능력, 자연언어의 이해능력 등을 
    컴퓨터 프로그램으로 실현한 기술이다. 인간의 지능으로 할 수 있는 사고, 학습, 
    자기계발 등을 컴퓨터가 할 수 있도록 하는 방법을 연구하는 컴퓨터 공학 및 
    정보기술의 한 분야로서, 컴퓨터가 인간의 지능적인 행동을 모방할 수 있도록 
    하는 것을 인공지능이라고 한다.
    """
    
    data = {"content": test_text.strip()}
    
    print("=" * 60)
    print("표절 검사 API 테스트")
    print("=" * 60)
    print(f"\n요청 URL: {url}")
    print(f"텍스트: {test_text.strip()}\n")
    
    try:
        response = requests.post(url, json=data, timeout=30)
        
        print(f"상태 코드: {response.status_code}")
        print(f"\n응답 내용:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            result = response.json()
            print("\n" + "=" * 60)
            print("결과 요약:")
            print(f"- 표절 가능성: {result.get('is_plagiarized', False)}")
            print(f"- 전체 유사도: {result.get('overall_similarity', 0):.2f}%")
            print(f"- 발견된 소스: {len(result.get('matched_sources', []))}개")
            print("=" * 60)
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except requests.exceptions.Timeout:
        print("❌ 요청 시간 초과")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    test_plagiarism_check()
