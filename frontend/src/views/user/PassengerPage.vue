<template>
  <div class="user-layout">
    <div class="sidebar">
      <a-menu mode="inline" :selectedKeys="['passengers']">
        <a-menu-item key="profile">个人中心</a-menu-item>
        <a-menu-item key="passengers">常用联系人</a-menu-item>
        <a-menu-item key="orders">我的订单</a-menu-item>
      </a-menu>
    </div>
    <div class="content">
      <div class="header">
        <h2>常用联系人</h2>
        <a-button type="primary" @click="showAddModal">添加</a-button>
      </div>
      
      <div class="filter">
        <a-input-search
          v-model:value="searchText"
          placeholder="输入乘客姓名搜索"
          style="width: 200px"
          @search="onSearch"
        />
      </div>

      <a-table :columns="columns" :data-source="filteredPassengers" :loading="loading" row-key="id">
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'type'">
            {{ getPassengerTypeLabel(record.type) }}
          </template>
          <template v-if="column.key === 'id_type'">
            {{ getIdTypeLabel(record.id_type) }}
          </template>
          <template v-if="column.key === 'verify_status'">
            <span :style="{ color: record.verify_status === 1 ? 'green' : 'orange' }">
              {{ record.verify_status === 1 ? '已通过' : '待核验' }}
            </span>
          </template>
          <template v-if="column.key === 'action'">
            <a-space>
              <a @click="editPassenger(record)">编辑</a>
              <a-popconfirm 
                v-if="!record.is_default"
                title="确定删除吗?" 
                @confirm="removePassenger(record.id)"
              >
                <a style="color: red">删除</a>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>

      <a-modal
        v-model:open="modalVisible"
        :title="isEdit ? '编辑乘客' : '添加乘客'"
        @ok="handleModalOk"
      >
        <a-form :model="formState" :label-col="{ span: 6 }" :wrapper-col="{ span: 16 }">
          <a-form-item label="姓名" required>
            <a-input v-model:value="formState.name" placeholder="请输入姓名" />
          </a-form-item>
          <a-form-item label="证件类型" required>
            <a-select v-model:value="formState.id_type">
              <a-select-option :value="0">身份证</a-select-option>
              <a-select-option :value="1">护照</a-select-option>
              <a-select-option :value="2">台胞证</a-select-option>
              <a-select-option :value="3">港澳通行证</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item label="证件号码" required>
            <a-input v-model:value="formState.id_card" placeholder="请输入证件号码" />
          </a-form-item>
          <a-form-item label="旅客类型">
            <a-select v-model:value="formState.type">
              <a-select-option :value="0">成人</a-select-option>
              <a-select-option :value="1">学生</a-select-option>
              <a-select-option :value="2">儿童</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item label="手机号" required>
            <a-input v-model:value="formState.phone" placeholder="请输入手机号" />
          </a-form-item>
        </a-form>
      </a-modal>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import { message } from 'ant-design-vue';
import { getPassengers, createPassenger, updatePassenger, deletePassenger } from '../../api/passenger';

const passengers = ref([]);
const loading = ref(false);
const searchText = ref('');
const modalVisible = ref(false);
const isEdit = ref(false);
const currentId = ref(null);

const formState = reactive({
  name: '',
  id_type: 0,
  id_card: '',
  type: 0,
  phone: ''
});

const columns = [
  { title: '姓名', dataIndex: 'name', key: 'name' },
  { title: '证件类型', dataIndex: 'id_type', key: 'id_type' },
  { title: '证件号码', dataIndex: 'id_card', key: 'id_card' },
  { title: '旅客类型', dataIndex: 'type', key: 'type' },
  { title: '手机号', dataIndex: 'phone', key: 'phone' },
  { title: '核验状态', dataIndex: 'verify_status', key: 'verify_status' },
  { title: '操作', key: 'action' },
];

const fetchPassengers = async () => {
  loading.value = true;
  try {
    const res = await getPassengers();
    passengers.value = res.data;
  } catch (error) {
    message.error('获取乘客列表失败');
  } finally {
    loading.value = false;
  }
};

const onSearch = () => {
  // Client side filtering for now
};

const filteredPassengers = computed(() => {
  if (!searchText.value) return passengers.value;
  return passengers.value.filter(p => p.name.includes(searchText.value));
});

const getPassengerTypeLabel = (val) => {
  const map = { 0: '成人', 1: '学生', 2: '儿童' };
  return map[val] || val;
};

const getIdTypeLabel = (val) => {
  const map = { 0: '身份证', 1: '护照', 2: '台胞证', 3: '港澳通行证' };
  return map[val] || val;
};

const showAddModal = () => {
  isEdit.value = false;
  currentId.value = null;
  Object.assign(formState, {
    name: '',
    id_type: 0,
    id_card: '',
    type: 0,
    phone: ''
  });
  modalVisible.value = true;
};

const editPassenger = (record) => {
  isEdit.value = true;
  currentId.value = record.id;
  Object.assign(formState, {
    name: record.name,
    id_type: record.id_type,
    id_card: record.id_card,
    type: record.type,
    phone: record.phone
  });
  modalVisible.value = true;
};

const removePassenger = async (id) => {
  try {
    await deletePassenger(id);
    message.success('删除成功');
    fetchPassengers();
  } catch (error) {
    message.error('删除失败: ' + (error.response?.data?.detail || error.message));
  }
};

const handleModalOk = async () => {
  try {
    if (isEdit.value) {
      await updatePassenger(currentId.value, formState);
      message.success('更新成功');
    } else {
      await createPassenger(formState);
      message.success('添加成功');
    }
    modalVisible.value = false;
    fetchPassengers();
  } catch (error) {
    message.error('操作失败: ' + (error.response?.data?.detail || error.message));
  }
};

onMounted(() => {
  fetchPassengers();
});
</script>

<style scoped>
.user-layout {
  display: flex;
  min-height: 100vh;
}
.sidebar {
  width: 200px;
  background: #fff;
  border-right: 1px solid #f0f0f0;
}
.content {
  flex: 1;
  padding: 24px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.filter {
  margin-bottom: 16px;
}
</style>
