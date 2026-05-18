<!-- src/components/chat/InputArea.vue -->
<template>
  <div class="input-area">
    <el-input
      v-model="text"
      class="prompt-input"
      placeholder="描述故障现象、服务名、时间范围或想查询的运维知识..."
      @keyup.enter="send"
      :disabled="busy"
    />
    <el-button class="send-btn" type="primary" @click="send" :loading="busy">发送</el-button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

defineProps<{ busy?: boolean }>();
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
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 10px;
  border: 1px solid var(--dm-border);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.88);
  padding: 10px;
  box-shadow: var(--dm-shadow-soft);
}

.send-btn {
  min-width: 92px;
  border-radius: 10px;
  font-weight: 760;
}

@media (max-width: 640px) {
  .input-area {
    grid-template-columns: 1fr;
  }
}
</style>
