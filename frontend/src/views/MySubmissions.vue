<script setup>
import { ref, onMounted } from 'vue'
import { getAllSubmissions } from '../api'
import { useAppStore } from '../stores'
import StatusBadge from '../components/StatusBadge.vue'

const store = useAppStore()

const submissions = ref([])
const loading = ref(true)
const error = ref(null)

const userSubmissions = ref([])

const fetchSubmissions = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await getAllSubmissions()
    submissions.value = response.data
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
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="16" y1="13" x2="8" y2="13" />
          <line x1="16" y1="17" x2="8" y2="17" />
        </svg>
        我的提交
      </h1>
      <p class="subtitle">查看你提交的插件审核状态</p>
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
      <button class="btn btn-secondary" @click="fetchSubmissions">重新加载</button>
    </div>

    <!-- Empty -->
    <div class="state-card empty-state" v-if="!loading && !error && userSubmissions.length === 0">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="state-icon">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
      </svg>
      <h2>暂无提交记录</h2>
      <p>你还没有提交任何插件</p>
      <router-link to="/submit" class="btn btn-primary">提交插件</router-link>
    </div>

    <!-- Submissions list -->
    <div class="submissions-list" v-if="!loading && !error && userSubmissions.length > 0">
      <div
        v-for="submission in userSubmissions"
        :key="submission.submission_id"
        class="submission-card"
      >
        <div class="card-header">
          <div class="header-left">
            <span class="plugin-name">{{ submission.plugin?.name }}</span>
            <StatusBadge :status="submission.review_status?.status" size="sm" />
          </div>
          <span class="submission-id">{{ submission.submission_id }}</span>
        </div>

        <div class="card-body">
          <p class="plugin-description">{{ submission.plugin?.description }}</p>
          <div class="meta-row">
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

        <div class="card-footer" v-if="submission.review_status?.status === 'approved'">
          <router-link :to="`/plugins/${submission.plugin?.name}`" class="btn btn-secondary btn-sm">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
            </svg>
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
}

.error-state .state-icon {
  color: var(--color-error);
}

/* Submissions list */
.submissions-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.submission-card {
  background: var(--color-card);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  transition: border-color var(--transition-fast);
}

.submission-card:hover {
  border-color: var(--color-border);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-3);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.plugin-name {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 500;
  color: var(--color-text);
}

.submission-id {
  font-family: var(--font-display);
  font-size: 11px;
  color: var(--color-text-dim);
}

.card-body {
  margin-bottom: var(--space-3);
}

.plugin-description {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-3);
  line-height: 1.5;
}

.meta-row {
  display: flex;
  gap: var(--space-6);
}

.meta-item {
  font-size: 12px;
  color: var(--color-text-muted);
}

.meta-label {
  color: var(--color-text-dim);
}

.review-info {
  background: var(--color-bg-subtle);
  border: 1px solid var(--color-border-subtle);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  margin-top: var(--space-3);
}

.review-meta {
  display: flex;
  gap: var(--space-6);
  margin-bottom: var(--space-2);
}

.notes-label {
  font-family: var(--font-display);
  font-size: 11px;
  color: var(--color-text-dim);
}

.notes-text {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-top: var(--space-1);
}

.card-footer {
  margin-top: var(--space-4);
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border-subtle);
  display: flex;
  justify-content: flex-end;
}

.btn-sm {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-3);
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 500;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  text-decoration: none;
  transition: all var(--transition-fast);
}

.btn-sm:hover {
  background: var(--color-card-hover);
  color: var(--color-text);
  border-color: var(--color-text-muted);
}
</style>
