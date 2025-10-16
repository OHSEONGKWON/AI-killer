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
     <header>
        <div class="container">
             <div class="logo">Tech up</div>
            <nav>
             <ul>
                 <li><a href="#" class="btn-primary">회원가입</a></li>
             </ul>
         </nav>
    </div>
</header>

    <main>
    <section class="detection-area">
        <div class="container">
            <h2>텍스트 분석하기</h2>
      <div class="input-section">
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

const PROXY_ENDPOINT = 'http://localhost:3000/api/analyze';

const inputText = ref('');
const isAnalyzing = ref(false);
const showResult = ref(false);
const subjectText = ref('');

const result = reactive({
  isAIDetected: false,
  likelihood: 0,
  detailedText: '',
});

const analyzeText = async () => {
  if (inputText.value.trim() === '') {
    alert('분석할 텍스트를 입력해주세요.');
    return;
  }

  isAnalyzing.value = true;
  showResult.value = false; // 이전 결과 숨기기

  let analysisSuccess = false; // 분석 성공 여부를 추적할 변수

  try {
    const payload = { text: inputText.value, subject: subjectText.value, promptType: 'json_reasoning' };
    const response = await axios.post(PROXY_ENDPOINT, payload);

    // 3. API 응답 데이터 처리
    const responseText = response.data.candidates[0].content.parts[0].text.trim();
    let likelihoodValue = parseInt(responseText);

    // 숫자가 아닌 응답이 오면 안전하게 50으로 처리
    if (isNaN(likelihoodValue) || likelihoodValue < 0 || likelihoodValue > 100) {
      likelihoodValue = 50;
    }

    const isDetected = likelihoodValue > 60; // 60%를 기준으로 AI 여부를 결정

    // 4. Vue 반응형 상태 업데이트
    result.isAIDetected = isDetected;
    result.likelihood = likelihoodValue;

    // 5. 상세 텍스트 업데이트 로직 추가
    if (isDetected) {
      result.detailedText = '<span class="highlight-ai">높은 AI 생성 가능성이 감지되었습니다.</span> 이 텍스트는 반복적이거나 예측 가능한 패턴을 가질 수 있습니다.';
    } else {
      result.detailedText = '<span class="highlight-human">AI보다는 인간이 작성했을 가능성이 높습니다.</span> 다양하고 창의적인 표현이 돋보입니다.';
    }

    analysisSuccess = true; // 성공!
  } catch (error) {
    // 5. 오류 처리
    console.error('API 호출 중 오류 발생:', error);

    // 오류 유형별 메시지
    let errorMessage = '텍스트 분석에 실패했습니다. (API 오류)';
    if (error.response && error.response.status === 403) {
      errorMessage = 'API 키가 유효하지 않거나 사용 권한이 없습니다. (403 Forbidden)';
    } else if (error.response && error.response.status === 429) {
      errorMessage = '사용 한도를 초과했습니다. 잠시 후 다시 시도해주세요. (429 Rate Limit)';
    }

    alert(errorMessage);

    analysisSuccess = false; // 실패
  } finally {
    // 6. 분석 상태 해제 및 결과 표시 결정
    isAnalyzing.value = false;
    // 오직 성공했을 때만 결과 섹션을 표시
    showResult.value = analysisSuccess;
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
}

.input-section input[type="text"]:focus {
    border-color: #00C4CC;
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
