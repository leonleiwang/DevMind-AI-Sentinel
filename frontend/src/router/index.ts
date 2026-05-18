// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '@/views/LoginView.vue';
import FaultDiagnosisView from '@/views/FaultDiagnosisView.vue';
import { useAuthStore } from '@/store/auth';
import CodeReviewView from '@/views/CodeReviewView.vue';
import DocQAView from '@/views/DocQAView.vue'
import DashboardView from '@/views/DashboardView.vue';
import IncidentAnalysisView from '@/views/IncidentAnalysisView.vue';


const routes = [
  { path: '/', redirect: '/fault-diagnosis' },
  { path: '/login', component: LoginView },
  {
    path: '/fault-diagnosis',
    component: FaultDiagnosisView,
    meta: { requiresAuth: true },
  },
  { path: '/incident-analysis', component: IncidentAnalysisView, meta: { requiresAuth: true } },
  { path: '/code-review', component: CodeReviewView, meta: { requiresAuth: true } },
  { path: '/doc-qa', component: DocQAView, meta: { requiresAuth: true } },
  { path: '/dashboard', component: DashboardView, meta: { requiresAuth: true } }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 全局守卫
router.beforeEach((to, _from, next) => {    // 将 from 改为 _from（前导下划线表示有意不使用）
  const auth = useAuthStore();
  if (to.meta.requiresAuth && !auth.token) {
    next('/login');
  } else {
    next();
  }
});

export default router;
