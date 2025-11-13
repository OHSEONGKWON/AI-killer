import { createApp } from 'vue';
import App from './App.vue';
import router from './router'; // './router/index.js' 파일을 불러옵니다.

// 1. 앱을 **한 번만** 생성합니다.
const app = createApp(App);

// 2. 생성된 앱에 우리가 만든 라우터 설정을 등록합니다.
app.use(router);

// 3. 모든 설정이 끝난 앱을 화면에 연결합니다.
app.mount('#app');