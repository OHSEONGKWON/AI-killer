<template>
  <main>
    <section class="detection-area">
      <div class="container">
        <h2>표절 / 유사도 검사</h2>
        <div class="input-section">
          <textarea v-model="content" placeholder="검사할 텍스트를 입력하세요." />
          <div class="input-controls">
            <span>{{ content.length }} 글자</span>
            <button class="btn-analyze" @click="checkPlagiarism" :disabled="loading || content.trim().length < 10">
              {{ loading ? '검사 중...' : '검사 시작' }}
            </button>
          </div>
        </div>

        <div class="result-section" v-if="result">
          <h3>검사 결과</h3>
          <div class="result-summary">
            <div class="result-box">
              <strong>전체 유사도</strong>
              <span>{{ Math.round(result.overall_similarity * 100) }}%</span>
            </div>
            <div class="result-box">
              <strong>표절 여부</strong>
              <span>{{ result.is_plagiarized ? '의심됨' : '아님' }}</span>
            </div>
          </div>

          <div class="detailed-analysis">
            <h4>유사 출처</h4>
            <ul>
              <li v-for="(m, idx) in result.matched_sources" :key="idx">
                <a :href="m.source_url" target="_blank" rel="noopener">{{ m.source_title || m.source_url }}</a>
                <small> — 유사도 {{ Math.round(m.similarity_score * 100) }}%</small>
                <div class="matched-text">{{ m.matched_text }}</div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref } from 'vue';
import { plagiarismAPI } from '../services/api';

const content = ref('');
const loading = ref(false);
const result = ref(null);


const checkPlagiarism = async () => {
  if (content.value.trim().length < 10) return;
  loading.value = true;
  result.value = null;
  try {
    const { data } = await plagiarismAPI.check({
      content: content.value,
      check_web: true,
      check_internal: false,
    });
    result.value = data;
  } catch (e) {
    console.error(e);
    alert('표절 검사 중 오류가 발생했습니다.');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* 공통 스타일은 common.css 사용 */
.result-summary { display: flex; gap: 16px; margin-bottom: 16px; }
.result-box { flex: 1; background: #fff; border: 1px solid #e0e0e0; padding: 16px; border-radius: 8px; text-align: center; }
.matched-text { margin-top: 6px; font-size: .95em; color: #555; white-space: pre-wrap; }
</style>
