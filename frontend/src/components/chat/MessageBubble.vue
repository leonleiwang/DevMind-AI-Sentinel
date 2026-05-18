<!-- src/components/chat/MessageBubble.vue -->
<template>
  <div :class="['message', message.role]">
    <div class="bubble">
      <div v-if="message.role === 'agent' && message.steps?.length" class="trace-list">
        <div v-for="(step, idx) in message.steps" :key="idx" :class="['trace-step', step.type]">
          <div class="trace-meta">
            <span class="trace-dot"></span>
            <strong>{{ stepLabel(step.type) }}</strong>
          </div>
          <pre>{{ formatStepData(step.data) }}</pre>
        </div>
      </div>
      <div v-if="message.content" class="final-output">{{ message.content }}</div>
      <div v-else-if="message.role === 'agent'" class="thinking">Agent 正在收集证据并生成结论...</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ChatMessage } from '@/store/chat';

defineProps<{ message: ChatMessage }>();

function stepLabel(type: string) {
  const labels: Record<string, string> = {
    thought: 'Reasoning',
    action: 'Tool Call',
    observation: 'Observation',
  };
  return labels[type] || type;
}

function formatStepData(data: unknown) {
  if (typeof data === 'string') return data;
  return JSON.stringify(data, null, 2);
}
</script>

<style scoped>
.message {
  margin: 12px 0;
  display: flex;
}

.message.user {
  justify-content: flex-end;
}

.message.agent {
  justify-content: flex-start;
}

.bubble {
  max-width: min(760px, 78%);
  border: 1px solid var(--dm-border);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.94);
  padding: 14px;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
}

.message.user .bubble {
  border-color: rgba(29, 78, 216, 0.16);
  background: #eef4ff;
  color: #173166;
}

.trace-list {
  display: grid;
  gap: 8px;
}

.trace-step {
  border: 1px solid var(--dm-border);
  border-radius: 10px;
  background: #fbfdff;
  padding: 10px;
}

.trace-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--dm-ink-soft);
  font-size: 12px;
}

.trace-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: var(--dm-blue);
}

.trace-step.action .trace-dot {
  background: var(--dm-amber);
}

.trace-step.observation .trace-dot {
  background: var(--dm-green);
}

.trace-step pre {
  margin: 8px 0 0;
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--dm-ink-soft);
  font-family: var(--dm-mono);
  font-size: 12px;
  line-height: 1.6;
}

.final-output {
  margin-top: 10px;
  color: var(--dm-ink);
  white-space: pre-wrap;
  line-height: 1.7;
  font-size: 14px;
}

.thinking {
  color: var(--dm-ink-muted);
  font-size: 13px;
}

@media (max-width: 720px) {
  .bubble {
    max-width: 92%;
  }
}
</style>
