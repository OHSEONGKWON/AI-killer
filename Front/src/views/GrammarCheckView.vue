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
import { grammarAPI } from '../services/api';

const inputText = ref('');
const isAnalyzing = ref(false);
const showResult = ref(false);

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
    const payload = { content: inputText.value };
    const response = await grammarAPI.check(payload);

    const data = response.data;
    if (data.corrected_text) {
      result.correctedText = data.corrected_text;
    } else if (Array.isArray(data.errors) && data.errors.length > 0) {
      result.correctedText = data.errors
        .map(e => `- [${e.error_type}] ${e.message} (범위: ${e.start_index}~${e.end_index})\n  제안: ${e.suggestions?.join(', ') || '-'}`)
        .join('\n\n');
    } else {
      result.correctedText = '오류가 발견되지 않았습니다.';
    }

    analysisSuccess = true;

  } catch (error) {
    console.error('API 호출 중 오류 발생:', error);
    let errorMessage = '문법 검사에 실패했습니다.';
    if (error.response) {
      errorMessage += ` (오류: ${error.response.status})`;
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
</script>

<style scoped>
/* 이 뷰는 공통 스타일(common.css)을 사용하므로 추가 스타일이 없습니다. */
</style>
