<template>
  <a-layout style="min-height: 100vh">
    <Header12306 />
    <a-layout-content style="padding: 24px; display: flex; justify-content: center; align-items: center">
      <a-card title="账号登录" style="width: 400px">
        <a-form layout="vertical" @submit.prevent>
          <a-form-item label="用户名/邮箱/手机号">
            <a-input v-model:value="username" placeholder="用户名/邮箱/手机号" />
          </a-form-item>
          <a-form-item label="密码">
            <a-input-password v-model:value="password" placeholder="密码" />
          </a-form-item>
          <a-form-item>
            <a-button
              type="primary"
              block
              aria-label="登录"
              :loading="isSubmitting"
              @click="onSubmit"
            >
              登录
            </a-button>
          </a-form-item>
          <div style="display: flex; justify-content: space-between; font-size: 12px">
            <a href="javascript:void(0)" @click.prevent="goRegister">注册12306账号</a>
            <a href="javascript:void(0)" @click.prevent="goForgotPassword">忘记密码</a>
          </div>
          <div v-if="errorText" style="margin-top: 8px; color: #ff4d4f">{{ errorText }}</div>
        </a-form>
      </a-card>
    </a-layout-content>
  </a-layout>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { login } from '../../api/auth.js';
import { getProfile } from '../../api/user.js';
import { useUserStore } from '../../stores/user.js';
import Header12306 from '../../components/Header12306.vue';

const router = useRouter();
const userStore = useUserStore();

const username = ref('');
const password = ref('');
const isSubmitting = ref(false);
const errorText = ref('');

const goRegister = () => {
  router.push('/register');
};

const goForgotPassword = () => {
  router.push('/forgot-password');
};

const onSubmit = async () => {
  if (!username.value || !password.value) {
    errorText.value = '请输入用户名/邮箱/手机号和密码';
    return;
  }

  isSubmitting.value = true;
  errorText.value = '';
  try {
    const res = await login({ username: username.value, password: password.value });
    if (res.data && res.data.code === 200 && res.data.data) {
      const token = res.data.data.access_token;
      userStore.setAuth(token, username.value);
      try {
        const profileRes = await getProfile();
        if (
          profileRes.data &&
          profileRes.data.code === 200 &&
          profileRes.data.data &&
          profileRes.data.data.username
        ) {
          userStore.setAuth(token, profileRes.data.data.username);
        }
      } catch (e) {}
      router.push('/');
      return;
    }
  } catch (e) {
  } finally {
    isSubmitting.value = false;
  }

  userStore.clearAuth();
  errorText.value = '登录失败';
};
</script>
