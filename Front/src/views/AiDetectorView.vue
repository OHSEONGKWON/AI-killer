<template>

  <div v-if="isAnalyzing" class="loading-overlay">
    <div class="spinner"></div>
    <p>AI 표절 검사를 진행 중입니다. 잠시만 기다려주세요...</p>
  </div>

  <main>
    <section class="detection-area">
      <div class="container">
        <h2>AI 텍스트 분석</h2>
        
        <div class="input-section">
          <input 
            v-model="title"
            type="text"
            placeholder="제목을 입력하세요 (예: 논문/에세이 제목)"
            :disabled="isAnalyzing"
          />
          <textarea 
            v-model="inputText" 
            placeholder="검사할 텍스트를 여기에 붙여넣으세요... (최소 50자 이상)"
            :disabled="isAnalyzing"
          ></textarea>
          <div class="input-controls">
            <span id="charCount">{{ inputText.length }} 글자</span>
            <div class="action-buttons">
              <button class="icon-btn" @click="clearText"><i class="fas fa-eraser"></i></button>
            </div>
          </div>
          <button @click="analyzeText" class="btn-analyze" :disabled="isAnalyzing || inputText.length < 10">
            {{ isAnalyzing ? '검사 중...' : '검사 시작' }}
          </button>
        </div>
      </div>

      <div class="result-section" v-if="result">
        <h3>검사 결과</h3>
        
        <div class="result-summary">
          <div class="result-box ai-score">
            <strong>AI 생성 확률</strong>
            <span>{{ result.aiProbability }}%</span>
          </div>
          <div class="result-box plagiarism-score">
            <strong>KoBERT 점수</strong>
            <span>{{ result.kobertScore }}%</span>
          </div>
        </div>
        
        <div class="detailed-analysis">
          <h4>상세 분석</h4>
          <p class="corrected-text">AI 생성 확률과 KoBERT 점수는 백엔드 분석 결과를 기반으로 계산됩니다.</p>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref } from 'vue';
import { analysisAPI } from '../services/api';

// 백엔드 분석 엔드포인트
const title = ref('');
const inputText = ref('');
const isAnalyzing = ref(false); // isLoading -> isAnalyzing로 이름 변경
const result = ref(null); // showResult 대신 result 객체로 v-if 처리

// 분석 시작 함수
const analyzeText = async () => {
  if (inputText.value.trim().length < 10) {
    alert('최소 10자 이상 입력해주세요.');
    return;
  }

  isAnalyzing.value = true;
  result.value = null; // 이전 결과 초기화

  try {
    const payload = { title: title.value || 'Untitled', content: inputText.value };
    const response = await analysisAPI.analyze(payload);

    // FastAPI 응답: { ai_probability: float, analysis_details: { kobert_score, similarity_score } }
    const data = response.data;
    result.value = {
      aiProbability: Math.round((data.ai_probability || 0) * 100),
      kobertScore: Math.round(((data.analysis_details?.kobert_score) || 0) * 100),
    };

  } catch (error) {
    console.error('API 호출 중 오류 발생:', error);
    alert('검사에 실패했습니다. 서버 로그를 확인해주세요.');
  } finally {
    isAnalyzing.value = false;
  }
};

// 입력 초기화
const clearText = () => {
  inputText.value = '';
  result.value = null;
};
</script>

<style scoped>
/* 뷰 전용 스타일 (공통 스타일은 common.css 사용) */
.result-summary {
  display: flex;
  gap: 20px;
  margin-bottom: 25px; /* 상세 분석과 간격 둠 */
}
.result-box {
  flex: 1;
  background-color: #FFFFFF;
  border: 1px solid #E0E0E0;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05); /* 약간의 그림자 */
}
.result-box strong {
  display: block;
  font-size: 1.1em;
  color: #333;
  margin-bottom: 10px;
}
.result-box span {
  font-size: 2.5em; /* 점수 텍스트 강조 */
  font-weight: bold;
}
/* 점수별로 색상 구분 */
.result-box.ai-score span {
  color: #FF6B6B; /* AI 점수는 붉은 계열 */
}
.result-box.plagiarism-score span {
  color: #FFA500; /* 표절 점수는 주황 계열 */
}
/* corrected-text 등 공통 클래스는 common.css에서 로드됨 */
</style>