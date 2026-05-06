// src/store/auth.ts
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || '');
  const user = ref<{ email: string; full_name: string } | null>(null);

  function setToken(newToken: string) {
    token.value = newToken;
    localStorage.setItem('access_token', newToken);
  }

  function setUser(u: any) {
    user.value = u;
  }

  function logout() {
    token.value = '';
    user.value = null;
    localStorage.removeItem('access_token');
  }

  return { token, user, setToken, setUser, logout };
});