<template>
  <div class="signup-container">
    <h2>회원가입</h2>
    <form @submit.prevent="submitForm">
      <div class="form-group">
        <label for="email">이메일</label>
        <input type="email" id="email" v-model="email" placeholder="이메일을 입력하세요" required>
      </div>
      <div class="form-group">
        <label for="password">비밀번호</label>
        <input type="password" id="password" v-model="password" placeholder="비밀번호를 입력하세요" required>
      </div>
      <div class="form-group">
        <label for="password-confirm">비밀번호 확인</label>
        <input type="password" id="password-confirm" v-model="passwordConfirm" placeholder="비밀번호를 다시 입력하세요" required>
      </div>
      <button type="submit" class="btn-primary">가입하기</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const email = ref('');
const password = ref('');
const passwordConfirm = ref('');
const router = useRouter();

const submitForm = async () => {
  if (password.value !== passwordConfirm.value) {
    alert('비밀번호가 일치하지 않습니다.');
    return;
  }

  try {
    const response = await axios.post('http://localhost:3000/api/register', {
      email: email.value,
      password: password.value,
    });

    alert('회원가입에 성공했습니다!');
    router.push('/'); 

  } catch (error) {
    if (error.response) {
      alert(`회원가입 실패: ${error.response.data.error}`);
    } else {
      alert('서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인하세요.');
    }
    console.error('회원가입 실패:', error);
  }
};
</script>

<style scoped>
/* 회원가입 폼 전용 스타일 */
.signup-container {
  width: 90%;
  max-width: 500px;
  margin: 40px auto;
  padding: 40px;
  background-color: #FFFFFF;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.08);
}

h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #495057;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ced4da;
  border-radius: 8px;
  font-size: 1em;
}

.btn-primary {
  width: 100%;
  padding: 15px;
  border: none;
  border-radius: 8px;
  background-color: #00C4CC;
  color: white;
  font-size: 1.1em;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.btn-primary:hover {
  background-color: #009999;
}
</style>