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
  return `/plugin install ${pluginName.value}@internal`
})

const copyInstall = () => {
  navigator.clipboard.writeText(installCommand.value)
}

// Fetch plugin
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

// Submit rating
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
    // Refresh plugin to get updated rating
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
    <!-- Back button -->
    <button class="back-btn" @click="router.push('/plugins')">
      ← 返回列表
    </button>

    <!-- Loading -->
    <div class="loading-state" v-if="loading">
      <div class="loading-spinner"></div>
    </div>

    <!-- Error -->
    <div class="error-state" v-if="error && !loading">
      <span class="error-icon">⚠️</span>
      <h2>{{ error }}</h2>
      <button class="btn btn-secondary" @click="router.push('/plugins')">
        返回插件列表
      </button>
    </div>

    <!-- Plugin detail -->
    <div class="plugin-detail" v-if="plugin && !loading">
      <!-- Header -->
      <header class="detail-header">
        <div class="header-main">
          <div class="plugin-title">
            <h1 class="title">{{ plugin.name }}</h1>
            <span class="version-badge">v{{ plugin.version }}</span>
          </div>
          <div class="plugin-meta">
            <span class="author">
              <span class="author-icon">👤</span>
              {{ plugin.author?.name || '未知作者' }}
            </span>
            <span class="divider">•</span>
            <RatingStars :rating="plugin.average_rating" :count="plugin.total_ratings" size="lg" />
          </div>
        </div>
        <div class="header-actions">
          <button class="install-btn btn-primary" @click="copyInstall">
            <span class="btn-icon">📋</span>
            复制安装命令
          </button>
        </div>
      </header>

      <!-- Description -->
      <section class="detail-section">
        <h2 class="section-title">描述</h2>
        <p class="description-text">{{ plugin.description }}</p>
      </section>

      <!-- Keywords -->
      <section class="detail-section" v-if="plugin.keywords?.length">
        <h2 class="section-title">关键词</h2>
        <div class="keywords-list">
          <span class="keyword" v-for="kw in plugin.keywords" :key="kw">
            {{ kw }}
          </span>
        </div>
      </section>

      <!-- Install command -->
      <section class="detail-section install-section">
        <h2 class="section-title">安装</h2>
        <div class="install-code">
          <code class="command">{{ installCommand }}</code>
          <button class="copy-btn" @click="copyInstall">
            <span>📋</span>
          </button>
        </div>
        <p class="install-hint">
          在 Claude Code CLI 中运行上述命令即可安装此插件
        </p>
      </section>

      <!-- Version history -->
      <section class="detail-section" v-if="plugin.versions">
        <h2 class="section-title">版本历史</h2>
        <div class="versions-list">
          <div
            v-for="v in plugin.versions.versions"
            :key="v.version"
            :class="['version-item', v.status]"
          >
            <div class="version-info">
              <span class="version-number">{{ v.version }}</span>
              <span class="version-date">{{ v.released_at }}</span>
              <span class="version-status" v-if="v.status === 'current'">当前版本</span>
              <span class="version-status deprecated" v-if="v.status === 'deprecated'">已废弃</span>
            </div>
            <p class="version-changelog" v-if="v.changelog">{{ v.changelog }}</p>
          </div>
        </div>
      </section>

      <!-- Rating section -->
      <section class="detail-section rating-section">
        <h2 class="section-title">评分</h2>

        <!-- Rating form -->
        <div class="rating-form" v-if="!ratingSubmitted">
          <p class="rating-prompt">为此插件评分:</p>
          <div class="rating-input">
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
            class="btn btn-primary submit-rating-btn"
            @click="submitRating"
            :disabled="!userRating || ratingLoading"
          >
            {{ ratingLoading ? '提交中...' : '提交评分' }}
          </button>
        </div>

        <!-- Rating submitted -->
        <div class="rating-success" v-if="ratingSubmitted">
          <span class="success-icon">✓</span>
          <p>评分已提交，感谢你的反馈！</p>
        </div>
      </section>

      <!-- Homepage link -->
      <section class="detail-section" v-if="plugin.homepage">
        <h2 class="section-title">更多信息</h2>
        <a :href="plugin.homepage" target="_blank" class="homepage-link">
          <span class="link-icon">🔗</span>
          查看项目主页
        </a>
      </section>
    </div>
  </div>
</template>

<style scoped>
.plugin-detail-page {
  max-width: 800px;
}

.back-btn {
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  font-family: var(--font-display);
  font-size: 14px;
  cursor: pointer;
  padding: var(--space-sm) 0;
  margin-bottom: var(--space-lg);
}

.back-btn:hover {
  color: var(--color-primary);
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
  text-align: center;
  padding: var(--space-xl);
}

.error-icon {
  font-size: 48px;
}

.error-state h2 {
  font-family: var(--font-display);
  color: var(--color-text);
  margin: var(--space-md) 0;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: var(--space-lg);
  border-bottom: 1px solid var(--color-border-subtle);
  margin-bottom: var(--space-xl);
}

.plugin-title {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.title {
  font-family: var(--font-display);
  font-size: 32px;
  color: var(--color-text);
}

.version-badge {
  font-family: var(--font-display);
  font-size: 14px;
  color: var(--color-primary);
  background: var(--color-primary-muted);
  padding: 4px 12px;
  border-radius: var(--radius-md);
}

.plugin-meta {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-top: var(--space-sm);
}

.author {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--color-text-muted);
}

.divider {
  color: var(--color-border);
}

.install-btn {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.detail-section {
  margin-bottom: var(--space-xl);
}

.section-title {
  font-family: var(--font-display);
  font-size: 18px;
  color: var(--color-text);
  margin-bottom: var(--space-md);
}

.description-text {
  font-family: var(--font-body);
  font-size: 16px;
  color: var(--color-text-secondary);
  line-height: 1.7;
}

.keywords-list {
  display: flex;
  gap: var(--space-sm);
}

.keyword {
  font-family: var(--font-display);
  font-size: 13px;
  color: var(--color-text-muted);
  background: var(--color-bg);
  border: 1px solid var(--color-border-subtle);
  padding: 6px 14px;
  border-radius: var(--radius-md);
}

.install-section {
  background: var(--color-card);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
}

.install-code {
  display: flex;
  align-items: center;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-md);
  gap: var(--space-md);
}

.command {
  font-family: var(--font-display);
  font-size: 14px;
  color: var(--color-primary);
}

.copy-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: var(--color-text-muted);
}

.copy-btn:hover {
  color: var(--color-primary);
}

.install-hint {
  font-size: 13px;
  color: var(--color-text-muted);
  margin-top: var(--space-sm);
}

.versions-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.version-item {
  padding: var(--space-md);
  background: var(--color-card);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-md);
}

.version-item.current {
  border-color: var(--color-primary);
}

.version-item.deprecated {
  opacity: 0.6;
}

.version-info {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.version-number {
  font-family: var(--font-display);
  color: var(--color-text);
}

.version-date {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--color-text-muted);
}

.version-status {
  font-family: var(--font-display);
  font-size: 11px;
  color: var(--color-primary);
  background: var(--color-primary-muted);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.version-status.deprecated {
  color: var(--color-error);
  background: rgba(212, 95, 95, 0.2);
}

.version-changelog {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-top: var(--space-sm);
}

.rating-section {
  background: var(--color-card);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
}

.rating-prompt {
  font-size: 14px;
  color: var(--color-text-muted);
  margin-bottom: var(--space-md);
}

.rating-input {
  margin-bottom: var(--space-md);
}

.comment-input {
  margin-bottom: var(--space-md);
}

.submit-rating-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.rating-success {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  color: var(--color-success);
}

.success-icon {
  font-size: 24px;
}

.homepage-link {
  display: inline-flex;
  align-items: center;
  gap: var(--space-sm);
  color: var(--color-primary);
  font-size: 14px;
}

.homepage-link:hover {
  color: var(--color-primary-hover);
}

@media (max-width: 768px) {
  .detail-header {
    flex-direction: column;
    gap: var(--space-lg);
  }
}
</style>