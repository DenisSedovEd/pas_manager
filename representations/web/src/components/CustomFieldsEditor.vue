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
const newField = ref({
  name: '',
  is_required: false,
  is_secret: false,
})

const attachedIds = computed(() => new Set(items.value.map((i) => i.field_id).filter(Boolean)))
const availableCatalog = computed(() =>
  catalog.value.filter((f) => !attachedIds.value.has(f.id)),
)

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

const removeItem = (index) => {
  items.value.splice(index, 1)
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
        <input v-model="newField.name" type="text" placeholder="Название поля" />
        <label class="check-label">
          <input v-model="newField.is_required" type="checkbox" />
          Обязательное
        </label>
        <label class="check-label">
          <input v-model="newField.is_secret" type="checkbox" />
          Как пароль (шифрование и маскировка)
        </label>
        <button type="button" class="btn-primary-sm" @click="createAndAdd">Создать и добавить</button>
      </div>
    </div>

    <div v-if="!items.length" class="empty-hint">Кастомные поля не добавлены</div>

    <div v-for="(item, index) in items" :key="item._key" class="form-group field-row">
      <div class="field-label-row">
        <label>
          {{ item.name }}
          <span v-if="item.is_required">*</span>
          <span v-if="item.is_secret" class="secret-tag">секрет</span>
        </label>
        <button type="button" class="remove-btn" title="Убрать" @click="removeItem(index)">✕</button>
      </div>
      <div v-if="item.is_secret" class="password-input-wrap">
        <input
          v-model="item.value"
          :type="revealed[item._key] ? 'text' : 'password'"
          :placeholder="item.name"
        />
        <button type="button" class="toggle-btn" @click="toggleReveal(item._key)">
          {{ revealed[item._key] ? '🔓' : '🔒' }}
        </button>
      </div>
      <input v-else v-model="item.value" type="text" :placeholder="item.name" />
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
}

.add-btn,
.create-link,
.remove-btn,
.btn-primary-sm {
  background: var(--color-surface);
  border: 1.5px solid var(--color-border);
  border-radius: 10px;
  padding: 0.4rem 0.75rem;
  cursor: pointer;
  color: var(--color-text);
  font-size: 0.9rem;
}

.remove-btn {
  padding: 0.2rem 0.5rem;
  font-size: 0.85rem;
}

.picker-panel {
  background: var(--color-hover, rgba(128, 128, 128, 0.12));
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

.badges {
  display: flex;
  gap: 0.35rem;
}

.badge,
.secret-tag {
  font-size: 0.7rem;
  color: var(--color-hint, #888);
  text-transform: lowercase;
}

.empty-hint {
  margin: 0;
  font-size: 0.85rem;
  color: var(--color-hint, #888);
}

.create-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.check-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  text-transform: none;
  color: var(--color-text);
}

.field-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.35rem;
}

.field-row label {
  margin: 0;
}

.password-input-wrap {
  display: flex;
  gap: 0.5rem;
}

.password-input-wrap input {
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
</style>
