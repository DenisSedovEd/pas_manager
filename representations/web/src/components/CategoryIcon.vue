<script setup>
import { computed, ref, watch } from 'vue'
import {
  customIconFileUrl,
  iconDisplayLabel,
  isCustomIcon,
} from '../api/customIcon.js'

const props = defineProps({
  icon: { type: String, default: null },
  fallback: { type: String, default: '📁' },
  size: { type: String, default: 'md' },
})

const imgFailed = ref(false)

const custom = computed(() => isCustomIcon(props.icon) && !imgFailed.value)
const src = computed(() => (custom.value ? customIconFileUrl(props.icon) : null))
const text = computed(() => iconDisplayLabel(props.icon, props.fallback))

watch(
  () => props.icon,
  () => {
    imgFailed.value = false
  },
)
</script>

<template>
  <img
    v-if="custom && src"
    class="category-icon-img"
    :class="[`size-${size}`]"
    :src="src"
    alt=""
    @error="imgFailed = true"
  />
  <span v-else class="category-icon-text" :class="[`size-${size}`]">{{ text }}</span>
</template>

<style scoped>
.category-icon-img {
  object-fit: contain;
  flex-shrink: 0;
  display: block;
}

.category-icon-text {
  flex-shrink: 0;
  line-height: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.size-sm {
  width: 1.25rem;
  height: 1.25rem;
  font-size: 1.25rem;
}

.size-md {
  width: 1.5rem;
  height: 1.5rem;
  font-size: 1.5rem;
}

.size-lg {
  width: 2.5rem;
  height: 2.5rem;
  font-size: 2.2rem;
}

.size-xl {
  width: 3.5rem;
  height: 3.5rem;
  font-size: 3.5rem;
}
</style>
