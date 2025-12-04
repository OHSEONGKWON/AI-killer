<template>
  <div class="result-section">
    <h3>분석 결과</h3>
    <div class="result-summary">
      <template v-if="isAIDetected">
        <i class="fas fa-robot result-icon ai-detected"></i>
        <span class="result-text ai-detected">AI 생성 가능성: {{ likelihood }}%</span>
      </template>
      <template v-else>
        <i class="fas fa-feather-alt result-icon human-detected"></i>
        <span class="result-text human-detected">AI 생성 가능성: {{ likelihood }}%</span>
      </template>
    </div>
    <div class="detailed-analysis">
      <h4>상세 분석</h4>
      <p v-html="detailedText"></p>
    </div>
    <div class="result-actions">
      <button class="btn-secondary" @click="copyResult">
        <i class="fas fa-copy"></i> 결과 복사
      </button>
      <button class="btn-secondary" @click="downloadResult">
        <i class="fas fa-download"></i> 결과 다운로드
      </button>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  isAIDetected: {
    type: Boolean,
    required: true
  },
  likelihood: {
    type: Number,
    required: true
  },
  detailedText: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['copy', 'download']);

const copyResult = () => {
  emit('copy');
};

const downloadResult = () => {
  emit('download');
};
</script>

<style scoped>
.result-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.result-summary {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.result-icon {
  font-size: 2rem;
}

.result-icon.ai-detected {
  color: #e74c3c;
}

.result-icon.human-detected {
  color: #27ae60;
}

.result-text {
  font-size: 1.2rem;
  font-weight: 600;
}

.result-text.ai-detected {
  color: #e74c3c;
}

.result-text.human-detected {
  color: #27ae60;
}

.detailed-analysis {
  margin-bottom: 1.5rem;
  padding: 1rem;
  border-left: 4px solid #3498db;
  background: #f8f9fa;
}

.detailed-analysis h4 {
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.result-actions {
  display: flex;
  gap: 1rem;
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background 0.3s;
}

.btn-secondary:hover {
  background: #5a6268;
}

.btn-secondary i {
  font-size: 1rem;
}
</style>
