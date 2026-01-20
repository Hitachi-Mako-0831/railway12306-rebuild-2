<template>
  <div style="padding: 24px">
      <!-- 1. Train Info -->
      <a-card title="列车信息" bordered class="train-info" style="margin-bottom: 24px">
        <a-descriptions bordered>
          <a-descriptions-item label="车次">{{ trainNo }}</a-descriptions-item>
          <a-descriptions-item label="日期">{{ travelDate }}</a-descriptions-item>
          <a-descriptions-item label="出发站">{{ fromStation }}</a-descriptions-item>
          <a-descriptions-item label="到达站">{{ toStation }}</a-descriptions-item>
          <a-descriptions-item label="出发时间">{{ departureTime }}</a-descriptions-item>
          <a-descriptions-item label="到达时间">{{ arrivalTime }}</a-descriptions-item>
        </a-descriptions>
      </a-card>

      <!-- 2. Passenger Selection -->
      <a-card title="乘客选择" bordered style="margin-bottom: 24px">
        <div v-if="loadingPassengers">加载联系人中...</div>
        <div v-else>
          <a-checkbox-group v-model:value="selectedPassengerIds" @change="handlePassengerChange">
            <a-row>
              <a-col :span="8" v-for="p in passengers" :key="p.id">
                <a-checkbox :value="p.id" class="passenger-item">{{ p.name }} ({{ p.type }})</a-checkbox>
              </a-col>
            </a-row>
          </a-checkbox-group>
        </div>
      </a-card>

      <!-- 3. Ticket/Seat Selection (Dynamic Rows) -->
      <a-card title="选座与票种" bordered style="margin-bottom: 24px" v-if="selectedPassengers.length > 0">
        <a-table :dataSource="selectedPassengers" :columns="columns" pagination="false" rowKey="id" class="ticket-row">
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'seatType'">
              <a-select v-model:value="record.seatType" style="width: 120px" @change="updatePrice(record)">
                <a-select-option value="second_class">二等座</a-select-option>
                <a-select-option value="first_class">一等座</a-select-option>
              </a-select>
            </template>
            <template v-if="column.key === 'ticketType'">
               <a-select v-model:value="record.ticketType" style="width: 120px">
                <a-select-option value="adult">成人票</a-select-option>
                <a-select-option value="child">儿童票</a-select-option>
              </a-select>
            </template>
            <template v-if="column.key === 'price'">
              <span style="color: orange">¥{{ record.price }}</span>
            </template>
          </template>
        </a-table>
      </a-card>

      <!-- 4. Submit Bar -->
      <div style="text-align: right; background: #fff; padding: 16px; border: 1px solid #f0f0f0">
         <span style="margin-right: 16px">总票价: <span style="color: red; font-size: 20px">¥{{ totalPrice }}</span></span>
         <a-button type="primary" size="large" @click="submitOrder" :loading="submitting">提交订单</a-button>
      </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import apiClient from '../../api/index.js';

const route = useRoute();
const router = useRouter();

// Query Params
const trainId = route.query.trainId;
const trainNo = route.query.trainNo;
const travelDate = route.query.travelDate;
const fromStation = route.query.fromStation;
const toStation = route.query.toStation;
const departureTime = route.query.departureTime;
const arrivalTime = route.query.arrivalTime;

// State
const passengers = ref([]);
const loadingPassengers = ref(false);
const selectedPassengerIds = ref([]);
const selectedPassengers = ref([]);
const submitting = ref(false);

const columns = [
  { title: '姓名', dataIndex: 'name', key: 'name' },
  { title: '证件号', dataIndex: 'id_card', key: 'id_card' },
  { title: '席别', key: 'seatType' },
  { title: '票种', key: 'ticketType' },
  { title: '票价', key: 'price' },
];

const fetchPassengers = async () => {
  loadingPassengers.value = true;
  try {
    const res = await apiClient.get('/v1/passengers/');
    passengers.value = Array.isArray(res.data) ? res.data : [];
  } catch (e) {
    passengers.value = [];
  } finally {
    loadingPassengers.value = false;
  }
};

onMounted(() => {
  fetchPassengers();
});

const handlePassengerChange = () => {
  // Sync selectedPassengerIds -> selectedPassengers
  // Preserve existing selections (seatType etc) if possible
  const newSelection = [];
  selectedPassengerIds.value.forEach(id => {
    const p = passengers.value.find(p => p.id === id);
    if (p) {
        // Check if already in selectedPassengers to keep settings
        const existing = selectedPassengers.value.find(sp => sp.id === id);
        if (existing) {
            newSelection.push(existing);
        } else {
            newSelection.push({
                ...p,
                seatType: 'second_class',
                ticketType: 'adult',
                price: 100 // Mock price
            });
        }
    }
  });
  selectedPassengers.value = newSelection;
};

const updatePrice = (record) => {
    // Mock price logic
    if (record.seatType === 'first_class') record.price = 200;
    else record.price = 100;
};

const totalPrice = computed(() => {
    return selectedPassengers.value.reduce((sum, p) => sum + p.price, 0);
});

const submitOrder = async () => {
    if (selectedPassengers.value.length === 0) {
        message.error('请至少选择一位乘客');
        return;
    }
    
    submitting.value = true;
    try {
        const payload = {
            train_id: parseInt(trainId) || 1,
            departure_date: travelDate,
            total_price: totalPrice.value,
            items: selectedPassengers.value.map(p => ({
                passenger_name: p.name,
                passenger_id_card: p.id_card,
                seat_type: p.seatType,
                price: p.price
            }))
        };

        const res = await apiClient.post('/v1/orders/', payload);
        const data = res.data;
        if (data && data.id) {
            message.success('订单提交成功');
            router.push(`/order/pay/${data.id}`);
        } else {
            message.error('提交失败');
        }
    } catch (e) {
        const status = e && e.response && e.response.status;
        const rawUser = typeof window !== 'undefined' ? window.localStorage.getItem('user') : null;
        if (status === 401 || !rawUser) {
            message.error('请先登录后再提交订单');
        } else if (e && e.response && e.response.data && e.response.data.detail) {
            const detail = e.response.data.detail;
            let msg = '';
            if (typeof detail === 'string') {
                msg = detail;
            } else if (Array.isArray(detail) && detail.length > 0) {
                const first = detail[0];
                if (typeof first === 'string') {
                    msg = first;
                } else if (first && typeof first === 'object') {
                    msg = first.msg || first.message || '';
                }
            } else if (detail && typeof detail === 'object') {
                msg = detail.msg || detail.message || '';
            }
            if (!msg) {
                msg = '请求失败，请稍后重试';
            }
            message.error(msg);
        } else {
            message.error('网络错误');
        }
    } finally {
        submitting.value = false;
    }
};

</script>

<style scoped>
.train-info {
    background: #f0f2f5;
}
.ticket-row {
    /* Marker class for test */
}
</style>
