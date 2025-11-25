import { createRouter, createWebHistory } from 'vue-router';
import SignUpView from '../views/SignUpView.vue';
import Login from '../views/Login.vue';
import MyPageView from '../views/MyPageView.vue';
import GrammarCheckView from '../views/GrammarCheckView.vue';
import PlagiarismCheckView from '../views/PlagiarismCheckView.vue';
import AuthCallback from '../views/AuthCallback.vue';
import AdminUsersView from '../views/AdminUsersView.vue';
import SimilarityCheckView from '../views/SimilarityCheckView.vue';
const routes = [
  { path: '/', redirect: '/similarity' },
  { path: '/auth/callback', name: 'auth-callback', component: AuthCallback },
  { path: '/signup', name: 'signup', component: SignUpView },
  { path: '/login', name: 'login', component: Login },
  { path: '/mypage', name: 'mypage', component: MyPageView },
  { path: '/plagiarism-check', name: 'plagiarism-check', component: PlagiarismCheckView },
  { path: '/similarity', name: 'similarity-check', component: SimilarityCheckView },
  { path: '/grammar-check', name: 'grammar-check', component: GrammarCheckView },
  { path: '/admin/users', name: 'admin-users', component: AdminUsersView },
];

const router = createRouter({
  history: createWebHistory(), // ◀️ 괄호 안을 비워주세요.
  routes
});

export default router;