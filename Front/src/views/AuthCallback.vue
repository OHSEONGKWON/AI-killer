<template>
  <div class="callback-container">
    <div v-if="loading">
      <div class="spinner"></div>
      <p>로그인 처리 중...</p>
    </div>
    <div v-else-if="error">
      <p class="error">{{ error }}</p>
      <button @click="goHome" class="btn">홈으로 돌아가기</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import auth from '../store/auth.js';

const router = useRouter();
const loading = ref(true);
const error = ref(null);

onMounted(async () => {
  try {
    // URL에서 token 파라미터 추출
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (!token) {
      error.value = '토큰을 받지 못했습니다. 다시 로그인해주세요.';
      loading.value = false;
      return;
    }
    
    // 토큰을 localStorage에 저장
    localStorage.setItem('access_token', token);
    
    // auth 상태 초기화 (사용자 정보 로드)
    await auth.initAuth();
    
    console.log('카카오 로그인 성공, 사용자 정보:', auth.state.user);
    
    // 로그인 성공 - 홈으로 이동
    setTimeout(() => {
      router.push('/');
    }, 500);
    
  } catch (err) {
    console.error('인증 처리 중 오류:', err);
    error.value = '로그인 처리 중 오류가 발생했습니다.';
    loading.value = false;
  }
});

const goHome = () => {
  router.push('/');
};
</script>

<style scoped>
.callback-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  text-align: center;
}

.spinner {
  width: 60px;
  height: 60px;
  border: 8px solid #f3f3f3;
  border-top: 8px solid #00C4CC;
  border-radius: 50%;
  animation: spin 1.5s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

p {
  font-size: 1.2em;
  color: #333;
  margin: 20px 0;
}

.error {
  color: #dc3545;
  font-weight: 500;
}

.btn {
  padding: 12px 24px;
  background-color: #00C4CC;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.btn:hover {
  background-color: #009999;
}
</style>
