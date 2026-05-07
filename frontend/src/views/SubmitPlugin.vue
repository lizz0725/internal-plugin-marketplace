<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { submitPlugin, submitPluginUpload, submitPluginGit } from '../api'
import { useAppStore } from '../stores'
import SubmitFormTab from './SubmitFormTab.vue'
import SubmitUploadTab from './SubmitUploadTab.vue'
import SubmitGitSyncTab from './SubmitGitSyncTab.vue'

const router = useRouter()
const store = useAppStore()

const activeTab = ref('form')
const loading = ref(false)
const submitted = ref(false)
const submissionId = ref('')
const error = ref(null)
const uploadProgress = ref(0)

// Shared submitter info
const submitter = reactive({
  name: store.userName || '',
  email: store.userEmail || '',
  department: '',
  message: ''
})

// Form tab model (plugin fields only, submitter is managed separately)
const formModel = reactive({
  pluginName: '',
  pluginDescription: '',
  pluginVersion: '',
  pluginKeywords: '',
  pluginHomepage: ''
})

const isSubmitterValid = () => {
  return submitter.name && submitter.email
}

const handleFormSubmit = async (pluginData) => {
  if (!isSubmitterValid() || loading.value) return
  loading.value = true
  error.value = null
  try {
    const payload = {
      plugin: {
        name: pluginData.plugin.name,
        description: pluginData.plugin.description,
        version: pluginData.plugin.version,
        author: {
          name: submitter.name,
          email: submitter.email
        },
        keywords: pluginData.plugin.keywords,
        homepage: pluginData.plugin.homepage || null,
        license: 'proprietary'
      },
      submitter: {
        name: submitter.name,
        email: submitter.email,
        department: submitter.department || null,
        submitted_at: new Date().toISOString(),
        message: submitter.message || null
      }
    }
    const response = await submitPlugin(payload)
    submissionId.value = response.data.submission_id
    submitted.value = true
  } catch (err) {
    error.value = err.response?.data?.detail || '提交失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

const handleUploadSubmit = async (formData) => {
  if (!isSubmitterValid() || loading.value) return
  loading.value = true
  error.value = null
  uploadProgress.value = 1
  try {
    const response = await submitPluginUpload(formData)
    submissionId.value = response.data.submission_id
    submitted.value = true
  } catch (err) {
    error.value = err.response?.data?.detail || '上传提交失败，请稍后重试'
  } finally {
    loading.value = false
    uploadProgress.value = 0
  }
}

const handleGitSubmit = async (payload) => {
  if (!isSubmitterValid() || loading.value) return
  loading.value = true
  error.value = null
  try {
    const response = await submitPluginGit(payload)
    submissionId.value = response.data.submission_id
    submitted.value = true
  } catch (err) {
    error.value = err.response?.data?.detail || 'Git 同步提交失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  submitted.value = false
  submissionId.value = ''
  error.value = null
  formModel.pluginName = ''
  formModel.pluginDescription = ''
  formModel.pluginVersion = ''
  formModel.pluginKeywords = ''
  formModel.pluginHomepage = ''
  submitter.department = ''
  submitter.message = ''
}
</script>

<template>
  <div class="submit-page">
    <!-- Header -->
    <header class="page-header">
      <h1 class="title">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="title-icon">
          <path d="M12 20h9" />
          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
        </svg>
        提交插件
      </h1>
      <p class="subtitle">提交你的插件到企业内部市场，等待管理员审核</p>
    </header>

    <!-- Success state -->
    <div class="success-state" v-if="submitted">
      <div class="success-card">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="success-icon">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
          <polyline points="22 4 12 14.01 9 11.01" />
        </svg>
        <h2>提交成功！</h2>
        <p class="submission-id">
          提交编号: <code>{{ submissionId }}</code>
        </p>
        <p class="success-message">
          你的插件已进入审核队列，审核通过后将在插件市场展示。
        </p>
        <div class="success-actions">
          <button class="btn btn-secondary" @click="resetForm">提交新插件</button>
          <router-link to="/my-submissions" class="btn btn-primary">
            查看我的提交
          </router-link>
        </div>
      </div>
    </div>

    <!-- Form -->
    <div class="form-container" v-if="!submitted">
      <!-- Method tabs -->
      <div class="method-tabs">
        <button
          :class="['tab', { active: activeTab === 'form' }]"
          @click="activeTab = 'form'"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
            <path d="M12 20h9" />
            <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
          </svg>
          手动填写
        </button>
        <button
          :class="['tab', { active: activeTab === 'upload' }]"
          @click="activeTab = 'upload'"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
          上传压缩包
        </button>
        <button
          :class="['tab', { active: activeTab === 'git' }]"
          @click="activeTab = 'git'"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
            <circle cx="18" cy="18" r="3" />
            <circle cx="6" cy="6" r="3" />
            <path d="M13 6h3a2 2 0 0 1 2 2v7" />
            <line x1="6" y1="9" x2="6" y2="21" />
          </svg>
          Git 同步
        </button>
      </div>

      <!-- Shared submitter section -->
      <div class="shared-section">
        <h2 class="form-section-title">提交者信息</h2>
        <div class="form-row">
          <div class="form-group">
            <label for="submitterName">姓名 *</label>
            <div class="input-wrapper">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="input-icon">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
              <input
                id="submitterName"
                v-model="submitter.name"
                required
              />
            </div>
          </div>
          <div class="form-group">
            <label for="submitterEmail">邮箱 *</label>
            <div class="input-wrapper">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="input-icon">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                <polyline points="22,6 12,13 2,6" />
              </svg>
              <input
                id="submitterEmail"
                v-model="submitter.email"
                type="email"
                required
              />
            </div>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label for="submitterDepartment">部门</label>
            <div class="input-wrapper">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="input-icon">
                <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
                <line x1="8" y1="21" x2="16" y2="21" />
                <line x1="12" y1="17" x2="12" y2="21" />
              </svg>
              <input
                id="submitterDepartment"
                v-model="submitter.department"
                placeholder="例如: 数据平台团队"
              />
            </div>
          </div>
          <div class="form-group">
            <label for="submitterMessage">备注信息</label>
            <div class="input-wrapper">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="input-icon">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
              <input
                id="submitterMessage"
                v-model="submitter.message"
                placeholder="向审核人员说明的额外信息..."
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Tab content: Manual form -->
      <SubmitFormTab
        v-if="activeTab === 'form'"
        v-model="formModel"
        :disabled="loading"
        @submit="handleFormSubmit"
      />

      <!-- Tab content: Upload zip -->
      <SubmitUploadTab
        v-else-if="activeTab === 'upload'"
        :submitter-info="submitter"
        :upload-progress="uploadProgress"
        :disabled="loading"
        @submit="handleUploadSubmit"
      />

      <!-- Tab content: Git sync -->
      <SubmitGitSyncTab
        v-else-if="activeTab === 'git'"
        :submitter-info="submitter"
        :disabled="loading"
        @submit="handleGitSubmit"
      />

      <!-- Shared error -->
      <div class="form-error" v-if="error">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16" class="error-icon">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
        {{ error }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.submit-page {
  max-width: 640px;
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

/* Success */
.success-state {
  padding: var(--space-8) 0;
}

.success-card {
  background: var(--color-card);
  border: 1px solid var(--color-success-muted);
  border-radius: var(--radius-xl);
  padding: var(--space-10);
  text-align: center;
}

.success-icon {
  width: 48px;
  height: 48px;
  color: var(--color-success);
  margin-bottom: var(--space-4);
}

.success-card h2 {
  font-family: var(--font-display);
  font-size: 20px;
  color: var(--color-success);
  margin-bottom: var(--space-3);
}

.submission-id {
  font-size: 14px;
  color: var(--color-text-muted);
  margin-bottom: var(--space-3);
}

.submission-id code {
  font-family: var(--font-display);
  background: var(--color-bg);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  color: var(--color-primary);
}

.success-message {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-6);
}

.success-actions {
  display: flex;
  gap: var(--space-3);
  justify-content: center;
}

/* Form container */
.form-container {
  background: var(--color-card);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
}

/* Method tabs */
.method-tabs {
  display: flex;
  gap: 0;
  margin-bottom: var(--space-6);
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  padding: 3px;
}

.tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tab:hover {
  color: var(--color-text-secondary);
}

.tab.active {
  background: var(--color-card);
  color: var(--color-primary);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Shared section */
.shared-section {
  margin-bottom: var(--space-2);
  padding-bottom: var(--space-6);
  border-bottom: 1px solid var(--color-border-subtle);
}

.form-section-title {
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 500;
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--space-4);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
  margin-bottom: 0;
}

.form-group {
  margin-bottom: var(--space-3);
}

label {
  display: block;
  font-family: var(--font-display);
  font-size: 11px;
  font-weight: 500;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--space-1);
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: var(--color-bg-subtle);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.input-wrapper:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-muted);
}

.input-icon {
  width: 16px;
  height: 16px;
  color: var(--color-text-dim);
  flex-shrink: 0;
}

.input-wrapper input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-family: var(--font-body);
  font-size: 14px;
  color: var(--color-text);
  padding: 0;
}

.input-wrapper input::placeholder {
  color: var(--color-text-dim);
}

/* Error */
.form-error {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  color: var(--color-error);
  background: var(--color-error-muted);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  margin-top: var(--space-6);
  font-size: 14px;
}

.form-error .error-icon {
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
