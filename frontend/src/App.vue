<template>
  <a-layout style="min-height: 100vh">
    <GlobalHeader />
    <a-layout-content>
      <router-view />
    </a-layout-content>
  </a-layout>
</template>

<script setup>
import GlobalHeader from './components/GlobalHeader.vue';
</script>

<style>
html,
body,
#app {
  margin: 0;
  padding: 0;
  height: 100%;
}
</style>

