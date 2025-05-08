<template>
  <div v-if="show" class="settings-modal" @click="handleClose">
    <div class="settings-modal-content" @click.stop>
      <div class="settings-modal-header">
        <h3>设置</h3>
        <button class="close-button" @click="handleClose">×</button>
      </div>
      <div class="settings-modal-body">
        <div class="settings-form">
          <div class="form-group">
            <label for="apiKey">API Key</label>
            <input
              type="text"
              id="apiKey"
              placeholder="请输入app-xxxx格式的key"
              v-model="apiKeyInput"
              pattern="app-[a-zA-Z0-9]+"
            />
            <small class="form-text">格式：app-xxxx</small>
          </div>
          <button class="save-button" @click="handleSave">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, watch } from 'vue';

const props = defineProps({
  show: Boolean,
  apiKey: {
    type: String,
    default: ''
  }
});
const emit = defineEmits(['update:show', 'save']);

const apiKeyInput = ref(props.apiKey);

watch(() => props.apiKey, (val) => {
  apiKeyInput.value = val;
});

const handleClose = () => {
  emit('update:show', false);
};

const handleSave = () => {
  if (!apiKeyInput.value || !/^app-[a-zA-Z0-9]+$/.test(apiKeyInput.value)) {
    alert('请输入正确格式的API Key (app-xxxx)');
    return;
  }
  emit('save', apiKeyInput.value);
  emit('update:show', false);
};
</script>

<style scoped>
.settings-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  justify-content: center;
  align-items: center;
}
.settings-modal-content {
  width: 90%;
  max-width: 400px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  animation: fade-in 0.3s ease-out;
}
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.settings-modal-header {
  padding: 16px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.settings-modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
  font-weight: 600;
}
.settings-modal-body {
  padding: 20px;
}
.settings-form {
  display: flex;
  flex-direction: column;
}
.form-group {
  margin-bottom: 20px;
}
.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}
.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  background-color: #f8f8f8;
}
.form-group input:focus {
  border-color: #ff6700;
  outline: none;
  box-shadow: 0 0 0 2px rgba(255, 103, 0, 0.1);
}
.form-text {
  font-size: 12px;
  color: #666;
  margin-top: 6px;
  display: block;
}
.save-button {
  background-color: #ff6700;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 12px 20px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  align-self: flex-end;
}
.save-button:hover {
  background-color: #e65c00;
}
.save-button:active {
  transform: translateY(1px);
}
.close-button {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #999;
  margin-left: 10px;
}
</style>
