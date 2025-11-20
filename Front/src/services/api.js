import axios from 'axios';

// Axios 인스턴스: Vue devServer의 proxy('/api' -> FastAPI) 활용
const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터: 모든 요청에 JWT 토큰 자동 추가
api.interceptors.request.use(
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

// 응답 인터셉터: 401 에러 시 자동 로그아웃
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 토큰 만료 또는 무효화
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API 메서드들
export const authAPI = {
  // 회원가입
  register: (userData) => api.post('/auth/register', userData),
  
  // 로그인 (Form 데이터)
  login: (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    return api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
  },
  
  // 로그아웃
  logout: () => api.post('/auth/logout'),
  
  // 현재 사용자 정보 조회
  getCurrentUser: () => api.get('/users/me'),

  // 내 정보 수정 (username 등)
  updateMe: (data) => api.patch('/users/me', data),

  // 비밀번호 변경
  changePassword: (data) => api.put('/users/me/password', data),

  // 회원 탈퇴
  deleteMe: () => api.delete('/users/me'),
};

export const analysisAPI = {
  // 텍스트 분석
  analyze: (data) => api.post('/analyze', data),
};

export const grammarAPI = {
  // 문법 검사
  check: (data) => api.post('/grammar/check', data),
};

export const plagiarismAPI = {
  // 표절/유사도 검사
  check: (data) => api.post('/plagiarism/check', data),
};

export default api;

// 관리자 API
export const adminAPI = {
  listUsers: (params) => api.get('/admin/users', { params }),
  updateUser: (id, data) => api.patch(`/admin/users/${id}`, data),
  resetPassword: (id) => api.post(`/admin/users/${id}/reset-password`),
  toggleStatus: (id, active = null) => {
    // active가 null이면 토글, 값이 있으면 지정
    const data = active === null ? null : { active };
    return api.patch(`/admin/users/${id}/status`, data);
  },
};
