<template>
  <link
    rel="stylesheet"
    href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"
  />
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
        
        <div class="detailed-analysis">
          <h4>수정된 텍스트</h4>
          <p class="corrected-text">{{ result.correctedText }}</p>
        </div>

        <div class="result-actions">
          <button class="btn-secondary"><i class="fas fa-copy"></i> 결과 복사</button>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref, reactive } from 'vue';
import axios from 'axios';

// 문법 검사 백엔드 엔드포인트
const GRAMMAR_CHECK_ENDPOINT = '/api/v1/grammar/check'

const inputText = ref('');
const isAnalyzing = ref(false);
const showResult = ref(false);

// 2. 결과 객체를 수정합니다. (likelihood 등 제거)
const result = reactive({
  correctedText: '',
});

const analyzeText = async () => {
  if (inputText.value.trim() === '') {
    alert('검사할 텍스트를 입력해주세요.');
    return;
  }

  isAnalyzing.value = true;
  showResult.value = false;

  let analysisSuccess = false;

  try {
    // 요청 페이로드: { content }
    const payload = { content: inputText.value };
    const response = await axios.post(GRAMMAR_CHECK_ENDPOINT, payload);

    // FastAPI 응답: { errors: [...], total_errors, corrected_text }
    const data = response.data;
    // corrected_text가 없으므로 errors를 사람이 읽을 수 있게 변환
    if (data.corrected_text) {
      result.correctedText = data.corrected_text;
    } else if (Array.isArray(data.errors) && data.errors.length > 0) {
      result.correctedText = data.errors
        .map(e => `- [${e.error_type}] ${e.message} (범위: ${e.start_index}~${e.end_index})\n  제안: ${e.suggestions?.join(', ') || '-'}`)
        .join('\n\n');
    } else {
      result.correctedText = '오류가 발견되지 않았습니다.';
    }

    analysisSuccess = true; // 성공!

  } catch (error) {
    // 7. 오류 처리
    console.error('API 호출 중 오류 발생:', error);
    let errorMessage = '문법 검사에 실패했습니다.';
    if (error.response) {
      errorMessage += ` (오류: ${error.response.status})`;
    }
    alert(errorMessage);
    analysisSuccess = false; // 실패
    
  } finally {
    // 8. 분석 상태 해제 및 결과 표시 결정
    isAnalyzing.value = false;
    showResult.value = analysisSuccess;
  }
};

const clearText = () => {
  inputText.value = '';
  showResult.value = false;
};
</script>

<style scoped>
/* AI 탐지기 컴포넌트(HomeView.vue)의 <style> 내용을 
  여기에 그대로 복사/붙여넣기 하세요. 
  (로딩, 버튼, textarea 스타일 등을 재사용)
*/

/* 이 컴포넌트 전용 스타일만 추가 */
.corrected-text {
  font-size: 1.1em;
  line-height: 1.7;
  white-space: pre-wrap; /* 줄바꿈 및 공백 유지 */
  background-color: #fdfdfd;
  padding: 15px;
  border-radius: 5px;
  border: 1px solid #eee;
}

/* 기존 스타일을 그대로 가져옵니다 */
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
</style>