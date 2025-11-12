# Vue 프론트엔드 연동 가이드

## 📋 백엔드 준비 완료!

Vue 프론트엔드와 연동하기 위한 모든 백엔드 준비가 완료되었습니다.

### ✅ 완료된 작업

1. **CORS 설정** - Vue 개발 서버(8080) 허용
2. **카카오 로그인 API** - OAuth 2.0 플로우 완전 구현
3. **일반 로그인/회원가입 API** - 이메일/비밀번호 방식
4. **환경변수 설정** - 카카오 REST API 키, JWT 키, 프론트엔드 URL

---

## 🚀 백엔드 서버 시작

```powershell
cd C:\GitHub\AI-killer\Back\Web
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

서버가 시작되면:
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

---

## 🔐 카카오 로그인 연동

### 1. 카카오 로그인 플로우

```
Vue 앱 → 백엔드 → 카카오 → 백엔드 → Vue 앱
```

### 2. Vue에서 카카오 로그인 버튼 구현

```vue
<template>
  <div>
    <button @click="handleKakaoLogin" class="kakao-login-btn">
      카카오로 시작하기
    </button>
  </div>
</template>

<script>
export default {
  methods: {
    handleKakaoLogin() {
      // 백엔드의 카카오 로그인 엔드포인트로 이동
      // 백엔드가 자동으로 카카오 로그인 페이지로 리다이렉트함
      window.location.href = 'http://localhost:8000/api/v1/auth/kakao';
    }
  }
}
</script>

<style scoped>
.kakao-login-btn {
  background-color: #FEE500;
  color: #000000;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
}
</style>
```

### 3. 카카오 로그인 콜백 페이지 생성

**`src/views/AuthCallback.vue`** 파일 생성:

```vue
<template>
  <div class="callback-container">
    <div v-if="loading">
      <p>로그인 처리 중...</p>
    </div>
    <div v-else-if="error">
      <p>{{ error }}</p>
      <button @click="$router.push('/')">홈으로 돌아가기</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AuthCallback',
  data() {
    return {
      loading: true,
      error: null
    }
  },
  mounted() {
    // URL에서 토큰 추출
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (token) {
      // 토큰을 localStorage에 저장
      localStorage.setItem('access_token', token);
      
      // 사용자 정보 조회 (선택 사항)
      this.fetchUserInfo(token);
      
      // 메인 페이지로 리다이렉트
      this.$router.push('/dashboard');
    } else {
      this.loading = false;
      this.error = '로그인에 실패했습니다.';
    }
  },
  methods: {
    async fetchUserInfo(token) {
      try {
        const response = await fetch('http://localhost:8000/api/v1/users/me', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (response.ok) {
          const user = await response.json();
          // Vuex store에 사용자 정보 저장
          this.$store.commit('setUser', user);
        }
      } catch (error) {
        console.error('사용자 정보 조회 실패:', error);
      }
    }
  }
}
</script>

<style scoped>
.callback-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
</style>
```

### 4. Vue Router 설정

**`src/router/index.js`**에 콜백 라우트 추가:

```javascript
import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import AuthCallback from '../views/AuthCallback.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/auth/callback',
    name: 'AuthCallback',
    component: AuthCallback
  },
  // ... 다른 라우트
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
```

---

## 🔑 일반 로그인/회원가입 연동

### 1. API 클라이언트 설정

**`src/api/client.js`** 생성:

```javascript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// 요청 인터셉터: 토큰 자동 추가
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터: 401 에러 처리
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 토큰 만료 시 로그인 페이지로
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### 2. 인증 API 함수

**`src/api/auth.js`** 생성:

```javascript
import apiClient from './client';

export const authAPI = {
  // 회원가입
  async register(username, email, password) {
    const response = await apiClient.post('/api/v1/auth/register', {
      username,
      email,
      password
    });
    return response.data;
  },

  // 로그인
  async login(username, password) {
    const response = await apiClient.post('/api/v1/auth/login', null, {
      params: { username, password }
    });
    
    const { access_token } = response.data;
    localStorage.setItem('access_token', access_token);
    
    return response.data;
  },

  // 로그아웃
  logout() {
    localStorage.removeItem('access_token');
  },

  // 현재 사용자 정보 조회
  async getCurrentUser() {
    const response = await apiClient.get('/api/v1/users/me');
    return response.data;
  },

  // 토큰 확인
  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  }
};
```

### 3. 로그인 페이지

**`src/views/Login.vue`**:

```vue
<template>
  <div class="login-container">
    <h2>로그인</h2>
    
    <!-- 일반 로그인 폼 -->
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label>사용자명</label>
        <input v-model="username" type="text" required />
      </div>
      
      <div class="form-group">
        <label>비밀번호</label>
        <input v-model="password" type="password" required />
      </div>
      
      <button type="submit" :disabled="loading">
        {{ loading ? '로그인 중...' : '로그인' }}
      </button>
      
      <p v-if="error" class="error">{{ error }}</p>
    </form>
    
    <div class="divider">또는</div>
    
    <!-- 카카오 로그인 -->
    <button @click="handleKakaoLogin" class="kakao-btn">
      카카오로 시작하기
    </button>
    
    <p class="register-link">
      계정이 없으신가요? <router-link to="/register">회원가입</router-link>
    </p>
  </div>
</template>

<script>
import { authAPI } from '@/api/auth';

export default {
  name: 'Login',
  data() {
    return {
      username: '',
      password: '',
      loading: false,
      error: null
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true;
      this.error = null;
      
      try {
        await authAPI.login(this.username, this.password);
        
        // 로그인 성공 - 대시보드로 이동
        this.$router.push('/dashboard');
      } catch (error) {
        this.error = error.response?.data?.detail || '로그인에 실패했습니다.';
      } finally {
        this.loading = false;
      }
    },
    
    handleKakaoLogin() {
      window.location.href = 'http://localhost:8000/api/v1/auth/kakao';
    }
  }
}
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
}

.form-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  width: 100%;
  padding: 12px;
  margin-top: 10px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
}

button[type="submit"] {
  background-color: #007bff;
  color: white;
}

.kakao-btn {
  background-color: #FEE500;
  color: #000000;
}

.divider {
  text-align: center;
  margin: 20px 0;
  color: #999;
}

.error {
  color: red;
  margin-top: 10px;
}

.register-link {
  text-align: center;
  margin-top: 20px;
}
</style>
```

---

## 📊 AI 분석 API 연동

### AI 분석 함수

**`src/api/analysis.js`**:

```javascript
import apiClient from './client';

export const analysisAPI = {
  // AI 작성 확률 분석
  async analyzeText(title, content, textType = 'paper') {
    const response = await apiClient.post('/api/v1/analyze', {
      title,
      content,
      text_type: textType  // 'paper', 'essay', 'blog'
    });
    return response.data;
  },

  // 표절 검사
  async checkPlagiarism(content) {
    const response = await apiClient.post('/api/v1/plagiarism/check', {
      content,
      check_web: true,
      check_internal: false
    });
    return response.data;
  },

  // 문법 검사
  async checkGrammar(content) {
    const response = await apiClient.post('/api/v1/grammar/check', {
      content
    });
    return response.data;
  }
};
```

### AI 분석 페이지

**`src/views/Analysis.vue`**:

```vue
<template>
  <div class="analysis-container">
    <h2>AI 작성 확률 분석</h2>
    
    <form @submit.prevent="handleAnalyze">
      <div class="form-group">
        <label>제목</label>
        <input v-model="title" type="text" required />
      </div>
      
      <div class="form-group">
        <label>내용</label>
        <textarea v-model="content" rows="10" required></textarea>
      </div>
      
      <div class="form-group">
        <label>텍스트 유형</label>
        <select v-model="textType">
          <option value="paper">논문</option>
          <option value="essay">에세이</option>
          <option value="blog">블로그</option>
        </select>
      </div>
      
      <button type="submit" :disabled="loading">
        {{ loading ? '분석 중...' : '분석하기' }}
      </button>
    </form>
    
    <!-- 분석 결과 -->
    <div v-if="result" class="result">
      <h3>분석 결과</h3>
      
      <div class="probability">
        <h4>AI 작성 확률</h4>
        <div class="progress-bar">
          <div 
            class="progress" 
            :style="{ width: (result.ai_probability * 100) + '%' }"
          ></div>
        </div>
        <p>{{ (result.ai_probability * 100).toFixed(1) }}%</p>
      </div>
      
      <div class="details">
        <h4>세부 점수</h4>
        <ul>
          <li>KoBERT 점수: {{ (result.analysis_details.kobert_score * 100).toFixed(1) }}%</li>
          <li>SBERT 유사도: {{ (result.analysis_details.similarity_score * 100).toFixed(1) }}%</li>
          <li>Perplexity: {{ (result.analysis_details.perplexity_score * 100).toFixed(1) }}%</li>
          <li>Burstiness: {{ (result.analysis_details.burstiness_score * 100).toFixed(1) }}%</li>
        </ul>
      </div>
    </div>
    
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script>
import { analysisAPI } from '@/api/analysis';

export default {
  name: 'Analysis',
  data() {
    return {
      title: '',
      content: '',
      textType: 'paper',
      loading: false,
      result: null,
      error: null
    }
  },
  methods: {
    async handleAnalyze() {
      this.loading = true;
      this.error = null;
      this.result = null;
      
      try {
        this.result = await analysisAPI.analyzeText(
          this.title,
          this.content,
          this.textType
        );
      } catch (error) {
        this.error = error.response?.data?.detail || '분석에 실패했습니다.';
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
.analysis-container {
  max-width: 800px;
  margin: 50px auto;
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.result {
  margin-top: 30px;
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.probability {
  margin-bottom: 20px;
}

.progress-bar {
  width: 100%;
  height: 30px;
  background-color: #e0e0e0;
  border-radius: 15px;
  overflow: hidden;
  margin: 10px 0;
}

.progress {
  height: 100%;
  background: linear-gradient(to right, #4caf50, #ff9800, #f44336);
  transition: width 0.5s ease;
}

.details ul {
  list-style: none;
  padding: 0;
}

.details li {
  padding: 8px 0;
  border-bottom: 1px solid #ddd;
}

.error {
  color: red;
  margin-top: 20px;
}
</style>
```

---

## 🛡️ 라우트 가드 (인증 필요한 페이지)

**`src/router/index.js`**에 네비게이션 가드 추가:

```javascript
import { authAPI } from '@/api/auth';

// ... 라우트 정의 ...

// 전역 네비게이션 가드
router.beforeEach((to, from, next) => {
  const isAuthenticated = authAPI.isAuthenticated();
  
  // 인증이 필요한 페이지
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  
  if (requiresAuth && !isAuthenticated) {
    // 로그인 페이지로 리다이렉트
    next('/login');
  } else if (to.path === '/login' && isAuthenticated) {
    // 이미 로그인된 사용자는 대시보드로
    next('/dashboard');
  } else {
    next();
  }
});

export default router;
```

라우트에 메타 필드 추가:

```javascript
const routes = [
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }  // 인증 필요
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: Analysis,
    meta: { requiresAuth: true }  // 인증 필요
  }
]
```

---

## 🎯 환경변수 설정

**`.env.development`** (Vue 프로젝트 루트):

```env
VUE_APP_API_BASE_URL=http://localhost:8000
VUE_APP_FRONTEND_URL=http://localhost:8080
```

API 클라이언트에서 사용:

```javascript
const apiClient = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000',
  // ...
});
```

---

## ✅ 테스트 체크리스트

### 백엔드 테스트
- [ ] 서버 실행: `uvicorn main:app --reload`
- [ ] API 문서 확인: http://localhost:8000/docs
- [ ] 카카오 로그인 테스트: http://localhost:8000/api/v1/auth/kakao

### Vue 프론트엔드 테스트
- [ ] Vue 개발 서버 실행: `npm run serve`
- [ ] 카카오 로그인 버튼 클릭
- [ ] 카카오 로그인 후 콜백 처리
- [ ] JWT 토큰 localStorage 저장 확인
- [ ] 일반 로그인/회원가입 테스트
- [ ] AI 분석 API 호출 테스트

---

## 🐛 문제 해결

### CORS 오류
**증상**: "No 'Access-Control-Allow-Origin' header"

**해결**:
1. 백엔드 `main.py`의 `origins` 배열에 Vue 주소 확인
2. Vue 개발 서버 포트 확인 (기본 8080)
3. 백엔드 서버 재시작

### 401 Unauthorized
**증상**: API 호출 시 401 오류

**해결**:
1. localStorage에 토큰 저장 확인
2. Authorization 헤더 형식 확인: `Bearer <토큰>`
3. 토큰 만료 확인 (기본 60분)

### 카카오 로그인 실패
**증상**: "invalid_request" 오류

**해결**:
1. 카카오 개발자 콘솔에서 Redirect URI 확인
2. `.env` 파일의 `KAKAO_REST_API_KEY` 확인
3. `.env` 파일의 `KAKAO_REDIRECT_URI` 확인

---

## 📚 추가 자료

- **백엔드 API 문서**: http://localhost:8000/docs
- **Postman Collection**: `AI-killer.postman_collection.json`
- **카카오 Developers**: https://developers.kakao.com/

---

**🎉 Vue 프론트엔드 연동 준비 완료!**

모든 백엔드 API가 준비되었습니다. 이제 Vue에서 자유롭게 API를 호출하실 수 있습니다!
