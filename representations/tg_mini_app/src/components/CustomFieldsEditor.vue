<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTelegram } from '../composables/useTelegram'
import { customFieldApi } from '../api/customField.js'

const props = defineProps({
  entityType: { type: String, required: true },
  entityId: { type: [String, Number], default: null },
})

const { tg, initData } = useTelegram()

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
  catalog.value = await customFieldApi.getList(initData)
}

const loadValues = async () => {
  if (!props.entityId) {
    items.value = []
    return
  }
  const values = await customFieldApi.getValues(initData, props.entityType, props.entityId)
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
    tg.showAlert('Введите название поля')
    return
  }
  try {
    const created = await customFieldApi.create(initData, {
      name,
      is_required: newField.value.is_required,
      is_secret: newField.value.is_secret,
    })
    catalog.value.push(created)
    addFromCatalog(created)
    newField.value = { name: '', is_required: false, is_secret: false }
    showCreate.value = false
  } catch (err) {
    tg.showAlert(err.message || 'Ошибка создания поля')
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
      tg.showAlert(`Поле «${item.name}» обязательно`)
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
  return customFieldApi.replaceValues(initData, props.entityType, id, buildPayload())
}

defineExpose({ save, validate, buildPayload })

onMounted(async () => {
  try {
    await loadCatalog()
    await loadValues()
  } catch {
    tg.showAlert('Не удалось загрузить кастомные поля')
  }
})
</script>

<template>
  <div class="custom-fields">
    <div class="section-header">
      <span class="section-title">Кастомные поля</span>
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
        <input v-model="newField.name" type="text" class="main-input" placeholder="Название поля" />
        <label class="check-label">
          <input v-model="newField.is_required" type="checkbox" />
          Обязательное
        </label>
        <label class="check-label">
          <input v-model="newField.is_secret" type="checkbox" />
          Как пароль (шифрование и маскировка)
        </label>
        <button type="button" class="btn-save-sm" @click="createAndAdd">Создать и добавить</button>
      </div>
    </div>

    <p v-if="!items.length" class="empty-hint">Кастомные поля не добавлены</p>

    <div v-for="(item, index) in items" :key="item._key" class="input-group">
      <div class="field-label-row">
        <label>
          {{ item.name }}
          <span v-if="item.is_required">*</span>
          <span v-if="item.is_secret" class="secret-tag">секрет</span>
        </label>
        <button type="button" class="remove-btn" @click="removeItem(index)">✕</button>
      </div>
      <div v-if="item.is_secret" class="password-row">
        <input
          v-model="item.value"
          :type="revealed[item._key] ? 'text' : 'password'"
          class="main-input"
          :placeholder="item.name"
        />
        <button type="button" class="toggle-btn" @click="toggleReveal(item._key)">
          {{ revealed[item._key] ? '🔓' : '🔒' }}
        </button>
      </div>
      <input v-else v-model="item.value" type="text" class="main-input" :placeholder="item.name" />
    </div>
  </div>
</template>

<style scoped>
.custom-fields {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
  padding-top: 12px;
  border-top: 1px solid rgba(128, 128, 128, 0.2);
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--tg-theme-text-color);
}
.add-btn,
.create-link,
.remove-btn,
.btn-save-sm,
.toggle-btn {
  background: var(--tg-theme-secondary-bg-color);
  border: 1px solid rgba(128, 128, 128, 0.25);
  border-radius: 10px;
  padding: 6px 10px;
  color: var(--tg-theme-text-color);
  cursor: pointer;
  font-size: 13px;
}
.picker-panel {
  background: var(--tg-theme-secondary-bg-color);
  border-radius: 12px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.catalog-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 160px;
  overflow-y: auto;
}
.catalog-item {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  width: 100%;
  text-align: left;
  background: var(--tg-theme-bg-color);
  border: 1px solid rgba(128, 128, 128, 0.2);
  border-radius: 10px;
  padding: 10px 12px;
  color: var(--tg-theme-text-color);
  cursor: pointer;
}
.badges { display: flex; gap: 6px; }
.badge, .secret-tag {
  font-size: 11px;
  color: var(--tg-theme-hint-color);
}
.empty-hint {
  margin: 0;
  font-size: 13px;
  color: var(--tg-theme-hint-color);
}
.create-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.check-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--tg-theme-text-color);
}
.field-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.field-label-row label {
  margin: 0;
  font-size: 13px;
  color: var(--tg-theme-hint-color);
}
.password-row {
  display: flex;
  gap: 8px;
}
.password-row .main-input { flex: 1; }
.main-input {
  width: 100%;
  background: var(--tg-theme-secondary-bg-color);
  border: 1px solid rgba(128, 128, 128, 0.2);
  border-radius: 12px;
  padding: 13px 16px;
  color: var(--tg-theme-text-color);
  font-size: 16px;
  box-sizing: border-box;
  outline: none;
}
</style>
