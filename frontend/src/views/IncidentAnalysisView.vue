<template>
  <MainLayout>
    <div class="dm-page">
      <header class="dm-page-header">
        <div>
          <p class="dm-eyebrow">Incident Timeline</p>
          <h1 class="dm-title">事故 RCA 分析</h1>
          <p class="dm-subtitle">
            聚合发布、告警、指标和工单事件，形成面向 SRE 的时间线、证据链和修复建议。
          </p>
        </div>
        <div class="dm-chip-row">
          <span class="dm-chip is-blue">Timeline</span>
          <span class="dm-chip is-green">Evidence chain</span>
        </div>
      </header>

      <div class="quick-prompts">
        <button @click="handleSend('分析今天下午 1 点订单服务故障的根因')">订单服务故障根因</button>
        <button @click="handleSend('复盘 13:00 到 14:00 的线上延迟事故')">线上延迟事故复盘</button>
      </div>

      <div class="chat-wrapper">
        <ChatWindow :messages="messages" />
        <InputArea :busy="busy" @send="handleSend" />
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import MainLayout from '@/components/layout/MainLayout.vue';
import ChatWindow from '@/components/chat/ChatWindow.vue';
import InputArea from '@/components/chat/InputArea.vue';
import type { ChatMessage } from '@/store/chat';
import { connectIncidentAnalysisStream } from '@/api/incident';

const messages = ref<ChatMessage[]>([]);
const busy = ref(false);

function addMessage(msg: ChatMessage) {
  messages.value.push(msg);
}

function appendStep(step: NonNullable<ChatMessage['steps']>[number]) {
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

async function typewriterEffect(text: string) {
  let index = 0;
  const speed = 18;
  updateLastAgentContent('');
  while (index < text.length) {
    await new Promise((resolve) => setTimeout(resolve, speed));
    updateLastAgentContent(text.substring(0, index + 1));
    index++;
  }
}

function handleSend(message: string) {
  if (busy.value) return;

  addMessage({ role: 'user', content: message });
  addMessage({ role: 'agent', content: '', steps: [] });
  busy.value = true;

  try {
    connectIncidentAnalysisStream(
      { message },
      (event, data) => {
        switch (event) {
          case 'intent':
            appendStep({ type: 'thought', data: `意图识别: ${data.intent}` });
            break;
          case 'thought':
            appendStep({ type: 'thought', data: data.content || '准备获取事故时间线' });
            break;
          case 'action':
            appendStep({ type: 'action', data });
            break;
          case 'observation':
            appendStep({ type: 'observation', data: data.content });
            break;
          case 'final':
            typewriterEffect(data.content).finally(() => {
              busy.value = false;
            });
            break;
        }
      },
      (error) => {
        busy.value = false;
        updateLastAgentContent('连接发生错误，请重试。');
        console.error(error);
      }
    );
  } catch {
    busy.value = false;
    updateLastAgentContent('无法发送消息，请检查网络或重新登录。');
  }
}
</script>

<style scoped>
.quick-prompts {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.quick-prompts button {
  border: 1px solid var(--dm-border);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.82);
  color: var(--dm-ink-soft);
  padding: 8px 12px;
  font-size: 13px;
  font-weight: 650;
  cursor: pointer;
}

.quick-prompts button:hover {
  border-color: rgba(29, 78, 216, 0.28);
  background: var(--dm-blue-soft);
  color: var(--dm-blue);
}

.chat-wrapper {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
