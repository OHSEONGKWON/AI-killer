<template>
   <main class="container">
    <div class="logo">
       Tech up
    </div>
    <section class="detection-area">       
      <h2>텍스트 분석하기</h2>
      <div class="input-section">
        <textarea v-model="inputText" placeholder="여기에 텍스트를 입력해주세요."></textarea>
        <div class="input-controls">
          <span id="charCount">{{ inputText.length }} 글자</span>
          <div class="action-buttons">
            <button class="icon-btn"><i class="fas fa-file-upload"></i></button>
            <button class="icon-btn" @click="clearText"><i class="fas fa-eraser"></i></button>
          </div>
        </div>
        <button @click="analyzeText" class="btn-analyze" :disabled="isAnalyzing">
          {{ isAnalyzing ? '분석 중...' : '분석 시작' }}
        </button>
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

// ref를 사용해 반응형 데이터를 만듭니다.
const inputText = ref('');
const isAnalyzing = ref(false);
const showResult = ref(false);

// reactive를 사용해 여러 데이터를 가진 객체를 반응형으로 만듭니다.
const result = reactive({
  isAIDetected: false,
  likelihood: 0,
  detailedText: ''
});

// 분석 로직을 함수(메서드)로 분리합니다.
const analyzeText = () => {
  if (inputText.value.trim() === '') {
    alert('분석할 텍스트를 입력해주세요.');
    return;
  }
  
  isAnalyzing.value = true;
  showResult.value = false; // 이전 결과 숨기기

  setTimeout(() => {
    const isDetected = Math.random() > 0.5;
    const likelihoodValue = Math.floor(Math.random() * 100);

    // 데이터의 상태를 변경합니다. DOM을 직접 건드리지 않습니다.
    result.isAIDetected = isDetected;
    result.likelihood = likelihoodValue;

    if (isDetected) {
      result.detailedText = `<span class="highlight-ai">이 텍스트의 일부에서 AI가 생성했을 가능성이 높은 패턴이 감지되었습니다.</span> 자연스러운 흐름과 반복적인 표현을 주의 깊게 살펴보세요.`;
    } else {
      result.detailedText = `<span class="highlight-human">이 텍스트는 AI보다는 인간이 작성했을 가능성이 높습니다.</span> 다양하고 창의적인 표현이 돋보입니다.`;
    }

    isAnalyzing.value = false;
    showResult.value = true; // 결과 표시
  }, 2000);
};

// 지우기 기능을 함수로 분리합니다.
const clearText = () => {
  inputText.value = '';
  showResult.value = false;
};
</script>

<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
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
    padding: 20px 0;
}

/* 헤더 */
header {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E0E0E0;
    padding: 15px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

header .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    font-size: 1.8em;
    color: #007BFF;
    font-weight: bold;
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
    transition: color 0.3s ease;
}

nav a:hover {
    color: #0056b3;
}

/* 버튼 스타일 */
.btn-primary {
    background-color: #007BFF;
    color: #FFFFFF;
    padding: 8px 15px;
    border-radius: 5px;
    text-decoration: none;
    transition: background-color 0.3s ease;
}

.btn-primary:hover {
    background-color: #0056b3;
}

.btn-analyze {
    display: block;
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
    margin-top: 40px;
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

/* 반응형 (모바일) */
@media (max-width: 768px) {
    header .container {
        flex-direction: column;
        gap: 15px;
    }

    nav ul {
        flex-direction: column;
        gap: 10px;
        text-align: center;
    }

    .logo {
        margin-bottom: 10px;
    }

    .detection-area {
        padding: 20px;
        margin-top: 20px;
    }

    .detection-area h2 {
        font-size: 1.5em;
    }

    textarea {
        min-height: 180px;
    }

    .result-icon {
        font-size: 2.5em;
    }

    .result-text {
        font-size: 1.4em;
    }

    .result-summary, .detailed-analysis {
        padding: 15px;
    }

    .result-actions {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    .btn-secondary {
        margin-right: 0;
        width: 100%;
    }
}
</style>
