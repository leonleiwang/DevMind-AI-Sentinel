<!-- src/views/FaultDiagnosisView.vue -->
<template>
  <MainLayout>
    <div class="dm-page">
      <header class="dm-page-header">
        <div>
          <p class="dm-eyebrow">Fault Diagnosis</p>
          <h1 class="dm-title">故障排查工作台</h1>
          <p class="dm-subtitle">
            通过自然语言触发 Supervisor Agent，串联指标、日志、告警和 MCP 工具调用，输出可解释的排查路径。
          </p>
        </div>
        <div class="dm-chip-row">
          <span class="dm-chip is-green">SSE streaming</span>
          <span class="dm-chip is-blue">Tool trace</span>
          <span class="dm-chip">Confidence gate</span>
        </div>
      </header>

      <section class="dm-kpi-grid">
        <article class="dm-card dm-kpi-card">
          <div class="dm-kpi-label">Agent mode</div>
          <div class="dm-kpi-value">RCA</div>
          <div class="dm-kpi-caption">intent → action → evidence</div>
        </article>
        <article class="dm-card dm-kpi-card">
          <div class="dm-kpi-label">Connected tools</div>
          <div class="dm-kpi-value">5</div>
          <div class="dm-kpi-caption">Prometheus / Jira / GitLab...</div>
        </article>
        <article class="dm-card dm-kpi-card">
          <div class="dm-kpi-label">Clarification</div>
          <div class="dm-kpi-value">0.7</div>
          <div class="dm-kpi-caption">low confidence threshold</div>
        </article>
        <article class="dm-card dm-kpi-card">
          <div class="dm-kpi-label">Output</div>
          <div class="dm-kpi-value">Trace</div>
          <div class="dm-kpi-caption">visible reasoning process</div>
        </article>
      </section>

      <div class="quick-prompts">
        <button @click="handleSend('订单服务今天下午 1 点开始延迟升高，请帮我定位可能原因')">
          订单服务延迟升高
        </button>
        <button @click="handleSend('支付服务 5xx 错误率突然升高，先帮我确认影响范围')">
          支付服务错误率升高
        </button>
        <button @click="handleSend('这个告警我看不懂，帮我判断需要先查什么')">
          模糊告警澄清
        </button>
      </div>

      <div class="chat-wrapper">
        <ChatWindow :messages="chatStore.messages" />
        <InputArea @send="handleSend" />
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import MainLayout from '@/components/layout/MainLayout.vue';
import ChatWindow from '@/components/chat/ChatWindow.vue';
import InputArea from '@/components/chat/InputArea.vue';
import { useChatStore } from '@/store/chat';
import { connectChatStream } from '@/api/chat';

const chatStore = useChatStore();

async function typewriterEffect(text: string) {
  let index = 0;
  const speed = 25;
  chatStore.updateLastAgentContent('');
  while (index < text.length) {
    await new Promise((resolve) => setTimeout(resolve, speed));
    chatStore.updateLastAgentContent(text.substring(0, index + 1));
    index++;
  }
}

async function handleSend(message: string) {
  chatStore.addMessage({ role: 'user', content: message });
  chatStore.addMessage({ role: 'agent', content: '', steps: [] });

  try {
    connectChatStream(
      { message },
      (event, data) => {
        switch (event) {
          case 'intent':
            chatStore.appendStep({ type: 'thought', data: `意图识别: ${data.intent}` });
            break;
          case 'thought':
            chatStore.appendStep({ type: 'thought', data: data.content });
            break;
          case 'action':
            chatStore.appendStep({ type: 'action', data });
            break;
          case 'observation':
            chatStore.appendStep({ type: 'observation', data: data.content });
            break;
          case 'final':
            typewriterEffect(data.content);
            break;
        }
      },
      (error) => {
        chatStore.updateLastAgentContent('连接发生错误，请重试。');
        console.error(error);
      }
    );
  } catch (e) {
    chatStore.updateLastAgentContent('无法发送消息，请检查网络或重新登录。');
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
  transition: border 0.18s, background 0.18s, transform 0.18s;
}

.quick-prompts button:hover {
  border-color: rgba(29, 78, 216, 0.28);
  background: var(--dm-blue-soft);
  color: var(--dm-blue);
  transform: translateY(-1px);
}

.chat-wrapper {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
