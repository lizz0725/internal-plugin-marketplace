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
    <span class="search-icon">🔍</span>
    <input
      type="text"
      v-model="searchInput"
      :placeholder="placeholder"
      @focus="isFocused = true"
      @blur="isFocused = false"
    />
    <button class="clear-btn" v-if="searchInput" @click="clearSearch">
      ✕
    </button>
  </div>
</template>

<style scoped>
.search-bar {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  background: var(--color-bg-subtle);
  border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg);
  padding: var(--space-sm) var(--space-md);
  transition: all var(--transition-fast);
  max-width: 400px;
}

.search-bar.focused {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px var(--color-primary-muted);
}

.search-icon {
  font-size: 16px;
  color: var(--color-text-muted);
}

input {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--color-text);
  font-size: 14px;
  padding: 0;
}

input:focus {
  outline: none;
}

input::placeholder {
  color: var(--color-text-muted);
}

.clear-btn {
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  font-size: 12px;
  padding: 4px;
}

.clear-btn:hover {
  color: var(--color-text);
}
</style>