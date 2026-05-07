<script setup>
import { ref, onMounted } from 'vue'
import { getSyncStatus } from '../api'

const syncData = ref(null)
const loading = ref(true)
const error = ref(null)

const fetchStatus = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await getSyncStatus()
    syncData.value = res.data
  } catch (err) {
    error.value = '获取同步状态失败'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchStatus)
</script>

<template>
  <div class="sync-page">
    <div class="page-header">
      <h1 class="page-title">同步面板</h1>
      <button class="btn btn-primary" @click="fetchStatus">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
          <polyline points="23 4 23 10 17 10" />
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
        </svg>
        刷新
      </button>
    </div>

    <!-- Loading -->
    <div class="loading-state" v-if="loading">
      <div class="loading-spinner"></div>
    </div>

    <!-- Error -->
    <div class="state-card error-state" v-if="error && !loading">
      <p>{{ error }}</p>
    </div>

    <!-- Sync overview -->
    <div class="stats-grid" v-if="syncData && !loading">
      <div class="stat-card">
        <div class="stat-value">{{ syncData.total_plugins }}</div>
        <div class="stat-label">总插件数</div>
      </div>
      <div class="stat-card success">
        <div class="stat-value">{{ syncData.synced }}</div>
        <div class="stat-label">已同步</div>
      </div>
      <div class="stat-card warning">
        <div class="stat-value">{{ syncData.pending }}</div>
        <div class="stat-label">待同步</div>
      </div>
      <div class="stat-card danger">
        <div class="stat-value">{{ syncData.failed }}</div>
        <div class="stat-label">失败</div>
      </div>
    </div>

    <!-- Last sync time -->
    <div class="sync-info" v-if="syncData?.last_updated">
      最近同步: {{ syncData.last_updated }}
    </div>

    <!-- Plugin sync table -->
    <div class="sync-table" v-if="syncData?.plugins?.length">
      <table>
        <thead>
          <tr>
            <th>插件名称</th>
            <th>类型</th>
            <th>状态</th>
            <th>Stars</th>
            <th>最近同步</th>
            <th>Commit</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in syncData.plugins" :key="p.name">
            <td class="cell-name">{{ p.display_name || p.name }}</td>
            <td><span class="type-badge">{{ p.type }}</span></td>
            <td>
              <span :class="['status-badge', 'status-' + p.status]">
                {{ p.status }}
              </span>
            </td>
            <td class="cell-stars" v-if="p.stars">★ {{ (p.stars / 1000).toFixed(1) }}k</td>
            <td class="cell-stars" v-else>-</td>
            <td class="cell-date">{{ p.last_sync_at ? p.last_sync_at.slice(0, 10) : '-' }}</td>
            <td class="cell-sha">{{ p.commit_sha || '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.sync-page {
  max-width: 900px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
}

.page-title {
  font-family: var(--font-display);
  font-size: 20px;
  color: var(--color-text);
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: var(--space-12);
}

.loading-spinner {
  width: 36px;
  height: 36px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.state-card {
  padding: var(--space-8);
  text-align: center;
  background: var(--color-card);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.stat-card {
  background: var(--color-card);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  text-align: center;
}

.stat-value {
  font-family: var(--font-display);
  font-size: 28px;
  font-weight: 600;
  color: var(--color-text);
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-muted);
  margin-top: var(--space-1);
}

.stat-card.success .stat-value { color: var(--color-success); }
.stat-card.warning .stat-value { color: var(--color-warning); }
.stat-card.danger .stat-value { color: var(--color-error); }

.sync-info {
  font-size: 13px;
  color: var(--color-text-dim);
  margin-bottom: var(--space-4);
}

.sync-table {
  background: var(--color-card);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  text-align: left;
  font-family: var(--font-display);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--color-text-muted);
  padding: var(--space-3) var(--space-4);
  background: var(--color-bg-subtle);
  border-bottom: 1px solid var(--color-border-subtle);
}

td {
  padding: var(--space-3) var(--space-4);
  font-size: 13px;
  color: var(--color-text);
  border-bottom: 1px solid var(--color-border-subtle);
}

tr:last-child td {
  border-bottom: none;
}

.cell-name {
  font-family: var(--font-display);
}

.cell-stars {
  color: var(--color-primary);
  font-size: 12px;
}

.cell-date {
  font-size: 12px;
  color: var(--color-text-muted);
}

.cell-sha {
  font-family: var(--font-display);
  font-size: 11px;
  color: var(--color-text-dim);
}

.type-badge {
  font-size: 11px;
  color: var(--color-text-dim);
  background: var(--color-bg-subtle);
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.status-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.status-success { color: var(--color-success); background: var(--color-success-muted, rgba(74, 222, 128, 0.1)); }
.status-failed { color: var(--color-error); background: var(--color-error-muted, rgba(248, 113, 113, 0.1)); }
.status-pending { color: var(--color-warning); background: var(--color-warning-muted, rgba(250, 204, 21, 0.1)); }

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
