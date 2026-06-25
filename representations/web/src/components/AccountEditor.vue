<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { accountApi } from '../api/account.js'
import { categoryApi } from '../api/category.js'
import { resourceApi } from '../api/resource.js'

const props = defineProps(['account', 'currentCategory', 'resources', 'defaultResourceId', 'suggestions'])
const emit = defineEmits(['save', 'cancel', 'resource-created'])

const isLoading = ref(false)
const showPassword = ref(false)
const showCategoryWarning = ref(false)
const categoryError = ref(false)
const activeSuggestion = ref(null)
const categories = ref([])
const localResources = ref([])
watch(
  () => props.resources,
  (newVal) => {
    localResources.value = [...(newVal || [])]
  },
  { immediate: true }
)
const isEditing = computed(() => !!props.account?.id)
const prevResourceId = ref(props.account?.resource_id || props.defaultResourceId || '')

const formData = ref({
  id: props.account?.id || null,
  category_id: String(props.currentCategory?.id || props.account?.category_id || ''),
  resource_id: props.account?.resource_id || props.defaultResourceId || '',
  label: props.account?.label || '',
  login: props.account?.login || '',
  password: props.account?.password || '',
  email: props.account?.email || '',
  phone: props.account?.phone || '',
})

const handleResourceChange = (e) => {
  if (e.target.value === '__add_new__') {
    formData.value.resource_id = prevResourceId.value
    addNewResource()
  } else {
    formData.value.resource_id = e.target.value
    prevResourceId.value = e.target.value
  }
}

const addNewResource = async () => {
  const name = prompt('Название новой площадки:')
  if (!name?.trim()) return
  try {
    const created = await resourceApi.create({ resource_name: name.trim() })
    localResources.value.push(created)
    formData.value.resource_id = created.id
    prevResourceId.value = created.id
    emit('resource-created', created)
  } catch {
    alert('Ошибка создания площадки')
  }
}

const generatePassword = () => {
  const charset = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#$%^&*()_+-=[]{}|;:,.<>?'
  const length = 16
  const values = new Uint32Array(length)
  crypto.getRandomValues(values)
  formData.value.password = Array.from(values, (v) => charset[v % charset.length]).join('')
  showPassword.value = true
}

const dismissCategoryWarning = () => {
  showCategoryWarning.value = false
}

const cancelWithoutSave = () => {
  showCategoryWarning.value = false
  emit('cancel')
}

const handleSave = async () => {
  if (!formData.value.login.trim()) { alert('Введи логин'); return }
  if (!formData.value.password.trim()) { alert('Введи пароль'); return }
  if (!formData.value.category_id.trim()) {
    categoryError.value = true
    showCategoryWarning.value = true
    return
  }
  categoryError.value = false
  isLoading.value = true
  try {
    if (isEditing.value) {
      await accountApi.update(formData.value.id, formData.value)
    } else {
      await accountApi.create(formData.value)
    }
    emit('save')
  } catch {
    alert('Ошибка при сохранении')
  } finally {
    isLoading.value = false
  }
}

const handleDelete = async () => {
  if (!confirm('Удалить этот аккаунт?')) return
  try {
    await accountApi.delete(formData.value.id)
    emit('save')
  } catch {
    alert('Ошибка удаления')
  }
}

const categoryLabel = (category) => {
  const prefix = category.parent_id ? '↳ ' : ''
  return `${prefix}${category.icon || ''} ${category.name}`.trim()
}

const filteredSuggestions = (field) => {
  const value = formData.value[field]?.toLowerCase() || ''
  return (props.suggestions?.[field] || []).filter(
    (s) => s && s.toLowerCase().includes(value) && s !== formData.value[field]
  )
}

const showSuggestions = (field) => {
  activeSuggestion.value = field
}

const selectSuggestion = (field, value) => {
  formData.value[field] = value
  activeSuggestion.value = null
}

const handleOutsideClick = (event) => {
  if (!event.target.closest('.autocomplete-group')) {
    activeSuggestion.value = null
  }
}

onMounted(async () => {
  document.addEventListener('mousedown', handleOutsideClick)
  try {
    const response = await categoryApi.getAll()
    categories.value = (response.data || response).map(c => ({ ...c, id: String(c.id) }))
  } catch {
    alert('Ошибка загрузки категорий')
  }
})

onUnmounted(() => {
  document.removeEventListener('mousedown', handleOutsideClick)
})
</script>

<template>
  <div class="screen">
    <div class="screen-header">
      <h2>{{ isEditing ? 'Редактировать' : 'Новый аккаунт' }}</h2>
    </div>

    <div class="form">
      <div class="form-group">
        <label>Площадка</label>
        <select :value="formData.resource_id" @change="handleResourceChange">
          <option value="">— не выбрано —</option>
          <option v-for="r in localResources" :key="r.id" :value="r.id">{{ r.resource_name }}</option>
          <option value="__add_new__">+ Добавить площадку</option>
        </select>
      </div>

      <div class="form-group" :class="{ 'form-group-error': categoryError }">
        <label>Категория *</label>
        <select v-model="formData.category_id" @change="categoryError = false">
          <option value="" disabled>— выберите категорию —</option>
          <option v-for="c in categories" :key="c.id" :value="String(c.id)">{{ categoryLabel(c) }}</option>
        </select>
      </div>

      <div class="form-group autocomplete-group">
        <label>Метка (необязательно)</label>
        <input
          v-model="formData.label"
          type="text"
          placeholder="Например: рабочий аккаунт"
          @focus="showSuggestions('label')"
        />
        <div v-if="activeSuggestion === 'label' && filteredSuggestions('label').length" class="suggestions-list">
          <button
            v-for="s in filteredSuggestions('label')"
            :key="s"
            type="button"
            class="suggestion-item"
            @mousedown.prevent="selectSuggestion('label', s)"
          >
            {{ s }}
          </button>
        </div>
      </div>

      <div class="form-group autocomplete-group">
        <label>Логин *</label>
        <input
          v-model="formData.login"
          type="text"
          placeholder="Логин или email"
          @focus="showSuggestions('login')"
        />
        <div v-if="activeSuggestion === 'login' && filteredSuggestions('login').length" class="suggestions-list">
          <button
            v-for="s in filteredSuggestions('login')"
            :key="s"
            type="button"
            class="suggestion-item"
            @mousedown.prevent="selectSuggestion('login', s)"
          >
            {{ s }}
          </button>
        </div>
      </div>

      <div class="form-group password-group">
        <div class="password-label-row">
          <label>Пароль *</label>
          <button type="button" class="generate-btn" @click="generatePassword">Сгенерировать</button>
        </div>
        <div class="password-input-wrap">
          <input v-model="formData.password" :type="showPassword ? 'text' : 'password'" placeholder="Пароль" />
          <button type="button" class="toggle-btn" @click="showPassword = !showPassword">
            {{ showPassword ? '🔓' : '🔒' }}
          </button>
        </div>
      </div>

      <div class="form-group autocomplete-group">
        <label>Email (необязательно)</label>
        <input
          v-model="formData.email"
          type="email"
          placeholder="email@example.com"
          @focus="showSuggestions('email')"
        />
        <div v-if="activeSuggestion === 'email' && filteredSuggestions('email').length" class="suggestions-list">
          <button
            v-for="s in filteredSuggestions('email')"
            :key="s"
            type="button"
            class="suggestion-item"
            @mousedown.prevent="selectSuggestion('email', s)"
          >
            {{ s }}
          </button>
        </div>
      </div>

      <div class="form-group autocomplete-group">
        <label>Телефон (необязательно)</label>
        <input
          v-model="formData.phone"
          type="tel"
          placeholder="+7..."
          @focus="showSuggestions('phone')"
        />
        <div v-if="activeSuggestion === 'phone' && filteredSuggestions('phone').length" class="suggestions-list">
          <button
            v-for="s in filteredSuggestions('phone')"
            :key="s"
            type="button"
            class="suggestion-item"
            @mousedown.prevent="selectSuggestion('phone', s)"
          >
            {{ s }}
          </button>
        </div>
      </div>

      <div class="form-actions">
        <button class="btn-primary" :disabled="isLoading" @click="handleSave">
          {{ isLoading ? 'Сохранение...' : (isEditing ? 'Обновить' : 'Сохранить') }}
        </button>
        <button v-if="isEditing" class="btn-danger" @click="handleDelete">Удалить</button>
        <button class="btn-secondary" @click="$emit('cancel')">Отмена</button>
      </div>
    </div>

    <div v-if="showCategoryWarning" class="warning-backdrop" @click.self="dismissCategoryWarning">
      <div class="warning-card" role="alertdialog" aria-labelledby="category-warning-title">
        <h3 id="category-warning-title">Категория не выбрана</h3>
        <p>Выберите категорию для аккаунта или отмените сохранение.</p>
        <div class="warning-actions">
          <button type="button" class="btn-primary" @click="dismissCategoryWarning">
            Вернуться к заполнению
          </button>
          <button type="button" class="btn-secondary" @click="cancelWithoutSave">
            Не сохранять
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.form-group-error select {
  border-color: #e74c3c;
}

.warning-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  z-index: 1000;
}

.warning-card {
  width: min(100%, 420px);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 14px;
  padding: 1.25rem;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
}

.warning-card h3 {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
}

.warning-card p {
  margin: 0 0 1rem;
  color: var(--color-text-muted, #888);
  line-height: 1.45;
}

.warning-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.password-input-wrap { display: flex; gap: 0.5rem; }
.password-input-wrap input { flex: 1; }

.toggle-btn {
  background: var(--color-surface);
  border: 1.5px solid var(--color-border);
  border-radius: 10px;
  padding: 0 0.75rem;
  font-size: 1.1rem;
  cursor: pointer;
  color: var(--color-text);
}

.password-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.generate-btn {
  background: var(--color-surface);
  border: 1.5px solid var(--color-border);
  border-radius: 10px;
  padding: 0.45rem 0.75rem;
  font-size: 0.95rem;
  cursor: pointer;
  color: var(--color-text);
}

.generate-btn:hover {
  background: var(--color-hover);
}

.autocomplete-group {
  position: relative;
}

.suggestions-list {
  position: absolute;
  top: calc(100% + 0.25rem);
  left: 0;
  right: 0;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  max-height: 180px;
  overflow-y: auto;
  z-index: 20;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
}

.suggestion-item {
  display: block;
  width: 100%;
  padding: 0.65rem 0.85rem;
  background: none;
  border: none;
  border-bottom: 1px solid var(--color-separator);
  color: var(--color-text);
  font-size: 0.95rem;
  text-align: left;
  cursor: pointer;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-item:hover {
  background: var(--color-hover);
}
</style>
