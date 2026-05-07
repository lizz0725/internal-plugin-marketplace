<script setup>
import { ref, computed } from 'vue'

const emit = defineEmits(['submit'])
const props = defineProps({
  submitterInfo: { type: Object, required: true },
  uploadProgress: { type: Number, default: 0 },
  disabled: { type: Boolean, default: false }
})

const selectedFile = ref(null)
const dragOver = ref(false)
const fileError = ref('')

const maxSizeMB = 50

const fileSizeOk = computed(() => {
  if (!selectedFile.value) return true
  return selectedFile.value.size <= maxSizeMB * 1024 * 1024
})

const filePreview = computed(() => {
  if (!selectedFile.value) return null
  const sizeMB = (selectedFile.value.size / 1024 / 1024).toFixed(1)
  return {
    name: selectedFile.value.name,
    size: `${sizeMB} MB`
  }
})

const isValid = computed(() => {
  return selectedFile.value && fileSizeOk.value && !fileError.value
})

function onDragOver(e) {
  e.preventDefault()
  dragOver.value = true
}

function onDragLeave() {
  dragOver.value = false
}

function onDrop(e) {
  e.preventDefault()
  dragOver.value = false
  const files = e.dataTransfer?.files
  if (files?.length) validateAndSet(files[0])
}

function onFileChange(e) {
  const files = e.target?.files
  if (files?.length) validateAndSet(files[0])
}

function validateAndSet(file) {
  fileError.value = ''

  if (!file.name.endsWith('.zip')) {
    fileError.value = '仅支持 .zip 格式的压缩包'
    selectedFile.value = null
    return
  }

  const maxBytes = maxSizeMB * 1024 * 1024
  if (file.size > maxBytes) {
    fileError.value = `文件大小超过 ${maxSizeMB}MB 限制`
    selectedFile.value = null
    return
  }

  if (file.size === 0) {
    fileError.value = '文件为空'
    selectedFile.value = null
    return
  }

  selectedFile.value = file
}

function removeFile() {
  selectedFile.value = null
  fileError.value = ''
}

function handleSubmit() {
  if (!isValid.value || props.disabled) return

  const formData = new FormData()
  formData.append('file', selectedFile.value)
  formData.append('submitter_name', props.submitterInfo.name)
  formData.append('submitter_email', props.submitterInfo.email)
  if (props.submitterInfo.department) {
    formData.append('submitter_department', props.submitterInfo.department)
  }
  if (props.submitterInfo.message) {
    formData.append('submitter_message', props.submitterInfo.message)
  }

  emit('submit', formData)
}
</script>

<template>
  <div class="tab-content">
    <div class="form-section">
      <h2 class="form-section-title">上传插件压缩包</h2>
      <p class="section-desc">上传包含 .claude-plugin/ 目录的 ZIP 压缩包</p>

      <!-- Drop zone -->
      <div
        class="drop-zone"
        :class="{ 'drag-over': dragOver, 'has-file': selectedFile }"
        @dragover="onDragOver"
        @dragleave="onDragLeave"
        @drop="onDrop"
      >
        <template v-if="!selectedFile">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="drop-icon">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
          <p class="drop-text">拖拽 ZIP 文件到此处</p>
          <p class="drop-hint">或点击选择文件</p>
          <input
            type="file"
            accept=".zip"
            class="file-input"
            @change="onFileChange"
          />
        </template>

        <template v-else>
          <div class="file-preview">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="file-icon">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
            </svg>
            <div class="file-info">
              <span class="file-name">{{ filePreview.name }}</span>
              <span class="file-size">{{ filePreview.size }}</span>
            </div>
            <button type="button" class="btn-remove" @click="removeFile" :disabled="disabled">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
        </template>
      </div>

      <p class="field-error" v-if="fileError">{{ fileError }}</p>

      <!-- Structure hint -->
      <div class="structure-hint">
        <p class="hint-title">期望的目录结构:</p>
        <pre class="hint-tree">
.claude-plugin/
├── plugin.json          (必需)
├── commands/            (可选)
├── hooks/               (可选)
└── assets/              (可选)</pre>
      </div>
    </div>

    <div class="form-actions">
      <button
        type="button"
        class="btn btn-primary submit-btn"
        :disabled="!isValid || disabled"
        @click="handleSubmit"
      >
        <svg v-if="uploadProgress > 0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16" class="spin">
          <line x1="12" y1="2" x2="12" y2="6" />
          <line x1="12" y1="18" x2="12" y2="22" />
          <line x1="4.93" y1="4.93" x2="7.76" y2="7.76" />
          <line x1="16.24" y1="16.24" x2="19.07" y2="19.07" />
          <line x1="2" y1="12" x2="6" y2="12" />
          <line x1="18" y1="12" x2="22" y2="12" />
          <line x1="4.93" y1="19.07" x2="7.76" y2="16.24" />
          <line x1="16.24" y1="7.76" x2="19.07" y2="4.93" />
        </svg>
        <span v-else>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
        </span>
        <span v-if="disabled">上传中...</span>
        <span v-else>上传并提交</span>
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

.drop-zone {
  position: relative;
  border: 2px dashed var(--color-border-subtle);
  border-radius: var(--radius-xl);
  padding: var(--space-10);
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-fast);
  background: var(--color-bg-subtle);
}

.drop-zone:hover,
.drop-zone.drag-over {
  border-color: var(--color-primary);
  background: var(--color-primary-muted);
}

.drop-zone.has-file {
  border-style: solid;
  border-color: var(--color-success-muted);
  background: var(--color-bg-subtle);
  padding: var(--space-6);
}

.file-input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.drop-icon {
  width: 40px;
  height: 40px;
  color: var(--color-text-dim);
  margin-bottom: var(--space-3);
}

.drop-text {
  font-size: 15px;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-1);
}

.drop-hint {
  font-size: 12px;
  color: var(--color-text-dim);
}

/* File preview */
.file-preview {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.file-icon {
  width: 32px;
  height: 32px;
  color: var(--color-primary);
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
}

.file-size {
  font-size: 12px;
  color: var(--color-text-dim);
}

.btn-remove {
  background: none;
  border: none;
  color: var(--color-text-dim);
  cursor: pointer;
  padding: var(--space-1);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.btn-remove:hover {
  color: var(--color-error);
  background: var(--color-error-muted);
}

.field-error {
  display: block;
  font-size: 13px;
  color: var(--color-error);
  margin-top: var(--space-2);
}

/* Structure hint */
.structure-hint {
  margin-top: var(--space-5);
  padding: var(--space-4);
  background: var(--color-bg);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-subtle);
}

.hint-title {
  font-size: 11px;
  font-weight: 500;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--space-2);
}

.hint-tree {
  font-family: var(--font-display);
  font-size: 12px;
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0;
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

@keyframes spin {
  to { transform: rotate(360deg); }
}

.spin {
  animation: spin 1s linear infinite;
}
</style>
