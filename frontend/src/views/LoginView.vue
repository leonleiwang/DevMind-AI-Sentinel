<!-- src/views/LoginView.vue -->
<template>
  <main class="login-page">
    <section class="login-hero">
      <div class="brand-lockup">
        <span class="brand-mark">D</span>
        <span>
          <strong>DevMind AI Sentinel</strong>
          <small>Agentic operations platform</small>
        </span>
      </div>

      <div class="hero-copy">
        <p class="dm-eyebrow">SRE Command Center</p>
        <h1>让多 Agent 运维过程变得可观察、可解释、可演示。</h1>
        <p>
          面向故障排查、事故复盘、代码审查和文档问答的智能运维平台。界面参考 LLM observability
          工具的 trace 工作流，并保持 Apple 风格的清爽留白。
        </p>
      </div>

      <div class="preview-panel">
        <div class="preview-header">
          <span>Live incident trace</span>
          <strong>p95 latency spike</strong>
        </div>
        <div class="trace-row">
          <span class="trace-index">01</span>
          <div>
            <strong>Intent</strong>
            <p>识别用户在询问订单服务延迟事故根因。</p>
          </div>
        </div>
        <div class="trace-row">
          <span class="trace-index">02</span>
          <div>
            <strong>Tool call</strong>
            <p>查询 Prometheus、GitLab deploy 与 incident timeline。</p>
          </div>
        </div>
        <div class="trace-row is-success">
          <span class="trace-index">03</span>
          <div>
            <strong>Evidence</strong>
            <p>发布后数据库连接池耗尽，与错误率上升时间重合。</p>
          </div>
        </div>
      </div>
    </section>

    <section class="login-panel dm-card">
      <p class="dm-eyebrow">Demo access</p>
      <h2>登录控制台</h2>
      <p class="panel-copy">使用测试账号进入故障排查、RCA、代码审查和监控大盘演示。</p>

      <el-form :model="form" label-position="top">
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-button class="login-btn" type="primary" @click="handleLogin" :loading="loading">
          进入 DevMind
        </el-button>
      </el-form>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { authApi } from '@/api/auth';
import { useAuthStore } from '@/store/auth';

const router = useRouter();
const authStore = useAuthStore();
const loading = ref(false);

const form = ref({
  email: 'leiwang@163.com',
  password: '',
});

async function handleLogin() {
  loading.value = true;
  try {
    const { data } = await authApi.login(form.value);
    authStore.setToken(data.access_token);
    const userRes = await authApi.getMe();
    authStore.setUser(userRes.data);
    router.push('/fault-diagnosis');
  } catch (e: any) {
    const detail = e.response?.data?.detail;
    const message = detail || (e.request ? '无法连接后端或被 CORS 拦截，请确认后端已重启并允许当前前端地址。' : '未知错误');
    alert(`登录失败：${message}`);
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 430px;
  gap: 48px;
  align-items: center;
  padding: 48px;
  background:
    radial-gradient(circle at 18% 18%, rgba(29, 78, 216, 0.14), transparent 32%),
    radial-gradient(circle at 76% 70%, rgba(15, 159, 110, 0.1), transparent 28%),
    var(--dm-bg);
}

.login-hero {
  min-height: 680px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.brand-lockup {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(145deg, #0b1220, #1d4ed8);
  color: #fff;
  font-weight: 800;
}

.brand-lockup strong,
.brand-lockup small {
  display: block;
}

.brand-lockup small {
  margin-top: 3px;
  color: var(--dm-ink-muted);
}

.hero-copy {
  max-width: 760px;
}

.hero-copy h1 {
  margin: 0;
  color: var(--dm-ink);
  font-size: clamp(44px, 7vw, 78px);
  line-height: 0.96;
  letter-spacing: -0.055em;
  text-wrap: pretty;
}

.hero-copy p:last-child {
  max-width: 620px;
  margin: 24px 0 0;
  color: var(--dm-ink-soft);
  font-size: 17px;
  line-height: 1.8;
}

.preview-panel {
  max-width: 720px;
  border: 1px solid var(--dm-border);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.74);
  box-shadow: var(--dm-shadow);
  backdrop-filter: blur(22px);
  padding: 18px;
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: var(--dm-ink-muted);
  font-size: 12px;
}

.preview-header strong {
  color: var(--dm-ink);
}

.trace-row {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr);
  gap: 12px;
  margin-top: 12px;
  border: 1px solid var(--dm-border);
  border-radius: 14px;
  background: #fff;
  padding: 14px;
}

.trace-index {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 999px;
  background: var(--dm-blue-soft);
  color: var(--dm-blue);
  font-size: 12px;
  font-weight: 800;
}

.trace-row.is-success .trace-index {
  background: var(--dm-green-soft);
  color: #087451;
}

.trace-row strong,
.trace-row p {
  margin: 0;
}

.trace-row p {
  margin-top: 4px;
  color: var(--dm-ink-muted);
  font-size: 13px;
}

.login-panel {
  padding: 28px;
}

.login-panel h2 {
  margin: 0;
  color: var(--dm-ink);
  font-size: 28px;
}

.panel-copy {
  margin: 10px 0 24px;
  color: var(--dm-ink-soft);
  line-height: 1.7;
}

.login-btn {
  width: 100%;
  height: 44px;
  border-radius: 10px;
  font-weight: 780;
}

@media (max-width: 980px) {
  .login-page {
    grid-template-columns: 1fr;
    padding: 28px;
  }

  .login-hero {
    min-height: auto;
    gap: 36px;
  }
}
</style>
