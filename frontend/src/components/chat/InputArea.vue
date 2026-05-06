<!-- src/components/chat/InputArea.vue -->
<template>
  <div class="input-area">
    <el-input
      v-model="text"
      placeholder="描述你的运维问题..."
      @keyup.enter="send"
      :disabled="busy"
    />
    <el-button type="primary" @click="send" :loading="busy">发送</el-button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{ busy?: boolean }>();
const emit = defineEmits<{ send: [text: string] }>();

const text = ref('');

function send() {
  if (!text.value.trim()) return;
  emit('send', text.value.trim());
  text.value = '';
}
</script>

<style scoped>
.input-area {
  display: flex;
  gap: 10px;
  padding: 10px 0;
}
</style>