<template>
  <a-layout style="min-height: 100vh">
    <a-layout-header>
       <div style="color: #fff; font-size: 18px">订单支付</div>
    </a-layout-header>
    <a-layout-content style="padding: 24px">
      <div v-if="loading">加载中...</div>
      <div v-else-if="!order">订单不存在</div>
      <div v-else>
         <a-card style="margin-bottom: 24px; text-align: center">
             <div style="margin-bottom: 16px">
                 <span style="font-size: 16px">订单提交成功，请您尽快支付！</span>
             </div>
             <div style="font-size: 24px; color: red; margin-bottom: 16px">
                 <span class="pay-amount">¥{{ order.total_price }}</span>
             </div>
             <div class="countdown" style="font-size: 16px; color: #faad14">
                 请在 {{ countdown }} 内完成支付
             </div>
         </a-card>

         <a-card title="支付方式" style="margin-bottom: 24px">
             <a-radio-group v-model:value="paymentMethod" style="width: 100%">
                 <a-radio value="alipay" style="display: block; margin-bottom: 10px">支付宝</a-radio>
                 <a-radio value="wechat" style="display: block">微信支付</a-radio>
             </a-radio-group>
         </a-card>

         <div style="text-align: center">
             <a-button type="primary" size="large" @click="handlePay" :loading="paying">立即支付</a-button>
         </div>
      </div>
    </a-layout-content>
  </a-layout>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import dayjs from 'dayjs';

const route = useRoute();
const router = useRouter();
const orderId = route.params.id;

const order = ref(null);
const loading = ref(false);
const paying = ref(false);
const paymentMethod = ref('alipay');
const countdown = ref('--:--');
let timer = null;

const fetchOrder = async () => {
    loading.value = true;
    try {
        const res = await fetch(`http://localhost:8000/api/v1/orders/${orderId}`);
        if (res.ok) {
            order.value = await res.json();
            startCountdown();
        } else {
            message.error('获取订单失败');
        }
    } catch (e) {
        message.error('网络错误');
    } finally {
        loading.value = false;
    }
};

const startCountdown = () => {
    if (!order.value) return;
    const expiresAt = dayjs(order.value.expires_at);
    
    timer = setInterval(() => {
        const now = dayjs();
        const diff = expiresAt.diff(now, 'second');
        if (diff <= 0) {
            countdown.value = '00:00';
            clearInterval(timer);
            // message.error('订单已超时'); // Optional: don't spam
        } else {
            const m = Math.floor(diff / 60);
            const s = diff % 60;
            countdown.value = `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
        }
    }, 1000);
};

const handlePay = async () => {
    paying.value = true;
    try {
        const res = await fetch(`http://localhost:8000/api/v1/orders/${orderId}/pay`, {
            method: 'POST'
        });
        if (res.ok) {
            message.success('支付成功');
            router.push(`/order/success?orderId=${orderId}`);
        } else {
            const data = await res.json();
            message.error(data.detail || '支付失败');
        }
    } catch (e) {
        message.error('网络错误');
    } finally {
        paying.value = false;
    }
};

onMounted(() => {
    fetchOrder();
});

onUnmounted(() => {
    if (timer) clearInterval(timer);
});
</script>
