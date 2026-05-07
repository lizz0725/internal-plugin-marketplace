<script setup>
import { ref, computed } from 'vue'

const emit = defineEmits(['submit'])
const props = defineProps({
  submitterInfo: { type: Object, required: true },
  disabled: { type: Boolean, default: false }
})

const gitUrl = ref('')
const gitRef = ref('main')
const gitToken = ref('')
const showToken = ref(false)

const isValid = computed(() => {
  if (!gitUrl.value) return false
  return gitUrl.value.startsWith('https://') ||
    gitUrl.value.startsWith('http://') ||
    gitUrl.value.startsWith('git@')
})

const urlError = computed(() => {
  if (!gitUrl.value) return ''
  if (!isValid.value) return 'Git URL 格式不正确 (应以 https://, http:// 或 git@ 开头)'
  return ''
})

function handleSubmit() {
  if (!isValid.value || props.disabled) return

  const payload = {
    git_url: gitUrl.value,
    git_ref: gitRef.value || 'main',
    submitter: {
      name: props.submitterInfo.name,
      email: props.submitterInfo.email,
      department: props.submitterInfo.department || null,
      submitted_at: new Date().toISOString(),
      message: props.submitterInfo.message || null
    }
  }

  if (gitToken.value) {
    payload.git_token = gitToken.value
  }

  emit('submit', payload)
}
</script>

<template>
  <div class="tab-content">
    <div class="form-section">
      <h2 class="form-section-title">从 Git 仓库同步</h2>
      <p class="section-desc">从第三方 Git 仓库同步插件（需包含 .claude-plugin/ 目录）</p>

      <div class="form-group">
        <label for="gitUrl">Git 仓库地址 *</label>
        <div class="input-wrapper">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="input-icon">
            <circle cx="18" cy="18" r="3" />
            <circle cx="6" cy="6" r="3" />
            <path d="M13 6h3a2 2 0 0 1 2 2v7" />
            <line x1="6" y1="9" x2="6" y2="21" />
          </svg>
          <input
            id="gitUrl"
            v-model="gitUrl"
            placeholder="https://github.com/user/plugin-repo.git"
            required
          />
        </div>
        <span class="field-error" v-if="urlError">{{ urlError }}</span>
      </div>

      <div class="form-group">
        <label for="gitRef">分支 / Tag / Commit</label>
        <div class="input-wrapper">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="input-icon">
            <line x1="6" y1="3" x2="6" y2="15" />
            <circle cx="18" cy="6" r="3" />
            <circle cx="6" cy="18" r="3" />
            <path d="M18 9a9 9 0 0 1-9 9" />
          </svg>
          <input
            id="gitRef"
            v-model="gitRef"
            placeholder="main (默认)"
          />
        </div>
      </div>

      <div class="form-group">
        <label for="gitToken">访问 Token (私有仓库需要)</label>
        <div class="input-wrapper">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="input-icon">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
          <input
            id="gitToken"
            v-model="gitToken"
            :type="showToken ? 'text' : 'password'"
            placeholder="ghp_xxxxxxxxxxxx"
          />
          <button
            type="button"
            class="toggle-token"
            @click="showToken = !showToken"
            :title="showToken ? '隐藏' : '显示'"
          >
            <svg v-if="!showToken" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
              <circle cx="12" cy="12" r="3" />
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
              <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" />
              <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
              <line x1="1" y1="1" x2="23" y2="23" />
            </svg>
          </button>
        </div>
        <span class="field-hint">仅用于此次克隆，不会持久化存储</span>
      </div>
    </div>

    <div class="form-actions">
      <button
        type="button"
        class="btn btn-primary submit-btn"
        :disabled="!isValid || disabled"
        @click="handleSubmit"
      >
        <svg v-if="!disabled" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
          <circle cx="18" cy="18" r="3" />
          <circle cx="6" cy="6" r="3" />
          <path d="M13 6h3a2 2 0 0 1 2 2v7" />
          <line x1="6" y1="9" x2="6" y2="21" />
        </svg>
        <span v-if="disabled">同步中...</span>
        <span v-else>同步并提交</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.tab-content {
  padding-top: var(--space-6);
}

.form-section {
  margin-bottom: var(--space-8);
}

.form-section-title {
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 500;
  color: var(--color-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--space-1);
}

.section-desc {
  font-size: 13px;
  color: var(--color-text-muted);
  margin-bottom: var(--space-5);
}

.form-group {
  margin-bottom: var(--space-4);
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

.toggle-token {
  background: none;
  border: none;
  color: var(--color-text-dim);
  cursor: pointer;
  padding: 2px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
}

.toggle-token:hover {
  color: var(--color-primary);
}

.field-error {
  display: block;
  font-size: 12px;
  color: var(--color-error);
  margin-top: var(--space-1);
}

.field-hint {
  display: block;
  font-size: 11px;
  color: var(--color-text-dim);
  margin-top: 4px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.submit-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  min-width: 160px;
  justify-content: center;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
