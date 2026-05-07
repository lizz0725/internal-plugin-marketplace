<script setup>
import { ref, onMounted, computed } from 'vue'
import { getPendingReviews, approveSubmission, rejectSubmission, getSubmissionFiles } from '../api'
import { useAppStore } from '../stores'
import StatusBadge from '../components/StatusBadge.vue'

const store = useAppStore()

const submissions = ref([])
const loading = ref(true)
const error = ref(null)
const filter = ref('all') // pending, approved, rejected, all

const filteredSubmissions = computed(() => {
  if (filter.value === 'all') return submissions.value
  return submissions.value.filter(s => s.review_status?.status === filter.value)
})

const counts = computed(() => ({
  all: submissions.value.length,
  pending: submissions.value.filter(s => s.review_status?.status === 'pending').length,
  approved: submissions.value.filter(s => s.review_status?.status === 'approved').length,
  rejected: submissions.value.filter(s => s.review_status?.status === 'rejected').length
}))

// Review modal state
const showReviewModal = ref(false)
const selectedSubmission = ref(null)
const reviewAction = ref('')
const reviewNotes = ref('')
const reviewLoading = ref(false)

// File viewer state
const showFileViewer = ref(false)
const fileViewerSubmission = ref(null)
const fileViewerData = ref(null)
const fileViewerLoading = ref(false)

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

const openFileViewer = async (submission) => {
  fileViewerSubmission.value = submission
  fileViewerData.value = null
  showFileViewer.value = true
  fileViewerLoading.value = true
  try {
    const response = await getSubmissionFiles(submission.submission_id)
    fileViewerData.value = response.data
  } catch (err) {
    console.error('Failed to load files:', err)
  } finally {
    fileViewerLoading.value = false
  }
}

const closeFileViewer = () => {
  showFileViewer.value = false
  fileViewerSubmission.value = null
  fileViewerData.value = null
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

const typeLabel = (method) => {
  const labels = { manual: '手动', upload: '上传', 'git-sync': 'Git同步' }
  return labels[method] || method || '手动'
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

onMounted(fetchSubmissions)
</script>

<template>
  <div class="admin-reviews-page">
    <!-- Header -->
    <header class="page-header">
      <h1 class="title">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon">
          <circle cx="12" cy="12" r="10" />
          <polyline points="12 6 12 12 16 14" />
        </svg>
        审核管理
      </h1>
      <p class="subtitle">审查和审批开发者提交的插件</p>
    </header>

    <!-- Filter chips -->
    <div class="filter-chips">
      <button
        :class="['filter-chip', { active: filter === 'all' }]"
        @click="filter = 'all'"
      >
        全部
        <span class="chip-count">{{ counts.all }}</span>
      </button>
      <button
        :class="['filter-chip', { active: filter === 'pending' }]"
        @click="filter = 'pending'"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
          <circle cx="12" cy="12" r="10" />
          <polyline points="12 6 12 12 16 14" />
        </svg>
        待审核
        <span class="chip-count pending">{{ counts.pending }}</span>
      </button>
      <button
        :class="['filter-chip', { active: filter === 'approved' }]"
        @click="filter = 'approved'"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
          <polyline points="20 6 9 17 4 12" />
        </svg>
        已批准
        <span class="chip-count approved">{{ counts.approved }}</span>
      </button>
      <button
        :class="['filter-chip', { active: filter === 'rejected' }]"
        @click="filter = 'rejected'"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
        已拒绝
        <span class="chip-count rejected">{{ counts.rejected }}</span>
      </button>
    </div>

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
    <div class="state-card empty-state" v-if="!loading && !error && filteredSubmissions.length === 0">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="state-icon">
        <polyline points="20 6 9 17 4 12" />
      </svg>
      <h2 v-if="filter === 'pending'">没有待审核的提交</h2>
      <h2 v-else>没有提交记录</h2>
    </div>

    <!-- Submissions table -->
    <div class="submissions-table" v-if="!loading && !error && filteredSubmissions.length > 0">
      <!-- Table header -->
      <div class="table-header">
        <span class="col-name">插件名称</span>
        <span class="col-author">作者</span>
        <span class="col-version">版本</span>
        <span class="col-type">提交方式</span>
        <span class="col-date">提交时间</span>
        <span class="col-status">状态</span>
        <span class="col-actions">操作</span>
      </div>

      <!-- Table rows -->
      <div
        v-for="submission in filteredSubmissions"
        :key="submission.submission_id"
        class="table-row"
      >
        <span class="col-name">
          <span class="plugin-name">{{ submission.plugin?.name }}</span>
        </span>
        <span class="col-author">
          <span class="author-name">{{ submission.submitter?.name }}</span>
        </span>
        <span class="col-version">
          <span class="version-text">v{{ submission.plugin?.version }}</span>
        </span>
        <span class="col-type">
          <span :class="['type-badge', submission.submission_type?.method || 'manual']">
            {{ typeLabel(submission.submission_type?.method) }}
          </span>
        </span>
        <span class="col-date">
          <span class="date-text">{{ formatDate(submission.submitter?.submitted_at) }}</span>
        </span>
        <span class="col-status">
          <StatusBadge :status="submission.review_status?.status" size="sm" />
        </span>
        <span class="col-actions">
          <button
            v-if="submission.submission_type?.method && submission.submission_type.method !== 'manual'"
            class="btn btn-outline btn-sm"
            @click="openFileViewer(submission)"
            title="查看文件"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
            </svg>
            文件
          </button>
          <template v-if="submission.review_status?.status === 'pending'">
            <button
              class="btn btn-success btn-sm"
              @click="openReviewModal(submission, 'approve')"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              批准
            </button>
            <button
              class="btn btn-error btn-sm"
              @click="openReviewModal(submission, 'reject')"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
              拒绝
            </button>
          </template>
          <template v-else>
            <span class="review-info-text" v-if="submission.review_status?.review_notes">
              {{ submission.review_status.review_notes }}
            </span>
          </template>
        </span>
      </div>
    </div>

    <!-- Review Modal -->
    <div class="modal-overlay" v-if="showReviewModal" @click.self="closeReviewModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>{{ reviewAction === 'approve' ? '通过审核' : '拒绝提交' }}</h2>
          <button class="modal-close" @click="closeReviewModal" aria-label="关闭">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <div class="modal-body">
          <p class="modal-plugin-name">{{ selectedSubmission?.plugin?.name }}</p>
          <p class="modal-version">v{{ selectedSubmission?.plugin?.version }}</p>

          <div class="modal-form-group">
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
          <button class="btn btn-secondary" @click="closeReviewModal">取消</button>
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

    <!-- File Viewer Modal -->
    <div class="modal-overlay" v-if="showFileViewer" @click.self="closeFileViewer">
      <div class="modal-content modal-wide">
        <div class="modal-header">
          <h2>插件文件 - {{ fileViewerSubmission?.plugin?.name }}</h2>
          <button class="modal-close" @click="closeFileViewer" aria-label="关闭">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <p class="file-viewer-meta" v-if="fileViewerData?.submission_type">
            提交方式: {{ typeLabel(fileViewerData.submission_type.method) }}
            <template v-if="fileViewerData.submission_type.source_url">
              · 来源: {{ fileViewerData.submission_type.source_url }}
            </template>
            <template v-if="fileViewerData.submission_type.file_count">
              · {{ fileViewerData.submission_type.file_count }} 个文件
            </template>
          </p>

          <div class="file-tree" v-if="fileViewerLoading">
            <div class="loading-spinner"></div>
            <p class="loading-text">加载文件列表...</p>
          </div>

          <div class="file-tree" v-else-if="fileViewerData?.files">
            <div
              v-for="file in fileViewerData.files"
              :key="file.path"
              class="file-tree-item"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="file-tree-icon">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
              </svg>
              <span class="file-tree-path">{{ file.path }}</span>
              <span class="file-tree-size">{{ formatFileSize(file.size) }}</span>
            </div>
          </div>

          <div class="file-tree" v-else>
            <p class="no-files">无文件</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeFileViewer">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-reviews-page {
  max-width: 1000px;
}

.page-header {
  margin-bottom: var(--space-6);
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

/* Filter chips */
.filter-chips {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-5);
  flex-wrap: wrap;
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-family: var(--font-display);
  font-size: 12px;
  border: 1px solid var(--color-border);
  color: var(--color-text-muted);
  background: transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.filter-chip:hover {
  border-color: var(--color-text-dim);
  color: var(--color-text);
}

.filter-chip.active {
  background: var(--color-primary-muted);
  border-color: var(--color-border-active);
  color: var(--color-primary);
}

.chip-count {
  font-family: var(--font-display);
  font-size: 11px;
  padding: 0 4px;
}

.chip-count.pending { color: var(--color-warning); }
.chip-count.approved { color: var(--color-success); }
.chip-count.rejected { color: var(--color-error); }

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

/* Table */
.submissions-table {
  background: var(--color-card);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 0.8fr 0.8fr 1fr 0.8fr 1.2fr;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-5);
  background: var(--color-bg-subtle);
  border-bottom: 1px solid var(--color-border-subtle);
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: 500;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 0.8fr 0.8fr 1fr 0.8fr 1.2fr;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-5);
  border-bottom: 1px solid var(--color-border-subtle);
  align-items: center;
  transition: background var(--transition-fast);
}

.table-row:last-child {
  border-bottom: none;
}

.table-row:hover {
  background: var(--color-card-hover);
}

.plugin-name {
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text);
}

.author-name {
  font-size: 12px;
  color: var(--color-text-dim);
}

.version-text {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--color-text-secondary);
}

.date-text {
  font-size: 12px;
  color: var(--color-text-dim);
}

.col-actions {
  display: flex;
  gap: var(--space-1);
}

.review-info-text {
  font-size: 12px;
  color: var(--color-text-dim);
  font-style: italic;
}

/* Type badges */
.type-badge {
  display: inline-block;
  font-family: var(--font-display);
  font-size: 10px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  text-transform: uppercase;
  letter-spacing: 0.3px;
}

.type-badge.manual {
  background: var(--color-bg-subtle);
  color: var(--color-text-muted);
  border: 1px solid var(--color-border-subtle);
}

.type-badge.upload {
  background: var(--color-primary-muted);
  color: var(--color-primary);
  border: 1px solid var(--color-border-active);
}

.type-badge.git-sync {
  background: rgba(99, 102, 241, 0.1);
  color: #818cf8;
  border: 1px solid rgba(99, 102, 241, 0.2);
}

/* Button sizes */
.btn-sm {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-1) var(--space-3);
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: 500;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
  height: 28px;
  white-space: nowrap;
}

.btn-success {
  background: var(--color-success);
  color: #1A1A1F;
  border-color: var(--color-success);
}
.btn-success:hover {
  filter: brightness(1.1);
}

.btn-outline {
  background: transparent;
  color: var(--color-text-secondary);
  border-color: var(--color-border);
}
.btn-outline:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.btn-error {
  background: var(--color-error);
  color: #fff;
  border-color: var(--color-error);
}
.btn-error:hover {
  filter: brightness(1.1);
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
  max-width: 420px;
  width: 100%;
  padding: var(--space-6);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-5);
}

.modal-header h2 {
  font-family: var(--font-display);
  font-size: 16px;
  color: var(--color-text);
}

.modal-close {
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: var(--space-1);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.modal-close:hover {
  color: var(--color-text);
  background: var(--color-card-hover);
}

.modal-body {
  margin-bottom: var(--space-6);
}

.modal-plugin-name {
  font-family: var(--font-display);
  font-size: 18px;
  color: var(--color-primary);
  margin-bottom: var(--space-1);
}

.modal-version {
  font-size: 13px;
  color: var(--color-text-dim);
  margin-bottom: var(--space-5);
}

.modal-form-group label {
  display: block;
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--color-text-muted);
  margin-bottom: var(--space-2);
}

.modal-form-group textarea {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  background: var(--color-bg-subtle);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-md);
  font-family: var(--font-body);
  font-size: 14px;
  color: var(--color-text);
  resize: vertical;
}

.modal-form-group textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
}

/* Wide modal for file viewer */
.modal-wide {
  max-width: 600px;
}

.file-viewer-meta {
  font-size: 13px;
  color: var(--color-text-muted);
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid var(--color-border-subtle);
}

.file-tree {
  max-height: 400px;
  overflow-y: auto;
}

.file-tree .loading-spinner {
  margin: var(--space-6) auto;
}

.loading-text {
  text-align: center;
  font-size: 13px;
  color: var(--color-text-dim);
  margin-bottom: var(--space-4);
}

.file-tree-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-family: var(--font-display);
  transition: background var(--transition-fast);
}

.file-tree-item:hover {
  background: var(--color-card-hover);
}

.file-tree-icon {
  width: 14px;
  height: 14px;
  color: var(--color-text-dim);
  flex-shrink: 0;
}

.file-tree-path {
  flex: 1;
  color: var(--color-text);
  word-break: break-all;
}

.file-tree-size {
  font-size: 11px;
  color: var(--color-text-dim);
  white-space: nowrap;
}

.no-files {
  text-align: center;
  font-size: 14px;
  color: var(--color-text-dim);
  padding: var(--space-6);
}
</style>
