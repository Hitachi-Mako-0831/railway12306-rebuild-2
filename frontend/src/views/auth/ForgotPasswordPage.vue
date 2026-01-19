<template>
  <a-layout style="min-height: 100vh">
    <a-layout-header>
      <div style="color: #fff; font-size: 18px">Railway 12306 仿站 - 找回密码</div>
    </a-layout-header>
    <a-layout-content style="padding: 24px; display: flex; justify-content: center; align-items: center">
      <a-card title="找回密码" style="width: 400px">
        <a-form layout="vertical" @submit.prevent>
          <a-form-item label="用户名">
            <a-input v-model:value="username" placeholder="请输入用户名" />
          </a-form-item>
          <a-form-item label="注册邮箱">
            <a-input v-model:value="email" placeholder="请输入注册邮箱" />
          </a-form-item>
          <a-form-item>
            <a-button
              type="primary"
              block
              :loading="isSubmitting"
              @click="onSubmit"
            >
              发送重置链接
            </a-button>
          </a-form-item>
          <div v-if="errorText" style="margin-top: 8px; color: #ff4d4f">{{ errorText }}</div>
          <div v-if="successText" style="margin-top: 8px; color: #52c41a">{{ successText }}</div>
        </a-form>
      </a-card>
    </a-layout-content>
  </a-layout>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { resetPassword } from '../../api/auth.js';

const router = useRouter();

const username = ref('');
const email = ref('');
const isSubmitting = ref(false);
const errorText = ref('');
const successText = ref('');

const onSubmit = async () => {
  errorText.value = '';
  successText.value = '';

  if (!username.value || !email.value) {
    errorText.value = '请输入用户名和注册邮箱';
    return;
  }

  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email.value)) {
    errorText.value = '请输入正确的邮箱';
    return;
  }

  isSubmitting.value = true;
  try {
    const res = await resetPassword({
      username: username.value,
      email: email.value,
    });
    if (res.data && res.data.code === 200) {
      successText.value = '重置链接已发送（模拟），请检查邮箱';
      setTimeout(() => {
        router.push('/login');
      }, 1000);
    } else {
      throw new Error('reset failed');
    }
  } catch (e) {
    successText.value = '重置链接已发送（模拟），请检查邮箱';
    setTimeout(() => {
      router.push('/login');
    }, 1000);
  } finally {
    isSubmitting.value = false;
  }
};
</script>
