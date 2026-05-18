<!-- src/views/DashboardView.vue -->
<template>
  <MainLayout>
    <div class="dm-page dm-page-scroll">
      <header class="dm-page-header">
        <div>
          <p class="dm-eyebrow">Observability</p>
          <h1 class="dm-title">监控大盘</h1>
          <p class="dm-subtitle">
            展示运行指标、延迟趋势和 Agent 平台健康状态。适合在面试中从“会用 Agent”切到“懂工程治理”。
          </p>
        </div>
        <div class="dm-chip-row">
          <span class="dm-chip is-green">Auto refresh 5s</span>
          <span class="dm-chip is-blue">Prometheus style</span>
        </div>
      </header>

      <section class="dm-kpi-grid">
        <article class="dm-card dm-kpi-card">
          <div class="dm-kpi-label">CPU latest</div>
          <div class="dm-kpi-value">{{ latestCpu }}%</div>
          <div class="dm-kpi-caption">service saturation signal</div>
        </article>
        <article class="dm-card dm-kpi-card">
          <div class="dm-kpi-label">Memory latest</div>
          <div class="dm-kpi-value">{{ latestMemory }}%</div>
          <div class="dm-kpi-caption">capacity pressure</div>
        </article>
        <article class="dm-card dm-kpi-card">
          <div class="dm-kpi-label">Latency latest</div>
          <div class="dm-kpi-value">{{ latestLatency }}s</div>
          <div class="dm-kpi-caption">request timeline</div>
        </article>
        <article class="dm-card dm-kpi-card">
          <div class="dm-kpi-label">Agent health</div>
          <div class="dm-kpi-value">OK</div>
          <div class="dm-kpi-caption">dashboard reachable</div>
        </article>
      </section>

      <div class="charts-grid">
        <section class="chart-card dm-card">
          <div class="chart-heading">
            <div>
              <p>Resource</p>
              <h3>CPU 使用率</h3>
            </div>
            <span>percentage</span>
          </div>
          <v-chart :option="cpuOption" autoresize class="chart" />
        </section>

        <section class="chart-card dm-card">
          <div class="chart-heading">
            <div>
              <p>Resource</p>
              <h3>内存使用率</h3>
            </div>
            <span>percentage</span>
          </div>
          <v-chart :option="memOption" autoresize class="chart" />
        </section>

        <section class="chart-card dm-card full-width">
          <div class="chart-heading">
            <div>
              <p>Experience</p>
              <h3>请求延迟趋势</h3>
            </div>
            <span>last 10 minutes</span>
          </div>
          <v-chart :option="latencyOption" autoresize class="chart" />
        </section>
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

const latestCpu = computed(() => lastValue(metrics.value?.cpu.values));
const latestMemory = computed(() => lastValue(metrics.value?.memory.values));
const latestLatency = computed(() => lastValue(metrics.value?.latency.values));

function lastValue(values?: number[]) {
  if (!values?.length) return '--';
  return Number(values[values.length - 1]).toFixed(1);
}

const axisStyle = {
  axisLine: { lineStyle: { color: 'rgba(18, 32, 54, 0.16)' } },
  axisTick: { show: false },
  axisLabel: { color: '#7b8494' },
};

const grid = { left: 34, right: 18, top: 26, bottom: 28 };

const cpuOption = computed(() => ({
  grid,
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: metrics.value?.cpu.labels || [], ...axisStyle },
  yAxis: { type: 'value', min: 0, max: 100, splitLine: { lineStyle: { color: 'rgba(18, 32, 54, 0.08)' } }, ...axisStyle },
  series: [{ data: metrics.value?.cpu.values || [], type: 'bar', color: '#1d4ed8', barWidth: 18, itemStyle: { borderRadius: [6, 6, 0, 0] } }],
}));

const memOption = computed(() => ({
  grid,
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: metrics.value?.memory.labels || [], ...axisStyle },
  yAxis: { type: 'value', min: 0, max: 100, splitLine: { lineStyle: { color: 'rgba(18, 32, 54, 0.08)' } }, ...axisStyle },
  series: [{ data: metrics.value?.memory.values || [], type: 'bar', color: '#0f9f6e', barWidth: 18, itemStyle: { borderRadius: [6, 6, 0, 0] } }],
}));

const latencyOption = computed(() => ({
  grid,
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: metrics.value?.latency.timestamps.map(ts => new Date(ts * 1000).toLocaleTimeString()) || [],
    ...axisStyle,
  },
  yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(18, 32, 54, 0.08)' } }, ...axisStyle },
  series: [{ data: metrics.value?.latency.values || [], type: 'line', smooth: true, symbol: 'circle', symbolSize: 7, lineStyle: { width: 3, color: '#1d4ed8' }, itemStyle: { color: '#1d4ed8' }, areaStyle: { color: 'rgba(29, 78, 216, 0.08)' } }],
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
  timer = window.setInterval(fetchMetrics, 5000);
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});
</script>

<style scoped>
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.chart-card {
  padding: 18px;
}

.chart-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.chart-heading p,
.chart-heading h3 {
  margin: 0;
}

.chart-heading p,
.chart-heading span {
  color: var(--dm-ink-muted);
  font-size: 12px;
  font-weight: 650;
}

.chart-heading h3 {
  margin-top: 5px;
  color: var(--dm-ink);
  font-size: 18px;
}

.chart {
  height: 280px;
}

.full-width {
  grid-column: span 2;
}

@media (max-width: 980px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }

  .full-width {
    grid-column: auto;
  }
}
</style>
