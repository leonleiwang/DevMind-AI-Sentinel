<!-- src/views/DocQAView.vue -->
<template>
  <MainLayout>
    <div class="qa-container">
      <h2>文档智能问答</h2>
      <div class="chat-window" ref="chatWindow">
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          class="message"
          :class="msg.role"
        >
          <div class="bubble">
            <div v-if="msg.steps && msg.steps.length > 0">
              <div
                v-for="(step, sIdx) in msg.steps"
                :key="sIdx"
                class="step-card"
              >
                <el-tag size="small" :type="step.type === 'thought' ? 'info' : ''">
                  {{ step.type }}
                </el-tag>
                <pre>{{ step.data }}</pre>
              </div>
            </div>
            <div class="final-text">{{ msg.content }}</div>
          </div>
        </div>
      </div>
      <InputArea @send="askQuestion" :busy="asking" />
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue';
import MainLayout from '@/components/layout/MainLayout.vue';
import InputArea from '@/components/chat/InputArea.vue';
import { SSE } from 'sse.js';
import { useAuthStore } from '@/store/auth';

const messages = ref<any[]>([]);
const asking = ref(false);
const chatWindow = ref<HTMLElement>();

// 打字机效果
async function typewriterEffect(target: any, text: string) {
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

  const userMsg = { role: 'user', content: message, steps: [] };
  const agentMsg = { role: 'agent', content: '', steps: [] };
  messages.value.push(userMsg, agentMsg);
  asking.value = true;

  nextTick(() => {
    if (chatWindow.value) {
      chatWindow.value.scrollTop = chatWindow.value.scrollHeight;
    }
  });

  const authStore = useAuthStore();
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
    // 启动打字机，完成后关闭连接
    typewriterEffect(agentMsg, data.content).then(() => {
      source.close();
      asking.value = false;
      nextTick(() => {
        if (chatWindow.value) {
          chatWindow.value.scrollTop = chatWindow.value.scrollHeight;
        }
      });
    });
  });

  source.onerror = () => {
    agentMsg.content = '连接错误，请重试。';
    source.close();
    asking.value = false;
  };
}
</script>

<style scoped>
.qa-container {
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
  padding: 20px 20px 0;
}
.qa-container h2 {
  margin: 0 0 10px;
  color: #303133;
}
.chat-window {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 10px;
  padding-right: 5px;
}
.input-area {
  display: flex;
  gap: 10px;
  padding: 10px 0;
  background: #fff;
  margin-bottom: 50px;  /* 关键：输入框底部留出空间 */
}
.message {
  margin: 10px 0;
  display: flex;
}
.user {
  justify-content: flex-end;
}
.agent {
  justify-content: flex-start;
}
.bubble {
  max-width: 70%;
  padding: 10px 15px;
  border-radius: 12px;
  background: #f0f2f5;
  word-break: break-word;
}
.user .bubble {
  background: #d9e1ff;
}
.final-text {
  margin-top: 8px;
  white-space: pre-wrap;
}
.step-card {
  margin: 6px 0;
  padding: 8px;
  background: #ffffff;
  border-left: 3px solid #409eff;
  border-radius: 4px;
}
.step-card pre {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 13px;
  margin: 4px 0 0;
  background: transparent;
}
</style>