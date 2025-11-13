import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import SignUpView from '../views/SignUpView.vue';
import Login from '../views/Login.vue';
import MyPageView from '../views/MyPageView.vue';
import AiDetectorView from '../views/AiDetectorView.vue';
import GrammerCheckView from '../views/GrammerCheckView.vue';
const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/signup',
    name: 'signup',
    component: SignUpView
  },
  {
    path: '/login',
    name: 'login',
    component: Login  
  },
  { 
    path: '/mypage',
    name: 'mypage',
    component: MyPageView
  },

  {
    path: '/Ai-detector', // 사이드바의 to="/ai-detector"와 일치
    name: 'Ai-detector',
    component: AiDetectorView 
  },

{
    path: '/grammar-check', // 사이드바의 to="/grammar-check"와 일치
    name: 'grammar-check',
    component: GrammerCheckView
  }
];

const router = createRouter({
  history: createWebHistory(), // ◀️ 괄호 안을 비워주세요.
  routes
});

export default router;