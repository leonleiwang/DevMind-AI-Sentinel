<!-- src/views/CodeReviewView.vue -->
<template>
  <MainLayout>
    <div class="page-container">
      <h2>代码审查</h2>
      <div class="content-wrapper">
        <el-button type="primary" @click="startReview" :loading="reviewing" class="action-btn">
          开始审查待处理 MR
        </el-button>
        <div class="review-output" ref="outputContainer">
          <div v-if="steps.length" class="review-steps">
            <div v-for="(step, idx) in steps" :key="idx" class="step-card">
              <el-tag :type="step.type === 'thought' ? 'info' : step.type === 'action' ? 'warning' : ''">
                {{ step.type }}
              </el-tag>
              <pre>{{ step.data }}</pre>
            </div>
          </div>
          <div v-if="finalOutput" class="final-output">{{ finalOutput }}</div>
        </div>
      </div>
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

// 打字机效果
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
    // 启动打字机，完成后关闭连接
    typewriterEffect(data.content).then(() => {
      source.close();
      reviewing.value = false;
      nextTick(() => {
        if (outputContainer.value) {
          outputContainer.value.scrollTop = outputContainer.value.scrollHeight;
        }
      });
    });
  });

  source.onerror = () => {
    finalOutput.value = '代码审查连接发生错误，请重试。';
    source.close();
    reviewing.value = false;
  };
}
</script>

<style scoped>
.page-container {
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
  padding: 20px 20px 0;
}
.page-container h2 {
  margin: 0 0 15px;
  color: #303133;
}
.content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin-bottom: 10px;  /* 操作按钮没必要底部留白太多，用在这已经足够 */
}
.action-btn {
  width: 200px;
  margin-bottom: 15px;
}
.review-output {
  flex: 1;
  overflow-y: auto;
  padding-right: 5px;
}
.step-card {
  margin: 10px 0;
  padding: 12px;
  background: #f8f9fa;
  border-left: 4px solid #409eff;
  border-radius: 6px;
}
.step-card pre {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 13px;
  margin: 8px 0 0;
  background: transparent;
}
.final-output {
  margin-top: 20px;
  padding: 16px;
  background: #f0f5ff;
  border: 1px solid #d0e2ff;
  border-radius: 8px;
  font-size: 15px;
  line-height: 1.6;
  white-space: pre-wrap;
}
</style>