<template>
  <a-layout style="min-height: 100vh">
    <a-layout-header>
      <div style="color: #fff; font-size: 18px; cursor: pointer" @click="$router.push('/')">Railway 12306 仿站</div>
    </a-layout-header>
    <a-layout>
      <a-layout-sider width="200" style="background: #fff">
        <a-menu
          mode="inline"
          :selectedKeys="selectedKeys"
          :style="{ height: '100%', borderRight: 0 }"
          @click="handleMenuClick"
        >
          <a-menu-item key="profile">个人中心</a-menu-item>
          <a-menu-item key="passengers">常用联系人</a-menu-item>
          <a-menu-item key="orders">我的订单</a-menu-item>
        </a-menu>
      </a-layout-sider>
      <a-layout style="padding: 0 24px 24px">
        <a-breadcrumb style="margin: 16px 0">
          <a-breadcrumb-item>首页</a-breadcrumb-item>
          <a-breadcrumb-item>个人中心</a-breadcrumb-item>
          <a-breadcrumb-item>{{ currentPageTitle }}</a-breadcrumb-item>
        </a-breadcrumb>
        <a-layout-content
          :style="{ background: '#fff', padding: '24px', margin: 0, minHeight: '280px' }"
        >
          <router-view></router-view>
        </a-layout-content>
      </a-layout>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

const selectedKeys = ref(['passengers']);

const currentPageTitle = computed(() => {
  switch (selectedKeys.value[0]) {
    case 'profile': return '个人中心';
    case 'passengers': return '常用联系人';
    case 'orders': return '我的订单';
    default: return '';
  }
});

watch(
  () => route.path,
  (val) => {
    if (val.includes('/user/passengers')) {
      selectedKeys.value = ['passengers'];
    } else if (val.includes('/user/orders')) {
      selectedKeys.value = ['orders'];
    } else if (val.includes('/user/profile')) {
      selectedKeys.value = ['profile'];
    }
  },
  { immediate: true }
);

const handleMenuClick = ({ key }) => {
  if (key === 'passengers') {
    router.push('/user/passengers');
  } else if (key === 'orders') {
    // router.push('/user/orders'); // Not implemented yet
    message.info('功能开发中');
  } else if (key === 'profile') {
    // router.push('/user/profile'); // Not implemented yet
    message.info('功能开发中');
  }
};
</script>
