<script setup>
import { ref, onMounted, computed } from 'vue'
import { getStatsOverview, getRatingsStats } from '../api'

const stats = ref({
  plugins_count: 0,
  pending_reviews: 0,
  total_ratings: 0,
  marketplace_name: ''
})

const ratingsDistribution = ref({ 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 })
const loading = ref(true)
const error = ref(null)

const totalFromDistribution = computed(() => {
  return Object.values(ratingsDistribution.value).reduce((a, b) => a + b, 0)
})

const averageFromDistribution = computed(() => {
  const total = totalFromDistribution.value
  if (total === 0) return '0.0'
  const sum = Object.entries(ratingsDistribution.value)
    .reduce((acc, [rating, count]) => acc + (parseInt(rating) * count), 0)
  return (sum / total).toFixed(1)
})

const maxCount = computed(() => {
  return Math.max(...Object.values(ratingsDistribution.value), 1)
})

const fetchStats = async () => {
  loading.value = true
  error.value = null
  try {
    const [overviewRes, ratingsRes] = await Promise.all([
      getStatsOverview(),
      getRatingsStats()
    ])
    stats.value = overviewRes.data
    ratingsDistribution.value = ratingsRes.data.distribution
  } catch (err) {
    error.value = '加载统计数据失败'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchStats)
</script>

<template>
  <div class="admin-stats-page">
    <!-- Header -->
    <header class="page-header">
      <h1 class="title">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon">
          <line x1="12" y1="20" x2="12" y2="10" />
          <line x1="18" y1="20" x2="18" y2="4" />
          <line x1="6" y1="20" x2="6" y2="16" />
        </svg>
        统计分析
      </h1>
      <p class="subtitle">插件市场数据概览</p>
    </header>

    <!-- Loading -->
    <div class="loading-state" v-if="loading">
      <div class="loading-spinner"></div>
    </div>

    <!-- Error -->
    <div class="state-card error-state" v-if="error">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="state-icon">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
      <p>{{ error }}</p>
      <button class="btn btn-secondary" @click="fetchStats">重新加载</button>
    </div>

    <!-- Stats content -->
    <div class="stats-content" v-if="!loading && !error">
      <!-- Overview cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="stat-svg packages">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
            </svg>
          </div>
          <div class="stat-value">{{ stats.plugins_count }}</div>
          <div class="stat-label">插件总数</div>
        </div>

        <div class="stat-card">
          <div class="stat-icon-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="stat-svg pending">
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
          </div>
          <div class="stat-value">{{ stats.pending_reviews }}</div>
          <div class="stat-label">待审核</div>
        </div>

        <div class="stat-card">
          <div class="stat-icon-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="stat-svg ratings">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
            </svg>
          </div>
          <div class="stat-value">{{ stats.total_ratings }}</div>
          <div class="stat-label">评分总数</div>
        </div>

        <div class="stat-card">
          <div class="stat-icon-wrap">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="stat-svg average">
              <path d="M18 20V10" />
              <path d="M12 20V4" />
              <path d="M6 20v-6" />
            </svg>
          </div>
          <div class="stat-value">{{ averageFromDistribution }}</div>
          <div class="stat-label">平均评分</div>
        </div>
      </div>

      <!-- Ratings distribution -->
      <div class="distribution-section">
        <h2 class="section-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
          </svg>
          评分分布
        </h2>
        <div class="distribution-chart">
          <div
            v-for="rating in [5, 4, 3, 2, 1]"
            :key="rating"
            class="bar-row"
          >
            <div class="bar-label">
              <span class="star-display">{{ '★'.repeat(rating) }}{{ '☆'.repeat(5 - rating) }}</span>
              <span class="bar-count">{{ ratingsDistribution[rating] }}</span>
            </div>
            <div class="bar-track">
              <div
                class="bar-fill"
                :style="{ width: `${(ratingsDistribution[rating] / maxCount) * 100}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Marketplace info -->
      <div class="info-section" v-if="stats.marketplace_name">
        <h2 class="section-title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="16" x2="12" y2="12" />
            <line x1="12" y1="8" x2="12.01" y2="8" />
          </svg>
          市场信息
        </h2>
        <div class="info-card">
          <p class="marketplace-name">{{ stats.marketplace_name }}</p>
          <p class="marketplace-desc">企业内部 Claude Code 插件仓库</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-stats-page {
  max-width: 800px;
}

.page-header {
  margin-bottom: var(--space-8);
}

.title {
  font-family: var(--font-display);
  font-size: 24px;
  font-weight: 600;
  color: var(--color-text);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-1);
}

.title-icon {
  width: 24px;
  height: 24px;
  color: var(--color-primary);
}

.subtitle {
  font-size: 14px;
  color: var(--color-text-muted);
}

/* States */
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
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-12);
  text-align: center;
  background: var(--color-card);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-xl);
}

.state-icon {
  width: 48px;
  height: 48px;
  color: var(--color-error);
  margin-bottom: var(--space-4);
}

.state-card p {
  font-size: 14px;
  color: var(--color-text-muted);
  margin-bottom: var(--space-5);
}

/* Stats content */
.stats-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--space-4);
}

.stat-card {
  background: var(--color-card);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  text-align: center;
  transition: all var(--transition-normal);
}

.stat-card:hover {
  border-color: var(--color-border-active);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.stat-icon-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: var(--space-3);
}

.stat-svg {
  width: 28px;
  height: 28px;
}

.stat-svg.packages { color: var(--color-primary); }
.stat-svg.pending { color: var(--color-warning); }
.stat-svg.ratings { color: var(--color-primary); }
.stat-svg.average { color: var(--color-success); }

.stat-value {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 500;
  color: var(--color-primary);
  line-height: 1;
  margin-bottom: var(--space-1);
}

.stat-label {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Distribution */
.distribution-section,
.info-section {
  background: var(--color-card);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
}

.section-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--space-5);
}

.distribution-chart {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.bar-row {
  display: grid;
  grid-template-columns: 100px 1fr;
  align-items: center;
  gap: var(--space-3);
}

.bar-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
}

.star-display {
  color: var(--color-primary);
  font-size: 13px;
  letter-spacing: 1px;
}

.bar-count {
  font-family: var(--font-display);
  font-size: 13px;
  color: var(--color-text-muted);
  min-width: 20px;
  text-align: right;
}

.bar-track {
  flex: 1;
  height: 22px;
  background: var(--color-bg);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary), var(--color-primary-hover));
  border-radius: var(--radius-sm);
  transition: width var(--transition-slow);
  min-width: 4px;
}

/* Info card */
.info-card {
  text-align: center;
}

.marketplace-name {
  font-family: var(--font-display);
  font-size: 18px;
  color: var(--color-text);
  margin-bottom: var(--space-1);
}

.marketplace-desc {
  font-size: 14px;
  color: var(--color-text-muted);
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
