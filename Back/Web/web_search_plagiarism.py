"""
실시간 웹 검색 기반 표절 검사 모듈 (Serper API 사용)

Gemini AI와 실제 웹 검색을 결합하여 정확한 표절 탐지를 수행합니다.

사용법:
1. Serper API 키 발급: https://serper.dev/
2. .env 파일에 SERPER_API_KEY=your_key 추가
3. pip install requests
"""

import logging
import requests
from typing import Dict, List, Optional
from .config import settings

logger = logging.getLogger(__name__)


def search_web(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """
    Serper API를 사용하여 실시간 웹 검색을 수행합니다.
    
    Args:
        query: 검색할 텍스트 (최대 200자 권장)
        num_results: 반환할 결과 수 (기본 5개, 범위: 1-10)
    
    Returns:
        검색 결과 리스트 [
            {
                "title": "페이지 제목",
                "link": "URL",
                "snippet": "요약문"
            },
            ...
        ]
    """
    # 입력값 검증
    if not query or not query.strip():
        logger.warning("빈 검색 쿼리가 입력되었습니다")
        return []
    
    if not settings.SERPER_API_KEY:
        logger.warning("SERPER_API_KEY가 설정되지 않았습니다. 웹 검색을 건너뜁니다.")
        return []
    
    # 쿼리 정제 및 길이 제한
    search_query = f'"{query.strip()[:200]}"'
    num_results = max(1, min(num_results, 10))  # 1~10 범위로 제한
    
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": settings.SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "q": search_query,
        "num": num_results,
        "gl": "kr",  # 한국 검색 결과
        "hl": "ko"   # 한국어
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        # organic 검색 결과 파싱
        for item in data.get("organic", [])[:num_results]:
            # title과 link가 필수 필드
            title = item.get("title", "").strip()
            link = item.get("link", "").strip()
            snippet = item.get("snippet", "").strip()
            
            if title and link:  # 최소한 title과 link는 있어야 함
                results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet
                })
        
        logger.info(f"웹 검색 완료: {len(results)}개 결과 발견")
        return results
        
    except requests.exceptions.Timeout:
        logger.error(f"Serper API 요청 시간 초과 (타임아웃: 15초)")
        return []
    except requests.exceptions.HTTPError as e:
        logger.error(f"Serper API HTTP 오류: {e.response.status_code} - {e.response.text[:200]}")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Serper API 네트워크 오류: {e}")
        return []
    except ValueError as e:
        logger.error(f"웹 검색 JSON 파싱 오류: {e}")
        return []
    except Exception as e:
        logger.error(f"웹 검색 중 예상치 못한 오류: {e}", exc_info=True)
        return []


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    두 텍스트의 유사도를 n-gram과 단어 오버랩을 결합하여 계산합니다.
    
    Args:
        text1: 비교할 텍스트 1
        text2: 비교할 텍스트 2
    
    Returns:
        유사도 (0.0 ~ 1.0)
    """
    import re
    
    # 텍스트 정규화 (소문자, 특수문자 제거, 공백 정리)
    def normalize(text):
        text = text.lower()
        text = re.sub(r'[^\w\s가-힣]', '', text)  # 특수문자 제거 (한글, 영문, 숫자만)
        text = re.sub(r'\s+', ' ', text).strip()  # 연속 공백 제거
        return text
    
    text1_norm = normalize(text1)
    text2_norm = normalize(text2)
    
    if not text1_norm or not text2_norm:
        return 0.0
    
    # 1. 문자 수준 유사도 (Longest Common Subsequence 비율)
    def lcs_ratio(s1, s2):
        """최장 공통 부분 문자열 비율"""
        m, n = len(s1), len(s2)
        if m == 0 or n == 0:
            return 0.0
        
        # DP 테이블 (메모리 최적화)
        prev = [0] * (n + 1)
        for i in range(1, m + 1):
            curr = [0] * (n + 1)
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    curr[j] = prev[j-1] + 1
                else:
                    curr[j] = max(curr[j-1], prev[j])
            prev = curr
        
        lcs_length = prev[n]
        return (2.0 * lcs_length) / (m + n)
    
    char_similarity = lcs_ratio(text1_norm, text2_norm)
    
    # 2. 단어 수준 Jaccard 유사도
    words1 = set(text1_norm.split())
    words2 = set(text2_norm.split())
    
    if words1 and words2:
        word_jaccard = len(words1 & words2) / len(words1 | words2)
    else:
        word_jaccard = 0.0
    
    # 3. Bigram (2-gram) 유사도
    def get_ngrams(text, n):
        words = text.split()
        if len(words) < n:
            return set()
        return set(tuple(words[i:i+n]) for i in range(len(words) - n + 1))
    
    bigrams1 = get_ngrams(text1_norm, 2)
    bigrams2 = get_ngrams(text2_norm, 2)
    
    if bigrams1 and bigrams2:
        bigram_jaccard = len(bigrams1 & bigrams2) / len(bigrams1 | bigrams2)
    else:
        bigram_jaccard = 0.0
    
    # 4. Trigram (3-gram) 유사도 - 더 긴 구문 매칭
    trigrams1 = get_ngrams(text1_norm, 3)
    trigrams2 = get_ngrams(text2_norm, 3)
    
    if trigrams1 and trigrams2:
        trigram_jaccard = len(trigrams1 & trigrams2) / len(trigrams1 | trigrams2)
    else:
        trigram_jaccard = 0.0
    
    # 5. 연속 문자 매칭 (긴 공통 부분 문자열)
    def longest_common_substring_ratio(s1, s2):
        """가장 긴 공통 부분 문자열의 비율"""
        m, n = len(s1), len(s2)
        if m == 0 or n == 0:
            return 0.0
        
        max_len = 0
        dp = [[0] * (n + 1) for _ in range(2)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i-1] == s2[j-1]:
                    dp[i % 2][j] = dp[(i-1) % 2][j-1] + 1
                    max_len = max(max_len, dp[i % 2][j])
                else:
                    dp[i % 2][j] = 0
        
        return (2.0 * max_len) / (m + n)
    
    substring_ratio = longest_common_substring_ratio(text1_norm, text2_norm)
    
    # 가중 평균 (문자 LCS 25%, 단어 20%, bigram 25%, trigram 20%, 연속문자 10%)
    similarity = (
        (char_similarity * 0.25) + 
        (word_jaccard * 0.20) + 
        (bigram_jaccard * 0.25) + 
        (trigram_jaccard * 0.20) +
        (substring_ratio * 0.10)
    )
    
    return similarity


def detect_plagiarism_with_web_search(text: str, threshold: float = 0.7) -> Dict:
    """
    실시간 웹 검색을 통한 표절 탐지.
    
    Args:
        text: 검사할 텍스트
        threshold: 표절 판단 임계값 (0.0 ~ 1.0)
    
    Returns:
        {
            "is_plagiarized": bool,
            "max_similarity": float,
            "sources": [
                {
                    "title": str,
                    "url": str,
                    "snippet": str,
                    "similarity": float
                }
            ],
            "searched": bool  # 실제 검색 수행 여부
        }
    """
    # 텍스트가 너무 짧으면 검색하지 않음
    if len(text.strip()) < 20:
        return {
            "is_plagiarized": False,
            "max_similarity": 0.0,
            "sources": [],
            "searched": False,
            "message": "텍스트가 너무 짧아 검색하지 않았습니다."
        }
    
    # 문장 단위로 분할 (간단한 구현)
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
    
    if not sentences:
        return {
            "is_plagiarized": False,
            "max_similarity": 0.0,
            "sources": [],
            "searched": False,
            "message": "유효한 문장이 없습니다."
        }
    
    # 텍스트 길이에 따라 검색할 문장 수 조절 (API 할당량 절약)
    # - 짧은 글 (1-3문장): 1개만 검색
    # - 중간 글 (4-10문장): 2개 검색  
    # - 긴 글 (11개 이상): 3개 검색
    if len(sentences) <= 3:
        num_to_search = 1
    elif len(sentences) <= 10:
        num_to_search = 2
    else:
        num_to_search = 3
    
    sentences_to_search = sorted(sentences, key=len, reverse=True)[:num_to_search]
    
    all_sources = []
    max_similarity = 0.0
    
    # 전체 텍스트로도 한 번 검색 (가장 중요)
    full_text_search = search_web(text[:300], num_results=10)  # 300자까지만
    
    for result in full_text_search:
        snippet = result.get("snippet", "")
        # 전체 텍스트 vs snippet 유사도
        full_similarity = calculate_text_similarity(text, snippet)
        
        all_sources.append({
            "title": result.get("title", ""),
            "url": result.get("link", ""),
            "snippet": snippet,
            "similarity": round(full_similarity, 3),
            "matched_sentence": text[:100]  # 전체 텍스트 일부
        })
        
        if full_similarity > max_similarity:
            max_similarity = full_similarity
    
    # 개별 문장으로도 검색 (추가 검증)
    for sentence in sentences_to_search:
        num_results = 8 if sentence == sentences_to_search[0] else 5
        search_results = search_web(sentence, num_results=num_results)
        
        for result in search_results:
            snippet = result.get("snippet", "")
            # 문장 vs snippet 유사도
            sentence_similarity = calculate_text_similarity(sentence, snippet)
            # 전체 텍스트 vs snippet 유사도도 계산
            full_similarity = calculate_text_similarity(text, snippet)
            # 둘 중 높은 값 사용
            best_similarity = max(sentence_similarity, full_similarity)
            
            all_sources.append({
                "title": result.get("title", ""),
                "url": result.get("link", ""),
                "snippet": snippet,
                "similarity": round(best_similarity, 3),
                "matched_sentence": sentence[:100]
            })
            
            if best_similarity > max_similarity:
                max_similarity = best_similarity
    
    # 유사도 높은 순으로 정렬
    all_sources.sort(key=lambda x: x["similarity"], reverse=True)
    
    # 중복 URL 제거 (같은 출처는 하나만)
    seen_urls = set()
    unique_sources = []
    for source in all_sources:
        if source["url"] not in seen_urls:
            seen_urls.add(source["url"])
            unique_sources.append(source)
    
    return {
        "is_plagiarized": max_similarity >= threshold,
        "max_similarity": round(max_similarity, 3),
        "sources": unique_sources[:5],  # 상위 5개만
        "searched": True,
        "threshold": threshold
    }


def hybrid_plagiarism_check(text: str) -> Dict:
    """
    Gemini AI 분석 + 실시간 웹 검색을 결합한 하이브리드 표절 검사.
    
    Args:
        text: 검사할 텍스트
    
    Returns:
        종합 표절 검사 결과
    """
    # Step 1: Gemini AI 분석 (기존 코드 사용)
    from .gemini_plagiarism import detect_plagiarism
    
    ai_result = detect_plagiarism(text)
    
    # Step 2: 실시간 웹 검색
    web_result = detect_plagiarism_with_web_search(text, threshold=0.7)
    
    # Step 3: 결과 통합
    final_result = {
        "ai_analysis": {
            "suspected_source": ai_result.get("suspected_source", ""),
            "overall_similarity_score": ai_result.get("overall_similarity_score", 0),
            "highlight_segments": ai_result.get("highlight_segments", [])
        },
        "web_search": {
            "is_plagiarized": web_result.get("is_plagiarized", False),
            "max_similarity": web_result.get("max_similarity", 0.0),
            "sources": web_result.get("sources", []),
            "searched": web_result.get("searched", False)
        },
        "final_verdict": {
            "is_plagiarized": (
                ai_result.get("overall_similarity_score", 0) > 60 or
                web_result.get("is_plagiarized", False)
            ),
            "confidence": "high" if web_result.get("searched") else "medium",
            "recommendation": ""
        }
    }
    
    # 추천 메시지 생성
    if final_result["final_verdict"]["is_plagiarized"]:
        if web_result.get("sources"):
            final_result["final_verdict"]["recommendation"] = (
                f"표절 의심: 웹에서 {len(web_result['sources'])}개의 유사 출처 발견"
            )
        else:
            final_result["final_verdict"]["recommendation"] = (
                "표절 의심: AI가 학습 데이터에서 유사 콘텐츠 발견 (웹 검색 미확인)"
            )
    else:
        final_result["final_verdict"]["recommendation"] = "독창적인 콘텐츠로 판단됩니다."
    
    return final_result
