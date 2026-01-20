<template>
  <div class="order-page">
    <div style="margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center">
        <h1>我的订单</h1>
        <a-button @click="fetchOrders">刷新</a-button>
    </div>
    
    <a-table 
        :dataSource="orders" 
        :columns="columns" 
        :loading="loading" 
        rowKey="id"
        :pagination="false"
    >
        <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'status'">
                <a-tag :color="getStatusColor(record.status)">
                    {{ getStatusText(record.status) }}
                </a-tag>
            </template>
            <template v-if="column.key === 'total_price'">
                <span style="color: red">¥{{ record.total_price }}</span>
            </template>
            <template v-if="column.key === 'action'">
                <a-space>
                    <a-button type="link" @click="router.push(`/order/detail/${record.id}`)">详情</a-button>
                    <a-button type="link" v-if="record.status === 'pending'" @click="router.push(`/order/pay/${record.id}`)">去支付</a-button>
                </a-space>
            </template>
        </template>
    </a-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import apiClient from '../../api/index.js';

const router = useRouter();
const orders = ref([]);
const loading = ref(false);

const columns = [
  { title: '订单号', dataIndex: 'id', key: 'id' },
  { title: '车次', dataIndex: 'train_id', key: 'train_id' }, // Ideally join with train info or store train_number
  { title: '出发日期', dataIndex: 'departure_date', key: 'departure_date' },
  { title: '总价', dataIndex: 'total_price', key: 'total_price' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at' },
  { title: '操作', key: 'action' },
];

const getStatusColor = (status) => {
    switch(status) {
        case 'pending': return 'orange';
        case 'paid': return 'green';
        case 'cancelled': return 'grey';
        case 'refunded': return 'blue';
        default: return 'default';
    }
};

const getStatusText = (status) => {
    const map = {
        'pending': '待支付',
        'paid': '已支付',
        'cancelled': '已取消',
        'refunded': '已退款',
        'completed': '已完成'
    };
    return map[status] || status;
};

const fetchOrders = async () => {
    loading.value = true;
    try {
        // Try apiClient first
        const res = await apiClient.get('/v1/orders/');
        orders.value = res.data;
    } catch (e) {
        console.error(e);
        // Fallback to direct URL if apiClient base/proxy is wrong (just in case)
        try {
            const res = await fetch('http://localhost:8000/api/v1/orders/');
            if (res.ok) {
                orders.value = await res.json();
            } else {
                 message.error('获取订单列表失败');
            }
        } catch (e2) {
            message.error('网络错误');
        }
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    fetchOrders();
});
</script>

<style scoped>
.order-page {
  padding: 24px;
}
</style>
