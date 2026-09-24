<script setup>
import { ref, computed, onMounted } from 'vue'
import { customFieldApi } from '../api/customField.js'

const props = defineProps({
  entityType: { type: String, required: true },
  entityId: { type: [String, Number], default: null },
})

const catalog = ref([])
const items = ref([])
const showPicker = ref(false)
const showCreate = ref(false)
const revealed = ref({})
const pendingRemoveIndex = ref(null)
const newField = ref({
  name: '',
  is_required: false,
  is_secret: false,
})

const attachedIds = computed(() => new Set(items.value.map((i) => i.field_id).filter(Boolean)))
const availableCatalog = computed(() =>
  catalog.value.filter((f) => !attachedIds.value.has(f.id)),
)
const pendingRemoveName = computed(() => {
  const idx = pendingRemoveIndex.value
  if (idx === null || idx < 0 || idx >= items.value.length) return ''
  return items.value[idx]?.name || ''
})

const loadCatalog = async () => {
  catalog.value = await customFieldApi.getList()
}

const loadValues = async () => {
  if (!props.entityId) {
    items.value = []
    return
  }
  const values = await customFieldApi.getValues(props.entityType, props.entityId)
  items.value = values.map((v) => ({
    field_id: v.field_id,
    name: v.name,
    is_required: v.is_required,
    is_secret: v.is_secret,
    value: v.value || '',
    _key: v.field_id,
  }))
}

const addFromCatalog = (field) => {
  items.value.push({
    field_id: field.id,
    name: field.name,
    is_required: field.is_required,
    is_secret: field.is_secret,
    value: '',
    _key: field.id,
  })
  showPicker.value = false
}

const createAndAdd = async () => {
  const name = newField.value.name.trim()
  if (!name) {
    alert('Введи название поля')
    return
  }
  try {
    const created = await customFieldApi.create({
      name,
      is_required: newField.value.is_required,
      is_secret: newField.value.is_secret,
    })
    catalog.value.push(created)
    addFromCatalog(created)
    newField.value = { name: '', is_required: false, is_secret: false }
    showCreate.value = false
  } catch (err) {
    alert(err.message || 'Ошибка создания поля')
  }
}

const requestRemoveItem = (index) => {
  pendingRemoveIndex.value = index
}

const cancelRemoveItem = () => {
  pendingRemoveIndex.value = null
}

const confirmRemoveItem = () => {
  const index = pendingRemoveIndex.value
  if (index !== null && index >= 0) {
    items.value.splice(index, 1)
  }
  pendingRemoveIndex.value = null
}

const toggleReveal = (key) => {
  revealed.value = { ...revealed.value, [key]: !revealed.value[key] }
}

const validate = () => {
  for (const item of items.value) {
    if (item.is_required && !String(item.value || '').trim()) {
      alert(`Поле «${item.name}» обязательно`)
      return false
    }
  }
  return true
}

const buildPayload = () =>
  items.value.map((item) => ({
    field_id: item.field_id,
    value: item.value || '',
  }))

const save = async (entityId) => {
  if (!validate()) throw new Error('validation')
  const id = entityId ?? props.entityId
  if (!id) throw new Error('entityId required')
  return customFieldApi.replaceValues(props.entityType, id, buildPayload())
}

defineExpose({ save, validate, buildPayload })

onMounted(async () => {
  try {
    await loadCatalog()
    await loadValues()
  } catch {
    alert('Не удалось загрузить кастомные поля')
  }
})
</script>

<template>
  <div class="custom-fields">
    <div class="section-header">
      <h3>Кастомные поля</h3>
      <button type="button" class="add-btn" @click="showPicker = !showPicker">
        {{ showPicker ? 'Скрыть' : '+ Добавить' }}
      </button>
    </div>

    <div v-if="showPicker" class="picker-panel">
      <div v-if="availableCatalog.length" class="catalog-list">
        <button
          v-for="field in availableCatalog"
          :key="field.id"
          type="button"
          class="catalog-item"
          @click="addFromCatalog(field)"
        >
          <span>{{ field.name }}</span>
          <span class="badges">
            <span v-if="field.is_required" class="badge">обяз.</span>
            <span v-if="field.is_secret" class="badge">секрет</span>
          </span>
        </button>
      </div>
      <p v-else class="empty-hint">Нет доступных полей в каталоге</p>
      <button type="button" class="create-link" @click="showCreate = !showCreate">
        {{ showCreate ? 'Отмена создания' : '+ Создать новое поле' }}
      </button>
      <div v-if="showCreate" class="create-form">
        <div class="field-block">
          <label class="field-label">Название поля</label>
          <input
            v-model="newField.name"
            type="text"
            class="field-input"
            placeholder="Название поля"
          />
        </div>
        <button
          type="button"
          class="check-chip"
          :class="{ active: newField.is_required }"
          @click="newField.is_required = !newField.is_required"
        >
          <span class="check-mark">{{ newField.is_required ? '✓' : '' }}</span>
          Обязательное
        </button>
        <button
          type="button"
          class="check-chip"
          :class="{ active: newField.is_secret }"
          @click="newField.is_secret = !newField.is_secret"
        >
          <span class="check-mark">{{ newField.is_secret ? '✓' : '' }}</span>
          Как пароль (шифрование и маскировка)
        </button>
        <button type="button" class="btn-primary-sm" @click="createAndAdd">Создать и добавить</button>
      </div>
    </div>

    <div v-if="!items.length" class="empty-hint">Кастомные поля не добавлены</div>

    <div v-for="(item, index) in items" :key="item._key" class="field-block field-row">
      <div class="field-label-row">
        <label class="field-label">
          {{ item.name }}
          <span v-if="item.is_required">*</span>
          <span v-if="item.is_secret" class="secret-tag">секрет</span>
        </label>
        <button
          type="button"
          class="remove-btn"
          title="Убрать"
          @click="requestRemoveItem(index)"
        >✕</button>
      </div>
      <div v-if="item.is_secret" class="password-input-wrap">
        <input
          v-model="item.value"
          class="field-input"
          :type="revealed[item._key] ? 'text' : 'password'"
          :placeholder="item.name"
        />
        <button type="button" class="toggle-btn" @click="toggleReveal(item._key)">
          {{ revealed[item._key] ? '🔓' : '🔒' }}
        </button>
      </div>
      <input
        v-else
        v-model="item.value"
        class="field-input"
        type="text"
        :placeholder="item.name"
      />
    </div>

    <div
      v-if="pendingRemoveIndex !== null"
      class="confirm-backdrop"
      @click.self="cancelRemoveItem"
    >
      <div class="confirm-card" role="alertdialog" aria-labelledby="remove-field-title">
        <h3 id="remove-field-title">Убрать поле?</h3>
        <p>
          Поле «{{ pendingRemoveName }}» будет отвязано от этой записи.
          Определение останется в каталоге.
        </p>
        <div class="confirm-actions">
          <button type="button" class="btn-danger-sm" @click="confirmRemoveItem">Убрать</button>
          <button type="button" class="btn-secondary-sm" @click="cancelRemoveItem">Отмена</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-fields {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 0.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-separator, var(--color-border));
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
}

.add-btn,
.create-link,
.remove-btn,
.btn-primary-sm,
.btn-secondary-sm,
.btn-danger-sm {
  background: var(--color-surface);
  border: 1.5px solid var(--color-border);
  border-radius: 10px;
  padding: 0.4rem 0.75rem;
  cursor: pointer;
  color: var(--color-text);
  font-size: 0.9rem;
}

.btn-primary-sm:hover,
.add-btn:hover,
.create-link:hover,
.btn-secondary-sm:hover {
  background: var(--color-hover);
}

.btn-danger-sm {
  border-color: var(--color-danger);
  color: #fff;
  background: var(--color-danger);
}

.remove-btn {
  padding: 0.2rem 0.5rem;
  font-size: 0.85rem;
}

.picker-panel {
  background: var(--color-hover);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.catalog-list {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  max-height: 180px;
  overflow-y: auto;
}

.catalog-item {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  width: 100%;
  text-align: left;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 0.55rem 0.75rem;
  cursor: pointer;
  color: var(--color-text);
}

.catalog-item:hover {
  background: var(--color-hover);
}

.badges {
  display: flex;
  gap: 0.35rem;
}

.badge,
.secret-tag {
  font-size: 0.7rem;
  color: var(--color-hint);
  text-transform: lowercase;
}

.empty-hint {
  margin: 0;
  font-size: 0.85rem;
  color: var(--color-hint);
}

.create-form {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.field-block {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.field-label {
  font-size: 0.8rem;
  color: var(--color-hint);
  text-transform: uppercase;
  font-weight: 500;
}

.field-input {
  width: 100%;
  box-sizing: border-box;
  padding: 0.7rem 0.9rem;
  border: 1.5px solid var(--color-border);
  border-radius: 10px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s;
  background: var(--color-hover);
  color: var(--color-text);
}

.field-input:focus {
  border-color: var(--color-accent);
}

.field-input::placeholder {
  color: var(--color-hint);
}

.check-chip {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  width: 100%;
  text-align: left;
  padding: 0.65rem 0.85rem;
  border: 1.5px solid var(--color-border);
  border-radius: 10px;
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 0.9rem;
  cursor: pointer;
}

.check-chip:hover {
  background: var(--color-hover);
}

.check-chip.active {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.check-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.15rem;
  height: 1.15rem;
  border: 1.5px solid var(--color-border);
  border-radius: 5px;
  font-size: 0.75rem;
  line-height: 1;
  flex-shrink: 0;
  background: var(--color-hover);
  color: var(--color-accent);
}

.check-chip.active .check-mark {
  border-color: var(--color-accent);
  background: rgba(97, 175, 239, 0.15);
}

.field-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.password-input-wrap {
  display: flex;
  gap: 0.5rem;
}

.password-input-wrap .field-input {
  flex: 1;
}

.toggle-btn {
  background: var(--color-surface);
  border: 1.5px solid var(--color-border);
  border-radius: 10px;
  padding: 0 0.75rem;
  font-size: 1.1rem;
  cursor: pointer;
  color: var(--color-text);
}

.confirm-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  z-index: 1100;
}

.confirm-card {
  width: min(100%, 420px);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 14px;
  padding: 1.25rem;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);
}

.confirm-card h3 {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
  color: var(--color-text);
}

.confirm-card p {
  margin: 0 0 1rem;
  color: var(--color-hint);
  line-height: 1.45;
}

.confirm-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
</style>
