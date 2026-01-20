<template>
  <div style="padding: 24px">
     <div style="margin-bottom: 16px">
         <a-button type="link" @click="router.back()"> &lt; 返回</a-button>
         <span style="font-size: 18px; font-weight: bold;">订单详情</span>
       </div>
      <div v-if="loading">加载中...</div>
      <div v-else-if="!order">订单不存在</div>
      <div v-else>
         <!-- Status Bar -->
         <a-card class="order-status" style="margin-bottom: 24px">
            <a-result :status="statusMap[order.status]?.icon || 'info'" :title="statusMap[order.status]?.text || order.status">
                <template #extra>
                    <div class="order-no">订单号: {{ order.id }}</div>
                    <a-button type="primary" v-if="order.status === 'pending'" @click="goToPay">去支付</a-button>
                    <a-button v-if="['paid', 'partial_refunded'].includes(order.status)" @click="showRefundModal">退票</a-button>
                    <a-button danger v-if="['pending', 'paid'].includes(order.status)" @click="showCancelModal">取消订单</a-button>
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
            <a-table :dataSource="order.items" :columns="columns" :pagination="false" rowKey="id" class="passenger-table">
                <template #bodyCell="{ column, record }">
                    <template v-if="column.key === 'seat_type'">
                        {{ seatTypeMap[record.seat_type] || record.seat_type }}
                    </template>
                    <template v-if="column.key === 'status'">
                        {{ statusMap[record.status]?.text || record.status }}
                    </template>
                </template>
            </a-table>
         </a-card>
         
         <!-- Price -->
         <a-card style="text-align: right">
            <span class="total-price" style="font-size: 20px; color: red">总价: ¥{{ order.total_price }}</span>
         </a-card>

         <a-modal
            v-model:open="cancelModalVisible"
            title="确认取消订单?"
            @ok="confirmCancel"
            okText="确定"
            cancelText="取消"
         >
            <p>取消后座位将不予保留。</p>
         </a-modal>

         <a-modal
            v-model:open="refundModalVisible"
            title="申请退票"
            @ok="confirmRefund"
            class="refund-modal"
            okText="确认退票"
            cancelText="取消"
         >
            <p>请选择需要退票的乘客：</p>
            <a-checkbox-group v-model:value="refundSelection" style="width: 100%">
                <div v-for="item in refundableItems" :key="item.id" style="margin-bottom: 8px">
                    <a-checkbox :value="item.id">
                        {{ item.passenger_name }} ({{ seatTypeMap[item.seat_type] || item.seat_type }}) - ¥{{ item.price }}
                    </a-checkbox>
                </div>
            </a-checkbox-group>
         </a-modal>
      </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import apiClient from '../../api/index.js';

const route = useRoute();
const router = useRouter();
const orderId = route.params.id;

const order = ref(null);
const loading = ref(false);
const cancelModalVisible = ref(false);
const refundModalVisible = ref(false);
const refundSelection = ref([]);

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
    refunded: { text: '已退票', icon: 'info' },
    partial_refunded: { text: '部分退票', icon: 'info' }
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

const refundableItems = computed(() => {
    return order.value?.items.filter(item => item.status !== 'refunded') || [];
});

const fetchOrder = async () => {
    loading.value = true;
    try {
        const res = await apiClient.get(`/v1/orders/${orderId}`);
        order.value = res.data;
    } catch (e) {
        order.value = null;
        message.error('获取订单失败');
    } finally {
        loading.value = false;
    }
};

const goToPay = () => {
    router.push(`/order/pay/${orderId}`);
};

const showCancelModal = () => {
    console.log('showCancelModal called');
    cancelModalVisible.value = true;
};

const confirmCancel = async () => {
    cancelModalVisible.value = false;
    try {
        const res = await apiClient.post(`/v1/orders/${orderId}/cancel`);
        const data = res.data;
        if (data) {
            order.value = data;
        } else if (order.value) {
            order.value.status = 'cancelled';
        }
        message.success('订单已取消');
    } catch (e) {
        message.error('网络错误');
    }
};

const showRefundModal = () => {
    refundSelection.value = [];
    refundModalVisible.value = true;
};

const confirmRefund = async () => {
    if (refundSelection.value.length === 0) {
        message.warn('请至少选择一张车票');
        return;
    }
    refundModalVisible.value = false;
    try {
        await apiClient.post(`/v1/orders/${orderId}/refund`, {
            order_item_ids: refundSelection.value,
        });
        message.success('退票成功');
        fetchOrder();
    } catch (e) {
        message.error('网络错误');
    }
};

const cancelOrder = () => {
    // Deprecated in favor of showCancelModal, but keeping if button calls this
    showCancelModal();
};

onMounted(() => {
    fetchOrder();
});
</script>
