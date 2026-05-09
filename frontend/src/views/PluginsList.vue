<script setup>
import { ref, computed, onMounted } from 'vue'
import { getPlugins } from '../api'
import PluginCard from '../components/PluginCard.vue'
import SearchBar from '../components/SearchBar.vue'

const plugins = ref([])
const loading = ref(true)
const error = ref(null)
const searchQuery = ref('')

// Filtered plugins
const filteredPlugins = computed(() => {
  if (!searchQuery.value) return plugins.value
  const query = searchQuery.value.toLowerCase()
  return plugins.value.filter(p =>
    p.name.toLowerCase().includes(query) ||
    p.description.toLowerCase().includes(query) ||
    p.keywords?.some(k => k.toLowerCase().includes(query))
  )
})

// Fetch plugins
const fetchPlugins = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await getPlugins()
    plugins.value = response.data
  } catch (err) {
    error.value = '加载插件列表失败'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchPlugins)
</script>

<template>
  <div class="plugins-list-page">
    <!-- Page header -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="title">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
          </svg>
          插件浏览
        </h1>
        <p class="subtitle">浏览和安装企业内部 Claude Code 插件</p>
      </div>
      <div class="header-actions">
        <SearchBar v-model="searchQuery" placeholder="搜索插件名称、描述或关键词..." />
        <router-link to="/submit" class="btn btn-primary">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
            <path d="M12 5v14" />
            <path d="M5 12h14" />
          </svg>
          提交插件
        </router-link>
      </div>
    </header>

    <!-- Loading state -->
    <div class="loading-state" v-if="loading">
      <div class="loading-spinner"></div>
      <p class="loading-text">加载中...</p>
    </div>

    <!-- Error state -->
    <div class="state-card error-state" v-if="error">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="state-icon">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
      <p>{{ error }}</p>
      <button class="btn btn-secondary" @click="fetchPlugins">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
          <polyline points="23 4 23 10 17 10" />
          <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
        </svg>
        重新加载
      </button>
    </div>

    <!-- Empty state -->
    <div class="state-card empty-state" v-if="!loading && !error && plugins.length === 0">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="state-icon">
        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
      </svg>
      <h2>暂无插件</h2>
      <p>目前没有上架的插件，点击上方按钮提交第一个插件吧！</p>
      <router-link to="/submit" class="btn btn-primary">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
          <path d="M12 5v14" />
          <path d="M5 12h14" />
        </svg>
        提交插件
      </router-link>
    </div>

    <!-- Search empty state -->
    <div class="state-card search-empty" v-if="!loading && plugins.length > 0 && filteredPlugins.length === 0">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="state-icon">
        <circle cx="11" cy="11" r="8" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
      </svg>
      <p>没有找到匹配 "<strong>{{ searchQuery }}</strong>" 的插件</p>
      <button class="btn btn-secondary" @click="searchQuery = ''">清除搜索</button>
    </div>

    <!-- Plugins grid -->
    <div class="plugins-grid" v-if="!loading && !error && filteredPlugins.length > 0">
      <PluginCard
        v-for="plugin in filteredPlugins"
        :key="plugin.name"
        :plugin="plugin"
      />
    </div>

    <!-- Results count -->
    <div class="results-info" v-if="!loading && filteredPlugins.length > 0">
      <p>
        共 {{ filteredPlugins.length }} 个插件
        <span v-if="searchQuery && filteredPlugins.length !== plugins.length">
          (筛选自 {{ plugins.length }} 个)
        </span>
      </p>
    </div>
  </div>
</template>

<style scoped>
.plugins-list-page {
  max-width: 1200px;
}

/* Header */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: var(--space-8);
  gap: var(--space-6);
}

.header-left {
  flex-shrink: 0;
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
  flex-shrink: 0;
}

.subtitle {
  font-size: 14px;
  color: var(--color-text-muted);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-shrink: 0;
}

/* States */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-16) var(--space-8);
}

.loading-spinner {
  width: 36px;
  height: 36px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: var(--space-3);
}

.loading-text {
  font-size: 13px;
  color: var(--color-text-dim);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.state-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12) var(--space-8);
  text-align: center;
  background: var(--color-card);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-xl);
}

.state-icon {
  width: 48px;
  height: 48px;
  color: var(--color-text-dim);
  margin-bottom: var(--space-4);
}

.state-card h2 {
  font-family: var(--font-display);
  font-size: 18px;
  color: var(--color-text);
  margin-bottom: var(--space-2);
}

.state-card p {
  font-size: 14px;
  color: var(--color-text-muted);
  margin-bottom: var(--space-5);
  max-width: 360px;
  line-height: 1.6;
}

.error-state .state-icon {
  color: var(--color-error);
}

/* Grid */
.plugins-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--space-4);
}

.results-info {
  margin-top: var(--space-5);
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border-subtle);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.results-info p {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--color-text-muted);
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .plugins-grid {
    grid-template-columns: 1fr;
  }
}
</style>
