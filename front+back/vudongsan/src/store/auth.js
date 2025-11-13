import { reactive, readonly } from 'vue';

// 앱 전체에서 공유될 사용자 상태
const state = reactive({
  user: null, // 로그인하지 않았을 때는 null
  isLoggedIn: false,
});

// 로그인 시 호출할 함수
const setUser = (userData) => {
  state.user = userData;
  state.isLoggedIn = true;
};

// 로그아웃 시 호출할 함수
const clearUser = () => {
  state.user = null;
  state.isLoggedIn = false;
};

// 외부에서는 user와 isLoggedIn을 읽기만 가능하도록 설정 (실수 방지)
// setUser와 clearUser 함수를 통해서만 상태를 변경할 수 있음
export default {
  user: readonly(state),
  setUser,
  clearUser,
};