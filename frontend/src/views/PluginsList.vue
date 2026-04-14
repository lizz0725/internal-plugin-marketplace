<script setup>
import { ref, computed, onMounted, watch } from 'vue'
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
      <div class="header-title">
        <h1 class="title">
          <span class="title-icon">📦</span>
          插件浏览
        </h1>
        <p class="subtitle">浏览和安装企业内部 Claude Code 插件</p>
      </div>
      <div class="header-actions">
        <SearchBar v-model="searchQuery" placeholder="搜索插件名称、描述或关键词..." />
        <router-link to="/submit" class="submit-link">
          <span class="link-icon">✨</span>
          提交插件
        </router-link>
      </div>
    </header>

    <!-- Loading state -->
    <div class="loading-state" v-if="loading">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- Error state -->
    <div class="error-state" v-if="error">
      <span class="error-icon">⚠️</span>
      <p>{{ error }}</p>
      <button class="btn btn-secondary" @click="fetchPlugins">重新加载</button>
    </div>

    <!-- Empty state -->
    <div class="empty-state" v-if="!loading && !error && plugins.length === 0">
      <div class="empty-content">
        <span class="empty-icon">📭</span>
        <h2>暂无插件</h2>
        <p>目前没有上架的插件，点击上方按钮提交第一个插件吧！</p>
        <router-link to="/submit" class="btn btn-primary">
          提交插件
        </router-link>
      </div>
    </div>

    <!-- Search empty state -->
    <div class="search-empty" v-if="!loading && plugins.length > 0 && filteredPlugins.length === 0">
      <span class="search-icon">🔍</span>
      <p>没有找到匹配 "{{ searchQuery }}" 的插件</p>
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

.page-header {
  margin-bottom: var(--space-xl);
}

.header-title {
  margin-bottom: var(--space-lg);
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

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-lg);
}

.submit-link {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-lg);
  background: var(--color-primary);
  color: var(--color-bg);
  font-family: var(--font-display);
  font-size: 14px;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.submit-link:hover {
  background: var(--color-primary-hover);
  color: var(--color-bg);
}

.link-icon {
  font-size: 14px;
}

/* States */
.loading-state,
.error-state,
.empty-state,
.search-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-2xl);
  text-align: center;
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

.error-icon,
.empty-icon,
.search-icon {
  font-size: 48px;
  margin-bottom: var(--space-md);
}

.error-state p,
.empty-state p,
.search-empty p {
  color: var(--color-text-muted);
  margin-bottom: var(--space-lg);
}

.empty-content h2 {
  font-family: var(--font-display);
  color: var(--color-text);
  margin-bottom: var(--space-sm);
}

/* Grid */
.plugins-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--space-lg);
}

.results-info {
  margin-top: var(--space-lg);
  padding-top: var(--space-md);
  border-top: 1px solid var(--color-border-subtle);
}

.results-info p {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--color-text-muted);
}

@media (max-width: 768px) {
  .header-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .plugins-grid {
    grid-template-columns: 1fr;
  }
}
</style>