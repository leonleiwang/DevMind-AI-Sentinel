<!-- src/views/CodeReviewView.vue -->
<template>
  <MainLayout>
    <div class="dm-page">
      <header class="dm-page-header">
        <div>
          <p class="dm-eyebrow">Code Intelligence</p>
          <h1 class="dm-title">代码审查 Agent</h1>
          <p class="dm-subtitle">
            模拟接入 GitLab Merge Request，展示 Agent 如何检查风险、调用工具并输出审查建议。
          </p>
        </div>
        <el-button type="primary" class="run-button" @click="startReview" :loading="reviewing">
          开始审查待处理 MR
        </el-button>
      </header>

      <section class="review-grid">
        <aside class="review-summary dm-card">
          <p class="dm-eyebrow">Review plan</p>
          <h3>关注变更风险，而不是只给泛泛建议。</h3>
          <div class="summary-list">
            <span>安全边界</span>
            <span>异常处理</span>
            <span>数据库影响</span>
            <span>可回滚性</span>
          </div>
        </aside>

        <div class="review-output dm-card" ref="outputContainer">
          <div v-if="!steps.length && !finalOutput" class="empty-state">
            <h3>等待代码审查运行</h3>
            <p>点击开始后，这里会展示 intent、tool call、observation 和最终审查结论。</p>
          </div>
          <div v-if="steps.length" class="review-steps">
            <div v-for="(step, idx) in steps" :key="idx" :class="['step-card', step.type]">
              <strong>{{ stepLabel(step.type) }}</strong>
              <pre>{{ step.data }}</pre>
            </div>
          </div>
          <div v-if="finalOutput" class="final-output">{{ finalOutput }}</div>
        </div>
      </section>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue';
import MainLayout from '@/components/layout/MainLayout.vue';
import { SSE } from 'sse.js';
import { useAuthStore } from '@/store/auth';

const reviewing = ref(false);
const steps = ref<{ type: string; data: string }[]>([]);
const finalOutput = ref('');
const outputContainer = ref<HTMLElement>();

function stepLabel(type: string) {
  const labels: Record<string, string> = {
    thought: 'Reasoning',
    action: 'Tool Call',
    observation: 'Observation',
  };
  return labels[type] || type;
}

async function typewriterEffect(text: string) {
  let index = 0;
  const speed = 25;
  finalOutput.value = '';
  while (index < text.length) {
    await new Promise((resolve) => setTimeout(resolve, speed));
    finalOutput.value = text.substring(0, index + 1);
    index++;
  }
}

async function startReview() {
  reviewing.value = true;
  steps.value = [];
  finalOutput.value = '';
  let receivedFinal = false;

  const authStore = useAuthStore();
  const source = new SSE('http://127.0.0.1:8000/api/v1/code-review/stream', {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authStore.token}`,
    },
    method: 'POST',
    payload: JSON.stringify({ message: '请审查当前所有待处理的合并请求' }),
  });

  source.addEventListener('intent', (e: any) => {
    const data = JSON.parse(e.data);
    steps.value.push({ type: 'thought', data: `意图: ${data.intent}` });
  });

  source.addEventListener('thought', (e: any) => {
    const data = JSON.parse(e.data);
    if (data.content) steps.value.push({ type: 'thought', data: data.content });
  });

  source.addEventListener('action', (e: any) => {
    const data = JSON.parse(e.data);
    steps.value.push({
      type: 'action',
      data: `工具: ${data.tool}\n参数: ${JSON.stringify(data.input, null, 2)}`,
    });
  });

  source.addEventListener('observation', (e: any) => {
    const data = JSON.parse(e.data);
    if (data.content) steps.value.push({ type: 'observation', data: data.content });
  });

  source.addEventListener('final', (e: any) => {
    const data = JSON.parse(e.data);
    receivedFinal = true;
    source.close();
    typewriterEffect(data.content).then(() => {
      reviewing.value = false;
      nextTick(() => {
        if (outputContainer.value) {
          outputContainer.value.scrollTop = outputContainer.value.scrollHeight;
        }
      });
    });
  });

  source.onerror = (event: any) => {
    if (receivedFinal) return;
    console.error('Code review SSE error', event);
    finalOutput.value = '代码审查连接发生错误，请重试。';
    source.close();
    reviewing.value = false;
  };
}
</script>

<style scoped>
.run-button {
  height: 40px;
  border-radius: 10px;
  font-weight: 760;
}

.review-grid {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 16px;
}

.review-summary,
.review-output {
  padding: 18px;
}

.review-summary h3 {
  margin: 0;
  color: var(--dm-ink);
  font-size: 20px;
  line-height: 1.35;
}

.summary-list {
  display: grid;
  gap: 8px;
  margin-top: 18px;
}

.summary-list span {
  border: 1px solid var(--dm-border);
  border-radius: 10px;
  background: #fff;
  color: var(--dm-ink-soft);
  padding: 10px;
  font-size: 13px;
  font-weight: 650;
}

.review-output {
  overflow-y: auto;
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

.step-card {
  margin: 10px 0;
  border: 1px solid var(--dm-border);
  border-radius: 12px;
  background: #fbfdff;
  padding: 12px;
}

.step-card strong {
  color: var(--dm-blue);
  font-size: 12px;
}

.step-card.action strong {
  color: var(--dm-amber);
}

.step-card.observation strong {
  color: var(--dm-green);
}

.step-card pre {
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--dm-ink-soft);
  font-family: var(--dm-mono);
  font-size: 12px;
  line-height: 1.6;
  margin: 8px 0 0;
}

.final-output {
  margin-top: 16px;
  border: 1px solid rgba(15, 159, 110, 0.18);
  border-radius: 14px;
  background: var(--dm-green-soft);
  color: var(--dm-ink);
  padding: 16px;
  font-size: 14px;
  line-height: 1.7;
  white-space: pre-wrap;
}

@media (max-width: 980px) {
  .review-grid {
    grid-template-columns: 1fr;
  }
}
</style>
