<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { submitPlugin } from '../api'
import { useAppStore } from '../stores'

const router = useRouter()
const store = useAppStore()

const form = reactive({
  // Plugin info
  pluginName: '',
  pluginDescription: '',
  pluginVersion: '',
  pluginKeywords: '',
  pluginHomepage: '',
  // Submitter info
  submitterName: store.userName || '',
  submitterEmail: store.userEmail || '',
  submitterDepartment: '',
  submitterMessage: ''
})

const loading = ref(false)
const submitted = ref(false)
const submissionId = ref('')
const error = ref(null)

// Form validation
const isValid = computed(() => {
  return form.pluginName &&
    form.pluginDescription &&
    form.pluginVersion &&
    /^[0-9]+\.[0-9]+\.[0-9]+$/.test(form.pluginVersion) &&
    form.submitterName &&
    form.submitterEmail
})

const versionError = computed(() => {
  if (!form.pluginVersion) return ''
  if (!/^[0-9]+\.[0-9]+\.[0-9]+$/.test(form.pluginVersion)) {
    return '版本号格式应为 X.Y.Z (如 1.0.0)'
  }
  return ''
})

// Keywords parsing
const parseKeywords = (str) => {
  return str.split(',')
    .map(k => k.trim())
    .filter(k => k.length > 0)
}

// Submit
const handleSubmit = async () => {
  if (!isValid.value || loading.value) return

  loading.value = true
  error.value = null

  try {
    const payload = {
      plugin: {
        name: form.pluginName,
        description: form.pluginDescription,
        version: form.pluginVersion,
        author: {
          name: form.submitterName,
          email: form.submitterEmail
        },
        keywords: parseKeywords(form.pluginKeywords),
        homepage: form.pluginHomepage || null,
        license: 'proprietary'
      },
      submitter: {
        name: form.submitterName,
        email: form.submitterEmail,
        department: form.submitterDepartment || null,
        submitted_at: new Date().toISOString(),
        message: form.submitterMessage || null
      }
    }

    const response = await submitPlugin(payload)
    submissionId.value = response.data.submission_id
    submitted.value = true
  } catch (err) {
    error.value = err.response?.data?.detail || '提交失败，请稍后重试'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  submitted.value = false
  submissionId.value = ''
  form.pluginName = ''
  form.pluginDescription = ''
  form.pluginVersion = ''
  form.pluginKeywords = ''
  form.pluginHomepage = ''
  form.submitterMessage = ''
}
</script>

<template>
  <div class="submit-page">
    <!-- Header -->
    <header class="page-header">
      <h1 class="title">
        <span class="title-icon">✨</span>
        提交插件
      </h1>
      <p class="subtitle">提交你的插件到企业内部市场，等待管理员审核</p>
    </header>

    <!-- Success state -->
    <div class="success-state" v-if="submitted">
      <div class="success-card">
        <span class="success-icon">🎉</span>
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
      <form @submit.prevent="handleSubmit" class="submit-form">
        <!-- Plugin section -->
        <div class="form-section">
          <h2 class="section-title">插件信息</h2>

          <div class="form-group">
            <label for="pluginName">插件名称 *</label>
            <input
              id="pluginName"
              v-model="form.pluginName"
              placeholder="例如: nl2sql"
              required
            />
          </div>

          <div class="form-group">
            <label for="pluginDescription">插件描述 *</label>
            <textarea
              id="pluginDescription"
              v-model="form.pluginDescription"
              placeholder="简要描述插件功能..."
              rows="3"
              required
            ></textarea>
          </div>

          <div class="form-group">
            <label for="pluginVersion">版本号 *</label>
            <input
              id="pluginVersion"
              v-model="form.pluginVersion"
              placeholder="例如: 1.0.0"
              :class="{ error: versionError }"
              required
            />
            <span class="field-error" v-if="versionError">{{ versionError }}</span>
          </div>

          <div class="form-group">
            <label for="pluginKeywords">关键词 (逗号分隔)</label>
            <input
              id="pluginKeywords"
              v-model="form.pluginKeywords"
              placeholder="例如: database, sql, automation"
            />
          </div>

          <div class="form-group">
            <label for="pluginHomepage">项目主页 (可选)</label>
            <input
              id="pluginHomepage"
              v-model="form.pluginHomepage"
              type="url"
              placeholder="https://gitlab.company.com/..."
            />
          </div>
        </div>

        <!-- Submitter section -->
        <div class="form-section">
          <h2 class="section-title">提交者信息</h2>

          <div class="form-row">
            <div class="form-group">
              <label for="submitterName">姓名 *</label>
              <input
                id="submitterName"
                v-model="form.submitterName"
                required
              />
            </div>
            <div class="form-group">
              <label for="submitterEmail">邮箱 *</label>
              <input
                id="submitterEmail"
                v-model="form.submitterEmail"
                type="email"
                required
              />
            </div>
          </div>

          <div class="form-group">
            <label for="submitterDepartment">部门</label>
            <input
              id="submitterDepartment"
              v-model="form.submitterDepartment"
              placeholder="例如: 数据平台团队"
            />
          </div>

          <div class="form-group">
            <label for="submitterMessage">备注信息</label>
            <textarea
              id="submitterMessage"
              v-model="form.submitterMessage"
              placeholder="向审核人员说明的额外信息..."
              rows="2"
            ></textarea>
          </div>
        </div>

        <!-- Error -->
        <div class="form-error" v-if="error">
          <span class="error-icon">⚠️</span>
          {{ error }}
        </div>

        <!-- Submit button -->
        <div class="form-actions">
          <button
            type="submit"
            class="btn btn-primary submit-btn"
            :disabled="!isValid || loading"
          >
            <span v-if="loading">提交中...</span>
            <span v-else>提交审核</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.submit-page {
  max-width: 600px;
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

.success-state {
  padding: var(--space-xl);
}

.success-card {
  background: var(--color-card);
  border: 1px solid var(--color-success);
  border-radius: var(--radius-lg);
  padding: var(--space-xl);
  text-align: center;
}

.success-icon {
  font-size: 48px;
}

.success-card h2 {
  font-family: var(--font-display);
  color: var(--color-success);
  margin: var(--space-md) 0;
}

.submission-id code {
  font-family: var(--font-display);
  background: var(--color-bg);
  padding: 4px 8px;
  border-radius: var(--radius-sm);
}

.success-message {
  color: var(--color-text-secondary);
  margin-bottom: var(--space-lg);
}

.success-actions {
  display: flex;
  gap: var(--space-md);
  justify-content: center;
}

.form-container {
  background: var(--color-card);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-xl);
}

.form-section {
  margin-bottom: var(--space-xl);
}

.section-title {
  font-family: var(--font-display);
  font-size: 16px;
  color: var(--color-primary);
  margin-bottom: var(--space-md);
  padding-bottom: var(--space-sm);
  border-bottom: 1px solid var(--color-border-subtle);
}

.form-group {
  margin-bottom: var(--space-md);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-md);
}

input.error,
textarea.error {
  border-color: var(--color-error);
}

.field-error {
  font-size: 12px;
  color: var(--color-error);
  margin-top: var(--space-xs);
}

.form-error {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  color: var(--color-error);
  background: rgba(212, 95, 95, 0.1);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-lg);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.submit-btn {
  min-width: 120px;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>