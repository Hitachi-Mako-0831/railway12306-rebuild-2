<template>
  <div>
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

    <a-table 
      :columns="columns" 
      :data-source="passengers" 
      :loading="loading" 
      row-key="id"
      :pagination="{ pageSize: 20 }"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'name'">
          {{ record.name }}
          <a-tag v-if="record.is_default" color="blue" style="margin-left: 8px">本人</a-tag>
        </template>
        <template v-if="column.key === 'type'">
          {{ getPassengerTypeLabel(record.type) }}
        </template>
        <template v-if="column.key === 'id_type'">
          {{ getIdTypeLabel(record.id_type) }}
        </template>
        <template v-if="column.key === 'id_card'">
          {{ maskIdCard(record.id_card) }}
        </template>
        <template v-if="column.key === 'phone'">
          {{ maskPhone(record.phone) }}
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
      <a-form 
        ref="formRef"
        :model="formState" 
        :rules="rules"
        :label-col="{ span: 6 }" 
        :wrapper-col="{ span: 16 }"
      >
        <a-form-item label="姓名" name="name" required>
          <a-input 
            v-model:value="formState.name" 
            placeholder="请输入姓名" 
            :disabled="isEdit && formState.is_default"
          />
        </a-form-item>
        <a-form-item label="证件类型" name="id_type" required>
          <a-select 
            v-model:value="formState.id_type"
            :disabled="isEdit && formState.is_default"
          >
            <a-select-option :value="0">身份证</a-select-option>
            <a-select-option :value="1">护照</a-select-option>
            <a-select-option :value="2">台胞证</a-select-option>
            <a-select-option :value="3">港澳通行证</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="证件号码" name="id_card" required>
          <a-input 
            v-model:value="formState.id_card" 
            placeholder="请输入证件号码" 
            :disabled="isEdit && formState.is_default"
          />
        </a-form-item>
        <a-form-item label="旅客类型" name="type">
          <a-select v-model:value="formState.type">
            <a-select-option :value="0">成人</a-select-option>
            <a-select-option :value="1">学生</a-select-option>
            <a-select-option :value="2">儿童</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="手机号" name="phone" required>
          <a-input v-model:value="formState.phone" placeholder="请输入手机号" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue';
import { message } from 'ant-design-vue';
import { getPassengers, createPassenger, updatePassenger, deletePassenger } from '../../api/passenger';

const passengers = ref([]);
const loading = ref(false);
const searchText = ref('');
const modalVisible = ref(false);
const isEdit = ref(false);
const currentId = ref(null);
const formRef = ref(null);

const formState = reactive({
  name: '',
  id_type: 0,
  id_card: '',
  type: 0,
  phone: '',
  is_default: false
});

const PATTERN_PHONE_CN = /^1[3-9]\d{9}$/;
const PATTERN_ID_CARD_CN = /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/;
const PATTERN_PASSPORT = /^[a-zA-Z0-9]{5,15}$/;
const PATTERN_CHINESE_NAME = /^[\u4e00-\u9fa5]{2,15}(?:·[\u4e00-\u9fa5]{2,15})*$/;
const PATTERN_PASSPORT_NAME = /^[a-zA-Z]+(?:\s[a-zA-Z]+)*$/;

const validateName = async (_rule, value) => {
  if (!value) {
    return Promise.reject('请输入姓名');
  }
  if (PATTERN_CHINESE_NAME.test(value) || PATTERN_PASSPORT_NAME.test(value)) {
    return Promise.resolve();
  }
  return Promise.reject('姓名格式不正确(需为中文或英文姓名)');
};

const validateIdCard = async (_rule, value) => {
  if (!value) {
    return Promise.reject('请输入证件号码');
  }
  if (formState.id_type === 0) {
    if (!PATTERN_ID_CARD_CN.test(value)) {
      return Promise.reject('身份证格式不正确');
    }
  } else if (formState.id_type === 1) {
    if (!PATTERN_PASSPORT.test(value)) {
      return Promise.reject('护照号码格式不正确');
    }
  }
  return Promise.resolve();
};

const rules = {
  name: [{ required: true, validator: validateName, trigger: 'blur' }],
  id_type: [{ required: true, message: '请选择证件类型', trigger: 'change' }],
  id_card: [{ required: true, validator: validateIdCard, trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: PATTERN_PHONE_CN, message: '手机号格式不正确', trigger: 'blur' }
  ]
};

const columns = [
  { title: '姓名', dataIndex: 'name', key: 'name' },
  { title: '证件类型', dataIndex: 'id_type', key: 'id_type' },
  { title: '证件号码', dataIndex: 'id_card', key: 'id_card' },
  { title: '旅客类型', dataIndex: 'type', key: 'type' },
  { title: '手机号', dataIndex: 'phone', key: 'phone' },
  { title: '核验状态', dataIndex: 'verify_status', key: 'verify_status' },
  { title: '操作', key: 'action' },
];

const fetchPassengers = async (name = '') => {
  loading.value = true;
  try {
    const res = await getPassengers({ name });
    passengers.value = res.data;
  } catch (error) {
    message.error('获取乘客列表失败');
  } finally {
    loading.value = false;
  }
};

const onSearch = () => {
  fetchPassengers(searchText.value);
};

const maskIdCard = (val) => {
  if (!val || val.length < 10) return val;
  return val.substring(0, 6) + '****' + val.substring(val.length - 4);
};

const maskPhone = (val) => {
  if (!val || val.length < 11) return val;
  return val.substring(0, 3) + '****' + val.substring(val.length - 4);
};

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
    phone: '',
    is_default: false
  });
  modalVisible.value = true;
  nextTick(() => {
    formRef.value?.clearValidate();
  });
};

const editPassenger = (record) => {
  isEdit.value = true;
  currentId.value = record.id;
  Object.assign(formState, {
    name: record.name,
    id_type: record.id_type,
    id_card: record.id_card,
    type: record.type,
    phone: record.phone,
    is_default: record.is_default
  });
  modalVisible.value = true;
  nextTick(() => {
    formRef.value?.clearValidate();
  });
};

const removePassenger = async (id) => {
  try {
    await deletePassenger(id);
    message.success('删除成功');
    fetchPassengers(searchText.value);
  } catch (error) {
    message.error('删除失败: ' + (error.response?.data?.detail || error.message));
  }
};

const handleModalOk = async () => {
  try {
    await formRef.value.validate();
    if (isEdit.value) {
      await updatePassenger(currentId.value, formState);
      message.success('更新成功');
    } else {
      await createPassenger(formState);
      message.success('添加成功');
    }
    modalVisible.value = false;
    fetchPassengers(searchText.value);
  } catch (error) {
    if (error.errorFields) {
      return;
    }
    message.error('操作失败: ' + (error.response?.data?.detail || error.message));
  }
};

onMounted(() => {
  fetchPassengers();
});
</script>

<style scoped>
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
