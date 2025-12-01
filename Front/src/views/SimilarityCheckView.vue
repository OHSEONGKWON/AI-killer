<template>
  <div class="similarity-wrapper">
    <h2>🤖 AI 유사도 검사 (Gemini + SBERT)</h2>

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
      <p>AI 유사도 분석 중...</p>
    </div>

    <div v-if="result" class="result-section">
      <!-- 최종 점수 및 AI 판단 -->
      <div class="final-score-box" :class="getRiskClass(result.final_probability)">
        <div class="score-header">
          <div class="icon">{{ getRiskIcon(result.final_probability) }}</div>
          <div class="score-info">
            <h3>AI 작성 확률</h3>
            <div class="probability">{{ result.final_probability }}%</div>
            <div class="likelihood">{{ result.ai_likelihood }}</div>
          </div>
        </div>
        <div class="recommendation">
          <strong>💡 분석 결과:</strong> {{ result.recommendation }}
        </div>
        <div v-if="result.perplexity" class="perplexity-box">
          <span class="label">Perplexity:</span>
          <span class="value">{{ result.perplexity.toFixed(2) }}</span>
          <span class="info">(낮을수록 자연스러움)</span>
        </div>
      </div>

      <!-- 문장별 분석 통계 -->
      <div class="analysis-stats">
        <h3>📊 문장별 위험도 분석</h3>
        <div class="stats-grid">
          <div class="stat-card high" v-if="result.analysis">
            <div class="stat-number">{{ result.analysis.high_risk_sentences }}</div>
            <div class="stat-label">높은 위험</div>
          </div>
          <div class="stat-card medium" v-if="result.analysis">
            <div class="stat-number">{{ result.analysis.medium_risk_sentences }}</div>
            <div class="stat-label">중간 위험</div>
          </div>
          <div class="stat-card low" v-if="result.analysis">
            <div class="stat-number">{{ result.analysis.low_risk_sentences }}</div>
            <div class="stat-label">낮은 위험</div>
          </div>
          <div class="stat-card safe" v-if="result.analysis">
            <div class="stat-number">{{ result.analysis.safe_sentences }}</div>
            <div class="stat-label">안전</div>
          </div>
        </div>
      </div>

      <!-- 입력 텍스트 하이라이팅 -->
      <section class="highlight-section">
        <h3>🎨 입력 텍스트 분석 (문장별 위험도)</h3>
        <div class="sentence-list">
          <div
            v-for="sent in result.highlighted_sentences"
            :key="sent.sentence_idx"
            class="sentence-item"
            :class="'risk-' + sent.risk_level"
          >
            <div class="sentence-header">
              <span class="sentence-marker" :class="'marker-' + sent.risk_level">{{ sent.sentence_idx }}</span>
              <span class="similarity-badge">유사도: {{ (sent.similarity * 100).toFixed(1) }}%</span>
              <span class="match-info">매칭: AI 문단 #{{ sent.matched_gen_idx }}</span>
            </div>
            <div class="sentence-content">{{ sent.text }}</div>
          </div>
        </div>
        <div class="legend">
          <span class="legend-item risk-high">높음 (≥70%)</span>
          <span class="legend-item risk-medium">중간 (50-70%)</span>
          <span class="legend-item risk-low">낮음 (30-50%)</span>
          <span class="legend-item risk-safe">안전 (<30%)</span>
        </div>
      </section>

      <!-- Top-3 AI 생성 문단 -->
      <section class="top-summary">
        <h3>🏆 상위 3개 유사 AI 문단</h3>
        <div class="top-cards">
          <div v-for="(top, index) in result.top_scores" :key="top.idx" class="top-card">
            <div class="rank-badge">{{ index + 1 }}위</div>
            <div class="card-header">
              <span class="ai-badge">AI 생성 #{{ top.idx }}</span>
              <span class="score-value">{{ (top.score * 100).toFixed(1) }}%</span>
            </div>
            <p class="card-text">{{ top.text }}</p>
            <div class="card-footer">
              <span class="semantic-score">의미 유사도: {{ (top.semantic_similarity * 100).toFixed(1) }}%</span>
            </div>
          </div>
        </div>
      </section>

      <details class="raw-json">
        <summary>🔍 원본 응답 보기 (개발자용)</summary>
        <pre>{{ JSON.stringify(result, null, 2) }}</pre>
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

const dismissError = () => {
  error.value = '';
  clearTimeout(errorTimer);
};

const getRiskClass = (probability) => {
  if (probability >= 80) return 'risk-very-high';
  if (probability >= 60) return 'risk-high';
  if (probability >= 40) return 'risk-medium';
  return 'risk-low';
};

const getRiskIcon = (probability) => {
  if (probability >= 80) return '🚨';
  if (probability >= 60) return '⚠️';
  if (probability >= 40) return '⚡';
  return '✅';
};
</script>

<style scoped>
.similarity-wrapper { max-width: 1200px; margin: 0 auto; padding: 20px; }
.similarity-wrapper h2 { font-size: 28px; margin-bottom: 24px; color: #1a1a1a; }

/* Form */
.similarity-form { display: flex; flex-direction: column; gap: 16px; background:#fff; padding:28px; border:1px solid #e0e0e0; border-radius:16px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.similarity-form label { display:flex; flex-direction:column; font-weight:600; color:#333; font-size: 15px; }
.similarity-form input, .similarity-form textarea { margin-top:8px; padding:14px; border:2px solid #e0e0e0; border-radius:10px; font-size:14px; resize:vertical; transition: border-color 0.3s; }
.similarity-form input:focus, .similarity-form textarea:focus { outline: none; border-color: #00C4CC; }
.actions { display:flex; gap:12px; }
.actions button { padding:12px 24px; border:none; border-radius:10px; cursor:pointer; font-weight:600; font-size: 15px; transition: all 0.3s; }
.actions button[type=submit]{ background: linear-gradient(135deg, #00C4CC 0%, #00a8b8 100%); color:#fff; }
.actions button[type=submit]:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,196,204,0.3); }
.actions button[type=submit]:disabled{ background:#ccc; cursor:not-allowed; }
.actions button[type=button]{ background:#6c757d; color:#fff; }
.actions button[type=button]:hover { background:#5a6268; }
.helper { color:#d9534f; font-size:13px; margin-top: 4px; }

/* Result Section */
.result-section { margin-top:40px; }

/* Final Score Box */
.final-score-box { background:#fff; padding:32px; border-radius:16px; margin-bottom:32px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); border-left: 6px solid #00C4CC; }
.final-score-box.risk-very-high { border-left-color: #ff4757; background: linear-gradient(135deg, #fff 0%, #fff5f5 100%); }
.final-score-box.risk-high { border-left-color: #ffa502; background: linear-gradient(135deg, #fff 0%, #fffbf0 100%); }
.final-score-box.risk-medium { border-left-color: #ffd32a; background: linear-gradient(135deg, #fff 0%, #fffef0 100%); }
.final-score-box.risk-low { border-left-color: #26de81; background: linear-gradient(135deg, #fff 0%, #f0fff4 100%); }

.score-header { display: flex; align-items: center; gap: 24px; margin-bottom: 20px; }
.score-header .icon { font-size: 64px; }
.score-info h3 { margin: 0 0 8px; font-size: 18px; color: #666; font-weight: 500; }
.probability { font-size: 56px; font-weight: 800; background: linear-gradient(135deg, #00C4CC 0%, #00a8b8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1; }
.likelihood { font-size: 16px; color: #666; margin-top: 8px; font-weight: 600; }
.recommendation { background: #f8f9fa; padding: 16px; border-radius: 10px; margin-top: 16px; border-left: 4px solid #00C4CC; }
.recommendation strong { color: #00C4CC; }
.perplexity-box { margin-top: 20px; padding-top: 20px; border-top: 2px dashed #e0e0e0; display: flex; gap: 12px; align-items: center; font-size: 15px; }
.perplexity-box .label { font-weight: 600; color: #666; }
.perplexity-box .value { font-size: 24px; font-weight: 700; color: #ff6b6b; }
.perplexity-box .info { color: #999; font-size: 13px; }

/* Analysis Stats */
.analysis-stats { background: #fff; padding: 28px; border-radius: 16px; margin-bottom: 32px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.analysis-stats h3 { margin: 0 0 20px; font-size: 20px; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 16px; }
.stat-card { padding: 20px; border-radius: 12px; text-align: center; transition: transform 0.3s; }
.stat-card:hover { transform: translateY(-4px); }
.stat-card.high { background: linear-gradient(135deg, #ff4757 0%, #ff6b6b 100%); color: #fff; }
.stat-card.medium { background: linear-gradient(135deg, #ffa502 0%, #ffb142 100%); color: #fff; }
.stat-card.low { background: linear-gradient(135deg, #ffd32a 0%, #ffe66d 100%); color: #333; }
.stat-card.safe { background: linear-gradient(135deg, #26de81 0%, #4cd964 100%); color: #fff; }
.stat-number { font-size: 36px; font-weight: 800; line-height: 1; }
.stat-label { font-size: 13px; margin-top: 8px; font-weight: 600; opacity: 0.9; }

/* Highlighted Text */
.highlight-section { background: #fff; padding: 28px; border-radius: 16px; margin-bottom: 32px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.highlight-section h3 { margin: 0 0 20px; font-size: 20px; }
.sentence-list { display: flex; flex-direction: column; gap: 12px; }
.sentence-item { padding: 16px; border-radius: 10px; border-left: 4px solid; transition: all 0.3s; }
.sentence-item:hover { transform: translateX(4px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.sentence-item.risk-high { background: rgba(255, 71, 87, 0.08); border-left-color: #ff4757; }
.sentence-item.risk-medium { background: rgba(255, 165, 2, 0.08); border-left-color: #ffa502; }
.sentence-item.risk-low { background: rgba(255, 211, 42, 0.08); border-left-color: #ffd32a; }
.sentence-item.risk-safe { background: rgba(38, 222, 129, 0.06); border-left-color: #26de81; }
.sentence-header { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; flex-wrap: wrap; }
.sentence-marker { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 50%; font-size: 12px; font-weight: 700; color: #fff; }
.marker-high { background: #ff4757; }
.marker-medium { background: #ffa502; }
.marker-low { background: #ffd32a; color: #333; }
.marker-safe { background: #26de81; }
.similarity-badge { padding: 4px 12px; background: #f8f9fa; border-radius: 6px; font-size: 12px; font-weight: 600; color: #333; border: 1px solid #e0e0e0; }
.match-info { padding: 4px 12px; background: #e3f2fd; border-radius: 6px; font-size: 12px; font-weight: 600; color: #1976d2; }
.sentence-content { line-height: 1.6; color: #333; font-size: 14px; padding-left: 40px; }
.legend { margin-top: 20px; display: flex; gap: 16px; flex-wrap: wrap; }
.legend-item { padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; }
.legend-item.risk-high { background: #ff4757; color: #fff; }
.legend-item.risk-medium { background: #ffa502; color: #fff; }
.legend-item.risk-low { background: #ffd32a; color: #333; }
.legend-item.risk-safe { background: #26de81; color: #fff; }

/* Top Cards */
.top-summary { background: #fff; padding: 28px; border-radius: 16px; margin-bottom: 32px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.top-summary h3 { margin: 0 0 20px; font-size: 20px; }
.top-cards { display: grid; gap: 20px; }
.top-card { background: linear-gradient(135deg, #f8f9fa 0%, #fff 100%); border: 2px solid #e0e0e0; border-radius: 12px; padding: 20px; position: relative; transition: all 0.3s; }
.top-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); border-color: #00C4CC; }
.rank-badge { position: absolute; top: -12px; left: 20px; background: linear-gradient(135deg, #00C4CC 0%, #00a8b8 100%); color: #fff; padding: 6px 16px; border-radius: 20px; font-weight: 700; font-size: 13px; box-shadow: 0 4px 12px rgba(0,196,204,0.3); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-top: 8px; }
.ai-badge { background: #e0e0e0; padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; color: #666; }
.score-value { font-size: 18px; font-weight: 800; color: #00C4CC; }
.card-text { line-height: 1.7; color: #333; font-size: 14px; margin: 12px 0; }
.card-footer { padding-top: 12px; border-top: 1px solid #e0e0e0; }
.semantic-score { font-size: 13px; color: #666; font-weight: 600; }

/* Loading overlay */
.loading-overlay { position:fixed; inset:0; background: rgba(0,0,0,0.5); backdrop-filter:blur(4px); display:flex; flex-direction:column; align-items:center; justify-content:center; z-index:1000; }
.loading-overlay p { color: #fff; margin-top: 20px; font-size: 16px; font-weight: 600; }
.spinner { width:64px; height:64px; border:6px solid rgba(255,255,255,0.2); border-top-color:#00C4CC; border-radius:50%; animation:spin 0.8s linear infinite; }
@keyframes spin { to { transform:rotate(360deg); } }

/* Toast */
.toast { position:fixed; top:20px; right:20px; background:#fff; padding:16px 20px; border-radius:12px; box-shadow:0 4px 20px rgba(0,0,0,0.2); display:flex; gap:12px; align-items:center; font-size:14px; z-index:1100; }
.toast.error { border-left:6px solid #ff4d4f; }
.toast .close { background:transparent; border:none; font-size:20px; cursor:pointer; color:#666; }
.fade-enter-active, .fade-leave-active { transition: opacity .4s; }
.fade-enter-from, .fade-leave-to { opacity:0; }

/* Raw JSON */
.raw-json { margin-top:32px; background: #f8f9fa; padding: 20px; border-radius: 12px; }
.raw-json summary { cursor: pointer; font-weight: 600; padding: 12px; background: #fff; border-radius: 8px; user-select: none; }
.raw-json summary:hover { background: #e0e0e0; }
.raw-json pre { background:#1e1e1e; color:#f1f1f1; padding:20px; border-radius:8px; overflow:auto; font-size:12px; margin-top: 12px; line-height: 1.5; }
</style>
