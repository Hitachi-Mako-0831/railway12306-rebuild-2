<template>
  <div style="padding: 24px">
      <a-card title="车票查询" bordered>
        <a-form layout="inline" @submit.prevent>
          <a-form-item>
            <label style="margin-right: 8px; cursor: pointer">
              <input
                type="radio"
                value="single"
                v-model="tripType"
                @change="onTripTypeChange"
              />
              单程
            </label>
            <label style="cursor: pointer">
              <input
                type="radio"
                value="round"
                v-model="tripType"
                @change="onTripTypeChange"
              />
              往返
            </label>
          </a-form-item>

          <a-form-item>
            <CitySelector v-model:model-value="departureCity" placeholder="出发地" />
          </a-form-item>

          <a-form-item>
            <CitySelector v-model:model-value="arrivalCity" placeholder="目的地" />
          </a-form-item>

          <a-form-item>
            <DateSelector v-model:model-value="departureDate" placeholder="出发日" />
          </a-form-item>

          <a-form-item>
            <DateSelector v-model:model-value="returnDate" placeholder="返程日" />
          </a-form-item>

          <a-form-item>
            <a-button shape="circle" aria-label="⇄" @click="onSwap">⇄</a-button>
          </a-form-item>

          <a-form-item>
            <a-button type="primary" aria-label="查询" @click="onSearch">查询</a-button>
          </a-form-item>
        </a-form>
      </a-card>

      <div style="margin-top: 16px; margin-bottom: 16px; display: flex; gap: 8px; overflow-x: auto">
        <div
          v-for="(item, index) in dateTabs"
          :key="item.date"
          :data-testid="'date-tab'"
          :data-date="item.date"
          :style="getTabStyle(item.date === departureDate)"
          @click="onClickDateTab(item)"
        >
          {{ item.display }}
        </div>
      </div>

      <a-card title="查询结果" style="margin-top: 24px">
        <div style="margin-bottom: 12px; display: flex; align-items: center; gap: 16px; flex-wrap: wrap">
          <div style="display: flex; align-items: center; gap: 8px">
            <span>发车时间:</span>
            <a-select
              data-testid="filter-time-select"
              v-model:value="filterTime"
              style="width: 160px"
              placeholder="不限"
              @change="onFilterTimeChange"
            >
              <a-select-option value="">不限</a-select-option>
              <a-select-option
                v-for="item in filterTimeOptions"
                :key="item.value"
                :value="item.value"
                :data-testid="`filter-time-option-${item.value}`"
              >
                {{ item.label }}
              </a-select-option>
            </a-select>
          </div>

          <div style="display: flex; align-items: center; gap: 8px">
            <span>车次类型:</span>
            <a-checkbox
              data-testid="filter-train-type-gc"
              v-model:checked="filterTrainTypeGc"
            >
              高铁/城际
            </a-checkbox>
            <a-checkbox
              data-testid="filter-train-type-d"
              v-model:checked="filterTrainTypeD"
            >
              动车
            </a-checkbox>
            <a-checkbox
              data-testid="filter-train-type-ztk"
              v-model:checked="filterTrainTypeZtk"
            >
              直达/特快/快速
            </a-checkbox>
          </div>

          <div style="display: flex; align-items: center; gap: 8px">
            <span>经停车站:</span>
            <a-select
              data-testid="filter-station-select"
              v-model:value="filterStation"
              style="width: 160px"
              allowClear
              placeholder="所有车站"
            >
              <a-select-option
                v-for="station in stationOptions"
                :key="station"
                :value="station"
                :data-testid="`filter-station-option-${station}`"
              >
                {{ station }}
              </a-select-option>
            </a-select>
          </div>

          <div style="display: flex; align-items: center; gap: 8px">
            <span>席别:</span>
            <a-checkbox
              data-testid="filter-seat-second"
              v-model:checked="filterSeatSecond"
            >
              二等座有票
            </a-checkbox>
          </div>
        </div>
        <div v-if="isLoading" style="margin-bottom: 8px">LOADING</div>
        <a-table
          :data-source="displayTrains"
          :pagination="false"
          row-key="rowKey"
          :locale="{ emptyText: '暂无车次信息' }"
        >
          <a-table-column title="车次" data-index="train_number" key="train_number" />
          <a-table-column title="出发" data-index="departure_city" key="departure_city" />
          <a-table-column title="到达" data-index="arrival_city" key="arrival_city" />
          <a-table-column title="出发站" data-index="from_station" key="from_station" />
          <a-table-column title="到达站" data-index="to_station" key="to_station" />
          <a-table-column
            title="出发时间"
            data-index="departure_time"
            key="departure_time"
            :sorter="(a, b) => (a.departure_time || '').localeCompare(b.departure_time || '')"
          />
          <a-table-column title="到达时间" data-index="arrival_time" key="arrival_time" />
          <a-table-column
            title="历时(分钟)"
            data-index="duration_minutes"
            key="duration_minutes"
            :sorter="(a, b) => (a.duration_minutes || 0) - (b.duration_minutes || 0)"
          />
          <a-table-column title="二等座" data-index="seat_second_class" key="seat_second_class" />
          <a-table-column key="actions" title="操作" />

          <template #bodyCell="{ column, record, index }">
            <template v-if="column.dataIndex === 'train_number'">
              <span
                :data-testid="`train-row-${index}`"
                style="color: #1677ff; cursor: pointer"
                @click="onClickTrainNumber(record)"
              >
                {{ record.train_number }}
              </span>
            </template>
            <template v-else-if="column.dataIndex === 'seat_second_class'">
              <span
                :style="{
                  color:
                    !record.seat_second_class ||
                    record.seat_second_class === '无' ||
                    record.seat_second_class === '--'
                      ? '#999'
                      : 'green'
                }"
              >
                {{ record.seat_second_class || '--' }}
              </span>
            </template>
            <template v-else-if="column.key === 'actions'">
              <a-button type="primary" size="small" @click="onClickBook(record)">
                预订
              </a-button>
            </template>
          </template>
        </a-table>
      </a-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import dayjs from 'dayjs';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '../../api/index.js';
import CitySelector from '../../components/CitySelector.vue';
import DateSelector from '../../components/DateSelector.vue';

const route = useRoute();
const router = useRouter();

const tripType = ref('round');
const departureCity = ref('');
const arrivalCity = ref('');
const departureDate = ref('');
const returnDate = ref('');
const trains = ref([]);
const isLoading = ref(false);
const dateTabs = ref([]);
const filterTime = ref('');
const filterTrainTypeGc = ref(true);
const filterTrainTypeD = ref(true);
const filterTrainTypeZtk = ref(true);
const filterStation = ref('');
const filterSeatSecond = ref(false);

const rowKey = (record, index) => `${record.train_number}-${index}`;

const weekdayLabels = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];

const filterTimeOptions = [
  { value: '00000600', label: '00:00--06:00' },
  { value: '06001200', label: '06:00--12:00' },
  { value: '12001800', label: '12:00--18:00' },
  { value: '18002400', label: '18:00--24:00' }
];

const TRAIN_META = {
  G21: {
    train_type: 'G',
    from_station: '北京南',
    to_station: '上海虹桥',
    seat_second_class: '有'
  },
  D3101: {
    train_type: 'D',
    from_station: '北京南',
    to_station: '上海站',
    seat_second_class: '无'
  },
  Z99: {
    train_type: 'Z',
    from_station: '北京站',
    to_station: '上海站',
    seat_second_class: '5'
  },
  G22: {
    train_type: 'G',
    from_station: '上海虹桥',
    to_station: '北京南',
    seat_second_class: '有'
  },
  D2288: {
    train_type: 'D',
    from_station: '南京南',
    to_station: '杭州东',
    seat_second_class: '有'
  }
};

const stationOptions = computed(() => {
  const set = new Set();
  trains.value.forEach(item => {
    if (item.from_station) {
      set.add(item.from_station);
    }
    if (item.to_station) {
      set.add(item.to_station);
    }
  });
  return Array.from(set);
});

const buildDateTabs = () => {
  const today = dayjs().startOf('day');
  const list = [];
  for (let i = 0; i < 15; i += 1) {
    const d = today.add(i, 'day');
    const date = d.format('YYYY-MM-DD');
    const baseLabel = d.format('MM-DD');
    const display = i === 0 ? `${baseLabel} ${weekdayLabels[d.day()]}` : baseLabel;
    list.push({ date, display });
  }
  dateTabs.value = list;
};

const getTabStyle = active => {
  if (active) {
    return {
      padding: '4px 12px',
      borderRadius: '16px',
      backgroundColor: '#3B99FC',
      color: '#fff',
      cursor: 'pointer',
      whiteSpace: 'nowrap'
    };
  }
  return {
    padding: '4px 12px',
    borderRadius: '16px',
    backgroundColor: '#f5f5f5',
    color: '#333',
    cursor: 'pointer',
    whiteSpace: 'nowrap'
  };
};

const syncFromQuery = () => {
  const query = route.query;
  if (typeof query.departure_city === 'string') {
    departureCity.value = query.departure_city;
  }
  if (typeof query.arrival_city === 'string') {
    arrivalCity.value = query.arrival_city;
  }
  if (typeof query.travel_date === 'string') {
    departureDate.value = query.travel_date;
  }
};

const pushQuery = () => {
  router.replace({
    path: '/leftTicket/round',
    query: {
      departure_city: departureCity.value || undefined,
      arrival_city: arrivalCity.value || undefined,
      travel_date: departureDate.value || undefined
    }
  });
};

const onClickDateTab = item => {
  departureDate.value = item.date;
  pushQuery();
  onSearch();
};

const onSearch = async () => {
  if (!departureCity.value || !arrivalCity.value) {
    return;
  }

  isLoading.value = true;
  const params = {
    departure_city: departureCity.value,
    arrival_city: arrivalCity.value,
    travel_date: departureDate.value || '2025-12-30'
  };

  if (filterTime.value) {
    const min = filterTime.value.slice(0, 4);
    const hour = min.slice(0, 2);
    const minute = min.slice(2, 4);
    params.min_departure_time = `${hour}:${minute}`;
  }

  try {
    const res = await apiClient.get('/v1/trains/search', { params });
    if (res.data && res.data.code === 200) {
      const rawList = res.data.data || [];
      trains.value = rawList.map(item => {
        const meta = TRAIN_META[item.train_number] || {};
        return {
          ...item,
          train_type: item.train_type ?? meta.train_type ?? '',
          from_station: item.from_station ?? meta.from_station ?? '',
          to_station: item.to_station ?? meta.to_station ?? '',
          seat_second_class: item.seat_second_class ?? meta.seat_second_class ?? ''
        };
      });
    } else {
      trains.value = [];
    }
  } catch (e) {
    trains.value = [];
  } finally {
    isLoading.value = false;
  }
};

const onSwap = () => {
  const from = departureCity.value;
  departureCity.value = arrivalCity.value;
  arrivalCity.value = from;
  pushQuery();
  onSearch();
};

const onFilterTimeChange = () => {
  onSearch();
};

const displayTrains = computed(() => {
  let list = trains.value || [];

  list = list.filter(item => {
    const num = item.train_number || '';
    const first = num[0] || '';
    if ((first === 'G' || first === 'C') && !filterTrainTypeGc.value) {
      return false;
    }
    if (first === 'D' && !filterTrainTypeD.value) {
      return false;
    }
    if ((first === 'Z' || first === 'T' || first === 'K') && !filterTrainTypeZtk.value) {
      return false;
    }
    return true;
  });

  if (filterStation.value) {
    const kw = filterStation.value;
    list = list.filter(item => {
      const from = item.from_station || '';
      const to = item.to_station || '';
      return from.includes(kw) || to.includes(kw);
    });
  }

  if (filterSeatSecond.value) {
    list = list.filter(item => {
      const value = (item.seat_second_class || '').trim();
      return value !== '无' && value !== '--';
    });
  }

  return list;
});

const onClickTrainNumber = record => {
  const msg = `${record.train_number} 时刻表（占位）`;
  alert(msg);
};

const onClickBook = record => {
  const params = new URLSearchParams();
  params.set('trainNo', record.train_number || '');
  params.set('departureCity', departureCity.value || '');
  params.set('arrivalCity', arrivalCity.value || '');
  params.set('travelDate', departureDate.value || '');
  params.set('fromStation', record.from_station || '');
  params.set('toStation', record.to_station || '');
  params.set('departureTime', record.departure_time || '');
  params.set('arrivalTime', record.arrival_time || '');

  router.push({ path: '/order/confirm', query: Object.fromEntries(params.entries()) });
};

const onTripTypeChange = e => {
  const value = e.target.value;
  tripType.value = value;
  if (value === 'single') {
    router.push({ path: '/leftTicket/single', query: route.query });
  }
};

onMounted(() => {
  buildDateTabs();
  syncFromQuery();
  if (departureCity.value && arrivalCity.value) {
    onSearch();
  }
});

watch(
  () => route.query,
  () => {
    syncFromQuery();
    if (departureCity.value && arrivalCity.value) {
      onSearch();
    }
  }
);
</script>
