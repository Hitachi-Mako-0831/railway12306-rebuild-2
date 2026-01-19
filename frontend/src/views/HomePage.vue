<template>
  <a-layout style="min-height: 100vh">
    <Header12306 />
    <a-layout-content style="padding: 24px">
      <a-card title="首页" bordered>
        <p>前端：Vue 3 + Vite + Ant Design Vue</p>
        <p>后端：FastAPI + PostgreSQL</p>
      </a-card>
    </a-layout-content>
  </a-layout>
</template>

<script setup>
import Header12306 from '../components/Header12306.vue';
</script>
