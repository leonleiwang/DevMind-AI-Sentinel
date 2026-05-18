<!-- src/components/chat/ChatWindow.vue -->
<template>
  <div class="chat-window" ref="scrollContainer">
    <div v-if="!messages.length" class="empty-state">
      <span class="empty-mark">Trace</span>
      <h3>等待一次 Agent 运行</h3>
      <p>发起问题后，这里会展示意图识别、工具调用、观测结果和最终结论。</p>
    </div>
    <MessageBubble v-for="(msg, index) in messages" :key="index" :message="msg" />
  </div>
</template>

<script setup lang="ts">
import { watch, ref, nextTick } from 'vue';
import MessageBubble from './MessageBubble.vue';
import type { ChatMessage } from '@/store/chat';

const props = defineProps<{ messages: ChatMessage[] }>();
const scrollContainer = ref<HTMLElement>();

watch(
  () => props.messages.length,
  () => {
    nextTick(() => {
      if (scrollContainer.value) {
        scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight;
      }
    });
  }
);
</script>

<style scoped>
.chat-window {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  border: 1px solid var(--dm-border);
  border-radius: 16px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.88), rgba(248, 250, 252, 0.92)),
    var(--dm-surface-strong);
  padding: 18px;
}

.empty-state {
  height: 100%;
  min-height: 360px;
  display: grid;
  place-items: center;
  align-content: center;
  text-align: center;
  color: var(--dm-ink-muted);
}

.empty-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 76px;
  height: 34px;
  border-radius: 999px;
  background: var(--dm-blue-soft);
  color: var(--dm-blue);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.empty-state h3 {
  margin: 16px 0 8px;
  color: var(--dm-ink);
  font-size: 22px;
}

.empty-state p {
  max-width: 430px;
  margin: 0;
  font-size: 14px;
  line-height: 1.7;
}
</style>
