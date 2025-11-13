<template>
  <link
    rel="stylesheet"
    href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"
  />

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
import axios from 'axios'; // axios 임포트

// 백엔드 분석 엔드포인트
const API_ENDPOINT = '/api/v1/analyze';
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
    const response = await axios.post(API_ENDPOINT, payload);

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
/* 여기에 문법 검사기 컴포넌트의 <style> 내용을 
  그대로 복사/붙여넣기 하세요. 
*/

/* --- 표절 검사기 전용으로 추가된 스타일 --- */
.result-summary {
  display: flex;
  gap: 20px;
  margin-bottom: 25px; /* 상세 분석과 간격 둠 */
}
.result-box {
  flex: 1;
  background-color: #FFFFFF; /* .detailed-analysis와 동일한 배경 */
  border: 1px solid #E0E0E0;  /* .detailed-analysis와 동일한 테두리 */
  padding: 20px;
  border-radius: 8px; /* .detailed-analysis와 동일한 둥근 모서리 */
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

/* .detailed-analysis 스타일은 문법 검사기 CSS에 
  이미 정의되어 있으므로 재사용합니다.
*/
.detailed-analysis p.corrected-text {
  /* 문법 검사기의 .corrected-text 스타일이 그대로 적용됩니다. */
  font-size: 1.1em;
  line-height: 1.7;
  white-space: pre-wrap;
}


/* --- 아래는 문법 검사기에서 가져온 스타일 (반드시 포함) --- */
.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(255, 255, 255, 0.8);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 9999;
}
.loading-overlay p { margin-top: 20px; font-size: 1.2em; font-weight: 500; color: #333; }
.spinner {
    width: 60px;
    height: 60px;
    border: 8px solid #f3f3f3;
    border-top: 8px solid #00C4CC;
    border-radius: 50%;
    animation: spin 1.5s linear infinite;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
.container { width: 90%; max-width: 1200px; margin: 0 auto; }
.btn-analyze {
    display: block;
    width: 100%;
    padding: 15px 20px;
    background-color: #00C4CC;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    font-size: 1.2em;
    font-weight: bold;
    cursor: pointer;
    margin-top: 20px;
    transition: background-color 0.3s ease, transform 0.2s ease;
}
.btn-analyze:hover { background-color: #009999; transform: translateY(-2px); }
.btn-analyze:disabled { background-color: #ccc; cursor: not-allowed; }
.btn-secondary {
    background-color: #6C757D;
    color: #FFFFFF;
    padding: 10px 15px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 0.9em;
    margin-right: 10px;
    transition: background-color 0.3s ease;
}
.btn-secondary:hover { background-color: #5a6268; }
.btn-secondary i { margin-right: 5px; }
.detection-area { background-color: #FFFFFF; padding: 40px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.08); }
.detection-area h2 { font-size: 2em; color: #333; text-align: center; margin-bottom: 30px; }
.input-section { margin-bottom: 30px; }
textarea {
    width: 100%;
    min-height: 250px;
    padding: 15px;
    border: 2px solid #E0E0E0;
    border-radius: 8px;
    font-size: 1.1em;
    resize: vertical;
    outline: none;
    transition: border-color 0.3s ease;
    box-sizing: border-box;
}
textarea:focus { border-color: #00C4CC; }
.input-controls { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; color: #6C757D; font-size: 0.9em; }
.action-buttons { display: flex; gap: 10px; }
.icon-btn { background: none; border: none; font-size: 1.2em; color: #6C757D; cursor: pointer; transition: color 0.3s ease; }
.icon-btn:hover { color: #007BFF; }
.result-section { background-color: #f8f9fa; border: 1px solid #e0e0e0; padding: 30px; border-radius: 10px; margin-top: 30px; }
.result-section h3 { font-size: 1.8em; color: #333; margin-bottom: 20px; text-align: center; }
.detailed-analysis { background-color: #FFFFFF; border: 1px solid #E0E0E0; padding: 20px; border-radius: 8px; text-align: left; margin-bottom: 25px; }
.detailed-analysis h4 { font-size: 1.2em; color: #333; margin-bottom: 10px; }
.result-actions { margin-top: 20px; text-align: center; }

/* 문법 검사기 CSS의 .corrected-text 스타일 */
.corrected-text {
  font-size: 1.1em;
  line-height: 1.7;
  white-space: pre-wrap; /* 줄바꿈 및 공백 유지 */
  background-color: #fdfdfd;
  padding: 15px;
  border-radius: 5px;
  border: 1px solid #eee;
}
</style>