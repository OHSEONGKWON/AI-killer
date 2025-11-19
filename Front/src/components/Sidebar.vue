<template>
  <aside class="sidebar">
    <nav>
      <h3>기본 기능</h3>
      <ul>
        <li><router-link to="/">홈</router-link></li>
      </ul> 
      <br>
      <ul>
      <li><router-link to="/ai-detector">AI 텍스트 분석</router-link></li>
      </ul> 
      <br> 
      <ul>
      <li><router-link to="/plagiarism-check">표절 검사기</router-link></li>
      </ul>
      <br>
      <ul>
      <li><router-link to="/grammar-check">문법 검사기</router-link></li>
      </ul> 
    </nav>
  </aside>
</template>

<script setup>
// 이 컴포넌트는 링크만 보여주므로 스크립트는 비워둡니다.
</script>

<style scoped>
.sidebar {
  width: 240px; /* 사이드바 너비 */
  background-color: #f8f9fa; /* 배경색 */
  border-right: 1px solid #e0e0e0; /* 오른쪽 경계선 */
  padding: 20px;
  flex-shrink: 0; /* 화면이 줄어들어도 너비가 줄어들지 않도록 설정 */
}

h3 {
  margin-top: 0;
  color: #333;
  font-size: 1.2em;
  padding-bottom: 10px;
  border-bottom: 1px solid #e0e0e0;
}

/* 두 번째 h3(AI 기능)에 위쪽 여백을 주어 단을 시각적으로 구분합니다. */
h3.menu-divider {
  margin-top: 25px; 
}

ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

li a {
  display: block;
  padding: 12px 15px;
  color: #495057;
  text-decoration: none;
  border-radius: 8px;
  transition: background-color 0.2s ease, color 0.2s ease;
}

li a:hover {
  background-color: #e9ecef;
  color: #007bff;
}

/* 현재 활성화된 라우트 링크에 적용될 스타일 */
li a.router-link-exact-active {
  background-color: #00C4CC;
  color: white;
  font-weight: bold;
}
</style>