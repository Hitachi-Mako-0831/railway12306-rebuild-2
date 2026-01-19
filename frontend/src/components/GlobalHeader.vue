<template>
  <a-layout-header class="header">
    <div class="logo">Railway 12306 仿站</div>
    <a-menu
      v-model:selectedKeys="selectedKeys"
      theme="dark"
      mode="horizontal"
      :style="{ lineHeight: '64px' }"
    >
      <a-menu-item key="home">
        <router-link to="/">首页</router-link>
      </a-menu-item>
      <a-menu-item key="ticket">
        <router-link to="/leftTicket/single">车票查询</router-link>
      </a-menu-item>
      <a-menu-item key="orders">
        <router-link to="/user/orders">我的订单</router-link>
      </a-menu-item>
    </a-menu>
    <div class="user-actions">
        <!-- Placeholder for user login status -->
        <router-link to="/login" v-if="!isLoggedIn">登录/注册</router-link>
        <span v-else>欢迎, {{ username }}</span>
    </div>
  </a-layout-header>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import { useRoute } from 'vue-router';
// import { useUserStore } from '@/stores/user'; // Assuming user store exists

const route = useRoute();
const selectedKeys = ref(['home']);

// Simple mock for now, can integrate with Pinia store later
const isLoggedIn = ref(true); // Default to true for testing UI
const username = ref('User');

watch(
  () => route.path,
  (newPath) => {
    if (newPath === '/') {
      selectedKeys.value = ['home'];
    } else if (newPath.startsWith('/leftTicket')) {
      selectedKeys.value = ['ticket'];
    } else if (newPath.startsWith('/user/orders') || newPath.startsWith('/order')) {
      selectedKeys.value = ['orders'];
    }
  },
  { immediate: true }
);
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
}

.logo {
  float: left;
  width: 200px;
  height: 31px;
  color: white;
  font-size: 18px;
  font-weight: bold;
  line-height: 31px; /* Align with header height if needed, or flex handles it */
}

.user-actions {
    color: white;
}
</style>
