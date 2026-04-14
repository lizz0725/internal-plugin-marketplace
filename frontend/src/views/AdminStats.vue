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

// Total ratings count from distribution
const totalFromDistribution = computed(() => {
  return Object.values(ratingsDistribution.value).reduce((a, b) => a + b, 0)
})

// Average from distribution
const averageFromDistribution = computed(() => {
  const total = totalFromDistribution.value
  if (total === 0) return 0
  const sum = Object.entries(ratingsDistribution.value)
    .reduce((acc, [rating, count]) => acc + (parseInt(rating) * count), 0)
  return (sum / total).toFixed(1)
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

// Max count for chart scaling
const maxCount = computed(() => {
  return Math.max(...Object.values(ratingsDistribution.value), 1)
})

onMounted(fetchStats)
</script>

<template>
  <div class="admin-stats-page">
    <!-- Header -->
    <header class="page-header">
      <h1 class="title">
        <span class="title-icon">📊</span>
        统计分析
      </h1>
      <p class="subtitle">插件市场数据概览</p>
    </header>

    <!-- Loading -->
    <div class="loading-state" v-if="loading">
      <div class="loading-spinner"></div>
    </div>

    <!-- Error -->
    <div class="error-state" v-if="error">
      <span class="error-icon">⚠️</span>
      <p>{{ error }}</p>
      <button class="btn btn-secondary" @click="fetchStats">重新加载</button>
    </div>

    <!-- Stats content -->
    <div class="stats-content" v-if="!loading && !error">
      <!-- Overview cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">📦</div>
          <div class="stat-value">{{ stats.plugins_count }}</div>
          <div class="stat-label">插件总数</div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">⏳</div>
          <div class="stat-value">{{ stats.pending_reviews }}</div>
          <div class="stat-label">待审核</div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">⭐</div>
          <div class="stat-value">{{ stats.total_ratings }}</div>
          <div class="stat-label">评分总数</div>
        </div>

        <div class="stat-card">
          <div class="stat-icon">📈</div>
          <div class="stat-value">{{ averageFromDistribution }}</div>
          <div class="stat-label">平均评分</div>
        </div>
      </div>

      <!-- Ratings distribution -->
      <div class="distribution-section">
        <h2 class="section-title">评分分布</h2>
        <div class="distribution-chart">
          <div
            v-for="rating in [5, 4, 3, 2, 1]"
            :key="rating"
            class="bar-container"
          >
            <div class="bar-label">
              <span class="star-icon">{{ rating === 5 ? '★★★★★' : rating === 4 ? '★★★★☆' : rating === 3 ? '★★★☆☆' : rating === 2 ? '★★☆☆☆' : '★☆☆☆☆' }}</span>
              <span class="count">{{ ratingsDistribution[rating] }}</span>
            </div>
            <div class="bar-wrapper">
              <div
                class="bar"
                :style="{ width: `${(ratingsDistribution[rating] / maxCount) * 100}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Marketplace info -->
      <div class="marketplace-info" v-if="stats.marketplace_name">
        <h2 class="section-title">市场信息</h2>
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
  margin-bottom: var(--space-xl);
}

.title {
  font-family: var(--font-display);
  font-size: 28px;
  color: var(--color-text);
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.title-icon {
  font-size: 28px;
}

.subtitle {
  font-family: var(--font-body);
  font-size: 16px;
  color: var(--color-text-muted);
  margin-top: var(--space-xs);
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: var(--space-xl);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-xl);
  text-align: center;
}

.error-icon {
  font-size: 48px;
}

.stats-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-xl);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-lg);
}

.stat-card {
  background: var(--color-card);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  text-align: center;
  transition: all var(--transition-normal);
}

.stat-card:hover {
  border-color: var(--color-primary);
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 32px;
  margin-bottom: var(--space-sm);
}

.stat-value {
  font-family: var(--font-display);
  font-size: 36px;
  color: var(--color-primary);
}

.stat-label {
  font-family: var(--font-display);
  font-size: 13px;
  color: var(--color-text-muted);
  margin-top: var(--space-sm);
}

.distribution-section,
.marketplace-info {
  background: var(--color-card);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
}

.section-title {
  font-family: var(--font-display);
  font-size: 16px;
  color: var(--color-text);
  margin-bottom: var(--space-lg);
}

.distribution-chart {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.bar-container {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.bar-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-width: 150px;
}

.star-icon {
  color: var(--color-primary);
  font-size: 14px;
}

.count {
  font-family: var(--font-display);
  font-size: 14px;
  color: var(--color-text-muted);
  margin-left: var(--space-sm);
}

.bar-wrapper {
  flex: 1;
  height: 24px;
  background: var(--color-bg);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.bar {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary), var(--color-primary-hover));
  border-radius: var(--radius-sm);
  transition: width var(--transition-slow);
}

.info-card {
  text-align: center;
}

.marketplace-name {
  font-family: var(--font-display);
  font-size: 20px;
  color: var(--color-text);
  margin-bottom: var(--space-sm);
}

.marketplace-desc {
  font-family: var(--font-body);
  font-size: 14px;
  color: var(--color-text-muted);
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>