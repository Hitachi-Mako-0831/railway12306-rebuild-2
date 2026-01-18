<template>
  <a-date-picker
    v-model:value="innerValue"
    :disabled-date="disabledDate"
    :placeholder="placeholder"
    :disabled="props.disabled"
    format="YYYY-MM-DD"
    style="width: 180px"
    @change="handleChange"
  />
</template>

<script setup>
import dayjs from 'dayjs';
import { ref, watch } from 'vue';

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:modelValue']);

const innerValue = ref(props.modelValue ? dayjs(props.modelValue) : null);

watch(
  () => props.modelValue,
  value => {
    innerValue.value = value ? dayjs(value) : null;
  }
);

const disabledDate = current => {
  if (props.disabled) return true;
  if (!current) return false;
  const today = dayjs().startOf('day');
  return current < today;
};

const handleChange = value => {
  if (!value) {
    emit('update:modelValue', '');
    return;
  }
  emit('update:modelValue', value.format('YYYY-MM-DD'));
};
</script>
