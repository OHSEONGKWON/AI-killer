<template>
  <div class="login-container">
    <div class="login-form-container">
      <h3>로그인</h3>

      <div class="form-group">
        <label for="email">이메일</label>
        <input v-model="email" id="email" type="email" placeholder="이메일" />
      </div>
      <div class="form-group">
        <label for="password">비밀번호</label>
        <input v-model="password" id="password" type="password" placeholder="비밀번호" />
      </div>
      
      <button @click="submitLogin" class="btn btn-login">로그인</button>

      <div class="divider">
        <span>또는</span>
      </div>

      <button @click="loginWithKakao" class="btn kakao-login-btn">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
          <path fill="#191919" d="M12 4.1c-5.9 0-10.7 3.6-10.7 8.1 0 3.1 2.2 5.8 5.4 7.2.2.1.3-.1.3-.3v-1.9c0-.2 0-.4-.1-.5-.3-.2-.6-.4-.9-.7-.3-.3-.4-.7-.1-1 .3-.3.7-.1 1 .2.3.1.6.3.8.4 1.1.5 2.3.1 3.1-.7.1-.5.3-1 .5-1.3-3.6-.4-7.4-1.8-7.4-8.1 0-1.8.6-3.2 1.7-4.4-.2-.4-.7-2.1.2-4.3 0 0 1.4-.4 4.5 1.7 1.3-.4 2.7-.5 4.1-.5s2.8.2 4.1.5c3.1-2.1 4.5-1.7 4.5-1.7.9 2.2.3 3.9.2 4.3 1.1 1.1 1.7 2.6 1.7 4.4 0 6.3-3.8 7.7-7.4 8.1.3.3.5.7.5 1.5v2.2c0 .2.1.4.3.3 3.2-1.4 5.4-4.1 5.4-7.2 0-4.5-4.8-8.1-10.7-8.1z"/>
        </svg>
        <span>카카오로 로그인</span>
      </button>

      <div class="links">
        <a href="/register">회원가입</a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
// import auth from '../store/auth.js'; // auth 스토어 경로는 확인 필요

const email = ref('');
const password = ref('');
const router = useRouter();

const submitLogin = async () => {
  try {
    const response = await axios.post('http://localhost:3001/api/login', {
      email: email.value,
      password: password.value,
    });

    // auth.setUser(response.data.user); // 스토어 사용 시
    localStorage.setItem('user-token', response.data.token); // JWT 토큰 저장
    
    alert('로그인에 성공했습니다!');
    router.push('/'); 

  } catch (error) {
    if (error.response) {
      alert(`로그인 실패: ${error.response.data.error}`);
    } else {
      alert('서버에 연결할 수 없습니다. 백엔드 서버가 3001 포트에서 켜져 있는지 확인해주세요.');
    }
  }
};

const loginWithKakao = () => {
  const REST_API_KEY = '1a55fcb0d7c0b0bcbc72c07696d05038'; // 👈 여기에 키 입력
  const REDIRECT_URI = ''; // 👈 여기에 리디렉션 URI 입력
  const kakaoAuthUrl = `https://kauth.kakao.com/oauth/authorize?client_id=${REST_API_KEY}&redirect_uri=${REDIRECT_URI}&response_type=code`;
  
  window.location.href = kakaoAuthUrl;
};
</script>


<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  background-color: #f9f9f9;
}

.login-form-container {
  width: 100%;
  max-width: 400px;
  padding: 2.5rem;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  text-align: center;
}

h3 {
  margin-bottom: 1.5rem;
  font-size: 1.75rem;
  font-weight: 600;
  color: #333;
}

.form-group {
  margin-bottom: 1rem;
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #555;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-sizing: border-box; /* padding이 width를 넘지 않게 함 */
}

.btn {
  width: 100%;
  padding: 0.85rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem; /* 아이콘과 텍스트 사이 간격 */
}

/* 일반 로그인 버튼 */
.btn-login {
  background-color: #007bff;
  color: white;
}
.btn-login:hover {
  background-color: #0056b3;
}

/* 구분선 */
.divider {
  display: flex;
  align-items: center;
  text-align: center;
  margin: 1.5rem 0;
  color: #aaa;
}
.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #eee;
}
.divider span {
  padding: 0 1rem;
}

/* ⭐️ 카카오 로그인 버튼 스타일 ⭐️ */
.kakao-login-btn {
  background-color: #FEE500; /* 카카오 공식 노란색 */
  color: #191919; /* 카카오 공식 텍스트 색상 (검정) */
}
.kakao-login-btn:hover {
  background-color: #FDD800; /* 살짝 어두운 노란색 */
}
.kakao-login-btn svg {
  /* 아이콘 색상을 텍스트 색상과 맞춥니다. 
     (위 SVG의 fill 값을 #000000 또는 #191919로 설정하는 것이 좋습니다) 
     여기서는 fill="#191919"로 이미 설정했습니다. */
}

.links {
  margin-top: 1rem;
}
.links a {
  color: #007bff;
  text-decoration: none;
}
.links a:hover {
  text-decoration: underline;
}
</style>