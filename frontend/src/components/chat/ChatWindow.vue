<!-- src/components/chat/ChatWindow.vue -->
<template>
  <div class="chat-window" ref="scrollContainer">
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
  overflow-y: auto;
  margin-bottom: 10px;
}
</style>