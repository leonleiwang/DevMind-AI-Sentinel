// src/api/chat.ts
import { SSE } from 'sse.js';
import { useAuthStore } from '@/store/auth';

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export function connectChatStream(
  payload: ChatRequest,
  onMessage: (event: string, data: any) => void,
  onError?: (error: any) => void
) {
  const authStore = useAuthStore();
  const token = authStore.token;
  if (!token) throw new Error('未登录');
  let receivedFinal = false;

  const source = new SSE('http://127.0.0.1:8000/api/v1/chat/stream', {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    method: 'POST',
    payload: JSON.stringify(payload),
  });

  source.addEventListener('intent', (e: any) => {
    onMessage('intent', JSON.parse(e.data));
  });

  source.addEventListener('thought', (e: any) => {
    onMessage('thought', JSON.parse(e.data));
  });

  source.addEventListener('action', (e: any) => {
    onMessage('action', JSON.parse(e.data));
  });

  source.addEventListener('observation', (e: any) => {
    onMessage('observation', JSON.parse(e.data));
  });

  source.addEventListener('final', (e: any) => {
    receivedFinal = true;
    onMessage('final', JSON.parse(e.data));
    source.close();
  });

  source.onerror = (e: any) => {
    if (receivedFinal) return;
    console.error('Chat SSE error', e);
    if (onError) onError(e);
    source.close();
  };

  return source;
}
