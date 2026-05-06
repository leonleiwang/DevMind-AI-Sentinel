// src/store/chat.ts
import { defineStore } from 'pinia';
import { ref } from 'vue';

export interface ChatMessage {
  role: 'user' | 'agent';
  content: string;
  steps?: {
    type: 'thought' | 'action' | 'observation';
    data: any;
  }[];
}

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([]);

  function addMessage(msg: ChatMessage) {
    messages.value.push(msg);
  }

  function appendStep(step: NonNullable<ChatMessage['steps']>[number]) {
    // 给最后一条 agent 消息添加步骤
    const last = messages.value[messages.value.length - 1];
    if (last && last.role === 'agent') {
        if (!last.steps) last.steps = [];
        last.steps.push(step);
    }
  }

  function updateLastAgentContent(content: string) {
    const last = messages.value[messages.value.length - 1];
    if (last && last.role === 'agent') {
      last.content = content;
    }
  }

  function clearMessages() {
    messages.value = [];
  }

  return { messages, addMessage, appendStep, updateLastAgentContent, clearMessages };
});