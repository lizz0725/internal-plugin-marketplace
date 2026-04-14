<script setup>
import { ref, onMounted, computed } from 'vue'
import { getPendingReviews, approveSubmission, rejectSubmission } from '../api'
import { useAppStore } from '../stores'
import StatusBadge from '../components/StatusBadge.vue'

const store = useAppStore()

const submissions = ref([])
const loading = ref(true)
const error = ref(null)
const filter = ref('pending') // pending, all

const filteredSubmissions = computed(() => {
  if (filter.value === 'pending') {
    return submissions.value.filter(s => s.review_status?.status === 'pending')
  }
  return submissions.value
})

// Review modal state
const showReviewModal = ref(false)
const selectedSubmission = ref(null)
const reviewAction = ref('') // approve or reject
const reviewNotes = ref('')
const reviewLoading = ref(false)

const fetchSubmissions = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await getPendingReviews()
    submissions.value = response.data
  } catch (err) {
    error.value = '加载失败'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const openReviewModal = (submission, action) => {
  selectedSubmission.value = submission
  reviewAction.value = action
  reviewNotes.value = ''
  showReviewModal.value = true
}

const closeReviewModal = () => {
  showReviewModal.value = false
  selectedSubmission.value = null
}

const submitReview = async () => {
  if (!selectedSubmission.value || reviewLoading.value) return

  reviewLoading.value = true
  try {
    if (reviewAction.value === 'approve') {
      await approveSubmission(
        selectedSubmission.value.submission_id,
        store.userEmail,
        reviewNotes.value
      )
    } else {
      if (!reviewNotes.value) {
        alert('拒绝时必须填写原因')
        reviewLoading.value = false
        return
      }
      await rejectSubmission(
        selectedSubmission.value.submission_id,
        store.userEmail,
        reviewNotes.value
      )
    }
    closeReviewModal()
    await fetchSubmissions()
    store.fetchPendingCount()
    store.fetchStats()
  } catch (err) {
    console.error('Review failed:', err)
    alert('操作失败，请重试')
  } finally {
    reviewLoading.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(fetchSubmissions)
</script>

<template>
  <div class="admin-reviews-page">
    <!-- Header -->
    <header class="page-header">
      <h1 class="title">
        <span class="title-icon">⚖️</span>
        审核管理
      </h1>
      <p class="subtitle">审核待提交的插件</p>
    </header>

    <!-- Filters -->
    <div class="filters-bar">
      <button
        :class="['filter-btn', { active: filter === 'pending' }]"
        @click="filter = 'pending'"
      >
        待审核
        <span class="count-badge" v-if="filteredSubmissions.length">
          {{ submissions.filter(s => s.review_status?.status === 'pending').length }}
        </span>
      </button>
      <button
        :class="['filter-btn', { active: filter === 'all' }]"
        @click="filter = 'all'"
      >
        全部
      </button>
    </div>

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
    <div class="empty-state" v-if="!loading && !error && filteredSubmissions.length === 0">
      <span class="empty-icon">✓</span>
      <h2>{{ filter === 'pending' ? '没有待审核的提交' : '没有提交记录' }}</h2>
    </div>

    <!-- Submissions list -->
    <div class="submissions-list" v-if="!loading && !error && filteredSubmissions.length > 0">
      <div
        v-for="submission in filteredSubmissions"
        :key="submission.submission_id"
        class="submission-card"
      >
        <!-- Card header -->
        <div class="card-header">
          <div class="header-left">
            <h3 class="plugin-name">{{ submission.plugin?.name }}</h3>
            <span class="version-tag">v{{ submission.plugin?.version }}</span>
            <StatusBadge :status="submission.review_status?.status" />
          </div>
          <span class="submission-id">{{ submission.submission_id }}</span>
        </div>

        <!-- Card body -->
        <div class="card-body">
          <p class="description">{{ submission.plugin?.description }}</p>

          <div class="submitter-info">
            <span class="submitter-name">{{ submission.submitter?.name }}</span>
            <span class="submitter-email">{{ submission.submitter?.email }}</span>
            <span class="submitter-dept" v-if="submission.submitter?.department">
              {{ submission.submitter?.department }}
            </span>
          </div>

          <div class="keywords" v-if="submission.plugin?.keywords?.length">
            <span class="keyword" v-for="kw in submission.plugin.keywords" :key="kw">
              {{ kw }}
            </span>
          </div>

          <div class="submission-message" v-if="submission.submitter?.message">
            <span class="message-label">提交备注:</span>
            <p class="message-text">{{ submission.submitter.message }}</p>
          </div>
        </div>

        <!-- Card footer -->
        <div class="card-footer">
          <span class="submitted-date">
            提交于 {{ formatDate(submission.submitter?.submitted_at) }}
          </span>

          <!-- Action buttons (only for pending) -->
          <div class="action-buttons" v-if="submission.review_status?.status === 'pending'">
            <button
              class="btn btn-success approve-btn"
              @click="openReviewModal(submission, 'approve')"
            >
              ✓ 通过
            </button>
            <button
              class="btn btn-error reject-btn"
              @click="openReviewModal(submission, 'reject')"
            >
              ✕ 拒绝
            </button>
          </div>

          <!-- Review info (for processed) -->
          <div class="review-info" v-if="submission.review_status?.status !== 'pending'">
            <span class="reviewer">
              {{ submission.review_status?.reviewed_by }} 审核于
              {{ formatDate(submission.review_status?.reviewed_at) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Review Modal -->
    <div class="modal-overlay" v-if="showReviewModal" @click.self="closeReviewModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ reviewAction === 'approve' ? '通过审核' : '拒绝提交' }}</h2>
          <button class="modal-close" @click="closeReviewModal">✕</button>
        </div>

        <div class="modal-body">
          <p class="modal-plugin-name">
            {{ selectedSubmission?.plugin?.name }}
          </p>

          <div class="form-group">
            <label>
              {{ reviewAction === 'approve' ? '审核备注 (可选)' : '拒绝原因 *' }}
            </label>
            <textarea
              v-model="reviewNotes"
              :placeholder="reviewAction === 'approve' ? '审核备注...' : '请说明拒绝原因...'"
              rows="3"
            ></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeReviewModal">
            取消
          </button>
          <button
            :class="['btn', reviewAction === 'approve' ? 'btn-success' : 'btn-error']"
            @click="submitReview"
            :disabled="reviewLoading || (reviewAction === 'reject' && !reviewNotes)"
          >
            {{ reviewLoading ? '处理中...' : (reviewAction === 'approve' ? '确认通过' : '确认拒绝') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-reviews-page {
  max-width: 900px;
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

.filters-bar {
  display: flex;
  gap: var(--space-sm);
  margin-bottom: var(--space-lg);
}

.filter-btn {
  background: var(--color-card);
  border: 1px solid var(--color-border-subtle);
  color: var(--color-text-secondary);
  font-family: var(--font-display);
  font-size: 14px;
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.filter-btn.active {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.count-badge {
  background: var(--color-warning);
  color: var(--color-bg);
  font-size: 11px;
  padding: 2px 6px;
  border-radius: var(--radius-sm);
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

.empty-state h2 {
  font-family: var(--font-display);
  color: var(--color-text);
}

.submissions-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
}

.submission-card {
  background: var(--color-card);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-md);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.plugin-name {
  font-family: var(--font-display);
  font-size: 18px;
  color: var(--color-text);
}

.version-tag {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--color-primary);
  background: var(--color-primary-muted);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.submission-id {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--color-text-muted);
}

.card-body {
  margin-bottom: var(--space-md);
}

.description {
  font-family: var(--font-body);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-md);
}

.submitter-info {
  display: flex;
  gap: var(--space-md);
  font-size: 13px;
  color: var(--color-text-muted);
  margin-bottom: var(--space-sm);
}

.submitter-name {
  color: var(--color-text);
}

.keywords {
  display: flex;
  gap: var(--space-xs);
  margin-bottom: var(--space-md);
}

.keyword {
  font-family: var(--font-display);
  font-size: 11px;
  color: var(--color-text-muted);
  background: var(--color-bg);
  border: 1px solid var(--color-border-subtle);
  padding: 4px 10px;
  border-radius: var(--radius-sm);
}

.submission-message {
  background: var(--color-bg);
  padding: var(--space-md);
  border-radius: var(--radius-md);
}

.message-label {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--color-text-muted);
}

.message-text {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-top: var(--space-xs);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.submitted-date {
  font-size: 12px;
  color: var(--color-text-muted);
}

.action-buttons {
  display: flex;
  gap: var(--space-sm);
}

.approve-btn,
.reject-btn {
  font-family: var(--font-display);
  font-size: 13px;
  padding: 6px 16px;
}

.review-info {
  font-size: 13px;
  color: var(--color-text-muted);
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  max-width: 400px;
  width: 100%;
  padding: var(--space-xl);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-lg);
}

.modal-header h2 {
  font-family: var(--font-display);
  font-size: 18px;
  color: var(--color-text);
}

.modal-close {
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  font-size: 18px;
  cursor: pointer;
}

.modal-body {
  margin-bottom: var(--space-lg);
}

.modal-plugin-name {
  font-family: var(--font-display);
  font-size: 16px;
  color: var(--color-primary);
  margin-bottom: var(--space-lg);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-md);
}
</style>