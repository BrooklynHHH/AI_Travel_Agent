<template>
  <div class="advanced-container-wrapper">
    <!-- 搜索历史组件 -->
    <SearchHistory 
      :visible="showSearchHistory" 
      :current-input="searchInput"
      @close="closeSearchHistory"
      @select="handleHistorySelect"
      ref="searchHistoryRef"
    />
    <div class="advanced-container">
    <!-- 头部Logo区域 -->
    <div class="header-area">
      <div class="logo-container">
        <img src="../assets/mi-ai-search.jpg" alt="小米AI搜索" class="mi-logo-img" />
        <h1 class="logo-text">小米AI搜索</h1>
      </div>
      <p class="subtitle">我可以帮你搜索、答疑 请尽管发问</p>
    </div>

    <!-- 示例问题区域 -->
    <div class="example-questions">
      <h2 class="example-title">试试问</h2>
      <div class="question-cards-container">
        <div class="question-cards" ref="questionCardsRef">
          <div class="question-card fade-card" @click="handleQuickAction('直招军官体检通过率高吗 热点')">
            直招军官体检通过率高吗 <span class="hot-tag">热点</span>
          </div>
          <div class="question-card" @click="handleQuickAction('5个提升面部立体度的小动作 热点')">
            5个提升面部立体度的小动作 <span class="hot-tag">热点</span>
          </div>
          <div class="question-card" @click="handleQuickAction('试试生成AI头像 AI生图')">
            试试生成AI头像 <span class="ai-tag">AI生图</span>
          </div>
          <div class="question-card fade-card" @click="handleQuickAction('亚马逊和阿里伯伯比，哪个上网更快？ 热点')">
            亚马逊和阿里伯伯比，哪个上网更快？ <span class="hot-tag">热点</span>
          </div>
          <div class="question-card" @click="handleQuickAction('今年高考数学难不难 热点')">
            今年高考数学难不难 <span class="hot-tag">热点</span>
          </div>
          <div class="question-card" @click="handleQuickAction('如何申请公租房 热点')">
            如何申请公租房 <span class="hot-tag">热点</span>
          </div>
          <div class="question-card" @click="handleQuickAction('帮我写一段经典武侠小说风格的介绍')">
            帮我写一段经典武侠小说风格的介绍
          </div>
          <div class="question-card" @click="handleQuickAction('剑眉星目什么意思？词典')">
            剑眉星目什么意思？ <span class="ai-tag">词典</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 搜索输入框 -->
    <div class="search-bar-container">
      <div class="search-bar">
        <img src="../assets/search-input-logo.jpg" alt="搜索图标" class="search-icon" />
        <input 
          type="text" 
          class="search-input" 
          placeholder="输入你想问的问题" 
          @keyup.enter="handleSearch" 
          @focus="showSearchHistory = true"
          v-model="searchInput" 
        />
        <div class="search-controls">
          <template v-if="!hasSearchInput">
            <div class="voice-control">
              <img src="../assets/voice-control.jpg" alt="音量控制" class="voice-icon" />
            </div>
            <div class="add-button">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="16"></line><line x1="8" y1="12" x2="16" y2="12"></line></svg>
            </div>
          </template>
          <template v-else>
            <div class="send-button" @click="handleSearch">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather"><path d="M22 2L11 13M22 2L15 22L11 13L2 9L22 2z"></path></svg>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- 功能分类区域 -->
    <div class="feature-categories">
      <div class="category-row">
        <div class="category-box">
          <h3 class="category-title">办公</h3>
          <div class="category-items">
            <div class="category-item" @click="handleFeature('AI写作')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path></svg>
              </div>
              <div class="item-label">AI写作</div>
            </div>
            <div class="category-item" @click="handleFeature('文件总结')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
              </div>
              <div class="item-label">文件总结</div>
            </div>
            <div class="category-item" @click="handleFeature('AI PPT')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 16V4a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12"></path><path d="M22 16v4a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-4"></path><path d="M12 8v8"></path><path d="M8 12h8"></path></svg>
              </div>
              <div class="item-label">AI PPT</div>
            </div>
          </div>
        </div>
        <div class="category-box">
          <h3 class="category-title">学习</h3>
          <div class="category-items">
            <div class="category-item" @click="handleFeature('拍照搜题')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
              </div>
              <div class="item-label">拍照搜题</div>
            </div>
            <div class="category-item" @click="handleFeature('实时翻译')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 8v8"></path><path d="M5 12h14"></path><path d="M12 4v16"></path><path d="M9 4h6"></path><path d="M9 20h6"></path></svg>
              </div>
              <div class="item-label">实时翻译</div>
            </div>
            <div class="category-item" @click="handleFeature('思维导图')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
              </div>
              <div class="item-label">思维导图</div>
            </div>
          </div>
        </div>
      </div>
      <div class="category-row">
        <div class="category-box">
          <h3 class="category-title">创作</h3>
          <div class="category-items">
            <div class="category-item" @click="handleFeature('AI生图')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M12 16v-4"></path><path d="M12 8h.01"></path></svg>
              </div>
              <div class="item-label">AI生图</div>
            </div>
            <div class="category-item" @click="handleFeature('音乐生成')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"></path><circle cx="6" cy="18" r="3"></circle><circle cx="18" cy="16" r="3"></circle></svg>
              </div>
              <div class="item-label">音乐生成</div>
            </div>
            <div class="category-item" @click="handleFeature('照片动起来')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect><line x1="7" y1="2" x2="7" y2="22"></line><line x1="17" y1="2" x2="17" y2="22"></line><line x1="2" y1="12" x2="22" y2="12"></line><line x1="2" y1="7" x2="7" y2="7"></line><line x1="2" y1="17" x2="7" y2="17"></line><line x1="17" y1="17" x2="22" y2="17"></line><line x1="17" y1="7" x2="22" y2="7"></line></svg>
              </div>
              <div class="item-label">照片动起来</div>
            </div>
          </div>
        </div>
        <div class="category-box">
          <h3 class="category-title">生活</h3>
          <div class="category-items">
            <div class="category-item" @click="handleFeature('健康助手')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>
              </div>
              <div class="item-label">健康助手</div>
            </div>
            <div class="category-item" @click="handleFeature('法律咨询')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8h1a4 4 0 0 1 0 8h-1"></path><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path><line x1="6" y1="1" x2="6" y2="4"></line><line x1="10" y1="1" x2="10" y2="4"></line><line x1="14" y1="1" x2="14" y2="4"></line></svg>
              </div>
              <div class="item-label">法律咨询</div>
            </div>
            <div class="category-item" @click="handleFeature('AI解梦')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path></svg>
              </div>
              <div class="item-label">AI解梦</div>
            </div>
          </div>
        </div>
      </div>
      <div class="more-tools" @click="handleMoreTools">
        <span>更多AI工具</span>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="arrow-icon"><path d="M9 18l6-6-6-6"></path></svg>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import SearchHistory from '@/components/SearchHistory.vue';

const router = useRouter();
const searchInput = ref('');
const questionCardsRef = ref(null);
const autoScrollInterval = ref(null);
const showSearchHistory = ref(false);
const searchHistoryRef = ref(null);

// 计算属性：判断搜索输入框是否有内容
const hasSearchInput = computed(() => {
  return searchInput.value.trim().length > 0;
});

// 处理快速操作点击事件
const handleQuickAction = (text) => {
  // 这里可以实现跳转到聊天页面并设置输入内容为选定的问题
  console.log('选择了问题:', text);
  router.push({
    name: 'advanced-result', // 跳转到AdvancedResultView界面
    query: { 
      query: text, // 将被点中项的内容设置给query
      isdeep: false // isdeep为false
    }
  });
};

// 处理搜索功能
const handleSearch = () => {
  if (searchInput.value.trim()) {
    console.log('搜索:', searchInput.value);
    
    // 添加到搜索历史
    if (searchHistoryRef.value) {
      searchHistoryRef.value.addToHistory(searchInput.value);
    }
    
    router.push({
      path: '/mi',
      query: { q: searchInput.value }
    });
  }
};

// 关闭搜索历史页面
const closeSearchHistory = () => {
  showSearchHistory.value = false;
};

// 处理选择历史记录
const handleHistorySelect = (item) => {
  searchInput.value = item;
  handleSearch();
};

// 处理功能点击事件
const handleFeature = (feature) => {
  console.log('选择了功能:', feature);
  router.push({
    name: 'advanced-result', // 跳转到AdvancedResultView界面
    query: { 
      query: feature, // 将被点中项的内容设置给query
      isdeep: false // isdeep为false
    }
  });
};

// 处理更多工具点击事件
const handleMoreTools = () => {
  window.location.href = 'http://mify.pt.xiaomi.com';
};

// 自动滚动函数
const autoScrollQuestions = () => {
  const cardsElement = questionCardsRef.value;
  if (!cardsElement) return;
  
  // 滚动一个问题的高度（包括间距）
  const cardHeight = 55; // 问题卡片高度+间距
  
  // 计算当前滚动位置和总高度
  const isAtEnd = cardsElement.scrollTop + cardsElement.clientHeight >= cardsElement.scrollHeight - 10;
  
  // 如果已经滚动到最后，平滑回到顶部
  if (isAtEnd) {
    // 先移除平滑滚动以便立即回到顶部
    cardsElement.style.scrollBehavior = 'auto';
    cardsElement.scrollTop = 0;
    // 恢复平滑滚动
    setTimeout(() => {
      cardsElement.style.scrollBehavior = 'smooth';
    }, 50);
  } else {
    // 平滑滚动到下一个问题
    cardsElement.scrollTop += cardHeight;
  }
};

onMounted(() => {
  document.title = '小米AI搜索';
  
  // 复制问题卡实现无限滚动效果
  setTimeout(() => {
    const cardsElement = questionCardsRef.value;
    if (cardsElement) {
      const cards = cardsElement.querySelectorAll('.question-card');
      // 复制前4个问题到底部
      for (let i = 0; i < 4; i++) {
        if (cards[i]) {
          const clone = cards[i].cloneNode(true);
          cardsElement.appendChild(clone);
        }
      }
    }
    
    // 设置自动滚动，每2秒滚动一次
    autoScrollInterval.value = setInterval(autoScrollQuestions, 2000);
  }, 100);
});

// 在组件卸载时清除定时器
onUnmounted(() => {
  if (autoScrollInterval.value) {
    clearInterval(autoScrollInterval.value);
  }
});
</script>

<style scoped>
.advanced-container-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #f8f9fa;
  overflow-y: auto;
}

.advanced-container {
  display: flex;
  flex-direction: column;
  background-color: #f8f9fa;
  padding: 0 16px 60px; /* 增加底部padding确保内容不被遮挡 */
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  min-height: 100%;
}

/* 头部Logo区域 */
.header-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 0 24px;
  text-align: center;
}

.logo-container {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.mi-logo-img {
  height: 40px;
  width: 40px;
  margin-right: 8px;
}

.logo-text {
  font-size: 28px;
  font-weight: 700;
  color: #222;
  margin: 0;
}

.subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

/* 示例问题区域 */
.example-questions {
  margin-top: 24px;
}

.example-title {
  font-size: 18px;
  font-weight: 500;
  color: #666;
  margin-bottom: 16px;
}

.question-cards-container {
  position: relative;
  height: 220px; /* 显示4个问题的高度 */
  margin-bottom: 10px; /* 统一间距 */
  overflow: hidden;
}

.question-cards-container::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 50px;
  background: linear-gradient(to bottom, rgba(248, 249, 250, 1), rgba(248, 249, 250, 0));
  pointer-events: none;
  z-index: 2;
}

.question-cards-container::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 50px;
  background: linear-gradient(to top, rgba(248, 249, 250, 1), rgba(248, 249, 250, 0));
  pointer-events: none;
  z-index: 2;
}

.question-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
  overflow-y: auto;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
  scroll-behavior: smooth; /* 平滑滚动 */
  padding: 2px; /* 防止滚动时阴影被裁剪 */
  mask-image: linear-gradient(to bottom, transparent, black 25%, black 75%, transparent);
  -webkit-mask-image: linear-gradient(to bottom, transparent, black 25%, black 75%, transparent);
}

.question-cards::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

.question-card {
  background-color: #fff;
  border-radius: 16px;
  padding: 12px 16px;
  font-size: 16px;
  color: #333;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid #e8e8e8;
  flex-shrink: 0;
}

.fade-card {
  opacity: 0.6;
}

.question-card:hover {
  background-color: #f9f9f9;
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  opacity: 1;
}

.hot-tag, .ai-tag {
  display: inline-block;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  margin-left: 8px;
  font-weight: 500;
}

.hot-tag {
  background-color: #fff2e8;
  color: #ff6b00;
}

.ai-tag {
  background-color: #f0f1ff;
  color: #5c6ac4;
}

/* 底部控制台 */
/* 搜索框样式 */
.search-bar-container {
  margin: 0 auto 10px; /* 统一底部间距 */
  width: 100%;
  display: flex;
  justify-content: center;
  padding: 0;
}

.search-bar {
  display: flex;
  align-items: center;
  background-color: #fff;
  border-radius: 5px;
  width: 100%;
  padding: 6px 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #eee;
}

.search-input {
  flex: 1;
  border: none;
  padding: 8px 12px;
  font-size: 15px;
  outline: none;
  background: #fff;
  height: 60px; /* 增加高度以容纳三行文本 */
  line-height: 20px; /* 行高设为20px，三行就是60px */
  vertical-align: top; /* 文本顶部对齐 */
}

.search-icon {
  width: 20px;
  height: 20px;
  margin-right: 8px;
}

.search-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.voice-control {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #f1f1f1;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.voice-icon {
  width: 24px;
  height: 24px;
}

.add-button {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  cursor: pointer;
}

.voice-control svg, .add-button svg, .send-button svg {
  width: 24px;
  height: 24px;
}

.send-button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #f1f1f1;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #07C160;
  transition: background-color 0.2s;
}

.send-button:hover {
  background-color: #e6f7ef;
}

/* 功能分类区域 */
.feature-categories {
  margin-bottom: 50px; /* 增加底部间距 */
}

.category-row {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.category-box {
  flex: 1;
  background-color: #fff;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  border: 1px solid #eee;
}

.category-title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin: 0 0 12px 0;
}

.category-items {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.category-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  flex: 1;
}

.item-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
  color: #666;
}

.item-icon svg {
  width: 24px;
  height: 24px;
}

.item-label {
  font-size: 12px;
  color: #555;
  text-align: center;
}

.more-tools {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 14px;
  margin-top: 24px;
  margin-bottom: 16px; /* 添加底部间距 */
  cursor: pointer;
}

.arrow-icon {
  width: 16px;
  height: 16px;
  margin-left: 4px;
}

/* 移动设备适配 */
@media (max-width: 600px) {
  .category-row {
    flex-direction: column;
    gap: 12px;
  }
  
  .header-area {
    padding: 24px 0 16px;
  }
  
  .logo-text {
    font-size: 24px;
  }
  
  .subtitle {
    font-size: 14px;
  }
}
</style>
