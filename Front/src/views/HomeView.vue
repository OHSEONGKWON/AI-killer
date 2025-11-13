<template>
    <link
          rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"
          integrity="sha512-..." crossorigin="anonymous"
    />
  <div v-if="isAnalyzing" class="loading-overlay">
        <div class="spinner"></div>
        <p>분석 중입니다. 잠시만 기다려주세요...</p>
     </div>

    <main>
    <section class="detection-area">
        <div class="container">
            <h2>텍스트 분석하기</h2>
      <div class="input-section">
      <div class="form-group">
            <h4>문서 유형</h4>
            <select v-model="selectedDocType" class="type-select" :disabled="isAnalyzing">
              <option value="" disabled>유형을 선택하세요...</option>
              <option value="paper">논문</option>
              <option value="article">기사</option>
              <option value="news">신문</option>
                 <option value="news">SNS</option>
            </select>
          </div>
           <input type="text" v-model="subjectText" placeholder="주제를 입력해주세요.">
        <textarea v-model="inputText" placeholder="여기에 텍스트를 입력해주세요."></textarea>
        <div class="input-controls">
          <span id="charCount">{{ inputText.length }} 글자</span>
          <div class="action-buttons">
            <button class="icon-btn" @click="clearText"><i class="fas fa-eraser"></i></button>
          </div>
        </div>
        <button @click="analyzeText" class="btn-analyze" :disabled="isAnalyzing">
          {{ isAnalyzing ? '분석 중...' : '분석 시작' }}
        </button>
      </div>
    </div>

      <div class="result-section" v-if="showResult">
        <h3>분석 결과</h3>
        <div class="result-summary">
            <template v-if="result.isAIDetected">
                <i class="fas fa-robot result-icon ai-detected"></i>
                <span class="result-text ai-detected">AI 생성 가능성: {{ result.likelihood }}%</span>
            </template>
            <template v-else>
                <i class="fas fa-feather-alt result-icon human-detected"></i>
                <span class="result-text human-detected">AI 생성 가능성: {{ result.likelihood }}%</span>
            </template>
        </div>
    <div class="detailed-analysis">
          <h4>상세 분석</h4>
          <p v-html="result.detailedText"></p>
    </div>
        <div class="result-actions">
          <button class="btn-secondary"><i class="fas fa-copy"></i> 결과 복사</button>
          <button class="btn-secondary"><i class="fas fa-download"></i> 결과 다운로드</button>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref, reactive } from 'vue';
import axios from 'axios';

const inputText = ref('');
const isAnalyzing = ref(false);
const showResult = ref(false);
const subjectText = ref('');
const selectedDocType = ref('');

const result = reactive({
  isAIDetected: false,
  likelihood: 0,
  detailedText: '',
});

const analyzeText = async () => {
  if (inputText.value.trim() === '' || !selectedDocType.value) {
    alert('분석할 텍스트와 문서 유형을 입력해주세요.');
    return;
  }

  isAnalyzing.value = true;
  showResult.value = false;

  try {
    const payload = {
      title: subjectText.value || '제목 없음',
      content: inputText.value,
      text_type: selectedDocType.value
    };
    
    const response = await axios.post('/api/v1/analyze', payload);
    const data = response.data;

    // AI 확률을 백분율로 변환
    const likelihoodValue = Math.round(data.ai_probability * 100);
    const isDetected = likelihoodValue > 60;

    result.isAIDetected = isDetected;
    result.likelihood = likelihoodValue;

    if (isDetected) {
      result.detailedText = `<span class="highlight-ai">높은 AI 생성 가능성이 감지되었습니다.</span><br><br>
        <strong>세부 점수:</strong><br>
        - KoBERT: ${Math.round(data.analysis_details.kobert_score * 100)}%<br>
        - SBERT 유사도: ${Math.round(data.analysis_details.similarity_score * 100)}%<br>
        - Perplexity: ${Math.round(data.analysis_details.perplexity_score * 100)}%<br>
        - Burstiness: ${Math.round(data.analysis_details.burstiness_score * 100)}%`;
    } else {
      result.detailedText = `<span class="highlight-human">AI보다는 인간이 작성했을 가능성이 높습니다.</span><br><br>
        <strong>세부 점수:</strong><br>
        - KoBERT: ${Math.round(data.analysis_details.kobert_score * 100)}%<br>
        - SBERT 유사도: ${Math.round(data.analysis_details.similarity_score * 100)}%<br>
        - Perplexity: ${Math.round(data.analysis_details.perplexity_score * 100)}%<br>
        - Burstiness: ${Math.round(data.analysis_details.burstiness_score * 100)}%`;
    }

    showResult.value = true;
  } catch (error) {
    console.error('API 호출 중 오류 발생:', error);
    let errorMessage = '텍스트 분석에 실패했습니다.';
    
    if (error.response) {
      errorMessage += ` (오류: ${error.response.data.detail || error.response.statusText})`;
    } else {
      errorMessage += ' 백엔드 서버에 연결할 수 없습니다.';
    }
    
    alert(errorMessage);
  } finally {
    isAnalyzing.value = false;
  }
};

// 지우기 기능을 함수로 분리합니다.
const clearText = () => {
  inputText.value = '';
  showResult.value = false;
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

/* 로딩 오버레이 스타일 */
.loading-overlay {
    position: fixed; /* 화면 전체에 고정 */
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(255, 255, 255, 0.8); /* 반투명 흰색 배경 */
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    z-index: 9999; /* 다른 요소들 위에 보이도록 설정 */
}

.loading-overlay p {
    margin-top: 20px;
    font-size: 1.2em;
    font-weight: 500;
    color: #333;
}

/* 스피너 애니메이션 */
.spinner {
    width: 60px;
    height: 60px;
    border: 8px solid #f3f3f3; /* 연한 회색 테두리 */
    border-top: 8px solid #00C4CC; /* 메인 컬러 테두리 */
    border-radius: 50%;
    animation: spin 1.5s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* ... 나머지 스타일 코드는 동일 ... */
.input-section input[type="text"] {
    width: 100%;
    padding: 15px;
    border: 2px solid #E0E0E0;
    border-radius: 8px;
    font-size: 1.1em;
    margin-bottom: 20px; /* 아래 textarea와 간격 조절 */
    outline: none;
    transition: border-color 0.3s ease;
    box-sizing: border-box;
}

.input-section input[type="text"]:focus {
    border-color: #00C4CC;
}

.form-group {
  margin-bottom: 25px; 
}
.form-group h4 {
  font-size: 1.2em;
  color: #333;
  margin-bottom: 10px;
  font-weight: 600;
}
.type-select {
  width: 100%;
  padding: 12px 15px;
  font-size: 1.1em;
  border: 2px solid #E0E0E0;
  border-radius: 8px;
  background-color: #FFFFFF;
  color: #333;
  cursor: pointer;
}
body {
    font-family: 'Noto Sans KR', 'Pretendard', 'Inter', sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #F8F9FA;
}

.container {
    width: 90%;
    max-width: 1200px;
    margin: 0 auto;
}

/* 헤더 */
header {
    background-color: ffffff;
    border-bottom: 1px solid #E0E0E0;
    padding: 20px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

header .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    font-size: 2em;
    color: #00C4CC;
    font-weight: 900;
    text-align: left;
}

nav ul {
    list-style: none;
    display: flex;
    gap: 25px;
}

nav a {
    text-decoration: none;
    color: #6C757D;
    font-weight: 500;
    transition: color 0.2s ease;
}

nav a:hover {
    color: #0056b3;
}

/* 버튼 스타일 */
.btn-primary {
    background-color: #00C4CC;
    color: #FFFFFF;
    padding: 10px 18px;
    border-radius: 8px;
    font-weight: bold;
    text-decoration: none;
    transition: background-color 0.2s ease;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow : 0 4px 8px rgba(0,0,0,1);
    background-color: #009999;
}

.btn-analyze {
    display: block;
    margin-top:40px;
    width: 100%;
    padding: 15px 20px;
    background-color: #00C4CC; /* 청록색 계열 */
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    font-size: 1.2em;
    font-weight: bold;
    cursor: pointer;
    margin-top: 20px;
    transition: background-color 0.3s ease, transform 0.2s ease;
}

.btn-analyze:hover {
    background-color: #009999;
    transform: translateY(-2px);
}

.btn-analyze.loading {
    background-color: #009999;
    cursor: not-allowed;
    position: relative;
}

.btn-analyze.loading::after {
    content: '';
    display: inline-block;
    width: 15px;
    height: 15px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-left: 10px;
    vertical-align: middle;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

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

.btn-secondary:hover {
    background-color: #5a6268;
}

.btn-secondary i {
    margin-right: 5px;
}

/* 메인 감지 영역 */
.detection-area {
    background-color: #FFFFFF;
    padding: 40px;
    border-radius: 10px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.08);

}

.detection-area h2 {
    font-size: 2em;
    color: #333;
    text-align: center;
    margin-bottom: 30px;
}

.input-section {
    margin-bottom: 30px;
}

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

textarea:focus {
    border-color: #00C4CC;
}

.input-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
    color: #6C757D;
    font-size: 0.9em;
}
input[type="text"], textarea
{
  transition: all 0.2s ease-in-out;
}

.action-buttons {
    display: flex;
    gap: 10px;
}

.icon-btn {
    background: none;
    border: none;
    font-size: 1.2em;
    color: #6C757D;
    cursor: pointer;
    transition: color 0.3s ease;
}

.icon-btn:hover {
    color: #007BFF;
}

/* 결과 표시 영역 */
.result-section {
    background-color: #f0f8ff; /* 연한 파란색 배경 */
    border: 1px solid #cceeff;
    padding: 30px;
    border-radius: 10px;
    margin-top: 30px;
    text-align: center;
}

.result-section h3 {
    font-size: 1.8em;
    color: #007BFF;
    margin-bottom: 20px;
}

.result-summary {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-bottom: 25px;
}

.result-icon {
    font-size: 3.5em;
    margin-bottom: 15px;
}

.result-text {
    font-size: 1.8em;
    font-weight: bold;
}

.ai-detected {
    color: #DC3545; /* 빨간색 */
}

.human-detected {
    color: #28A745; /* 초록색 */
}

.detailed-analysis {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    padding: 20px;
    border-radius: 8px;
    text-align: left;
    margin-bottom: 25px;
}

.detailed-analysis h4 {
    font-size: 1.2em;
    color: #333;
    margin-bottom: 10px;
}

.highlight-ai {
    background-color: rgba(220, 53, 69, 0.2); /* 빨간색 투명 */
    padding: 2px 5px;
    border-radius: 3px;
    font-weight: bold;
}

.highlight-human {
    background-color: rgba(40, 167, 69, 0.2); /* 초록색 투명 */
    padding: 2px 5px;
    border-radius: 3px;
    font-weight: bold;
}

.result-actions {
    margin-top: 20px;
}

.hidden {
    display: none;
}
</style>
