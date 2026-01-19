<template>
  <a-layout style="min-height: 100vh">
    <a-layout-header>
      <div style="color: #fff; font-size: 18px">Railway 12306 仿站</div>
    </a-layout-header>
    <a-layout-content style="padding: 24px">
      <a-card title="首页" bordered>
        <p>前端：Vue 3 + Vite + Ant Design Vue</p>
        <p>后端：FastAPI + PostgreSQL</p>
        <div style="margin-top: 20px;">
          <a-button type="primary" @click="$router.push('/user/passengers')">进入个人中心 (乘客管理)</a-button>
        </div>
      </a-card>
    </a-layout-content>
  </a-layout>
</template>

<script setup>
</script>

