<template>
  <div class="mypage-container">
    <div v-if="auth.user.isLoggedIn">
      <h1>마이페이지</h1>
      <p>환영합니다, **{{ auth.user.user.email }}** 님!</p>
      <p>이곳에서 회원 정보를 확인하거나 수정할 수 있습니다.</p>
    </div>
    <div v-else>
      <p>로그인이 필요한 서비스입니다.</p>
    </div>
  </div>
</template>

<script setup>
import auth from '../store/auth.js'; // ◀️ 중앙 저장소에서 사용자 정보를 가져옵니다.
</script>

<style scoped>
.mypage-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 40px;
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.08);
  text-align: center;
}
</style>