<template>
  <a-layout-header style="display: flex; justify-content: space-between; align-items: center">
    <div style="color: #fff; font-size: 18px; cursor: pointer" @click="goHome">
      Railway 12306 仿站
    </div>
    <div style="color: #fff; display: flex; gap: 16px; align-items: center">
      <template v-if="isAuthenticated">
        <span>欢迎，{{ username }}</span>
        <a-dropdown trigger="hover">
          <a class="ant-dropdown-link" style="color: #fff" @click.prevent>
            我的12306
          </a>
          <template #overlay>
            <a-menu>
              <a-menu-item key="orders">火车票订单</a-menu-item>
              <a-menu-item key="my-tickets">本人车票</a-menu-item>
              <a-menu-item key="my-food">我的餐饮</a-menu-item>
              <a-menu-item key="my-insurance">我的保险</a-menu-item>
              <a-menu-item key="profile" @click="goProfile">个人中心</a-menu-item>
              <a-menu-item key="security">账户安全</a-menu-item>
              <a-menu-divider />
              <a-menu-item key="logout" @click="handleLogout">退出登录</a-menu-item>
            </a-menu>
          </template>
        </a-dropdown>
      </template>
      <template v-else>
        <a @click.prevent="goLogin" style="color: #fff">登录</a>
        <a @click.prevent="goRegister" style="color: #fff">注册</a>
      </template>
    </div>
  </a-layout-header>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { logout } from '../api/auth.js';
import { useUserStore } from '../stores/user.js';

const router = useRouter();
const userStore = useUserStore();

const isAuthenticated = computed(() => userStore.isAuthenticated);
const username = computed(() => userStore.username);

const goHome = () => {
  router.push('/');
};

const goLogin = () => {
  router.push('/login');
};

const goRegister = () => {
  router.push('/register');
};

const goProfile = () => {
  router.push('/profile');
};

const handleLogout = async () => {
  try {
    await logout();
  } catch (e) {}
  userStore.clearAuth();
  router.push('/');
};
</script>
