<template>
  <a-layout style="min-height: 100vh">
    <Header12306 />
    <a-layout>
      <a-layout-sider width="200" style="background: #f8f8f8">
        <div style="padding: 16px; font-weight: 600">我的12306</div>
        <a-menu mode="inline" style="border-right: 0">
          <a-menu-item key="profile">账户概览</a-menu-item>
        </a-menu>
      </a-layout-sider>
      <a-layout-content style="padding: 24px">
        <a-card title="个人中心" bordered>
          <div style="margin-bottom: 16px">{{ greetingText }}，{{ profile.real_name || profile.username }}</div>
          <a-row :gutter="16">
            <a-col :span="8">
              <a-card size="small" title="基本信息">
                <p>用户名：{{ profile.username }}</p>
                <p v-if="!basicEditing">姓名：{{ profile.real_name }}</p>
                <div v-else style="margin-bottom: 8px">
                  <span>姓名：</span>
                  <a-input v-model:value="editForm.real_name" style="width: 160px" />
                </div>
                <p>国家/地区：{{ profile.country }}</p>
                <p>证件类型：{{ profile.id_type }}</p>
                <p>证件号码：{{ maskedIdNumber }}</p>
                <div style="margin-top: 8px">
                  <a-button type="link" @click="toggleBasicEditing">
                    {{ basicEditing ? '取消' : '编辑' }}
                  </a-button>
                  <a-button
                    v-if="basicEditing"
                    type="primary"
                    size="small"
                    style="margin-left: 8px"
                    :loading="saving"
                    @click="saveProfile"
                  >
                    保存
                  </a-button>
                </div>
              </a-card>
            </a-col>
            <a-col :span="8">
              <a-card size="small" title="联系方式">
                <div v-if="!contactEditing">
                  <p>手机号：{{ maskedPhone }}</p>
                  <p>邮箱：{{ profile.email }}</p>
                </div>
                <div v-else>
                  <div style="margin-bottom: 8px">
                    <span>手机号：</span>
                    <a-input v-model:value="editForm.phone" style="width: 180px" />
                  </div>
                  <div>
                    <span>邮箱：</span>
                    <a-input v-model:value="editForm.email" style="width: 180px" />
                  </div>
                </div>
                <div style="margin-top: 8px">
                  <a-button type="link" @click="toggleContactEditing">
                    {{ contactEditing ? '取消' : '编辑联系方式' }}
                  </a-button>
                  <a-button
                    v-if="contactEditing"
                    type="primary"
                    size="small"
                    style="margin-left: 8px"
                    :loading="saving"
                    @click="saveProfile"
                  >
                    保存
                  </a-button>
                </div>
              </a-card>
            </a-col>
            <a-col :span="8">
              <a-card size="small" title="附加信息">
                <div v-if="!extraEditing">
                  <p>优惠类型：{{ profile.user_type }}</p>
                </div>
                <div v-else>
                  <span>优惠类型：</span>
                  <a-select v-model:value="editForm.user_type" style="width: 160px">
                    <a-select-option value="adult">成人</a-select-option>
                    <a-select-option value="child">儿童</a-select-option>
                    <a-select-option value="student">学生</a-select-option>
                    <a-select-option value="disabled_soldier">残疾军人</a-select-option>
                  </a-select>
                </div>
                <div style="margin-top: 8px">
                  <a-button type="link" @click="toggleExtraEditing">
                    {{ extraEditing ? '取消' : '编辑' }}
                  </a-button>
                  <a-button
                    v-if="extraEditing"
                    type="primary"
                    size="small"
                    style="margin-left: 8px"
                    :loading="saving"
                    @click="saveProfile"
                  >
                    保存
                  </a-button>
                </div>
              </a-card>
            </a-col>
          </a-row>
        </a-card>
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { getProfile, updateProfile } from '../../api/user.js';
import Header12306 from '../../components/Header12306.vue';

const profile = reactive({
  username: '',
  real_name: '',
  country: '',
  id_type: '',
  id_number: '',
  phone: '',
  email: '',
  user_type: '',
});

const editForm = reactive({
  real_name: '',
  phone: '',
  email: '',
  user_type: '',
});

const basicEditing = ref(false);
const contactEditing = ref(false);
const extraEditing = ref(false);
const saving = ref(false);

const greetingText = computed(() => {
  const hour = new Date().getHours();
  if (hour < 12) return '上午好';
  if (hour < 18) return '下午好';
  return '晚上好';
});

const maskedIdNumber = computed(() => {
  if (!profile.id_number || profile.id_number.length <= 7) return profile.id_number;
  const first = profile.id_number.slice(0, 4);
  const last = profile.id_number.slice(-3);
  return `${first}**********${last}`;
});

const maskedPhone = computed(() => {
  if (!profile.phone || profile.phone.length < 7) return profile.phone;
  const first = profile.phone.slice(0, 3);
  const last = profile.phone.slice(-4);
  return `+86 ${first}****${last}`;
});

onMounted(async () => {
  try {
    const res = await getProfile();
    if (res.data && res.data.code === 200 && res.data.data) {
      Object.assign(profile, res.data.data);
      editForm.real_name = profile.real_name;
      editForm.phone = profile.phone;
      editForm.email = profile.email;
      editForm.user_type = profile.user_type;
      if (typeof window !== 'undefined') {
        window.localStorage.setItem('profile', JSON.stringify(profile));
      }
      return;
    }
  } catch (e) {
    if (typeof window !== 'undefined') {
      const stored = window.localStorage.getItem('profile');
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          Object.assign(profile, parsed);
          editForm.real_name = profile.real_name;
          editForm.phone = profile.phone;
          editForm.email = profile.email;
          editForm.user_type = profile.user_type;
          return;
        } catch (_) {}
      }
      const rawUser = window.localStorage.getItem('user');
      if (rawUser) {
        try {
          const userInfo = JSON.parse(rawUser);
          profile.username = userInfo.username || '';
          profile.real_name = userInfo.username || '';
          profile.country = '中国';
          profile.id_type = 'id_card';
          profile.id_number = '000000000000000000';
          profile.phone = '';
          profile.email = userInfo.username ? `${userInfo.username}@example.com` : '';
          profile.user_type = 'adult';
          editForm.real_name = profile.real_name;
          editForm.phone = profile.phone;
          editForm.email = profile.email;
          editForm.user_type = profile.user_type;
        } catch (_) {}
      }
    }
  }
});

const toggleBasicEditing = () => {
  basicEditing.value = !basicEditing.value;
  if (basicEditing.value) {
    editForm.real_name = profile.real_name;
  }
};

const toggleContactEditing = () => {
  contactEditing.value = !contactEditing.value;
  if (contactEditing.value) {
    editForm.phone = profile.phone;
    editForm.email = profile.email;
  }
};

const toggleExtraEditing = () => {
  extraEditing.value = !extraEditing.value;
  if (extraEditing.value) {
    editForm.user_type = profile.user_type;
  }
};

const saveProfile = async () => {
  saving.value = true;
  try {
    const payload = {
      real_name: editForm.real_name,
      phone: editForm.phone,
      email: editForm.email,
      user_type: editForm.user_type || profile.user_type,
    };
    try {
      const res = await updateProfile(payload);
      if (res.data && res.data.code === 200 && res.data.data) {
        Object.assign(profile, res.data.data);
      } else {
        profile.real_name = payload.real_name;
        profile.phone = payload.phone;
        profile.email = payload.email;
        profile.user_type = payload.user_type;
      }
    } catch (e) {
      profile.real_name = payload.real_name;
      profile.phone = payload.phone;
      profile.email = payload.email;
      profile.user_type = payload.user_type;
    }
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('profile', JSON.stringify(profile));
    }
    basicEditing.value = false;
    contactEditing.value = false;
    extraEditing.value = false;
  } finally {
    saving.value = false;
  }
};
</script>
