import axios from 'axios';

// Axios 인스턴스: Vue devServer의 proxy('/api' -> FastAPI) 활용
const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
