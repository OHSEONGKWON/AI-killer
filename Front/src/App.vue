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
/* 기존 #app, body, header 등의 스타일은 그대로 둡니다. */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
/* ... (기존 스타일 생략) ... */


/* ▼▼▼ 이 CSS가 사이드바와 메인 영역을 나란히 배치합니다! ▼▼▼ */
.main-layout {
  display: flex; /* 자식 요소(Sidebar, main)를 가로로 나란히 배치 */
  /* 전체 화면 높이에서 헤더 높이(약 81px)를 뺀 만큼을 차지하도록 설정 */
  height: calc(100vh - 81px);
}

main {
  flex-grow: 1; /* main 영역이 사이드바를 제외한 남은 공간을 모두 차지하도록 설정 */
  padding: 40px;
  overflow-y: auto; /* 내용이 길어지면 main 영역만 스크롤되도록 설정 */
}

</style>