<template>
  <div class="mypage-container">
    <div v-if="isLoggedIn">
      <h2>마이페이지</h2>

      <div class="profile-box">
        <div class="row"><span class="label">이메일</span><span class="value">{{ user?.email }}</span></div>
        <div class="row"><span class="label">사용자명</span><span class="value">{{ user?.username }}</span></div>
        <div class="row"><span class="label">권한</span><span class="value">{{ user?.is_admin ? '관리자' : '일반 사용자' }}</span></div>
      </div>

      <section class="section">
        <h3>프로필 수정</h3>
        <div class="form-row">
          <label>새 사용자명</label>
          <input v-model="form.username" type="text" placeholder="표시할 사용자명" />
        </div>
        <button class="btn" :disabled="saving" @click="updateProfile">{{ saving ? '저장 중...' : '저장' }}</button>
      </section>

      <section class="section">
        <h3>비밀번호 변경</h3>
        <div class="form-row">
          <label>현재 비밀번호</label>
          <input v-model="password.current" type="password" placeholder="현재 비밀번호" />
        </div>
        <div class="form-row">
          <label>새 비밀번호</label>
          <input v-model="password.next" type="password" placeholder="새 비밀번호 (6~72자)" />
        </div>
        <button class="btn" :disabled="changing" @click="changePassword">{{ changing ? '변경 중...' : '비밀번호 변경' }}</button>
      </section>

      <section class="section danger">
        <h3>계정 관리</h3>
        <button class="btn outline" @click="logout">로그아웃</button>
        <button class="btn danger" @click="deleteAccount">회원 탈퇴</button>
      </section>
    </div>
    <div v-else>
      <p>로그인이 필요한 서비스입니다.</p>
    </div>
  </div>
  
</template>

<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import auth from '../store/auth.js';
import { authAPI } from '../services/api';

const router = useRouter();
const user = computed(() => auth.state.user);
const isLoggedIn = computed(() => auth.state.isLoggedIn);

const form = ref({ username: '' });
const saving = ref(false);
const password = ref({ current: '', next: '' });
const changing = ref(false);

const updateProfile = async () => {
  if (!form.value.username || form.value.username === user.value?.username) {
    alert('새 사용자명을 입력해주세요.');
    return;
  }
  saving.value = true;
  try {
    const res = await authAPI.updateMe({ username: form.value.username });
    // 상태 갱신
    await auth.initAuth();
    alert('프로필이 업데이트되었습니다.');
    form.value.username = '';
  } catch (e) {
    alert(e.response?.data?.detail || '프로필 업데이트에 실패했습니다.');
  } finally {
    saving.value = false;
  }
};

const changePassword = async () => {
  if (!password.value.current || !password.value.next) {
    alert('현재 비밀번호와 새 비밀번호를 입력해주세요.');
    return;
  }
  changing.value = true;
  try {
    await authAPI.changePassword({ current_password: password.value.current, new_password: password.value.next });
    alert('비밀번호가 변경되었습니다. 다시 로그인해주세요.');
    // 강제 로그아웃
    auth.clearUser();
    router.push('/login');
  } catch (e) {
    alert(e.response?.data?.detail || '비밀번호 변경에 실패했습니다.');
  } finally {
    changing.value = false;
  }
};

const logout = async () => {
  try { await authAPI.logout(); } catch {}
  auth.clearUser();
  router.push('/');
};

const deleteAccount = async () => {
  if (!confirm('정말 탈퇴하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) return;
  try {
    await authAPI.deleteMe();
    alert('회원 탈퇴가 완료되었습니다.');
    auth.clearUser();
    router.push('/');
  } catch (e) {
    alert(e.response?.data?.detail || '회원 탈퇴에 실패했습니다.');
  }
};
</script>

<style scoped>
.mypage-container {
  max-width: 720px;
  margin: 40px auto;
  padding: 28px;
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.08);
}
.profile-box { border: 1px solid #eee; border-radius: 8px; padding: 16px; margin-bottom: 20px; }
.row { display:flex; justify-content: space-between; padding: 6px 0; }
.label { color:#666; }
.value { font-weight:600; }
.section { margin-top: 22px; }
.section h3 { margin: 0 0 10px; }
.form-row { display:flex; flex-direction: column; gap:6px; margin-bottom: 12px; }
.form-row input { padding: 10px; border:1px solid #ddd; border-radius: 6px; }
.btn { padding: 10px 14px; background:#00C4CC; color:white; border:none; border-radius:6px; cursor:pointer; }
.btn.outline { background:white; color:#00C4CC; border:1px solid #00C4CC; margin-right:8px; }
.btn.danger { background:#dc3545; }
.section.danger { border-top:1px dashed #eee; padding-top: 16px; }
</style>