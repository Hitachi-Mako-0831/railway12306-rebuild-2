<template>
  <a-layout style="min-height: 100vh">
    <a-layout-header>
      <div style="color: #fff; font-size: 18px">Railway 12306 仿站 - 订单确认</div>
    </a-layout-header>
    <a-layout-content style="padding: 24px">
      <a-card title="订单确认占位页" bordered>
        <p>车次号: {{ trainNo }}</p>
        <p>出发城市: {{ departureCity }}</p>
        <p>到达城市: {{ arrivalCity }}</p>
        <p>出发日期: {{ travelDate }}</p>
        <p>出发站: {{ fromStation }}</p>
        <p>到达站: {{ toStation }}</p>
      </a-card>
    </a-layout-content>
  </a-layout>
</template>

<script setup>
import { useRoute } from 'vue-router';

const route = useRoute();

const trainNo = route.query.trainNo || '';
const departureCity = route.query.departureCity || '';
const arrivalCity = route.query.arrivalCity || '';
const travelDate = route.query.travelDate || '';
const fromStation = route.query.fromStation || '';
const toStation = route.query.toStation || '';
</script>

