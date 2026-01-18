<template>
  <div ref="root" style="position: relative; width: 160px">
    <a-input
      v-model:value="innerValue"
      :placeholder="placeholder"
      @focus="onFocus"
      @input="onInput"
    />
    <div
      data-testid="city-selector-popup"
      v-if="open && filteredOptions.length"
      style="position: absolute; z-index: 1000; top: 32px; left: 0; right: 0; max-height: 260px; overflow-y: auto; background: #fff; border: 1px solid #f0f0f0; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15)"
    >
      <div
        v-for="option in filteredOptions"
        :key="option.value"
        style="padding: 4px 8px; cursor: pointer"
        @mousedown.prevent
        @click="selectCity(option.value)"
      >
        {{ option.label }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['update:modelValue']);

const innerValue = ref(props.modelValue);
const query = ref('');
const open = ref(false);
const root = ref(null);

const cityOptions = [
  { label: '北京', value: '北京', pinyin: ['beijing', 'bj'] },
  { label: '上海', value: '上海', pinyin: ['shanghai', 'sh'] },
  { label: '南京', value: '南京', pinyin: ['nanjing', 'nj'] },
  { label: '杭州', value: '杭州', pinyin: ['hangzhou', 'hz'] }
];

watch(
  () => props.modelValue,
  value => {
    innerValue.value = value;
    query.value = value || '';
  }
);

watch(innerValue, value => {
  emit('update:modelValue', value);
});

const filteredOptions = computed(() => {
  if (!query.value) return cityOptions;
  const lower = query.value.toLowerCase();
  return cityOptions.filter(option => {
    if (option.label.includes(query.value)) return true;
    return option.pinyin.some(p => p.startsWith(lower));
  });
});

const onFocus = () => {
  open.value = true;
};

const onInput = e => {
  query.value = e.target.value;
  open.value = true;
};

const selectCity = value => {
  innerValue.value = value;
  query.value = value;
  open.value = false;
};

const handleDocumentClick = event => {
  if (!root.value) return;
  if (!root.value.contains(event.target)) {
    open.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', handleDocumentClick);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick);
});
</script>

