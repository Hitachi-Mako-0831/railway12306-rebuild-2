<template>
  <div style="display: flex; justify-content: center; align-items: center; padding: 50px 0;">
         <a-result
            status="success"
            title="支付成功"
            sub-title="您的订单已支付成功，祝您旅途愉快！"
            class="success-message"
          >
            <template #extra>
              <a-button key="console" type="primary" @click="router.push('/user/orders')">查看订单</a-button>
              <a-button key="buy" @click="router.push('/')">继续购票</a-button>
            </template>
          </a-result>
  </div>
</template>
<script setup>
import { useRouter } from 'vue-router';
const router = useRouter();
</script>
