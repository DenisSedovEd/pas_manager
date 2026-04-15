<script setup>
import { ref, computed, onMounted } from 'vue'
import { accountApi } from '../api/account.js'
import { categoryApi } from '../api/category.js'
import { resourceApi } from '../api/resource.js'

const props = defineProps(['account', 'currentCategory', 'resources', 'defaultResourceId', 'suggestions'])
const emit = defineEmits(['save', 'cancel', 'resource-created'])

const isLoading = ref(false)
const showPassword = ref(false)
const categories = ref([])
const localResources = ref([...(props.resources || [])])
const isEditing = computed(() => !!props.account?.id)
const prevResourceId = ref(props.account?.resource_id || props.defaultResourceId || '')

const formData = ref({
  id: props.account?.id || null,
  category_id: props.currentCategory?.id || props.account?.category_id,
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

const handleSave = async () => {
  if (!formData.value.login.trim()) { alert('Введи логин'); return }
  if (!formData.value.password.trim()) { alert('Введи пароль'); return }
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

onMounted(async () => {
  try {
    const response = await categoryApi.getList()
    categories.value = response.data || response
  } catch {
    console.error('Ошибка загрузки категорий')
  }
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
          <option value="">Без площадки</option>
          <option v-for="r in localResources" :key="r.id" :value="r.id">{{ r.resource_name }}</option>
          <option value="__add_new__">+ Добавить площадку</option>
        </select>
      </div>

      <div class="form-group">
        <label>Категория</label>
        <select v-model="formData.category_id">
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.icon }} {{ c.name }}</option>
        </select>
      </div>

      <div class="form-group">
        <label>Метка (необязательно)</label>
        <input v-model="formData.label" type="text" placeholder="Например: рабочий аккаунт" />
      </div>

      <div class="form-group">
        <label>Логин *</label>
        <input v-model="formData.login" type="text" placeholder="Логин или email" />
      </div>

      <div class="form-group password-group">
        <label>Пароль *</label>
        <div class="password-input-wrap">
          <input v-model="formData.password" :type="showPassword ? 'text' : 'password'" placeholder="Пароль" />
          <button type="button" class="toggle-btn" @click="showPassword = !showPassword">
            {{ showPassword ? '🔓' : '🔒' }}
          </button>
        </div>
      </div>

      <div class="form-group">
        <label>Email (необязательно)</label>
        <input v-model="formData.email" type="email" placeholder="email@example.com" />
      </div>

      <div class="form-group">
        <label>Телефон (необязательно)</label>
        <input v-model="formData.phone" type="tel" placeholder="+7..." />
      </div>

      <div class="form-actions">
        <button class="btn-primary" :disabled="isLoading" @click="handleSave">
          {{ isLoading ? 'Сохранение...' : (isEditing ? 'Обновить' : 'Сохранить') }}
        </button>
        <button v-if="isEditing" class="btn-danger" @click="handleDelete">Удалить</button>
        <button class="btn-secondary" @click="$emit('cancel')">Отмена</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.screen { padding: 0; }
.screen-header {
  padding: 1rem 1rem 0.5rem;
  border-bottom: 1px solid #eee;
}
.screen-header h2 { margin: 0; font-size: 1.25rem; }
.form { padding: 1rem; display: flex; flex-direction: column; gap: 1rem; }
.form-group { display: flex; flex-direction: column; gap: 0.3rem; }
label { font-size: 0.8rem; color: #888; text-transform: uppercase; font-weight: 500; }
input, select {
  padding: 0.7rem 0.9rem;
  border: 1.5px solid #ddd;
  border-radius: 10px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s;
}
input:focus, select:focus { border-color: #5856d6; }
.password-input-wrap { display: flex; gap: 0.5rem; }
.password-input-wrap input { flex: 1; }
.toggle-btn {
  background: none;
  border: 1.5px solid #ddd;
  border-radius: 10px;
  padding: 0 0.75rem;
  font-size: 1.1rem;
  cursor: pointer;
}
.form-actions { display: flex; flex-direction: column; gap: 0.6rem; margin-top: 0.5rem; }
.btn-primary {
  padding: 0.75rem;
  background: #5856d6;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  cursor: pointer;
}
.btn-primary:disabled { opacity: 0.5; }
.btn-danger {
  padding: 0.75rem;
  background: #ff3b30;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  cursor: pointer;
}
.btn-secondary {
  padding: 0.75rem;
  background: none;
  color: #666;
  border: 1.5px solid #ddd;
  border-radius: 10px;
  font-size: 1rem;
  cursor: pointer;
}
</style>
