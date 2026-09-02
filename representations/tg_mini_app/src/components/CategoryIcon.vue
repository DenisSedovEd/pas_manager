<script setup>
import { computed, ref, watch, onUnmounted } from 'vue'
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

const initData = window.Telegram?.WebApp?.initData ?? ''

const imgFailed = ref(false)
const blobUrl = ref(null)

const custom = computed(() => isCustomIcon(props.icon) && !imgFailed.value && !!blobUrl.value)
const text = computed(() => iconDisplayLabel(props.icon, props.fallback))

const loadCustomIcon = async () => {
  if (blobUrl.value) {
    URL.revokeObjectURL(blobUrl.value)
    blobUrl.value = null
  }
  imgFailed.value = false
  if (!isCustomIcon(props.icon)) return

  const url = customIconFileUrl(props.icon)
  if (!url) return

  try {
    const res = await fetch(url, {
      headers: { Authorization: initData },
    })
    if (!res.ok) throw new Error('Failed to load icon')
    const blob = await res.blob()
    blobUrl.value = URL.createObjectURL(blob)
  } catch {
    imgFailed.value = true
  }
}

watch(() => props.icon, loadCustomIcon, { immediate: true })

onUnmounted(() => {
  if (blobUrl.value) URL.revokeObjectURL(blobUrl.value)
})
</script>

<template>
  <img
    v-if="custom"
    class="category-icon-img"
    :class="[`size-${size}`]"
    :src="blobUrl"
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
  width: 3.25rem;
  height: 3.25rem;
  font-size: 3.25rem;
}

.size-fill {
  width: 100%;
  height: 100%;
  font-size: 24px;
}
</style>
