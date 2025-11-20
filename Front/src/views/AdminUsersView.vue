<template>
  <div>
    <h2>관리자: 사용자 관리</h2>

    <section class="filters">
      <input v-model="filters.q" type="text" placeholder="이름/이메일 검색" />
      <select v-model="filters.active">
        <option :value="''">상태: 전체</option>
        <option :value="'true'">활성</option>
        <option :value="'false'">비활성</option>
      </select>
      <select v-model="filters.is_admin">
        <option :value="''">권한: 전체</option>
        <option :value="'true'">관리자</option>
        <option :value="'false'">일반</option>
      </select>
      <button class="btn" @click="loadUsers">검색</button>
    </section>

    <table class="users">
      <thead>
        <tr>
          <th>ID</th>
          <th>Username</th>
          <th>Email</th>
          <th>Admin</th>
          <th>Active</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="u in users" :key="u.id">
          <td>{{ u.id }}</td>
          <td>
            <template v-if="editRow === u.id">
              <input v-model="editForm.username" />
            </template>
            <template v-else>{{ u.username }}</template>
          </td>
          <td>
            <template v-if="editRow === u.id">
              <input v-model="editForm.email" />
            </template>
            <template v-else>{{ u.email }}</template>
          </td>
          <td>
            <template v-if="editRow === u.id">
              <select v-model="editForm.is_admin">
                <option :value="true">true</option>
                <option :value="false">false</option>
              </select>
            </template>
            <template v-else>
              <span :class="['badge', u.is_admin ? 'green' : 'gray']">{{ u.is_admin }}</span>
            </template>
          </td>
          <td>
            <template v-if="editRow === u.id">
              <select v-model="editForm.active">
                <option :value="true">true</option>
                <option :value="false">false</option>
              </select>
            </template>
            <template v-else>
              <span :class="['badge', u.active ? 'green' : 'red']">{{ u.active ? 'active' : 'inactive' }}</span>
            </template>
          </td>
          <td class="actions">
            <template v-if="editRow === u.id">
              <button class="btn" @click="saveEdit(u)">저장</button>
              <button class="btn secondary" @click="cancelEdit">취소</button>
            </template>
            <template v-else>
              <button class="btn" @click="startEdit(u)">수정</button>
              <button class="btn warn" @click="doToggleStatus(u)">{{ u.active ? '비활성화' : '활성화' }}</button>
              <button class="btn secondary" @click="doResetPassword(u)">임시 비밀번호</button>
            </template>
          </td>
        </tr>
      </tbody>
    </table>

    <div class="pagination">
      <button class="btn" :disabled="page === 1" @click="page--; loadUsers()">이전</button>
      <span>{{ page }}</span>
      <button class="btn" :disabled="users.length < limit" @click="page++; loadUsers()">다음</button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { adminAPI } from '../services/api';
import auth from '../store/auth';
import { useRouter } from 'vue-router';

const router = useRouter();

const users = ref([]);
const page = ref(1);
const limit = 20;
const filters = reactive({ q: '', active: '', is_admin: '' });

const editRow = ref(null);
const editForm = reactive({ username: '', email: '', is_admin: false, active: true });

const loadUsers = async () => {
  // 관리자만 접근 가능
  if (!auth.state.user?.is_admin) {
    alert('관리자만 접근 가능합니다.');
    router.push('/');
    return;
  }
  const params = {
    skip: (page.value - 1) * limit,
    limit,
  };
  if (filters.q) params.q = filters.q;
  if (filters.active !== '') params.active = filters.active === 'true';
  if (filters.is_admin !== '') params.is_admin = filters.is_admin === 'true';

  const { data } = await adminAPI.listUsers(params);
  users.value = data;
};

const startEdit = (u) => {
  editRow.value = u.id;
  editForm.username = u.username;
  editForm.email = u.email;
  editForm.is_admin = !!u.is_admin;
  editForm.active = !!u.active;
};

const cancelEdit = () => {
  editRow.value = null;
};

const saveEdit = async (u) => {
  try {
    const payload = {
      username: editForm.username,
      email: editForm.email,
      is_admin: editForm.is_admin,
      active: editForm.active,
    };
    const { data } = await adminAPI.updateUser(u.id, payload);
    // 업데이트 반영
    const idx = users.value.findIndex(x => x.id === u.id);
    if (idx !== -1) users.value[idx] = data;
    editRow.value = null;
  } catch (e) {
    const msg = e?.response?.data?.detail || '업데이트 실패';
    alert(msg);
  }
};

const doResetPassword = async (u) => {
  if (!confirm(`[${u.username}] 임시 비밀번호를 발급할까요?`)) return;
  const { data } = await adminAPI.resetPassword(u.id);
  alert(`임시 비밀번호: ${data.temporary_password}`);
};

const doToggleStatus = async (u) => {
  const { data } = await adminAPI.toggleStatus(u.id);
  const idx = users.value.findIndex(x => x.id === u.id);
  if (idx !== -1) users.value[idx] = data;
};

onMounted(() => {
  loadUsers();
});
</script>

<style scoped>
.filters { display:flex; gap:10px; margin-bottom:15px; }
.users { width:100%; border-collapse: collapse; background:#fff; }
.users th, .users td { border:1px solid #e5e5e5; padding:10px; text-align:left; }
.badge { padding:3px 8px; border-radius:8px; font-size:12px; }
.badge.green { background:#e6ffed; color:#18794e; }
.badge.red { background:#ffecec; color:#c92a2a; }
.badge.gray { background:#f1f3f5; color:#495057; }
.actions .btn { margin-right:6px; }
.btn { background:#00C4CC; color:#fff; border:none; padding:8px 12px; border-radius:6px; cursor:pointer; }
.btn.secondary { background:#6C757D; }
.btn.warn { background:#ff6b6b; }
.pagination { margin-top:12px; display:flex; align-items:center; gap:10px; }
</style>
