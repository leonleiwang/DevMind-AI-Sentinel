import { SSE } from 'sse.js';
import { useAuthStore } from '@/store/auth';

export interface IncidentAnalysisRequest {
  message: string;
  conversation_id?: string;
}

export function connectIncidentAnalysisStream(
  payload: IncidentAnalysisRequest,
  onMessage: (event: string, data: any) => void,
  onError?: (error: any) => void
) {
  const authStore = useAuthStore();
  const token = authStore.token;
  if (!token) throw new Error('未登录');
  let receivedFinal = false;

  const source = new SSE('http://127.0.0.1:8000/api/v1/incident-analysis/stream', {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    method: 'POST',
    payload: JSON.stringify(payload),
  });

  for (const eventName of ['intent', 'thought', 'action', 'observation', 'final']) {
    source.addEventListener(eventName, (e: any) => {
      if (eventName === 'final') receivedFinal = true;
      onMessage(eventName, JSON.parse(e.data));
      if (eventName === 'final') source.close();
    });
  }

  source.onerror = (e: any) => {
    if (receivedFinal) return;
    console.error('Incident SSE error', e);
    if (onError) onError(e);
    source.close();
  };

  return source;
}
