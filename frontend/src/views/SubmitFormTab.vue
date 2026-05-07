<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Object, required: true },
  disabled: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'submit'])

const form = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const isValid = computed(() => {
  return form.value.pluginName &&
    form.value.pluginDescription &&
    form.value.pluginVersion &&
    /^[0-9]+\.[0-9]+\.[0-9]+$/.test(form.value.pluginVersion)
})

const versionError = computed(() => {
  if (!form.value.pluginVersion) return ''
  if (!/^[0-9]+\.[0-9]+\.[0-9]+$/.test(form.value.pluginVersion)) {
    return '版本号格式应为 X.Y.Z (如 1.0.0)'
  }
  return ''
})

const parseKeywords = (str) => {
  return str.split(',')
    .map(k => k.trim())
    .filter(k => k.length > 0)
}

const handleSubmit = () => {
  if (!isValid.value || props.disabled) return
  emit('submit', {
    plugin: {
      name: form.value.pluginName,
      description: form.value.pluginDescription,
      version: form.value.pluginVersion,
      keywords: parseKeywords(form.value.pluginKeywords),
      homepage: form.value.pluginHomepage || null
    }
  })
}

const updateField = (field, value) => {
  emit('update:modelValue', { ...props.modelValue, [field]: value })
}
</script>

<template>
  <div class="tab-content">
    <div class="form-section">
      <h2 class="form-section-title">插件信息</h2>

      <div class="form-group">
        <label for="pluginName">插件名称 *</label>
        <div class="input-wrapper">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="input-icon">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
          </svg>
          <input
            id="pluginName"
            :value="form.pluginName"
            @input="updateField('pluginName', $event.target.value)"
            placeholder="例如: nl2sql"
            required
          />
        </div>
      </div>

      <div class="form-group">
        <label for="pluginDescription">插件描述 *</label>
        <textarea
          id="pluginDescription"
          :value="form.pluginDescription"
          @input="updateField('pluginDescription', $event.target.value)"
          placeholder="简要描述插件功能..."
          rows="3"
          required
        ></textarea>
      </div>

      <div class="form-group">
        <label for="pluginVersion">版本号 *</label>
        <div class="input-wrapper">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="input-icon">
            <circle cx="12" cy="12" r="3" />
            <line x1="3" y1="12" x2="9" y2="12" />
            <line x1="15" y1="12" x2="21" y2="12" />
          </svg>
          <input
            id="pluginVersion"
            :value="form.pluginVersion"
            @input="updateField('pluginVersion', $event.target.value)"
            placeholder="例如: 1.0.0"
            :class="{ 'input-error': versionError }"
            required
          />
        </div>
        <span class="field-error" v-if="versionError">{{ versionError }}</span>
      </div>

      <div class="form-group">
        <label for="pluginKeywords">关键词 (逗号分隔)</label>
        <div class="input-wrapper">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="input-icon">
            <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" />
            <line x1="7" y1="7" x2="7.01" y2="7" />
          </svg>
          <input
            id="pluginKeywords"
            :value="form.pluginKeywords"
            @input="updateField('pluginKeywords', $event.target.value)"
            placeholder="database, sql, automation"
          />
        </div>
      </div>

      <div class="form-group">
        <label for="pluginHomepage">项目主页 (可选)</label>
        <div class="input-wrapper">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="input-icon">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
            <polyline points="15 3 21 3 21 9" />
            <line x1="10" y1="14" x2="21" y2="3" />
          </svg>
          <input
            id="pluginHomepage"
            :value="form.pluginHomepage"
            @input="updateField('pluginHomepage', $event.target.value)"
            type="url"
            placeholder="https://gitlab.company.com/..."
          />
        </div>
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
          <path d="M12 20h9" />
          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
        </svg>
        <span v-if="disabled">提交中...</span>
        <span v-else>提交审核</span>
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
  margin-bottom: var(--space-5);
  padding-bottom: var(--space-2);
  border-bottom: 1px solid var(--color-border-subtle);
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

.input-wrapper input,
.input-wrapper textarea {
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

textarea {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  background: var(--color-bg-subtle);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-md);
  font-family: var(--font-body);
  font-size: 14px;
  color: var(--color-text);
  resize: vertical;
  transition: all var(--transition-fast);
}

textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-muted);
}

textarea::placeholder {
  color: var(--color-text-dim);
}

.input-error {
  border-color: var(--color-error) !important;
}

.field-error {
  display: block;
  font-size: 12px;
  color: var(--color-error);
  margin-top: var(--space-1);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.submit-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  min-width: 140px;
  justify-content: center;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
