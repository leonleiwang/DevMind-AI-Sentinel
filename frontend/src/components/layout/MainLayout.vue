<!-- src/components/layout/MainLayout.vue -->
<template>
  <div class="app-shell">
    <aside class="sidebar">
      <router-link class="brand" to="/fault-diagnosis">
        <span class="brand-mark">D</span>
        <span>
          <strong>DevMind</strong>
          <small>AI Sentinel</small>
        </span>
      </router-link>

      <div class="nav-section">
        <p>Operate</p>
        <router-link to="/fault-diagnosis" active-class="active-link">故障排查</router-link>
        <router-link to="/incident-analysis" active-class="active-link">事故 RCA</router-link>
        <router-link to="/code-review" active-class="active-link">代码审查</router-link>
        <router-link to="/doc-qa" active-class="active-link">知识库问答</router-link>
      </div>

      <div class="nav-section">
        <p>Observe</p>
        <router-link to="/dashboard" active-class="active-link">监控大盘</router-link>
      </div>

      <div class="sidebar-card">
        <span class="status-dot"></span>
        <div>
          <strong>Agent Runtime</strong>
          <small>Trace / Tool / Evidence</small>
        </div>
      </div>
    </aside>

    <section class="workspace">
      <header class="topbar">
        <div>
          <p class="topbar-kicker">Operations Intelligence Platform</p>
          <strong>Multi-agent workflow observability</strong>
        </div>
        <div class="topbar-actions">
          <span class="health-pill">Healthy</span>
          <el-button class="dm-shell-button" size="small" @click="logout" plain>退出</el-button>
        </div>
      </header>

      <main class="content">
        <slot />
      </main>
    </section>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/auth';

const router = useRouter();
const authStore = useAuthStore();

function logout() {
  authStore.logout();
  router.push('/login');
}
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 276px minmax(0, 1fr);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.72), rgba(245, 247, 251, 0.92)),
    var(--dm-bg);
}

.sidebar {
  min-height: 100vh;
  border-right: 1px solid var(--dm-border);
  background: rgba(255, 255, 255, 0.76);
  backdrop-filter: blur(28px);
  padding: 22px 18px;
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--dm-ink);
  text-decoration: none;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: linear-gradient(145deg, #0b1220, #1d4ed8);
  color: #fff;
  font-weight: 800;
  box-shadow: 0 16px 35px rgba(29, 78, 216, 0.22);
}

.brand strong,
.brand small {
  display: block;
}

.brand strong {
  font-size: 16px;
  letter-spacing: -0.02em;
}

.brand small {
  margin-top: 2px;
  color: var(--dm-ink-muted);
  font-size: 12px;
}

.nav-section {
  display: grid;
  gap: 6px;
}

.nav-section p {
  margin: 0 0 6px 10px;
  color: var(--dm-ink-muted);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.nav-section a {
  border-radius: 10px;
  color: var(--dm-ink-soft);
  padding: 10px 12px;
  text-decoration: none;
  font-size: 14px;
  font-weight: 680;
  transition: background 0.18s, color 0.18s, transform 0.18s;
}

.nav-section a:hover {
  background: rgba(29, 78, 216, 0.07);
  color: var(--dm-blue);
}

.nav-section a.active-link {
  background: var(--dm-blue-soft);
  color: var(--dm-blue);
}

.sidebar-card {
  margin-top: auto;
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid var(--dm-border);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.78);
  padding: 12px;
}

.sidebar-card strong,
.sidebar-card small {
  display: block;
}

.sidebar-card strong {
  font-size: 13px;
}

.sidebar-card small {
  margin-top: 3px;
  color: var(--dm-ink-muted);
  font-size: 11px;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: var(--dm-green);
  box-shadow: 0 0 0 5px rgba(15, 159, 110, 0.12);
}

.workspace {
  min-width: 0;
  min-height: 100vh;
  display: grid;
  grid-template-rows: 68px minmax(0, 1fr);
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border-bottom: 1px solid var(--dm-border);
  background: rgba(255, 255, 255, 0.64);
  backdrop-filter: blur(28px);
  padding: 0 28px;
}

.topbar-kicker {
  margin: 0 0 3px;
  color: var(--dm-ink-muted);
  font-size: 12px;
  font-weight: 650;
}

.topbar strong {
  color: var(--dm-ink);
  font-size: 14px;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.health-pill {
  border-radius: 999px;
  background: var(--dm-green-soft);
  color: #087451;
  padding: 6px 10px;
  font-size: 12px;
  font-weight: 750;
}

.content {
  min-height: 0;
  padding: 28px;
}

@media (max-width: 900px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    min-height: auto;
    position: sticky;
    top: 0;
    z-index: 20;
    flex-direction: row;
    overflow-x: auto;
  }

  .nav-section,
  .sidebar-card {
    display: none;
  }
}
</style>
