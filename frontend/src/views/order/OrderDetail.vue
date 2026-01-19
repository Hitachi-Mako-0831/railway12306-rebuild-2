<template>
  <a-layout style="min-height: 100vh">
    <a-layout-header>
       <div style="color: #fff; font-size: 18px">
         <a-button type="link" @click="router.back()" style="color: #fff"> &lt; 返回</a-button>
         订单详情
       </div>
    </a-layout-header>
    <a-layout-content style="padding: 24px">
      <div v-if="loading">加载中...</div>
      <div v-else-if="!order">订单不存在</div>
      <div v-else>
         <!-- Status Bar -->
         <a-card class="order-status" style="margin-bottom: 24px">
            <a-result :status="statusMap[order.status]?.icon || 'info'" :title="statusMap[order.status]?.text || order.status">
                <template #extra>
                    <div class="order-no">订单号: {{ order.id }}</div>
                    <a-button type="primary" v-if="order.status === 'pending'" @click="goToPay">去支付</a-button>
                    <a-button danger v-if="['pending', 'paid'].includes(order.status)" @click="cancelOrder">取消订单</a-button>
                </template>
            </a-result>
         </a-card>
         
         <!-- Train Info -->
         <a-card title="车次信息" style="margin-bottom: 24px" class="train-info">
            <a-descriptions bordered>
                <a-descriptions-item label="车次">{{ trainInfo?.train_number }}</a-descriptions-item>
                <a-descriptions-item label="日期">{{ order.departure_date }}</a-descriptions-item>
                <a-descriptions-item label="出发站">{{ trainInfo?.from_station?.name }}</a-descriptions-item>
                <a-descriptions-item label="到达站">{{ trainInfo?.to_station?.name }}</a-descriptions-item>
                <a-descriptions-item label="出发时间">{{ trainInfo?.departure_time }}</a-descriptions-item>
                <a-descriptions-item label="到达时间">{{ trainInfo?.arrival_time }}</a-descriptions-item>
            </a-descriptions>
         </a-card>

         <!-- Passenger List -->
         <a-card title="乘客信息" style="margin-bottom: 24px">
            <a-table :dataSource="order.items" :columns="columns" pagination="false" rowKey="id" class="passenger-table">
                <template #bodyCell="{ column, record }">
                    <template v-if="column.key === 'seat_type'">
                        {{ seatTypeMap[record.seat_type] || record.seat_type }}
                    </template>
                </template>
            </a-table>
         </a-card>
         
         <!-- Price -->
         <a-card style="text-align: right">
            <span class="total-price" style="font-size: 20px; color: red">总价: ¥{{ order.total_price }}</span>
         </a-card>
      </div>
    </a-layout-content>
  </a-layout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { message } from 'ant-design-vue';

const route = useRoute();
const router = useRouter();
const orderId = route.params.id;

const order = ref(null);
const loading = ref(false);

const columns = [
  { title: '姓名', dataIndex: 'passenger_name', key: 'name' },
  { title: '证件号', dataIndex: 'passenger_id_card', key: 'id_card' },
  { title: '席别', dataIndex: 'seat_type', key: 'seat_type' },
  { title: '票价', dataIndex: 'price', key: 'price' },
  { title: '状态', dataIndex: 'status', key: 'status' },
];

const statusMap = {
    pending: { text: '待支付', icon: 'warning' },
    paid: { text: '已支付', icon: 'success' },
    cancelled: { text: '已取消', icon: 'error' },
    refunded: { text: '已退票', icon: 'info' }
};

const seatTypeMap = {
    first_class: '一等座',
    second_class: '二等座',
    business_class: '商务座',
    no_seat: '无座',
    hard_seat: '硬座',
    hard_sleeper: '硬卧',
    soft_sleeper: '软卧'
};

const trainInfo = computed(() => {
    // If backend returns 'train' (schema update), use it.
    // If backend returns 'train_info' (test mock), use it.
    return order.value?.train || order.value?.train_info; 
});

const fetchOrder = async () => {
    loading.value = true;
    try {
        const res = await fetch(`http://localhost:8000/api/v1/orders/${orderId}`);
        if (res.ok) {
            order.value = await res.json();
        } else {
            message.error('获取订单失败');
        }
    } catch (e) {
        message.error('网络错误');
    } finally {
        loading.value = false;
    }
};

const goToPay = () => {
    router.push(`/order/pay/${orderId}`);
};

const cancelOrder = () => {
    message.info('暂未实现取消功能');
};

onMounted(() => {
    fetchOrder();
});
</script>
