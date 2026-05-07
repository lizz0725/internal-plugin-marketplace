<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '搜索插件...'
  }
})

const emit = defineEmits(['update:modelValue'])

const searchInput = ref(props.modelValue)
const isFocused = ref(false)

watch(searchInput, (value) => {
  emit('update:modelValue', value)
})

const clearSearch = () => {
  searchInput.value = ''
}
</script>

<template>
  <div class="search-bar" :class="{ focused: isFocused }">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="search-icon">
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
    <input
      type="text"
      v-model="searchInput"
      :placeholder="placeholder"
      @focus="isFocused = true"
      @blur="isFocused = false"
    />
    <button class="clear-btn" v-if="searchInput" @click="clearSearch" aria-label="清除搜索">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
        <line x1="18" y1="6" x2="6" y2="18" />
        <line x1="6" y1="6" x2="18" y2="18" />
      </svg>
    </button>
    <span class="kbd">⌘K</span>
  </div>
</template>

<style scoped>
.search-bar {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-3) var(--space-4);
  transition: all var(--transition-fast);
  max-width: 400px;
}

.search-bar.focused {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-muted);
}

.search-icon {
  width: 18px;
  height: 18px;
  color: var(--color-text-dim);
  flex-shrink: 0;
}

input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-family: var(--font-body);
  font-size: 14px;
  color: var(--color-text);
  padding: 0;
}

input::placeholder {
  color: var(--color-text-dim);
}

.clear-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: var(--color-text-dim);
  cursor: pointer;
  padding: 2px;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.clear-btn:hover {
  color: var(--color-text);
}

.kbd {
  display: inline-flex;
  align-items: center;
  padding: 2px 6px;
  background: var(--color-bg-subtle);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-sm);
  font-family: var(--font-display);
  font-size: 11px;
  color: var(--color-text-dim);
  line-height: 1.4;
}
</style>
