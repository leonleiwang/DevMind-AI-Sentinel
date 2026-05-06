<!-- src/components/layout/MainLayout.vue -->
<template>
  <el-container>
    <el-header>
      <span>DevMind AI Sentinel</span>
      <div class="nav-actions">
        <router-link to="/fault-diagnosis" active-class="active-link">故障排查</router-link>
        <router-link to="/code-review" active-class="active-link">代码审查</router-link>
        <router-link to="/doc-qa" active-class="active-link">文档问答</router-link>
        <router-link to="/dashboard" active-class="active-link">监控大盘</router-link>
        <el-button @click="logout" size="small" type="danger" plain>退出</el-button>
      </div>
    </el-header>
    <el-main>
      <slot />
    </el-main>
  </el-container>
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
.el-container {
  height: 100vh;
}
.el-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #409eff;
  color: white;
  padding: 0 20px;
  height: 60px;
}
.nav-actions {
  display: flex;
  gap: 20px;
  align-items: center;
}
.nav-actions a {
  color: white;
  text-decoration: none;
  font-weight: 500;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}
.nav-actions a:hover {
  background: rgba(255, 255, 255, 0.2);
}
.active-link {
  background: rgba(255, 255, 255, 0.3);
}
.el-main {
  padding: 0;
  height: calc(100vh - 60px);
  overflow: hidden;
}
</style>