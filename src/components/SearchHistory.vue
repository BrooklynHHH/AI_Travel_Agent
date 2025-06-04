<template>
  <div class="search-history-container" v-if="visible" :class="{ 'fade-in': visible }">
    <div class="search-header">
      <div class="search-input-container">
        <textarea
          class="current-search-textarea"
          v-model="inputValue"
          rows="4"
        ></textarea>
        <button
          v-if="inputValue.trim() !== ''"
          class="send-btn"
          @click="onSend"
        >
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
      <div class="search-header-btn-row">
        <div class="btn-group-left">
          <div class="back-button" @click="close">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
          </div>
          <button
            class="deep-search-btn"
            :class="{ selected: deepSearchSelected }"
            @click="toggleDeepSearch"
          >
            <img src="@/assets/search-input-logo.jpg" class="deep-search-icon" />
            <span>深度搜索</span>
          </button>
        </div>
        <div class="add-button">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
        </div>
      </div>
    </div>
    
    <div class="history-section">
      <div class="history-header">
        <div class="history-title">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
          搜索历史
        </div>
        <div class="clear-history" @click="clearHistory">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
        </div>
      </div>
      
      <div v-if="searchHistory.length > 0">
        <div
          v-if="!showAll"
          class="history-items two-col"
        >
          <div
            v-for="(item, index) in searchHistory.slice(0, 5)"
            :key="item + '-' + index"
            class="history-item"
            @click="selectHistoryItem(item)"
          >
            {{ item }}
          </div>
          <div
            v-if="searchHistory.length > 5"
            class="more-history"
            @click="showAll = true"
          >
            更多历史
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-left:4px;width:16px;height:16px;">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </div>
        </div>
        <div
          v-else
          class="history-items one-col"
        >
          <div
            v-for="(item, index) in searchHistory"
            :key="item + '-all-' + index"
            class="history-item"
            @click="selectHistoryItem(item)"
          >
            {{ item }}
          </div>
        </div>
      </div>
      <div class="empty-history" v-else>
        <p>暂无搜索历史</p>
      </div>
    </div>
    
    <div class="voice-search">
      <div class="voice-button">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>
        语音搜索
      </div>
    </div>
  </div>
</template>

<script setup>
/* eslint-disable */
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps({
  visible: Boolean,
  currentInput: String
});

const emit = defineEmits(['close', 'select']);
const router = useRouter();

const searchHistory = ref([]);
// 是否展示全部历史（单列）
const showAll = ref(false);

// 用于 textarea 的输入值
const inputValue = ref(props.currentInput || '');

const deepSearchSelected = ref(false);
const toggleDeepSearch = () => {
  deepSearchSelected.value = !deepSearchSelected.value;
};

// 发送按钮点击
const onSend = () => {
  const query = inputValue.value.trim();
  if (query !== '') {
    addToHistory(query); // 保存到历史记录
    router.push({
      name: '高级搜索结果',
      query: {
        query: query,
        isdeep: deepSearchSelected.value,
      },
    });
  }
};

watch(
  () => props.currentInput,
  (val) => {
    inputValue.value = val || '';
  }
);

// 输入时同步到父组件
watch(
  inputValue,
  (val) => {
    // 这里可以 emit('update:currentInput', val) 如果父组件支持 v-model:currentInput
    // 或者 emit('input', val) 视具体实现
  }
);

// 初始化时从本地存储加载搜索历史
onMounted(() => {
  loadSearchHistory();
});

// 监听当前输入，如果按下回车时有内容，则添加到历史
watch(() => props.currentInput, (newVal) => {
  if (newVal && newVal.trim()) {
    // 注意：这里只是准备数据，实际添加在外部组件调用addToHistory时完成
  }
});

// 从localStorage加载搜索历史
const loadSearchHistory = () => {
  try {
    const history = localStorage.getItem('searchHistory');
    if (history) {
      searchHistory.value = JSON.parse(history);
    }
  } catch (error) {
    console.error('Error loading search history:', error);
    searchHistory.value = [];
  }
};

// 添加搜索记录到历史
const addToHistory = (text) => {
  if (!text || !text.trim()) return;
  
  // 如果已存在相同搜索词，先移除它
  const index = searchHistory.value.indexOf(text);
  if (index > -1) {
    searchHistory.value.splice(index, 1);
  }
  
  // 添加到开头
  searchHistory.value.unshift(text);
  
  // 限制最多10条记录
  if (searchHistory.value.length > 10) {
    searchHistory.value = searchHistory.value.slice(0, 10);
  }
  
  // 保存到本地存储
  saveSearchHistory();
};

// 保存搜索历史到localStorage
const saveSearchHistory = () => {
  try {
    localStorage.setItem('searchHistory', JSON.stringify(searchHistory.value));
  } catch (error) {
    console.error('Error saving search history:', error);
  }
};

// 清空搜索历史
const clearHistory = () => {
  searchHistory.value = [];
  saveSearchHistory();
};

// 选择历史记录项
const selectHistoryItem = (item) => {
  // emit('select', item); // 原始逻辑是emit，现在改为跳转
  router.push({
    name: '高级搜索结果',
    query: {
      query: item,
      isdeep: deepSearchSelected.value,
    },
  });
  close(); // 选择后依然关闭历史记录弹窗
};

// 关闭搜索历史页面
const close = () => {
  emit('close');
};


// 暴露方法给父组件
defineExpose({
  addToHistory
});
</script>

<style scoped>
.search-history-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: white;
  z-index: 100;
  display: flex;
  flex-direction: column;
  padding: 30px 0 0 0;
  opacity: 0;
  transition: opacity 0.5s ease;
}

.fade-in {
  opacity: 1;
}

.search-header {
  display: flex;
  flex-direction: column;
  padding: 10px 8px 10px 8px;
  border-radius: 10px;
  margin: 0 16px 20px;
  background-color: #f5f5f5;
  min-height: 80px;
  gap: 10px;
}

.search-input-container {
  width: 100%;
  margin: 0;
  display: flex;
  align-items: stretch;
}

.search-header-btn-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-top: 10px;
  width: 100%;
}
.btn-group-left {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
}

.back-button {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
}
.add-button {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
}

.deep-search-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
  padding: 0 18px;
  margin-left: 8px;
  margin-right: 8px;
  background: #f2f3f5;
  color: #333;
  border: none;
  border-radius: 20px;
  font-size: 15px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  box-shadow: 0 2px 8px rgba(200, 113, 237, 0.08);
  gap: 8px;
}
.deep-search-btn.selected {
  background: #e6f0fa;
  color: #1976d2;
}
.deep-search-btn:hover {
  background: #e6f0fa;
}

.deep-search-icon {
  width: 20px;
  height: 20px;
  object-fit: contain;
  margin-right: 4px;
}

.search-input-container {
  flex: 1;
  display: flex;
  align-items: center;
  margin: 0 10px;
  position: relative;
}

.send-btn {
  position: absolute;
  right: 8px;
  bottom: 8px;
  width: 36px;
  height: 36px;
  background: #1976d2;
  color: #fff;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(25, 118, 210, 0.08);
  transition: background 0.2s;
  padding: 0;
}
.send-btn:hover {
  background: #1565c0;
}


.current-search-textarea {
  width: 100%;
  min-height: 80px;
  resize: none;
  font-size: 18px;
  color: #333;
  border: none;
  background: transparent;
  outline: none;
  padding: 0;
  margin: 0;
  box-sizing: border-box;
  vertical-align: top;
  line-height: 1.5;
  text-align: left;
}

.history-section {
  flex: 1;
  padding: 0 16px;
  overflow-y: auto;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.history-title {
  display: flex;
  align-items: center;
  color: #333;
  font-size: 18px;
  font-weight: 500;
}

.history-title svg {
  width: 18px;
  height: 18px;
  margin-right: 8px;
}

.clear-history {
  color: #666;
  cursor: pointer;
}

.clear-history svg {
  width: 18px;
  height: 18px;
}

.history-items {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}
.history-items.two-col {
  flex-direction: row;
  flex-wrap: wrap;
  gap: 16px;
}
.history-items.two-col .history-item,
.history-items.two-col .more-history {
  width: calc(50% - 8px);
  box-sizing: border-box;
}
.history-items.one-col {
  flex-direction: column;
  gap: 10px;
}
.history-items.one-col .history-item {
  width: 100%;
}

.history-item {
  background-color: white;
  border: 1px solid #eee;
  padding: 8px 16px;
  border-radius: 4px;
  color: #333;
  font-size: 14px;
  cursor: pointer;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.more-history {
  display: flex;
  align-items: center;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  margin-top: 10px;
}

.more-history svg {
  width: 16px;
  height: 16px;
  margin-left: 4px;
}

.empty-history {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100px;
  color: #999;
}

.voice-search {
  padding: 20px 0;
  display: flex;
  justify-content: center;
}

.voice-button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 40px; /* 增加水平方向的内边距 */
  width: 180px; /* 设置固定宽度 */
  background: linear-gradient(to right, #c471ed, #f64f59);
  color: white;
  border-radius: 30px;
  font-size: 16px;
  white-space: nowrap; /* 防止文字换行 */
}

.voice-button svg {
  width: 20px;
  height: 20px;
  margin-right: 10px;
}
</style>
