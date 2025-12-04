<template>
  <div v-if="isAnalyzing" class="loading-overlay">
    <div class="spinner"></div>
    <p>문법을 검사 중입니다. 잠시만 기다려주세요...</p>
  </div>

  <main>
    <section class="detection-area">
      <div class="container">
        <h2>문법 검사기</h2>
        <div class="input-section">
          <textarea v-model="inputText" placeholder="여기에 문법 검사를 받을 텍스트를 입력해주세요."></textarea>
          <div class="input-controls">
            <span id="charCount">{{ inputText.length }} 글자</span>
            <div class="action-buttons">
              <button class="icon-btn" @click="clearText"><i class="fas fa-eraser"></i></button>
            </div>
          </div>
          <button @click="analyzeText" class="btn-analyze" :disabled="isAnalyzing">
            {{ isAnalyzing ? '검사 중...' : '검사 시작' }}
          </button>
        </div>
      </div>

      <div class="result-section" v-if="showResult">
        <h3>검사 결과</h3>
        
        <!-- 점수 박스 -->
        <div class="score-container">
          <div class="score-box">
            <h4>문법 점수</h4>
            <div class="score-value" :class="getScoreClass(result.score.grammar)">
              {{ result.score.grammar }}점
            </div>
          </div>
          <div class="score-box">
            <h4>자연스러움</h4>
            <div class="score-value" :class="getScoreClass(result.score.naturalness)">
              {{ result.score.naturalness }}점
            </div>
          </div>
        </div>

        <!-- 원문/교정/윤문 비교 -->
        <div class="text-comparison">
          <div class="text-box">
            <h4>📝 원문</h4>
            <p class="original-text">{{ result.originalText }}</p>
          </div>
          <div class="text-box">
            <h4>✅ 교정 (맞춤법/오타)</h4>
            <p class="corrected-text">{{ result.correctedText }}</p>
          </div>
          <div class="text-box highlight">
            <h4>✨ 윤문 (최종)</h4>
            <p class="refined-text">{{ result.refinedText }}</p>
          </div>
        </div>

        <!-- 수정 내역 상세 -->
        <div class="diff-section" v-if="result.diffExplanation.length > 0">
          <h4>🔧 수정 내역 상세</h4>
          <div class="diff-list">
            <div v-for="(diff, index) in result.diffExplanation" :key="index" class="diff-item">
              <div class="diff-change">
                <span class="original">'{{ diff.original }}'</span>
                <span class="arrow">→</span>
                <span class="changed">'{{ diff.changed }}'</span>
              </div>
              <div class="diff-reason">└ {{ diff.reason }}</div>
            </div>
          </div>
        </div>
        <div v-else class="no-errors">
          <p>🎉 수정할 내용이 없습니다. 완벽한 문장입니다!</p>
        </div>

        <!-- 뉘앙스 분석 -->
        <div class="nuance-section">
          <h4>💡 뉘앙스 분석</h4>
          <p>{{ result.nuanceFeedback }}</p>
        </div>

        <!-- 어휘 추천 -->
        <div class="vocab-section" v-if="result.vocabularySuggestions.length > 0">
          <h4>📚 어휘 추천</h4>
          <div class="vocab-list">
            <div v-for="(vocab, index) in result.vocabularySuggestions" :key="index" class="vocab-item">
              <span class="vocab-word">{{ vocab.word }}</span>
              <span class="arrow">→</span>
              <span class="vocab-suggestion">{{ vocab.suggestion }}</span>
              <span class="vocab-reason">({{ vocab.reason }})</span>
            </div>
          </div>
        </div>

        <div class="result-actions">
          <button class="btn-secondary" @click="copyToClipboard(result.refinedText)">
            <i class="fas fa-copy"></i> 윤문 결과 복사
          </button>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { grammarAPI } from '../services/api';
import auth from '../store/auth';

const router = useRouter();
const inputText = ref('');
const isAnalyzing = ref(false);
const showResult = ref(false);

const result = reactive({
  originalText: '',
  correctedText: '',
  refinedText: '',
  diffExplanation: [],
  nuanceFeedback: '',
  vocabularySuggestions: [],
  score: {
    grammar: 0,
    naturalness: 0
  }
});

const getScoreClass = (score) => {
  if (score >= 90) return 'excellent';
  if (score >= 70) return 'good';
  if (score >= 50) return 'fair';
  return 'poor';
};

const analyzeText = async () => {
  // 로그인 확인
  if (!auth.state.isLoggedIn) {
    alert('문법 검사는 로그인 후 이용 가능합니다.');
    router.push('/login');
    return;
  }

  if (inputText.value.trim() === '') {
    alert('검사할 텍스트를 입력해주세요.');
    return;
  }

  isAnalyzing.value = true;
  showResult.value = false;

  let analysisSuccess = false;

  try {
    const payload = { content: inputText.value };
    const response = await grammarAPI.check(payload);

    const data = response.data;
    result.originalText = data.original_text || inputText.value;
    result.correctedText = data.corrected_text || '';
    result.refinedText = data.refined_text || '';
    result.diffExplanation = data.diff_explanation || [];
    result.nuanceFeedback = data.nuance_feedback || '';
    result.vocabularySuggestions = data.vocabulary_suggestions || [];
    result.score = data.score || { grammar: 0, naturalness: 0 };

    analysisSuccess = true;

  } catch (error) {
    console.error('API 호출 중 오류 발생:', error);
    
    // 401 Unauthorized 에러 처리
    if (error.response?.status === 401) {
      alert('로그인이 필요합니다.\n로그인 페이지로 이동합니다.');
      router.push('/login');
      return;
    }
    
    let errorMessage = '문법 검사에 실패했습니다.';
    if (error.response) {
      errorMessage += ` (오류: ${error.response.status})`;
      if (error.response.data?.detail) {
        errorMessage += `\n${error.response.data.detail}`;
      }
    }
    alert(errorMessage);
    analysisSuccess = false;
  } finally {
    isAnalyzing.value = false;
    showResult.value = analysisSuccess;
  }
};

const clearText = () => {
  inputText.value = '';
  showResult.value = false;
};

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text).then(() => {
    alert('클립보드에 복사되었습니다!');
  }).catch(err => {
    console.error('복사 실패:', err);
    alert('복사에 실패했습니다.');
  });
};
</script>

<style scoped>
.score-container {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.score-box {
  flex: 1;
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.score-box h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #666;
}

.score-value {
  font-size: 36px;
  font-weight: bold;
  margin: 10px 0;
}

.score-value.excellent {
  color: #28a745;
}

.score-value.good {
  color: #5cb85c;
}

.score-value.fair {
  color: #ffc107;
}

.score-value.poor {
  color: #dc3545;
}

.text-comparison {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 30px;
}

.text-box {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #ddd;
}

.text-box.highlight {
  background: #e7f5ff;
  border-left-color: #007bff;
}

.text-box h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
}

.text-box p {
  margin: 0;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.diff-section,
.nuance-section,
.vocab-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.diff-section h4,
.nuance-section h4,
.vocab-section h4 {
  margin: 0 0 15px 0;
  font-size: 18px;
}

.diff-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.diff-item {
  padding: 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #dee2e6;
}

.diff-change {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  font-weight: 600;
}

.diff-change .original {
  color: #dc3545;
}

.diff-change .changed {
  color: #28a745;
}

.diff-change .arrow {
  color: #666;
}

.diff-reason {
  color: #666;
  font-size: 14px;
  padding-left: 10px;
}

.no-errors {
  text-align: center;
  padding: 40px;
  background: #d4edda;
  border-radius: 8px;
  margin-bottom: 20px;
}

.no-errors p {
  margin: 0;
  color: #155724;
  font-size: 18px;
  font-weight: 500;
}

.nuance-section p {
  margin: 0;
  line-height: 1.6;
  color: #495057;
}

.vocab-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.vocab-item {
  padding: 10px;
  background: white;
  border-radius: 6px;
  border: 1px solid #dee2e6;
  display: flex;
  align-items: center;
  gap: 8px;
}

.vocab-word {
  font-weight: 600;
  color: #495057;
}

.vocab-suggestion {
  font-weight: 600;
  color: #007bff;
}

.vocab-reason {
  color: #666;
  font-size: 14px;
}

.vocab-item .arrow {
  color: #999;
}
</style>
