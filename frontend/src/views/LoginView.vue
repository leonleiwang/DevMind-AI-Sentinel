<!-- src/views/LoginView.vue -->
<template>
  <el-container class="login-container">
    <el-card class="login-card">
      <h2>DevMind AI Sentinel</h2>
      <el-form :model="form" label-width="80px">
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading">登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </el-container>
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
    // 可选：获取用户信息
    const userRes = await authApi.getMe();
    authStore.setUser(userRes.data);
    router.push('/fault-diagnosis');
  } catch (e: any) {
    alert('登录失败：' + (e.response?.data?.detail || '未知错误'));
    // 简单处理，后续可用 ElMessage
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  justify-content: center;
  align-items: center;
}
.login-card {
  width: 400px;
}
</style>