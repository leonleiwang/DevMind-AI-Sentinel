<!-- src/views/DocQAView.vue -->
<template>
  <MainLayout>
    <div class="dm-page">
      <header class="dm-page-header">
        <div>
          <p class="dm-eyebrow">RAG Knowledge Base</p>
          <h1 class="dm-title">运维文档智能问答</h1>
          <p class="dm-subtitle">
            通过 Confluence / SOP 知识库检索增强回答，把“经验排查”沉淀为可复用的证据化问答。
          </p>
        </div>
        <div class="dm-chip-row">
          <span class="dm-chip is-blue">Vector search</span>
          <span class="dm-chip is-green">Grounded answer</span>
        </div>
      </header>

      <div class="qa-shell">
        <div class="source-panel dm-card">
          <p class="dm-eyebrow">Knowledge scope</p>
          <h3>回答应来自可追溯的运维知识。</h3>
          <div class="source-item">
            <strong>Runbook</strong>
            <span>服务重启、回滚、限流操作 SOP</span>
          </div>
          <div class="source-item">
            <strong>Postmortem</strong>
            <span>历史事故复盘与根因模式</span>
          </div>
          <div class="source-item">
            <strong>Service docs</strong>
            <span>服务依赖、指标口径、告警含义</span>
          </div>
        </div>

        <div class="qa-main">
          <div class="chat-window" ref="chatWindow">
            <div v-if="!messages.length" class="empty-state">
              <h3>向知识库提问</h3>
              <p>例如：订单服务延迟升高时应该先查哪些指标？数据库连接池耗尽如何处理？</p>
            </div>
            <div v-for="(msg, idx) in messages" :key="idx" class="message" :class="msg.role">
              <div class="bubble">
                <div v-if="msg.steps && msg.steps.length > 0" class="step-stack">
                  <div v-for="(step, sIdx) in msg.steps" :key="sIdx" :class="['step-card', step.type]">
                    <strong>{{ stepLabel(step.type) }}</strong>
                    <pre>{{ step.data }}</pre>
                  </div>
                </div>
                <div v-if="msg.content" class="final-text">{{ msg.content }}</div>
              </div>
            </div>
          </div>
          <InputArea @send="askQuestion" :busy="asking" />
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue';
import MainLayout from '@/components/layout/MainLayout.vue';
import InputArea from '@/components/chat/InputArea.vue';
import { SSE } from 'sse.js';
import { useAuthStore } from '@/store/auth';
import type { ChatMessage } from '@/store/chat';

const messages = ref<ChatMessage[]>([]);
const asking = ref(false);
const chatWindow = ref<HTMLElement>();
type AgentMessage = ChatMessage & { steps: NonNullable<ChatMessage['steps']> };

function stepLabel(type: string) {
  const labels: Record<string, string> = {
    thought: 'Retrieval',
    action: 'Tool Call',
    observation: 'Evidence',
  };
  return labels[type] || type;
}

async function typewriterEffect(target: ChatMessage, text: string) {
  let index = 0;
  const speed = 25;
  target.content = '';
  while (index < text.length) {
    await new Promise((resolve) => setTimeout(resolve, speed));
    target.content = text.substring(0, index + 1);
    index++;
  }
}

async function askQuestion(message: string) {
  if (!message.trim()) return;

  const userMsg: ChatMessage = { role: 'user', content: message };
  const agentMsg: AgentMessage = { role: 'agent', content: '', steps: [] };
  messages.value.push(userMsg, agentMsg);
  asking.value = true;

  nextTick(() => {
    if (chatWindow.value) {
      chatWindow.value.scrollTop = chatWindow.value.scrollHeight;
    }
  });

  const authStore = useAuthStore();
  let receivedFinal = false;
  const source = new SSE('http://127.0.0.1:8000/api/v1/doc-qa/stream', {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authStore.token}`,
    },
    method: 'POST',
    payload: JSON.stringify({ message }),
  });

  source.addEventListener('intent', (e: any) => {
    const data = JSON.parse(e.data);
    agentMsg.steps.push({ type: 'thought', data: `意图: ${data.intent}` });
  });

  source.addEventListener('thought', (e: any) => {
    const data = JSON.parse(e.data);
    if (data.content) {
      agentMsg.steps.push({ type: 'thought', data: data.content });
    }
  });

  source.addEventListener('action', (e: any) => {
    const data = JSON.parse(e.data);
    agentMsg.steps.push({
      type: 'action',
      data: `工具: ${data.tool}\n参数: ${JSON.stringify(data.input)}`,
    });
  });

  source.addEventListener('observation', (e: any) => {
    const data = JSON.parse(e.data);
    if (data.content) {
      agentMsg.steps.push({ type: 'observation', data: data.content });
    }
  });

  source.addEventListener('final', (e: any) => {
    const data = JSON.parse(e.data);
    receivedFinal = true;
    source.close();
    typewriterEffect(agentMsg, data.content).then(() => {
      asking.value = false;
      nextTick(() => {
        if (chatWindow.value) {
          chatWindow.value.scrollTop = chatWindow.value.scrollHeight;
        }
      });
    });
  });

  source.onerror = (event: any) => {
    if (receivedFinal) return;
    console.error('DocQA SSE error', event);
    agentMsg.content = '连接错误，请重试。';
    source.close();
    asking.value = false;
  };
}
</script>

<style scoped>
.qa-shell {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 16px;
}

.source-panel {
  padding: 18px;
}

.source-panel h3 {
  margin: 0 0 18px;
  color: var(--dm-ink);
  font-size: 20px;
  line-height: 1.35;
}

.source-item {
  border: 1px solid var(--dm-border);
  border-radius: 12px;
  background: #fff;
  padding: 12px;
  margin-top: 10px;
}

.source-item strong,
.source-item span {
  display: block;
}

.source-item strong {
  color: var(--dm-ink);
  font-size: 13px;
}

.source-item span {
  margin-top: 5px;
  color: var(--dm-ink-muted);
  font-size: 12px;
  line-height: 1.6;
}

.qa-main {
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-window {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  border: 1px solid var(--dm-border);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.9);
  padding: 18px;
}

.empty-state {
  min-height: 360px;
  display: grid;
  place-items: center;
  align-content: center;
  text-align: center;
  color: var(--dm-ink-muted);
}

.empty-state h3 {
  margin: 0 0 8px;
  color: var(--dm-ink);
}

.message {
  margin: 12px 0;
  display: flex;
}

.user {
  justify-content: flex-end;
}

.agent {
  justify-content: flex-start;
}

.bubble {
  max-width: min(760px, 78%);
  border: 1px solid var(--dm-border);
  border-radius: 14px;
  background: #fff;
  padding: 14px;
}

.user .bubble {
  background: #eef4ff;
  color: #173166;
}

.step-stack {
  display: grid;
  gap: 8px;
}

.step-card {
  border: 1px solid var(--dm-border);
  border-radius: 10px;
  background: #fbfdff;
  padding: 10px;
}

.step-card strong {
  color: var(--dm-blue);
  font-size: 12px;
}

.step-card pre {
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--dm-ink-soft);
  font-family: var(--dm-mono);
  font-size: 12px;
  margin: 8px 0 0;
}

.final-text {
  margin-top: 8px;
  white-space: pre-wrap;
  line-height: 1.7;
}

@media (max-width: 980px) {
  .qa-shell {
    grid-template-columns: 1fr;
  }
}
</style>
