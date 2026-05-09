<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPlugin, ratePlugin } from '../api'
import { useAppStore } from '../stores'
import RatingStars from '../components/RatingStars.vue'

const route = useRoute()
const router = useRouter()
const store = useAppStore()

const plugin = ref(null)
const loading = ref(true)
const error = ref(null)
const pluginName = computed(() => route.params.name)

// Rating state
const userRating = ref(0)
const userComment = ref('')
const ratingSubmitted = ref(false)
const ratingLoading = ref(false)

const installCommand = computed(() => {
  return `/plugin install ${pluginName.value}@cc-plugin-marketplace`
})

const copyInstall = () => {
  navigator.clipboard.writeText(installCommand.value)
}

const fetchPlugin = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await getPlugin(pluginName.value)
    plugin.value = response.data
  } catch (err) {
    if (err.response?.status === 404) {
      error.value = `插件 "${pluginName.value}" 不存在`
    } else {
      error.value = '加载插件详情失败'
    }
    console.error(err)
  } finally {
    loading.value = false
  }
}

const submitRating = async () => {
  if (!userRating.value || ratingLoading.value) return

  ratingLoading.value = true
  try {
    await ratePlugin(pluginName.value, {
      rating: userRating.value,
      comment: userComment.value,
      user_email: store.userEmail
    })
    ratingSubmitted.value = true
    await fetchPlugin()
  } catch (err) {
    console.error('Rating failed:', err)
  } finally {
    ratingLoading.value = false
  }
}

onMounted(fetchPlugin)
</script>

<template>
  <div class="plugin-detail-page">
    <!-- Breadcrumb -->
    <nav class="breadcrumb">
      <router-link to="/plugins" class="breadcrumb-link">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
        </svg>
        插件浏览
      </router-link>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="breadcrumb-sep">
        <polyline points="9 18 15 12 9 6" />
      </svg>
      <span class="breadcrumb-current">{{ pluginName }}</span>
    </nav>

    <!-- Loading -->
    <div class="loading-state" v-if="loading">
      <div class="loading-spinner"></div>
    </div>

    <!-- Error -->
    <div class="state-card error-state" v-if="error && !loading">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="state-icon">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
      <h2>{{ error }}</h2>
      <button class="btn btn-secondary" @click="router.push('/plugins')">返回插件列表</button>
    </div>

    <!-- Plugin detail -->
    <div class="plugin-detail" v-if="plugin && !loading">
      <div class="detail-layout">
        <!-- Main content -->
        <div class="detail-main">
          <!-- Hero section -->
          <div class="detail-section hero-section">
            <div class="hero-layout">
              <div class="hero-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M12 6v6l4 2" />
                </svg>
              </div>
              <div class="hero-info">
                <div class="hero-title-row">
                  <h1 class="plugin-title">{{ plugin.name }}</h1>
                  <span class="version-badge">v{{ plugin.version }}</span>
                </div>
                <div class="hero-meta">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                    <circle cx="12" cy="7" r="4" />
                  </svg>
                  <span>{{ plugin.author?.name || '未知作者' }}</span>
                  <RatingStars :rating="plugin.average_rating" :count="plugin.total_ratings" size="sm" />
                </div>
              </div>
            </div>
          </div>

          <!-- Description -->
          <div class="detail-section">
            <h3 class="section-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
              </svg>
              描述
            </h3>
            <p class="description-text">{{ plugin.description }}</p>
          </div>

          <!-- README (if available) -->
          <div class="detail-section" v-if="plugin.readme">
            <h3 class="section-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
                <polyline points="4 17 10 11 4 5" />
                <line x1="12" y1="19" x2="20" y2="19" />
              </svg>
              说明
            </h3>
            <div class="readme-content" v-html="plugin.readme"></div>
          </div>

          <!-- Version history -->
          <div class="detail-section" v-if="plugin.versions">
            <h3 class="section-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
                <circle cx="12" cy="12" r="3" />
                <line x1="3" y1="12" x2="9" y2="12" />
                <line x1="15" y1="12" x2="21" y2="12" />
              </svg>
              版本历史
            </h3>
            <div class="versions-list">
              <div
                v-for="v in plugin.versions.versions"
                :key="v.version"
                :class="['version-item', { 'is-current': v.status === 'current' }]"
              >
                <div class="version-info">
                  <span class="version-number">{{ v.version }}</span>
                  <span class="version-date">{{ v.released_at }}</span>
                  <span class="version-status-badge" v-if="v.status === 'current'">当前</span>
                  <span class="version-status-badge deprecated" v-if="v.status === 'deprecated'">已废弃</span>
                </div>
                <p class="version-changelog" v-if="v.changelog">{{ v.changelog }}</p>
              </div>
            </div>
          </div>

          <!-- Rating form -->
          <div class="detail-section">
            <h3 class="section-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
              </svg>
              评分
            </h3>

            <div class="rating-form" v-if="!ratingSubmitted">
              <p class="rating-prompt">为此插件评分:</p>
              <div class="rating-stars-input">
                <RatingStars
                  v-model:rating="userRating"
                  :rating="userRating"
                  interactive
                  size="lg"
                />
              </div>
              <textarea
                v-model="userComment"
                placeholder="写下你的评论 (可选)"
                rows="3"
                class="comment-input"
              ></textarea>
              <button
                class="btn btn-primary"
                @click="submitRating"
                :disabled="!userRating || ratingLoading"
              >
                {{ ratingLoading ? '提交中...' : '提交评分' }}
              </button>
            </div>

            <div class="rating-success" v-if="ratingSubmitted">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="24" height="24" class="success-icon">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              <p>评分已提交，感谢你的反馈！</p>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="detail-sidebar">
          <!-- Install card -->
          <div class="sidebar-card">
            <h3 class="sidebar-card-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              安装
            </h3>
            <div class="install-code-block">
              <code class="install-command">$ {{ installCommand }}</code>
              <button class="copy-btn" @click="copyInstall" title="复制命令">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                </svg>
              </button>
            </div>
            <p class="install-hint">在 Claude Code CLI 中运行此命令</p>
          </div>

          <!-- Info card -->
          <div class="sidebar-card">
            <h3 class="sidebar-card-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="16" x2="12" y2="12" />
                <line x1="12" y1="8" x2="12.01" y2="8" />
              </svg>
              信息
            </h3>
            <div class="info-list">
              <div class="info-row">
                <span class="info-label">作者</span>
                <span class="info-value">{{ plugin.author?.name || '未知' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">版本</span>
                <span class="info-value">{{ plugin.version }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">更新</span>
                <span class="info-value">{{ plugin.updated_at || plugin.created_at }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">评分</span>
                <span class="info-value">
                  <RatingStars :rating="plugin.average_rating" :count="plugin.total_ratings" size="sm" />
                </span>
              </div>
            </div>
          </div>

          <!-- Tags card -->
          <div class="sidebar-card" v-if="plugin.keywords?.length">
            <h3 class="sidebar-card-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
                <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" />
                <line x1="7" y1="7" x2="7.01" y2="7" />
              </svg>
              标签
            </h3>
            <div class="tags-list">
              <span class="tag" v-for="kw in plugin.keywords" :key="kw">{{ kw }}</span>
            </div>
          </div>

          <!-- Upstream Source -->
          <div class="sidebar-card" v-if="plugin.source && plugin.source.type !== 'manual'">
            <h3 class="sidebar-card-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
                <circle cx="12" cy="12" r="10" />
                <line x1="2" y1="12" x2="22" y2="12" />
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
              </svg>
              上游来源
            </h3>
            <div class="info-list">
              <div class="info-row" v-if="plugin.stars">
                <span class="info-label">Stars</span>
                <span class="info-value stars-value">★ {{ (plugin.stars / 1000).toFixed(1) }}k</span>
              </div>
              <div class="info-row" v-if="plugin.source.last_sync_at">
                <span class="info-label">同步时间</span>
                <span class="info-value">{{ plugin.source.last_sync_at.slice(0, 10) }}</span>
              </div>
              <div class="info-row" v-if="plugin.source.commit_sha">
                <span class="info-label">Commit</span>
                <span class="info-value mono">{{ plugin.source.commit_sha.slice(0, 12) }}</span>
              </div>
              <div class="info-row" v-if="plugin.source.last_sync_status">
                <span class="info-label">状态</span>
                <span :class="['info-value', 'status-' + plugin.source.last_sync_status]">
                  {{ plugin.source.last_sync_status }}
                </span>
              </div>
            </div>
          </div>

          <!-- Homepage -->
          <div class="sidebar-card" v-if="plugin.homepage">
            <h3 class="sidebar-card-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                <polyline points="15 3 21 3 21 9" />
                <line x1="10" y1="14" x2="21" y2="3" />
              </svg>
              链接
            </h3>
            <a :href="plugin.homepage" target="_blank" class="homepage-link">
              查看上游仓库
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="12" height="12">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                <polyline points="15 3 21 3 21 9" />
                <line x1="10" y1="14" x2="21" y2="3" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.plugin-detail-page {
  max-width: 1100px;
}

/* Breadcrumb */
.breadcrumb {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-6);
  font-size: 13px;
}

.breadcrumb-link {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  color: var(--color-text-muted);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.breadcrumb-link:hover {
  color: var(--color-primary);
}

.breadcrumb-sep {
  width: 14px;
  height: 14px;
  color: var(--color-text-dim);
}

.breadcrumb-current {
  color: var(--color-text);
  font-family: var(--font-display);
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

.state-card h2 {
  font-family: var(--font-display);
  font-size: 18px;
  color: var(--color-text);
  margin-bottom: var(--space-4);
}

/* Detail layout */
.detail-layout {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: var(--space-6);
  align-items: start;
}

.detail-main {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.detail-sidebar {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  position: sticky;
  top: var(--space-8);
}

/* Detail sections */
.detail-section {
  background: var(--color-card);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
}

.hero-section {
  background: linear-gradient(135deg, var(--color-card) 0%, var(--color-bg-subtle) 100%);
}

.hero-layout {
  display: flex;
  align-items: flex-start;
  gap: var(--space-5);
}

.hero-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  background: var(--color-primary-muted);
  border: 1px solid var(--color-border-active);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  flex-shrink: 0;
}

.hero-icon svg {
  width: 28px;
  height: 28px;
}

.hero-title-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-2);
}

.plugin-title {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 600;
  color: var(--color-text);
}

.version-badge {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--color-primary);
  background: var(--color-primary-muted);
  padding: 2px 10px;
  border-radius: var(--radius-full);
}

.hero-meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 13px;
  color: var(--color-text-muted);
}

.section-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--color-text-muted);
  margin-bottom: var(--space-4);
}

.section-title svg {
  color: var(--color-text-dim);
}

.description-text {
  font-size: 15px;
  color: var(--color-text-secondary);
  line-height: 1.7;
}

.readme-content {
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.8;
}

/* Versions */
.versions-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.version-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-3);
  background: var(--color-bg-subtle);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-md);
  transition: border-color var(--transition-fast);
}

.version-item.is-current {
  border-color: var(--color-border-active);
}

.version-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.version-number {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text);
}

.version-date {
  font-size: 12px;
  color: var(--color-text-dim);
}

.version-status-badge {
  font-family: var(--font-display);
  font-size: 10px;
  color: var(--color-primary);
  background: var(--color-primary-muted);
  padding: 2px 6px;
  border-radius: var(--radius-full);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.version-status-badge.deprecated {
  color: var(--color-error);
  background: var(--color-error-muted);
}

.version-changelog {
  font-size: 13px;
  color: var(--color-text-muted);
}

/* Rating form */
.rating-prompt {
  font-size: 13px;
  color: var(--color-text-muted);
  margin-bottom: var(--space-3);
}

.rating-stars-input {
  margin-bottom: var(--space-3);
}

.comment-input {
  width: 100%;
  padding: var(--space-3);
  background: var(--color-bg-subtle);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-md);
  color: var(--color-text);
  font-family: var(--font-body);
  font-size: 14px;
  resize: vertical;
  margin-bottom: var(--space-3);
}

.comment-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.rating-success {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  color: var(--color-success);
  font-size: 14px;
}

.success-icon {
  flex-shrink: 0;
}

/* Sidebar cards */
.sidebar-card {
  background: var(--color-card);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
}

.sidebar-card-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--color-text-muted);
  margin-bottom: var(--space-3);
}

/* Install command */
.install-code-block {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--color-bg-subtle);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-md);
  padding: var(--space-2) var(--space-3);
  gap: var(--space-2);
}

.install-command {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--color-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.copy-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: var(--color-text-dim);
  cursor: pointer;
  padding: var(--space-1);
  border-radius: var(--radius-sm);
  flex-shrink: 0;
  transition: all var(--transition-fast);
}

.copy-btn:hover {
  color: var(--color-primary);
  background: var(--color-primary-muted);
}

.install-hint {
  font-size: 11px;
  color: var(--color-text-dim);
  margin-top: var(--space-2);
}

/* Info list */
.info-list {
  display: flex;
  flex-direction: column;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-2) 0;
  border-bottom: 1px solid var(--color-border-subtle);
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 12px;
  color: var(--color-text-muted);
}

.info-value {
  font-size: 12px;
  color: var(--color-text);
  font-family: var(--font-display);
}

/* Tags */
.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-1);
}

.tag {
  font-family: var(--font-display);
  font-size: 10px;
  color: var(--color-text-dim);
  background: var(--color-bg-subtle);
  border: 1px solid var(--color-border-subtle);
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

/* Homepage */
.homepage-link {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: 13px;
  color: var(--color-primary);
}

.stars-value {
  color: var(--color-primary) !important;
}

.mono {
  font-family: var(--font-display) !important;
  font-size: 11px !important;
}

.status-success {
  color: var(--color-success) !important;
}

.status-failed {
  color: var(--color-error) !important;
}

.status-pending {
  color: var(--color-warning) !important;
}

@media (max-width: 768px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }

  .detail-sidebar {
    position: static;
  }
}
</style>
