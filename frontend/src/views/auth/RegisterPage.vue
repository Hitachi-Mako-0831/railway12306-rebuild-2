<template>
  <a-layout style="min-height: 100vh">
    <a-layout-header>
      <div style="color: #fff; font-size: 18px">Railway 12306 仿站 - 注册</div>
    </a-layout-header>
    <a-layout-content style="padding: 24px; display: flex; justify-content: center">
      <a-card title="用户注册" style="width: 600px">
        <a-form layout="vertical" @submit.prevent>
          <a-form-item label="用户名">
            <a-input v-model:value="username" placeholder="请输入用户名" />
            <div v-if="usernameError" style="color: #ff4d4f; margin-top: 4px">{{ usernameError }}</div>
          </a-form-item>

          <a-form-item label="密码">
            <a-input-password v-model:value="password" placeholder="请输入密码" />
            <div style="margin-top: 4px">
              <div>密码强度: {{ passwordStrengthLabel }}</div>
              <div v-if="passwordError" style="color: #ff4d4f; margin-top: 2px">{{ passwordError }}</div>
            </div>
          </a-form-item>

          <a-form-item label="确认密码">
            <a-input-password v-model:value="confirmPassword" placeholder="请再次输入密码" />
            <div v-if="confirmError" style="color: #ff4d4f; margin-top: 4px">{{ confirmError }}</div>
          </a-form-item>

          <a-form-item label="邮箱">
            <a-input v-model:value="email" placeholder="请输入邮箱" />
            <div v-if="emailError" style="color: #ff4d4f; margin-top: 4px">{{ emailError }}</div>
          </a-form-item>

          <a-form-item>
            <a-checkbox v-model:checked="accepted">
              我已阅读并同意《用户服务条款》和《隐私政策》
            </a-checkbox>
            <div v-if="acceptError" style="color: #ff4d4f; margin-top: 4px">{{ acceptError }}</div>
          </a-form-item>

          <a-form-item>
            <a-button type="primary" aria-label="下一步" :loading="isSubmitting" @click="onSubmit">
              下一步
            </a-button>
          </a-form-item>

          <div v-if="submitError" style="color: #ff4d4f; margin-top: 8px">{{ submitError }}</div>
        </a-form>
      </a-card>
    </a-layout-content>
  </a-layout>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { register } from '../../api/auth.js';

const router = useRouter();

const username = ref('');
const password = ref('');
const confirmPassword = ref('');
const email = ref('');
const accepted = ref(false);

const usernameError = ref('');
const passwordError = ref('');
const confirmError = ref('');
const emailError = ref('');
const acceptError = ref('');
const submitError = ref('');
const isSubmitting = ref(false);

const passwordStrengthLabel = computed(() => {
  if (!password.value) return '弱';
  const hasLetter = /[A-Za-z]/.test(password.value);
  const hasDigit = /[0-9]/.test(password.value);
  if (hasLetter && hasDigit && password.value.length >= 10) return '很强';
  if (hasLetter && hasDigit) return '中';
  return '弱';
});

const validateFields = () => {
  usernameError.value = '';
  passwordError.value = '';
  confirmError.value = '';
  emailError.value = '';
  acceptError.value = '';
  submitError.value = '';

  if (!username.value) {
    usernameError.value = '用户名为必填项';
  } else {
    const u = username.value;
    const ok =
      u.length >= 6 &&
      u.length <= 30 &&
      /^[A-Za-z][A-Za-z0-9_]*$/.test(u);
    if (!ok) {
      usernameError.value = '用户名格式错误';
    }
  }

  if (!password.value) {
    passwordError.value = '密码为必填项';
  } else {
    const hasLetter = /[A-Za-z]/.test(password.value);
    const hasDigit = /[0-9]/.test(password.value);
    if (!(hasLetter && hasDigit)) {
      passwordError.value = '密码必须包含字母和数字';
    }
  }

  if (!confirmPassword.value) {
    confirmError.value = '请再次输入密码';
  } else if (confirmPassword.value !== password.value) {
    confirmError.value = '两次输入密码不一致';
  }

  if (!email.value) {
    emailError.value = '邮箱为必填项';
  } else if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email.value)) {
    emailError.value = '请输入正确的邮箱';
  }

  if (!accepted.value) {
    acceptError.value = '请先阅读并同意条款';
  }

  return !(
    usernameError.value ||
    passwordError.value ||
    confirmError.value ||
    emailError.value ||
    acceptError.value
  );
};

const onSubmit = async () => {
  if (!validateFields()) {
    return;
  }

  isSubmitting.value = true;
  submitError.value = '';
  router.push('/login');
  try {
    const res = await register({
      username: username.value,
      password: password.value,
      confirm_password: confirmPassword.value,
      email: email.value,
    });
    if (!(res.data && res.data.code === 200)) {
      submitError.value = res.data?.message || '注册失败';
    }
  } catch (e) {
    submitError.value = '注册失败';
  } finally {
    isSubmitting.value = false;
  }
};
</script>
