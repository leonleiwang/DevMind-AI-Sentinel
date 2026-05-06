<!-- src/views/FaultDiagnosisView.vue -->
<template>
  <MainLayout>
    <div class="page-container">
      <h2>故障排查</h2>
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
.page-container {
  height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
  padding: 20px 20px 0;
}
.page-container h2 {
  margin: 0 0 10px;
  color: #303133;
}
.chat-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin-bottom: 50px;  /* 输入框与底部距离 */
}
</style>