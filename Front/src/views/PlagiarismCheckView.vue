<template>
  <main>
    <section class="detection-area">
      <div class="container">
        <h2>AI 표절 검사</h2>
        <p class="subtitle">AI가 자동으로 원본 출처를 추적하고 표절 여부를 분석합니다</p>
        
        <div class="input-section">
          <textarea v-model="content" placeholder="검사할 텍스트를 입력하세요 (10자 이상)..." rows="10" />
          <div class="input-controls">
            <span class="char-count">{{ content.length }} / 10000 글자</span>
            <button class="btn-analyze" @click="checkPlagiarism" :disabled="loading || content.trim().length < 10">
              {{ loading ? '🔍 AI 분석 중...' : '🚀 검사 시작' }}
            </button>
          </div>
        </div>

        <!-- 로딩 -->
        <div v-if="loading" class="loading-overlay">
          <div class="spinner"></div>
          <p>AI가 인터넷과 지식 베이스를 검색 중입니다...</p>
        </div>

        <!-- 결과 -->
        <div class="result-section" v-if="result">
          <h3>📊 검사 결과</h3>
          
          <div class="result-summary">
            <div class="result-box score-box">
              <strong>유사도 점수</strong>
              <div class="score" :class="getScoreClass(result.overall_similarity_score)">
                {{ result.overall_similarity_score }}%
              </div>
            </div>
            <div class="result-box source-box">
              <strong>추정 출처</strong>
              <div class="source">
                <span v-if="result.source_url">
                  <a :href="result.source_url" target="_blank" rel="noopener noreferrer" class="source-link">
                    {{ result.suspected_source }}
                  </a>
                </span>
                <span v-else>
                  {{ result.suspected_source }}
                </span>
              </div>
              <small :class="{ found: result.original_found }">
                {{ result.original_found ? '✅ 원본 발견됨' : '❌ 원본 미발견' }}
              </small>
            </div>
          </div>

          <!-- 하이라이트된 텍스트 -->
          <div class="highlight-section" v-if="result.highlight_segments && result.highlight_segments.length > 0">
            <h4>🔍 표절 의심 구간 (시각화)</h4>
            <div class="highlighted-text" v-html="result.highlighted_html"></div>
            
            <div class="legend">
              <span class="legend-item exact">🔴 정확 일치 (EXACT)</span>
              <span class="legend-item suspicious">🟡 의심 구간 (SUSPICIOUS)</span>
            </div>
          </div>

          <!-- 상세 분석 -->
          <div class="detailed-analysis" v-if="result.highlight_segments && result.highlight_segments.length > 0">
            <h4>💡 상세 분석</h4>
            <ul class="segment-list">
              <li v-for="(seg, idx) in result.highlight_segments" :key="idx" :class="seg.type.toLowerCase()">
                <span class="icon">{{ seg.type === 'EXACT' ? '🔴' : '🟡' }}</span>
                <div class="segment-content">
                  <div class="segment-type">[{{ seg.type }}]</div>
                  <div class="segment-text">"{{ seg.target_text }}"</div>
                  <div class="segment-reason">{{ seg.reason }}</div>
                </div>
              </li>
            </ul>
          </div>

          <div v-else class="no-plagiarism">
            ✅ 표절 의심 구간이 발견되지 않았습니다. 창작물일 가능성이 높습니다.
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { plagiarismAPI } from '../services/api';
import auth from '../store/auth';

const router = useRouter();
const content = ref('');
const loading = ref(false);
const result = ref(null);

const getScoreClass = (score) => {
  if (score >= 70) return 'high';
  if (score >= 40) return 'medium';
  return 'low';
};

const checkPlagiarism = async () => {
  // 로그인 확인
  if (!auth.state.isLoggedIn) {
    alert('표절 검사는 로그인 후 이용 가능합니다.');
    router.push('/login');
    return;
  }

  if (content.value.trim().length < 10) return;
  loading.value = true;
  result.value = null;
  try {
    const { data } = await plagiarismAPI.check({
      content: content.value,
    });
    result.value = data;
  } catch (e) {
    console.error(e);
    // 401 Unauthorized 에러 처리
    if (e.response?.status === 401) {
      alert('로그인이 필요합니다.');
      router.push('/login');
      return;
    }
    alert('표절 검사 중 오류가 발생했습니다: ' + (e.response?.data?.detail || e.message));
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.container { max-width: 1100px; margin: 0 auto; padding: 24px; }
h2 { margin-bottom: 8px; }
.subtitle { color: #666; margin-bottom: 24px; font-size: 14px; }

.input-section { background: #fff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 20px; margin-bottom: 24px; }
textarea { width: 100%; padding: 12px; border: 1px solid #ccc; border-radius: 8px; font-size: 14px; resize: vertical; font-family: inherit; }
.input-controls { display: flex; justify-content: space-between; align-items: center; margin-top: 12px; }
.char-count { color: #666; font-size: 13px; }
.btn-analyze { padding: 10px 24px; background: #00C4CC; color: #fff; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 14px; }
.btn-analyze:disabled { background: #ccc; cursor: not-allowed; }
.btn-analyze:hover:not(:disabled) { background: #00a8b0; }

.loading-overlay { position: fixed; inset: 0; backdrop-filter: blur(2px); display: flex; flex-direction: column; align-items: center; justify-content: center; z-index: 1000; }
.spinner { width: 54px; height: 54px; border: 6px solid #e0e0e0; border-top-color: #00C4CC; border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.result-section { background: #fff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 24px; }
.result-summary { display: grid; grid-template-columns: 1fr 2fr; gap: 16px; margin-bottom: 24px; }
.result-box { border: 1px solid #e0e0e0; padding: 20px; border-radius: 8px; text-align: center; }
.result-box strong { display: block; margin-bottom: 12px; color: #666; font-size: 14px; }
.score { font-size: 48px; font-weight: 800; }
.score.low { color: #28a745; }
.score.medium { color: #ffc107; }
.score.high { color: #dc3545; }
.source { font-size: 18px; font-weight: 700; color: #333; margin-bottom: 8px; }
.source-link { color: #00C4CC; text-decoration: none; border-bottom: 2px solid #00C4CC; transition: all 0.2s; }
.source-link:hover { color: #00a8b0; border-bottom-color: #00a8b0; }
.source-box small { font-size: 13px; color: #666; }
.source-box small.found { color: #28a745; font-weight: 600; }

.highlight-section { margin-bottom: 24px; padding: 20px; background: #f8f9fa; border-radius: 8px; }
.highlight-section h4 { margin-top: 0; margin-bottom: 16px; }
.highlighted-text { background: #fff; padding: 20px; border-radius: 8px; line-height: 1.8; font-size: 15px; white-space: pre-wrap; word-wrap: break-word; }
.highlighted-text :deep(mark.exact) { background: #ff4d4f; color: #fff; padding: 2px 4px; border-radius: 3px; font-weight: 600; }
.highlighted-text :deep(mark.suspicious) { background: #ffc107; color: #000; padding: 2px 4px; border-radius: 3px; }
.legend { display: flex; gap: 20px; margin-top: 12px; font-size: 13px; }
.legend-item.exact { color: #ff4d4f; }
.legend-item.suspicious { color: #ffc107; }

.detailed-analysis h4 { margin-bottom: 16px; }
.segment-list { list-style: none; padding: 0; margin: 0; }
.segment-list li { display: flex; gap: 12px; padding: 16px; margin-bottom: 12px; border: 1px solid #e0e0e0; border-radius: 8px; background: #fff; }
.segment-list li.exact { border-left: 4px solid #ff4d4f; }
.segment-list li.suspicious { border-left: 4px solid #ffc107; }
.icon { font-size: 20px; flex-shrink: 0; }
.segment-content { flex: 1; }
.segment-type { font-weight: 700; color: #666; font-size: 12px; margin-bottom: 6px; }
.segment-text { font-weight: 600; margin-bottom: 8px; color: #333; }
.segment-reason { color: #666; font-size: 14px; line-height: 1.5; }

.no-plagiarism { padding: 40px; text-align: center; background: #e6f9fa; border-radius: 8px; font-size: 16px; color: #00C4CC; font-weight: 600; }
</style>
