<script setup>
import { ref, onMounted } from 'vue'
import { getAllSubmissions } from '../api'
import { useAppStore } from '../stores'
import StatusBadge from '../components/StatusBadge.vue'

const store = useAppStore()

const submissions = ref([])
const loading = ref(true)
const error = ref(null)

// Filter by user email (mock)
const userSubmissions = ref([])

const fetchSubmissions = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await getAllSubmissions()
    submissions.value = response.data
    // Filter by current user (in production, this would be server-side)
    userSubmissions.value = submissions.value.filter(
      s => s.submitter?.email === store.userEmail
    )
  } catch (err) {
    error.value = '加载失败'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchSubmissions)

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}
</script>

<template>
  <div class="my-submissions-page">
    <!-- Header -->
    <header class="page-header">
      <h1 class="title">
        <span class="title-icon">📋</span>
        我的提交
      </h1>
      <p class="subtitle">查看你提交的插件审核状态</p>
    </header>

    <!-- Loading -->
    <div class="loading-state" v-if="loading">
      <div class="loading-spinner"></div>
    </div>

    <!-- Error -->
    <div class="error-state" v-if="error">
      <span class="error-icon">⚠️</span>
      <p>{{ error }}</p>
      <button class="btn btn-secondary" @click="fetchSubmissions">重新加载</button>
    </div>

    <!-- Empty -->
    <div class="empty-state" v-if="!loading && !error && userSubmissions.length === 0">
      <div class="empty-content">
        <span class="empty-icon">📭</span>
        <h2>暂无提交记录</h2>
        <p>你还没有提交任何插件</p>
        <router-link to="/submit" class="btn btn-primary">
          提交插件
        </router-link>
      </div>
    </div>

    <!-- Submissions list -->
    <div class="submissions-list" v-if="!loading && !error && userSubmissions.length > 0">
      <div
        v-for="submission in userSubmissions"
        :key="submission.submission_id"
        class="submission-item"
      >
        <div class="item-header">
          <div class="item-title">
            <span class="plugin-name">{{ submission.plugin?.name }}</span>
            <StatusBadge :status="submission.review_status?.status" />
          </div>
          <span class="submission-id">{{ submission.submission_id }}</span>
        </div>

        <div class="item-body">
          <p class="plugin-description">{{ submission.plugin?.description }}</p>
          <div class="item-meta">
            <span class="meta-item">
              <span class="meta-label">版本:</span>
              {{ submission.plugin?.version }}
            </span>
            <span class="meta-item">
              <span class="meta-label">提交时间:</span>
              {{ formatDate(submission.submitter?.submitted_at) }}
            </span>
          </div>
        </div>

        <!-- Review info (if reviewed) -->
        <div class="review-info" v-if="submission.review_status?.status !== 'pending'">
          <div class="review-meta">
            <span class="meta-item">
              <span class="meta-label">审核人:</span>
              {{ submission.review_status?.reviewed_by }}
            </span>
            <span class="meta-item">
              <span class="meta-label">审核时间:</span>
              {{ formatDate(submission.review_status?.reviewed_at) }}
            </span>
          </div>
          <div class="review-notes" v-if="submission.review_status?.review_notes">
            <span class="notes-label">审核备注:</span>
            <p class="notes-text">{{ submission.review_status?.review_notes }}</p>
          </div>
        </div>

        <!-- Link to plugin if approved -->
        <div class="item-footer" v-if="submission.review_status?.status === 'approved'">
          <router-link
            :to="`/plugins/${submission.plugin?.name}`"
            class="btn btn-secondary"
          >
            查看插件
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.my-submissions-page {
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

.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-xl);
  text-align: center;
}

.error-icon,
.empty-icon {
  font-size: 48px;
}

.empty-content h2 {
  font-family: var(--font-display);
  color: var(--color-text);
  margin-bottom: var(--space-sm);
}

.submissions-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.submission-item {
  background: var(--color-card);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-md);
}

.item-title {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.plugin-name {
  font-family: var(--font-display);
  font-size: 18px;
  color: var(--color-text);
}

.submission-id {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--color-text-muted);
}

.item-body {
  margin-bottom: var(--space-md);
}

.plugin-description {
  font-family: var(--font-body);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-md);
}

.item-meta {
  display: flex;
  gap: var(--space-lg);
}

.meta-item {
  font-size: 13px;
  color: var(--color-text-muted);
}

.meta-label {
  color: var(--color-text-secondary);
}

.review-info {
  background: var(--color-bg);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  margin-top: var(--space-md);
}

.review-meta {
  display: flex;
  gap: var(--space-lg);
  margin-bottom: var(--space-sm);
}

.notes-label {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--color-text-muted);
}

.notes-text {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-top: var(--space-xs);
}

.item-footer {
  margin-top: var(--space-md);
  display: flex;
  justify-content: flex-end;
}
</style>