<template>
  <a-layout style="min-height: 100vh">
    <Header12306 />
    <a-layout-content
      style="padding: 24px; display: flex; justify-content: center; align-items: flex-start; background: #f0f2f5;"
    >
      <div style="width: 100%; max-width: 1200px;">
        <div
          style="height: 300px; background: linear-gradient(135deg, #1890ff 0%, #36cfc9 100%); display: flex; align-items: center; justify-content: center; color: white; margin-bottom: -60px; border-radius: 4px; position: relative; z-index: 0;"
        >
          <div style="text-align: center">
            <h1 style="color: white; font-size: 48px; margin-bottom: 10px;">12306 创新服务</h1>
            <p style="font-size: 20px;">随时随地，便捷出行</p>
          </div>
        </div>

        <div
          style="display: flex; align-items: center; justify-content: space-between; margin-top: 24px; margin-bottom: 16px;"
        >
          <div style="font-size: 18px; font-weight: bold;">Railway 12306 仿站</div>
          <div>
            <a-button type="link" @click="router.push('/')">首页</a-button>
            <a-button type="link" @click="router.push('/leftTicket/single')">车票</a-button>
            <a-button type="primary" @click="router.push('/user/passengers')">个人中心</a-button>
          </div>
        </div>

        <a-card
          title="车票查询"
          :bordered="false"
          style="width: 100%; box-shadow: 0 4px 12px rgba(0,0,0,0.1); position: relative; z-index: 1; border-radius: 8px;"
        >
          <a-form layout="vertical">
            <a-row :gutter="24">
              <a-col :span="24">
                <a-radio-group v-model:value="tripType" style="margin-bottom: 16px;">
                  <a-radio value="single">单程</a-radio>
                  <a-radio value="round">往返</a-radio>
                </a-radio-group>
              </a-col>
            </a-row>

            <a-row :gutter="24" align="middle">
              <a-col :span="6">
                <a-form-item label="出发地">
                  <CitySelector v-model:model-value="departureCity" placeholder="出发地" />
                </a-form-item>
              </a-col>
              <a-col :span="2" style="text-align: center; padding-top: 10px;">
                <a-button shape="circle" @click="onSwap">⇄</a-button>
              </a-col>
              <a-col :span="6">
                <a-form-item label="目的地">
                  <CitySelector v-model:model-value="arrivalCity" placeholder="目的地" />
                </a-form-item>
              </a-col>
              <a-col :span="5">
                <a-form-item label="出发日">
                  <DateSelector v-model:model-value="departureDate" placeholder="出发日" />
                </a-form-item>
              </a-col>
              <a-col :span="5" v-if="tripType === 'round'">
                <a-form-item label="返程日">
                  <DateSelector v-model:model-value="returnDate" placeholder="返程日" />
                </a-form-item>
              </a-col>
            </a-row>

            <a-row>
              <a-col :span="24" style="text-align: right;">
                <a-button
                  type="primary"
                  size="large"
                  @click="onSearch"
                  style="width: 160px; height: 48px; font-size: 18px;"
                >
                  查询车票
                </a-button>
              </a-col>
            </a-row>
          </a-form>
        </a-card>

        <a-row :gutter="24" style="margin-top: 32px;">
          <a-col :span="8">
            <a-card hoverable @click="router.push('/user/passengers')" style="text-align: center">
              <template #cover>
                <div
                  style="height: 60px; background: #e6f7ff; display: flex; align-items: center; justify-content: center; font-size: 24px;"
                >
                  👤
                </div>
              </template>
              <a-card-meta title="常用联系人" description="管理您的乘车人信息"> </a-card-meta>
            </a-card>
          </a-col>
          <a-col :span="8">
            <a-card hoverable style="text-align: center">
              <template #cover>
                <div
                  style="height: 60px; background: #fff1b8; display: flex; align-items: center; justify-content: center; font-size: 24px;"
                >
                  🎫
                </div>
              </template>
              <a-card-meta title="我的订单" description="查看待支付与已完成订单"> </a-card-meta>
            </a-card>
          </a-col>
          <a-col :span="8">
            <a-card hoverable style="text-align: center">
              <template #cover>
                <div
                  style="height: 60px; background: #d9f7be; display: flex; align-items: center; justify-content: center; font-size: 24px;"
                >
                  💎
                </div>
              </template>
              <a-card-meta title="会员服务" description="会员积分与等级权益"> </a-card-meta>
            </a-card>
          </a-col>
        </a-row>
      </div>
    </a-layout-content>
    <a-layout-footer
      style="text-align: center; background: #001529; color: rgba(255, 255, 255, 0.65);"
    >
      Railway 12306 Rebuild ©2026 Created by Caleb | 仅供学习交流使用
    </a-layout-footer>
  </a-layout>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import dayjs from 'dayjs';
import Header12306 from '../components/Header12306.vue';
import CitySelector from '../components/CitySelector.vue';
import DateSelector from '../components/DateSelector.vue';

const router = useRouter();

const tripType = ref('single');
const departureCity = ref('北京');
const arrivalCity = ref('上海');
const departureDate = ref(dayjs().add(1, 'day').format('YYYY-MM-DD'));
const returnDate = ref('');

const onSwap = () => {
  const temp = departureCity.value;
  departureCity.value = arrivalCity.value;
  arrivalCity.value = temp;
};

const onSearch = () => {
  const query = {
    departure_city: departureCity.value,
    arrival_city: arrivalCity.value,
    travel_date: departureDate.value,
  };

  if (tripType.value === 'single') {
    router.push({ path: '/leftTicket/single', query });
  } else {
    if (returnDate.value) {
      query.return_date = returnDate.value;
    }
    router.push({ path: '/leftTicket/round', query });
  }
};
</script>
