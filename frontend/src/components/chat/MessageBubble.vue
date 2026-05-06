<!-- src/components/chat/MessageBubble.vue -->
<template>
  <div :class="['message', message.role]">
    <div class="bubble">
      <div v-if="message.role === 'agent' && message.steps">
        <div v-for="(step, idx) in message.steps" :key="idx" class="step">
          <el-tag size="small" :type="stepTagType(step.type)">{{ step.type }}</el-tag>
          <p>{{ step.data }}</p>
        </div>
      </div>
      <!-- 修改这里：改为纯文本显示，以支持打字机逐字输出 -->
      <div v-if="message.content" class="final-output">{{ message.content }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ChatMessage } from '@/store/chat';

const props = defineProps<{ message: ChatMessage }>();

function stepTagType(type: string) {
  return type === 'thought' ? 'info' : type === 'action' ? 'warning' : '';
}
</script>

<style scoped>
.message {
  margin: 10px 0;
  display: flex;
}
.message.user {
  justify-content: flex-end;
}
.message.agent {
  justify-content: flex-start;
}
.bubble {
  max-width: 70%;
  padding: 10px 15px;
  border-radius: 12px;
  background-color: #f0f2f5;
}
.message.user .bubble {
  background-color: #d9e1ff;
}
.final-output {
  margin-top: 8px;
  white-space: pre-wrap; /* 保留换行符 */
}
.step {
  margin-bottom: 8px;
}
</style>