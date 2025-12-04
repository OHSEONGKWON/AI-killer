"""
유사도 검사 API 엣지 케이스 테스트
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import asyncio

from Web.gemini_similarity import generate_gemini_texts
from Web.exceptions import AIServiceError


@pytest.mark.asyncio
class TestGeminiTextGeneration:
    """Gemini 텍스트 생성 테스트 (에러 처리 강화)"""
    
    @patch('Web.gemini_similarity.gemini_model')
    async def test_generate_texts_success(self, mock_gemini):
        """정상적인 텍스트 생성"""
        mock_response = MagicMock()
        mock_response.text = "이것은 생성된 테스트 문장입니다."
        mock_gemini.generate_content.return_value = mock_response
        
        texts = await generate_gemini_texts("인공지능", num_sentences=5)
        
        assert len(texts) > 0
        assert all(isinstance(t, str) for t in texts)
    
    @patch('Web.gemini_similarity.gemini_model')
    async def test_handle_empty_response(self, mock_gemini):
        """빈 응답 처리"""
        mock_response = MagicMock()
        mock_response.text = ""
        mock_response.parts = []
        mock_gemini.generate_content.return_value = mock_response
        
        # 30% 이상 실패하면 에러 발생
        with pytest.raises(AIServiceError):
            await generate_gemini_texts("테스트", num_sentences=3)
    
    @patch('Web.gemini_similarity.gemini_model')
    async def test_failure_threshold_exceeded(self, mock_gemini):
        """30% 이상 실패 시 에러 발생"""
        # 첫 번째 호출은 성공, 나머지는 실패
        call_count = [0]
        
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                response = MagicMock()
                response.text = "성공"
                response.parts = []
                return response
            raise Exception("API 오류")
        
        mock_gemini.generate_content.side_effect = side_effect
        
        # 5개 중 4개가 실패하면 (80% 실패 > 30%) 에러 발생
        with pytest.raises(AIServiceError) as exc_info:
            await generate_gemini_texts("테스트", num_sentences=5)
        
        assert "실패가 과다합니다" in str(exc_info.value.message)
    
    @patch('Web.gemini_similarity.gemini_model')
    async def test_minimum_success_rate(self, mock_gemini):
        """최소 50% 이상 생성되지 않으면 에러"""
        mock_response = MagicMock()
        mock_response.text = "생성"
        mock_gemini.generate_content.side_effect = [
            mock_response,  # 성공
            Exception("실패"),  # 실패
            Exception("실패"),  # 실패
        ]
        
        with pytest.raises(AIServiceError) as exc_info:
            await generate_gemini_texts("테스트", num_sentences=3)
        
        assert "충분한 AI 텍스트를 생성하지 못했습니다" in str(exc_info.value.message)


class TestInputValidation:
    """입력 값 유효성 검사"""
    
    def test_empty_text_rejection(self):
        """빈 텍스트는 거부되어야 함"""
        # API 레벨에서 검증
        from Web.models import AnalysisRequest
        
        with pytest.raises(Exception):  # Pydantic 검증 오류
            AnalysisRequest(title="", content="", text_type="paper")
    
    def test_minimum_text_length(self):
        """최소 텍스트 길이 검증"""
        from Web.models import AnalysisRequest
        
        # 10자 미만은 거부
        with pytest.raises(Exception):
            AnalysisRequest(
                title="test",
                content="short",  # 5자
                text_type="paper"
            )
    
    def test_maximum_text_length(self):
        """최대 텍스트 길이 검증"""
        from Web.models import AnalysisRequest
        
        # 10000자 초과는 거부
        long_text = "a" * 10001
        with pytest.raises(Exception):
            AnalysisRequest(
                title="test",
                content=long_text,
                text_type="paper"
            )
    
    def test_valid_text_accepted(self):
        """유효한 텍스트는 허용"""
        from Web.models import AnalysisRequest
        
        request = AnalysisRequest(
            title="좋은 제목",
            content="이것은 정확히 10자 이상의 유효한 텍스트입니다.",
            text_type="paper"
        )
        
        assert request.title == "좋은 제목"
        assert len(request.content) >= 10


class TestSpecialCharacters:
    """특수 문자 처리"""
    
    def test_unicode_text_handling(self):
        """유니코드 텍스트 처리"""
        from Web.models import AnalysisRequest
        
        # 한글, 이모지, 다국어 지원
        request = AnalysisRequest(
            title="테스트 🎯",
            content="한글 텍스트 테스트입니다. English mixed. 日本語も可能です.",
            text_type="paper"
        )
        
        assert "한글" in request.content
        assert "🎯" in request.title
    
    def test_sql_injection_prevention(self):
        """SQL 주입 시도 처리"""
        from Web.models import AnalysisRequest
        
        # SQL 주입 문자열도 단순 텍스트로 처리되어야 함
        request = AnalysisRequest(
            title="'; DROP TABLE users; --",
            content="SQL 인젝션 테스트 입니다. This is over 10 chars.",
            text_type="paper"
        )
        
        # 텍스트로 안전하게 저장됨
        assert request.title == "'; DROP TABLE users; --"
