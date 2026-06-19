<script setup>
import {ref, computed, onMounted, onUnmounted} from 'vue';
import {useTelegram} from '../composables/useTelegram';
import {accountApi} from '../api/account.js';
import {categoryApi} from '../api/category.js';
import ResourceEditor from './ResourceEditor.vue';

const props = defineProps(['account', 'currentCategory', 'resources', 'defaultResourceId', 'suggestions']);
const emit = defineEmits(['save', 'cancel', 'resource-created']);
const {tg, initData} = useTelegram();

const isLoading = ref(false);
const showPassword = ref(false);
const categories = ref([]);
const showResourceModal = ref(false);

// Локальная копия ресурсов — чтобы добавлять новые без перезагрузки
const localResources = ref([...(props.resources || [])]);

const isEditing = computed(() => !!props.account?.id);

const formData = ref({
  id: props.account?.id || null,
  category_id: props.currentCategory?.id || props.account?.category_id,
  resource_id: props.account?.resource_id || props.defaultResourceId || '',
  label: props.account?.label || '',
  login: props.account?.login || '',
  password: props.account?.password || '',
  email: props.account?.email || '',
  phone: props.account?.phone || ''
});

// Предыдущее значение resource_id — для восстановления если выбрали "добавить"
const prevResourceId = ref(formData.value.resource_id);
const activeSuggestion = ref(null)


const filteredSuggestions = (field) => {
  const value = formData.value[field]?.toLowerCase() || ''
  return (props.suggestions?.[field] || []).filter(
      s => s && s.toLowerCase().includes(value) && s !== formData.value[field]
  )
}

const selectSuggestion = (field, value) => {
  formData.value[field] = value
  activeSuggestion.value = null
}

const handleOutsideTouch = (e) => {
  if (!e.target.closest('.autocomplete-group')) {
    activeSuggestion.value = null
  }
}


const handleResourceChange = (e) => {
  if (e.target.value === '__add_new__') {
    // Возвращаем предыдущее значение, открываем модал
    formData.value.resource_id = prevResourceId.value;
    showResourceModal.value = true;
  } else {
    formData.value.resource_id = e.target.value;
    prevResourceId.value = e.target.value;
  }
};

const onResourceCreated = (newResource) => {
  // Добавляем в локальный список и сразу выбираем
  localResources.value.push(newResource);
  formData.value.resource_id = newResource.id;
  prevResourceId.value = newResource.id;
  showResourceModal.value = false;
  // Уведомляем родителя обновить свой список ресурсов
  emit('resource-created', newResource);
};

const categoryLabel = (category) => {
  const prefix = category.parent_id ? '↳ ' : '';
  return `${prefix}${category.icon || ''} ${category.name}`.trim();
};

onMounted(async () => {
  try {
    const response = await categoryApi.getAll(initData);
    categories.value = response.data || response;
  } catch (e) {
    console.error('Ошибка загрузки категорий', e);
  }

  tg.MainButton.setText(isEditing.value ? 'Обновить данные' : 'Сохранить аккаунт');
  tg.MainButton.onClick(handleSave);
  tg.MainButton.show();

  if (isEditing.value && tg.SecondaryButton) {
    tg.SecondaryButton.setParams({
      text: 'Удалить аккаунт',
      color: '#ff3b30',
      text_color: '#ffffff',
      is_visible: true,
      is_active: true,
    });
    tg.SecondaryButton.onClick(handleDelete);
  }
  document.addEventListener('touchstart', handleOutsideTouch)
  document.addEventListener('mousedown', handleOutsideTouch)
});

onUnmounted(() => {
  tg.MainButton.hide();
  tg.MainButton.offClick(handleSave);

  if (tg.SecondaryButton) {
    tg.SecondaryButton.hide();
    tg.SecondaryButton.offClick(handleDelete);
  }
  document.removeEventListener('touchstart', handleOutsideTouch)
  document.removeEventListener('mousedown', handleOutsideTouch)
});

const handleSave = async () => {
  if (!formData.value.login.trim() || !formData.value.password.trim()) {
    tg.showAlert('Логин и пароль обязательны');
    return;
  }

  if (!formData.value.resource_id) {
    tg.showAlert('Выберите площадку');
    return;
  }

  if (isEditing.value) {
    tg.showConfirm('Сохранить изменения?', (confirmed) => {
      if (confirmed) executeSave();
    });
  } else {
    executeSave();
  }
};

const executeSave = async () => {
  isLoading.value = true;
  tg.MainButton.showProgress(false);
  tg.MainButton.disable();
  try {
    if (isEditing.value) {
      await accountApi.update(initData, formData.value.id, formData.value);
    } else {
      await accountApi.create(initData, formData.value);
    }
    tg.HapticFeedback.notificationOccurred('success');
    emit('save');
  } catch (e) {
    tg.showAlert('Ошибка при сохранении');
  } finally {
    isLoading.value = false;
    tg.MainButton.hideProgress();
    tg.MainButton.enable();
  }
};

const handleDelete = () => {
  tg.showConfirm(
      'Удалить аккаунт? Вы потеряете доступ к сохраненным данным.',
      async (confirmed) => {
        if (!confirmed) return;
        try {
          await accountApi.delete(initData, formData.value.id);
          tg.HapticFeedback.notificationOccurred('success');
          emit('save');
        } catch (e) {
          tg.showAlert('Ошибка при удалении');
        }
      }
  );
};

const generatePassword = () => {
  const charset = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#$%^&*';
  const length = 16;

  const array = new Uint32Array(length);
  window.crypto.getRandomValues(array);

  let pass = '';
  for (let i = 0; i < length; i++) {
    pass += charset[array[i] % charset.length];
  }

  formData.value.password = pass;
  showPassword.value = true;

  tg.HapticFeedback.impactOccurred('medium');
};
</script>

<template>
  <div class="editor-container">
    <div class="form">

      <div class="icon-section">
        <div class="icon-preview">👤</div>
        <p class="category-name">{{ currentCategory?.name || 'Аккаунт' }}</p>
      </div>

      <!-- 1. Логин -->
      <div class="input-group">
        <label>Логин / Имя пользователя</label>
        <input
            v-model="formData.login"
            type="text"
            placeholder="username"
            class="main-input"
        />
      </div>

      <!-- 2. Пароль -->
      <div class="input-group">
        <div class="label-row">
          <label>Пароль</label>
          <span class="generate-btn" @click="generatePassword">Сгенерировать</span>
        </div>
        <div class="password-wrapper">
          <input
              :type="showPassword ? 'text' : 'password'"
              v-model="formData.password"
              placeholder="••••••••"
              class="main-input"
          />
          <button
              class="eye-btn"
              @click.prevent="showPassword = !showPassword"
              type="button"
          >
            {{ showPassword ? '🔓' : '🔒' }}
          </button>
        </div>
      </div>

      <!-- 3. Площадка -->
      <div class="input-group">
        <label>Площадка</label>
        <select
            :value="formData.resource_id"
            @change="handleResourceChange"
            class="main-input select-input"
        >
          <option value="" disabled>Выберите площадку</option>
          <option
              v-for="r in localResources"
              :key="r.id"
              :value="r.id"
          >
            {{ r.resource_name }}
          </option>
          <option value="__add_new__" class="add-new-option">
            + Добавить площадку
          </option>
        </select>
      </div>

      <!-- 4. Метка -->
      <div class="input-group autocomplete-group">
        <label>Название / Метка</label>
        <input v-model="formData.label" type="text" placeholder="Например: Основной"
               class="main-input"
               @click="activeSuggestion = activeSuggestion === 'label' ? null : 'label'">
        <div v-if="activeSuggestion === 'label' && filteredSuggestions('label').length" class="suggestions-list">
          <div v-for="s in filteredSuggestions('label')" :key="s"
               class="suggestion-item"
               @mousedown.prevent="selectSuggestion('label', s)"
               @touchend.prevent="selectSuggestion('label', s)">{{ s }}
          </div>
        </div>
      </div>

      <!-- 5. E-mail -->
      <div class="input-group autocomplete-group">
        <label>E-mail</label>
        <input v-model="formData.email" type="text" placeholder="example@mail.com"
               class="main-input"
               @click="activeSuggestion = activeSuggestion === 'email' ? null : 'email'">
        <div v-if="activeSuggestion === 'email' && filteredSuggestions('email').length" class="suggestions-list">
          <div v-for="s in filteredSuggestions('email')" :key="s"
               class="suggestion-item"
               @mousedown.prevent="selectSuggestion('email', s)"
               @touchend.prevent="selectSuggestion('email', s)">{{ s }}
          </div>
        </div>
      </div>

      <!-- 6. Телефон -->
      <div class="input-group autocomplete-group">
        <label>Телефон</label>
        <input v-model="formData.phone" type="text" placeholder="+7 (___) ___-__-__"
               class="main-input"
               @click="activeSuggestion = activeSuggestion === 'phone' ? null : 'phone'">
        <div v-if="activeSuggestion === 'phone' && filteredSuggestions('phone').length" class="suggestions-list">
          <div v-for="s in filteredSuggestions('phone')" :key="s"
               class="suggestion-item"
               @mousedown.prevent="selectSuggestion('phone', s)"
               @touchend.prevent="selectSuggestion('phone', s)">{{ s }}
          </div>
        </div>
      </div>

      <!-- 7. Категория -->
      <div class="input-group">
        <label>Категория</label>
        <select v-model="formData.category_id" class="main-input select-input">
          <option v-for="p in categories" :key="p.id" :value="p.id">
            {{ categoryLabel(p) }}
          </option>
        </select>
      </div>

    </div>
  </div>

  <!-- Модальное окно добавления площадки -->
  <ResourceEditor
      v-if="showResourceModal"
      @save="onResourceCreated"
      @cancel="showResourceModal = false"
  />
</template>

<style scoped>
.editor-container {
  padding: 16px;
  padding-bottom: 20px;
  max-width: 500px;
  margin: 0 auto;
}

.icon-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 24px;
}

.icon-preview {
  font-size: 44px;
  width: 80px;
  height: 80px;
  background: var(--tg-theme-secondary-bg-color);
  border-radius: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(128, 128, 128, 0.1);
}

.category-name {
  margin-top: 12px;
  font-weight: 600;
  font-size: 16px;
  color: var(--tg-theme-text-color);
}

.input-group {
  margin-bottom: 18px;
}

.label-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 6px;
  padding: 0 4px;
}

.input-group label {
  font-size: 13px;
  color: var(--tg-theme-hint-color);
}

.generate-btn {
  font-size: 12px;
  font-weight: 600;
  color: var(--tg-theme-button-color);
  cursor: pointer;
}

.password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.main-input {
  width: 100%;
  background: var(--tg-theme-secondary-bg-color);
  border: 1px solid rgba(128, 128, 128, 0.2);
  border-radius: 12px;
  padding: 12px 50px 12px 16px;
  color: var(--tg-theme-text-color);
  font-size: 16px;
  box-sizing: border-box;
  outline: none;
}

.main-input:focus {
  border-color: var(--tg-theme-button-color);
}

.eye-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  font-size: 20px;
  color: var(--tg-theme-text-color);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 10;
  pointer-events: auto;
}

.eye-btn:active {
  transform: translateY(-50%) scale(0.95);
}

.select-input {
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='rgba(128, 128, 128, 0.5)' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 16px;
  padding-right: 40px !important;
  cursor: pointer;
}

.add-new-option {
  color: var(--tg-theme-button-color);
  font-weight: 500;
}

.autocomplete-group {
  position: relative;
}

.suggestions-list {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--tg-theme-secondary-bg-color);
  border: 1px solid rgba(128, 128, 128, 0.2);
  border-radius: 12px;
  margin-top: 4px;
  z-index: 100;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.suggestion-item {
  padding: 12px 16px;
  font-size: 15px;
  color: var(--tg-theme-text-color);
  cursor: pointer;
  border-bottom: 1px solid rgba(128, 128, 128, 0.1);
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-item:active {
  background: rgba(128, 128, 128, 0.1);
}
</style>