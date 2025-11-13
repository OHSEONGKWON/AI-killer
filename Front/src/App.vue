<template>
  <header>
    <div class="container">
      <router-link to="/" class="logo">Tech up</router-link>
      <nav>
        <ul>
          <template v-if="!auth.user.isLoggedIn">
            <li><router-link to="/login">로그인</router-link></li>
            <li><router-link to="/signup" class="btn-primary">회원가입</router-link></li>
          </template>
          <template v-else>
            <li><router-link to="/mypage">마이페이지</router-link></li>
            <li><button @click="logout" class="btn-secondary">로그아웃</button></li>
          </template>
        </ul>
      </nav>
    </div>
  </header>

  <div class="main-layout">
    <Sidebar />

    <main>
      <router-view/>
    </main>
  </div>
</template>

<script setup>
import auth from './store/auth.js';
import { useRouter } from 'vue-router';
// 3. Sidebar.vue를 스크립트에서 import 해야 합니다.
import Sidebar from './components/Sidebar.vue';

const router = useRouter();

const logout = () => {
  auth.clearUser();
  alert('로그아웃되었습니다.');
  router.push('/');
};
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Noto Sans KR', 'Pretendard', sans-serif;
  background-color: #F8F9FA;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

/* 헤더 스타일 */
header {
  background-color: #ffffff;
  border-bottom: 1px solid #E0E0E0;
  padding: 20px 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 90%;
  max-width: 1200px;
  margin: 0 auto;
}

.logo {
  font-size: 2em;
  color: #00C4CC;
  font-weight: 900;
  text-decoration: none;
}

nav ul {
  list-style: none;
  display: flex;
  gap: 25px;
  align-items: center;
}

nav a {
  text-decoration: none;
  color: #6C757D;
  font-weight: 500;
  transition: color 0.2s ease;
}

nav a:hover {
  color: #0056b3;
}

.btn-primary {
  background-color: #00C4CC;
  color: #FFFFFF;
  padding: 10px 18px;
  border-radius: 8px;
  font-weight: bold;
  text-decoration: none;
  transition: background-color 0.2s ease;
}

.btn-primary:hover {
  background-color: #009999;
}

.btn-secondary {
  background-color: #6C757D;
  color: #FFFFFF;
  padding: 10px 18px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

/* 메인 레이아웃 */
.main-layout {
  display: flex;
  height: calc(100vh - 81px);
}

main {
  flex-grow: 1;
  padding: 40px;
  overflow-y: auto;
  background-color: #F8F9FA;
}
</style>