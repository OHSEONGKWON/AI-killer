<template>
  <div class="similarity-wrapper">
    <h2>AI 유사도 검사 (Gemini + SBERT)</h2>

    <form @submit.prevent="runSimilarityStream" class="similarity-form">
      <label>
        주제 (제목)
        <input v-model="topic" type="text" placeholder="예: 인공지능 윤리" required :disabled="loading" />
      </label>
      <label>
        검사할 텍스트
        <textarea v-model="userText" placeholder="여기에 비교할 사용자 텍스트를 입력하세요" rows="8" required :disabled="loading" />
      </label>
      <div class="actions">
        <button type="submit" :disabled="loading || userText.length < 10 || topic.length < 1">{{ loading ? '검사 중...' : '유사도 계산' }}</button>
        <button type="button" @click="resetAll" :disabled="loading">초기화</button>
      </div>
      <p class="helper" v-if="userText.length < 10">최소 10자 이상 입력해주세요.</p>
    </form>

    <!-- 에러 토스트 -->
    <transition name="fade">
      <div v-if="error" class="toast error" @click="dismissError">
        <strong>오류</strong> {{ error }}
        <button class="close" type="button" @click.stop="dismissError">×</button>
      </div>
    </transition>

    <!-- 로딩 오버레이 -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>유사도 및 Perplexity 계산 중...</p>
    </div>

    <div v-if="result" class="result-section">
      <div class="final-score-box">
        <h3>최종 유사도 확률</h3>
        <div class="probability">{{ result.final_probability }}%</div>
        <small>(Top-3 평균 기반)</small>
        <div v-if="result.perplexity !== null && result.perplexity !== undefined" class="perplexity-box">
          <h4>Perplexity</h4>
          <div class="perplexity-value">{{ result.perplexity }}</div>
          <small>(낮을수록 자연스러운 텍스트)</small>
        </div>
      </div>

      <!-- Top-3 요약 -->
      <section class="top-summary">
        <h3>상위 3개 문단 요약</h3>
        <ol>
          <li v-for="top in result.top_scores" :key="top.idx">
            <div class="top-score-header">
              <span class="badge">#{{ top.idx }}</span>
              <span class="score">{{ (top.score * 100).toFixed(1) }}%</span>
            </div>
            <p class="top-text">{{ top.text }}</p>
          </li>
        </ol>
      </section>

      <h3>생성된 20개 AI 문단과 개별 SBERT 유사도</h3>
      <table class="results-table">
        <thead>
          <tr>
            <th>#</th>
            <th>생성 문단 (200자)</th>
            <th>SBERT 유사도</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in result.scores" :key="row.idx" :class="{ top: isTop(row.idx) }">
            <td>{{ row.idx }}</td>
            <td class="gen-text">{{ row.text }}</td>
            <td><strong>{{ (row.semantic_similarity * 100).toFixed(1) }}%</strong></td>
          </tr>
        </tbody>
      </table>

      <details class="raw-json">
        <summary>원본 응답 보기 (디버그)</summary>
        <pre>{{ result }}</pre>
      </details>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { similarityAPI } from '../services/api';

const topic = ref('');
const userText = ref('');
const loading = ref(false);
const error = ref('');
const result = ref(null);

let errorTimer = null;

const runSimilarityStream = async () => {
  error.value = '';
  result.value = null;
  loading.value = true;
  try {
    const token = localStorage.getItem('access_token');
    const payload = { topic: topic.value, text: userText.value };
    const response = await fetch('/api/v1/similarity/check-stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
      },
      body: JSON.stringify(payload)
    });
    if (!response.ok) {
      console.error('Streaming HTTP status:', response.status);
      // Fallback: 일반 API로 재시도
      const fallback = await similarityAPI.check(payload).catch(()=>null);
      if (fallback?.data) {
        result.value = fallback.data;
        return;
      }
      throw new Error('스트리밍 요청 실패 (status ' + response.status + ')');
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split('\n\n');
      for (let i = 0; i < parts.length - 1; i++) {
        const chunk = parts[i];
        if (!chunk.startsWith('data:')) continue;
        const jsonStr = chunk.replace(/^data:\s*/, '');
        try {
          const event = JSON.parse(jsonStr);
          if (event.type === 'final') {
            result.value = event;
          } else if (event.type === 'error') {
            throw new Error(event.message || '오류 발생');
          }
        } catch (e) {
          console.warn('이벤트 파싱 오류', e);
        }
      }
      buffer = parts[parts.length - 1];
    }
  } catch (e) {
    console.error(e);
    error.value = e.message || '유사도 계산 실패';
    clearTimeout(errorTimer);
    errorTimer = setTimeout(() => { error.value = ''; }, 4000);
  } finally {
    loading.value = false;
  }
};

const resetAll = () => {
  topic.value = '';
  userText.value = '';
  result.value = null;
  error.value = '';
};

const isTop = (idx) => {
  if (!result.value?.top_scores) return false;
  return result.value.top_scores.some(s => s.idx === idx);
};

// 막대 그래프 제거됨

const dismissError = () => {
  error.value = '';
  clearTimeout(errorTimer);
};
</script>

<style scoped>
.similarity-wrapper { max-width: 1100px; margin: 0 auto; }
.similarity-form { display: flex; flex-direction: column; gap: 16px; background:#fff; padding:24px; border:1px solid #e0e0e0; border-radius:12px; }
.similarity-form label { display:flex; flex-direction:column; font-weight:600; color:#333; }
.similarity-form input, .similarity-form textarea { margin-top:6px; padding:12px; border:1px solid #ccc; border-radius:8px; font-size:14px; resize:vertical; }
.actions { display:flex; gap:12px; }
.actions button { padding:10px 18px; border:none; border-radius:8px; cursor:pointer; font-weight:600; }
.actions button[type=submit]{ background:#00C4CC; color:#fff; }
.actions button[type=submit]:disabled{ background:#80e2e6; cursor:not-allowed; }
.actions button[type=button]{ background:#6c757d; color:#fff; }
.helper { color:#d9534f; font-size:13px; }
.error-box { margin-top:18px; background:#ffe6e6; color:#b30000; padding:12px 16px; border-radius:8px; border:1px solid #ffb3b3; }
.result-section { margin-top:32px; }
.final-score-box { background:#fff; padding:20px; border:1px solid #e0e0e0; border-radius:12px; margin-bottom:24px; text-align:center; }
.final-score-box .probability { font-size:48px; font-weight:800; color:#00C4CC; }
.perplexity-box { margin-top:20px; padding-top:20px; border-top:1px solid #e0e0e0; }
.perplexity-box h4 { margin:0 0 8px; font-size:16px; color:#666; }
.perplexity-value { font-size:32px; font-weight:700; color:#ff6b6b; }
.results-table { width:100%; border-collapse:collapse; background:#fff; border:1px solid #e0e0e0; }
.results-table th, .results-table td { padding:10px 12px; border-bottom:1px solid #eee; vertical-align:top; }
.results-table th { background:#f8f9fa; text-align:left; }
.results-table tbody tr.top { background:#e6f9fa; }
.results-table tbody tr.top td:first-child { font-weight:700; }
.gen-text { font-size:13px; line-height:1.4; }
/* 막대 그래프 스타일 제거됨 */

/* Top summary */
.top-summary { background:#fff; border:1px solid #e0e0e0; border-radius:12px; padding:20px; margin-bottom:28px; }
.top-summary ol { margin:0; padding-left:18px; }
.top-summary li { margin-bottom:14px; }
.top-score-header { display:flex; align-items:center; gap:10px; }
.badge { background:#00C4CC; color:#fff; padding:4px 10px; border-radius:6px; font-size:12px; font-weight:600; }
.score { font-weight:700; color:#333; }
.top-text { margin:6px 0 0; font-size:13px; line-height:1.5; }

/* Loading overlay */
.loading-overlay { position:fixed; inset:0; backdrop-filter:blur(2px); display:flex; flex-direction:column; align-items:center; justify-content:center; z-index:1000; }
.spinner { width:54px; height:54px; border:6px solid #e0e0e0; border-top-color:#00C4CC; border-radius:50%; animation:spin 1s linear infinite; }
@keyframes spin { to { transform:rotate(360deg); } }

/* Toast */
.toast { position:fixed; top:20px; right:20px; background:#fff; padding:14px 18px; border-radius:10px; box-shadow:0 4px 18px rgba(0,0,0,0.15); display:flex; gap:10px; align-items:center; font-size:14px; z-index:1100; }
.toast.error { border-left:6px solid #ff4d4f; }
.toast .close { background:transparent; border:none; font-size:18px; cursor:pointer; color:#666; }
.fade-enter-active, .fade-leave-active { transition: opacity .4s; }
.fade-enter-from, .fade-leave-to { opacity:0; }
.raw-json { margin-top:24px; }
.raw-json pre { background:#1e1e1e; color:#f1f1f1; padding:16px; border-radius:8px; overflow:auto; font-size:12px; }
</style>
