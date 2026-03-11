<script setup>
import {ref, onMounted} from 'vue';
import {useRoute, useRouter} from 'vue-router';
import {accountApi} from '../api/account.js';
import {useTelegram} from '../composables/useTelegram';

const route = useRoute();
const router = useRouter();
const {tg, initData} = useTelegram();
const acc = ref(null);

onMounted(async () => {
  acc.value = await accountApi.getDetail(initData, route.params.accountId);
});

const copy = (val, label) => {
  navigator.clipboard.writeText(val);
  tg.HapticFeedback.impactOccurred('light');
  // Можно добавить toast уведомление здесь
};
</script>

<template>
  <div v-if="acc" class="page p-16">
    <div class="detail-card">
      <div class="field" @click="copy(acc.login, 'Логин')">
        <label>ЛОГИН</label>
        <div class="val">{{ acc.login }} 📋</div>
      </div>
      <div class="field" @click="copy(acc.password, 'Пароль')">
        <label>ПАРОЛЬ</label>
        <div class="val">******** 📋</div>
      </div>
      <div v-if="acc.email" class="field" @click="copy(acc.email, 'Email')">
        <label>EMAIL</label>
        <div class="val">{{ acc.email }} 📋</div>
      </div>
    </div>

    <div class="actions">
      <button class="edit-btn" @click="router.push(`/accounts/edit/${acc.id}`)">Редактировать</button>
    </div>
  </div>
</template>

<style scoped>
.detail-card {
  background: var(--tg-theme-secondary-bg-color);
  border-radius: 20px;
  padding: 20px;
}

.field {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(128, 128, 128, 0.1);
}

label {
  font-size: 10px;
  color: var(--tg-theme-button-color);
  font-weight: bold;
  letter-spacing: 1px;
}

.val {
  font-size: 18px;
  margin-top: 5px;
  display: flex;
  justify-content: space-between;
}

.edit-btn {
  width: 100%;
  margin-top: 20px;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid var(--tg-theme-button-color);
  color: var(--tg-theme-button-color);
  background: none;
  font-weight: bold;
}
</style>