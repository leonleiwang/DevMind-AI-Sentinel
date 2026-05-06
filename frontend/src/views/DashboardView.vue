<!-- src/views/DashboardView.vue -->
<template>
  <MainLayout>
    <div class="dashboard-container">
      <h2>监控大盘</h2>
      <div class="charts-grid">
        <div class="chart-card">
          <h3>CPU 使用率 (%)</h3>
          <v-chart :option="cpuOption" autoresize style="height: 280px" />
        </div>
        <div class="chart-card">
          <h3>内存使用率 (%)</h3>
          <v-chart :option="memOption" autoresize style="height: 280px" />
        </div>
        <div class="chart-card full-width">
          <h3>请求延迟 (秒) - 最近10分钟</h3>
          <v-chart :option="latencyOption" autoresize style="height: 280px" />
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import MainLayout from '@/components/layout/MainLayout.vue';
import VChart from 'vue-echarts';
import { use } from 'echarts/core';
import { BarChart, LineChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import axios from 'axios';

use([BarChart, LineChart, CanvasRenderer, GridComponent, TooltipComponent, LegendComponent]);

interface Metrics {
  cpu: { labels: string[]; values: number[] };
  memory: { labels: string[]; values: number[] };
  latency: { timestamps: number[]; values: number[] };
}

const metrics = ref<Metrics | null>(null);
let timer: number | null = null;

const cpuOption = computed(() => ({
  xAxis: { type: 'category', data: metrics.value?.cpu.labels || [] },
  yAxis: { type: 'value', min: 0, max: 100 },   // 固定范围
  series: [{ data: metrics.value?.cpu.values || [], type: 'bar', color: '#5470c6' }],
}));

const memOption = computed(() => ({
  xAxis: { type: 'category', data: metrics.value?.memory.labels || [] },
  yAxis: { type: 'value', min: 0, max: 100 },   // 固定范围
  series: [{ data: metrics.value?.memory.values || [], type: 'bar', color: '#fac858' }],
}));

const latencyOption = computed(() => ({
  xAxis: {
    type: 'category',
    data: metrics.value?.latency.timestamps.map(ts => new Date(ts * 1000).toLocaleTimeString()) || [],
  },
  yAxis: { type: 'value' },
  series: [{ data: metrics.value?.latency.values || [], type: 'line', smooth: true }],
}));

async function fetchMetrics() {
  try {
    const res = await axios.get('http://127.0.0.1:8000/api/v1/monitoring/metrics', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    });
    metrics.value = res.data;
  } catch (e) {
    console.error('获取监控数据失败', e);
  }
}

onMounted(() => {
  fetchMetrics();
  timer = window.setInterval(fetchMetrics, 5000); // 每5秒刷新
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  height: calc(100vh - 60px);
  overflow-y: auto;
}
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
.chart-card {
  background: #fff;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  /* 以下确保卡片不被撑开 */
  display: flex;
  flex-direction: column;
}
.chart-card h3 {
  margin: 0 0 10px;
}
.full-width {
  grid-column: span 2;
}
</style>