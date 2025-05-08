<template>
  <div class="advanced-result-wrapper">
    <!-- 搜索输入框 -->
    <div class="search-bar-row">
      <input
        v-model="searchInput"
        class="search-input"
        placeholder="小米汽车内饰颜色"
        @keyup.enter="onSearch"
      />
      <span class="search-divider"></span>
      <button class="search-btn" @click="onSearch">搜索</button>
    </div>

    <!-- tab标签 -->
    <div class="tab-row">
      <div
        v-for="tab in tabs"
        :key="tab.name"
        :class="['tab-item', { active: tab.name === activeTab }]"
        @click="activeTab = tab.name"
      >
        <span class="tab-icon">{{ tab.icon }}</span>
        <span>{{ tab.name }}</span>
      </div>
    </div>

    <!-- 大模型回答和搜索结果联动 -->
    <div v-if="activeTab === 'AI'">
      <div class="ai-answer-card">
        <div class="ai-answer-header">
          <span class="ai-label">AI为你找到参考资料</span>
          <div style="display: flex; align-items: center;">
            <span class="source-icons">
              <template v-for="(icon, idx) in refIcons" :key="idx">
                <img
                  v-if="icon"
                  :src="icon"
                  class="source-icon"
                  :style="{ marginLeft: idx === 0 ? '0' : '-8px', zIndex: 10 - idx }"
                />
              </template>
            </span>
            <span style="margin-left: 2px;" class="source-count">{{ refList.length }}个来源</span>
          </div>
        </div>
        <div v-if="thinkingList.length" class="ai-thinking-bar" @click="toggleThinkingExpand">
          <div v-if="!thinkingEnd" class="marquee">
            <span>{{ thinkingDisplay }}</span>
          </div>
          <div v-else class="thinking-finished">
            已完成思考（耗时{{ thinkingDuration }}秒）
          </div>
        </div>
        <div v-if="thinkingExpand && thinkingList.length" class="ai-thinking-detail">
          <pre v-html="thinkingMarkdown"></pre>
        </div>
        <div class="ai-answer-content markdown-body" v-html="renderedAnswer"></div>
        <div class="ai-answer-actions">
          <div class="action-group">
            <span class="action-btn" title="点赞">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#bbb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M7 10V21a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2v-7"></path>
                <path d="M14 9V5a3 3 0 0 0-6 0v5"></path>
                <path d="M2 10h5"></path>
              </svg>
            </span>
            <span class="action-btn" title="点踩">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#bbb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17 14V3a2 2 0 0 0-2-2H9A2 2 0 0 0 7 3v7"></path>
                <path d="M10 15v4a3 3 0 0 0 6 0v-5"></path>
                <path d="M22 14h-5"></path>
              </svg>
            </span>
            <span class="action-btn" title="复制">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#bbb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
            </span>
          </div>
          <div class="action-group action-group-right">
            <span class="action-btn action-btn-refresh" title="刷新">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#bbb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><path d="M1 20v-6h6"></path><path d="M3.51 9a9 9 0 0 1 14.13-3.36L23 10"></path><path d="M1 14l5.37 5.36A9 9 0 0 0 20.49 15"></path></svg>
            </span>
            <span class="action-btn" title="分享">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#bbb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"></circle><circle cx="6" cy="12" r="3"></circle><circle cx="18" cy="19" r="3"></circle><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"></line><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"></line></svg>
            </span>
          </div>
        </div>
      </div>
      <div class="search-result-list">
        <div
          class="result-card"
          v-for="item in resultList"
          :key="item.title + item.source"
          @click="onResultCardClick(item.url)"
          style="cursor: pointer;"
        >
          <div class="result-title">{{ item.title }}</div>
          <div class="result-desc">{{ item.desc }}</div>
          <div class="result-imgs">
            <div v-if="item.images && item.images.length">
              <img v-for="img in item.images" :key="img" :src="img" class="img-placeholder result-img" />
            </div>
            <div v-else>
              <div class="img-placeholder result-img" v-for="i in 3" :key="i"></div>
            </div>
          </div>
          <div class="result-source">
            <img v-if="item.icon" :src="item.icon" class="result-source-icon" />
            {{ item.source }}
          </div>
        </div>
      </div>
    </div>
    <div v-if="activeTab !== 'AI'">
      <div class="deving-block">
        <div class="deving-content">开发中</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watchEffect, computed, onMounted } from 'vue'; // 引入 onMounted
import { useRoute } from 'vue-router'; // 引入 useRoute
import { marked } from 'marked';

const route = useRoute(); // 获取路由实例

const searchInput = ref(''); // 删除默认文字
const tabs = [
  { name: 'AI', icon: '🤖' },
  { name: '百度', icon: '🌐' },
  { name: '搜狗', icon: '🦊' },
  { name: '360', icon: '🟢' },
  { name: '今日头条', icon: '📰' }
];
const activeTab = ref('AI');
const resultList = ref([]);

const answer = ref('');
const refList = ref([]);
// 提取前三个icon
const refIcons = ref([]);

watchEffect(() => {
  if (Array.isArray(refList.value) && refList.value.length) {
    refIcons.value = refList.value.slice(0, 3).map(r => r.icon).filter(Boolean);
  } else {
    refIcons.value = [];
  }
});

// markdown 渲染
const renderedAnswer = computed(() => marked.parse(answer.value || ''));

const thinkingList = ref([]);
const thinkingStart = ref(0);
const thinkingEnd = ref(false);
const thinkingExpand = ref(false);
const thinkingDisplay = computed(() => thinkingList.value.join(''));
const thinkingMarkdown = computed(() => {
  // markdown引用样式
  return '> ' + thinkingList.value.join('');
});
const thinkingDuration = computed(() => {
  if (!thinkingStart.value || !thinkingEnd.value) return 0;
  return Math.round((thinkingEnd.value - thinkingStart.value) / 1000);
});
function toggleThinkingExpand() {
  thinkingExpand.value = !thinkingExpand.value;
}

// 修复window.open报错，使用全局window对象
function onResultCardClick(url) {
  if (url && window && window.open) {
    window.open(url, '_blank');
  }
}

async function onSearch() {
  answer.value = '';
  refList.value = [];
  thinkingList.value = [];
  thinkingStart.value = 0;
  thinkingEnd.value = false;
  thinkingExpand.value = false;

  // 1. 先调用原有AI接口
  const body = {
    content: searchInput.value,
    oaid: "014764227945ac18",
    chatType: "SUMMARY",
    searchId: "MTk0NzA4MzI3Mw==1735626267349",
    miId: "M2U0N2Y5ODRmMzg3OTE5ZjQ5NDYxMjcxMTk2YTA3MjA=",
    tzData: "566f419916348dcc",
    tzResultData: "eyJoYXNoIjoiMTEzZDUxYTE4MzBhNjliYzc2NTJlYTBmNmEzMmYyNTE5OTk3Njc2NyIsInBhY2thZ2VOYW1lIjoiY29tLmFuZHJvaWQuYnJvd3Nlci5kZWJ1ZyIsImFwcFNpZ24iOiI4RkNCQTVENDBFQzlGMkU5NjJEMDREMjJGMTcyOTAzNjdEQTgyNTZCIiwibm9uY2UiOiJlZGtQTnN0Vm1xb0J1V1J5IiwidHpUb2tlbiI6Imw5RnFHV1NpREMwelBkUnRtK3NWXC9NcjBPTDRrVnF3Skp6ZUZWa2FCeW5KeWxKN0V1cU1vRG1ueVhIcHQ1VlF5Zm95d3UxR1FkSVpZTXpsRkJSUklKejB5SjV1d0huVHpZSjBHMU9YQndBMFBqNElnQnlXYXVWMldtZlNOSGVRUDJOeHE5enEwK3h1dXFQXC80VXN5UlBwTmhIbjlJWHF0N1hDV1Z2akZHY1pROUNjQkJiamRMSXlxQnMzMHlHSUN6VkJ1NE95S1BhMk5CVGREODR2bG1wMXVHRDBTUDBMTTVyVW5yXC91XC9wUTZvTHZoK1FoT2FIQXNXUkNDMnNGVXRWdFBUK25CbXF5YXZob2haSWExb3BmZ29nR0hlcGdFbmVlMkZaang5YUlybFZzZkd0aUV6V08wVGttVE9GMFVJaUUzaHV4Wis3TnZ2djZuRjJWNWNMaDNMMnM1SjI5XC84UHp0MjgrdUFuQlNpTnYyc0hXTUE2aUhVNWMyN3Z6NG5SMHV0dVc1WTJjXC9aMjNYWU9NOXlCR1ora3c0cVRBc0lTWWh1c3lYYVVNa1JzbW5xWFwvN0sxUGlhN1hlVlljZXNpaDd1WW5sOE9KY0RkVW04OGlGb2p2VmxST0RGa1pnMjhzOGFZWU50SkRHTEZiOHo0TmY0cHEzWFNENDVkOE9VYVwvNWtzY0tXZG9veitIV0c5aHEyUXRzM0U1N3llXC91TzFVMkRiSXNtK0ZjRnlKdStTSkg5ZDl1TEdScHRsYmxWTXFFeTFzbWVodFJWYUZQem9nVnVPaktcL2dvdUhaUGM1dkowZU5rMDJXYVpwRXpGelFOOHdwTDRqVWk1OGxkSjdXNG1vUHMrQXVyRHhrZk1Fc3Nib2xQQT09IiwidmVyc2lvbiI6InYyIiwic2lnbmF0dXJlIjoiS01yR3l0WlBrMXJqQ2hsQWNzeTNCV0JOaHJEaFVuR01PWWtsaHE4WXJPUDQtbWRqZ3hKYldXSElfV09LRnQ3ZGxwV1kzVW44eTVPSzZUOTI4QWZISkFJekhLRFVEM19lNnFLLTV5ckZ0SVp2N0RWdUtlblN4UHVJeTdHT1NabzJ4a1RoNU5VNG5TM1h6VmVqbXJxRm1GZ0UyUHRBTk0xMzhaaXB4d1U0UkJNPSJ9",
    tzErrorCode: "2",
    tzErrorMsg: "不支持Tz验签",
    rawLastQueryList: [],
    model: "DOUBAO",
    isDeepThinking: route.query.isdeep === 'true' // 从路由参数获取 isDeepThinking
  };

  // 并行调用bochaai接口
  const bochaaiPromise = fetch('https://api.bochaai.com/v1/web-search', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer sk-bb67b69442e7458cae6e7bca308487dd',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query: searchInput.value,
      freshness: 'noLimit',
      summary: true,
      count: 20
    })
  })
    .then(res => res.json())
    .then(data => {
      // 解析bochaai返回
      if (data && data.code === 200 && data.data && data.data.webPages && Array.isArray(data.data.webPages.value)) {
        const imagesArr = (data.data.images && Array.isArray(data.data.images.value)) ? data.data.images.value : [];
        resultList.value = data.data.webPages.value.map(item => {
          // 匹配图片
          let images = [];
          if (imagesArr.length && item.url) {
            images = imagesArr
              .filter(img => img.hostPageUrl === item.url)
              .map(img => img.contentUrl)
              .filter(Boolean);
          }
          return {
            title: item.name,
            desc: item.summary,
            source: item.siteName,
            icon: item.siteIcon,
            images,
            url: item.url
          };
        });
      } else {
        resultList.value = [];
      }
    })
    .catch(() => {
      resultList.value = [];
    });

  // 继续原有AI接口逻辑
  fetch('https://ai.search.miui.com/api/llm/query', {
    method: 'POST',
    headers: {
      'Accept': 'text/event-stream',
      'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  }).then(async res => {
    if (!res.body) return;
    const reader = res.body.getReader();
    let decoder = new TextDecoder('utf-8');
    let done = false;
    let buffer = '';
    while (!done) {
      const { value, done: readerDone } = await reader.read();
      done = readerDone;
      if (value) {
        buffer += decoder.decode(value, { stream: true });
        let lines = buffer.split('\n');
        buffer = lines.pop() || '';
        for (let line of lines) {
          line = line.trim();
          if (!line) continue;
          // 处理 data: 前缀
          if (line.startsWith('data:')) {
            line = line.slice(5).trim();
          }
          if (!line) continue;
          try {
            const data = JSON.parse(line);
            if (data.code === 200 && data.responseType === 'ANSWER') {
              if (data.answer) {
                console.log('解析到 answer 片段:', data.answer);
                answer.value += data.answer;
                console.log('当前 answer.value:', answer.value);
                await nextTick();
              }
              if (Array.isArray(data.ref) && data.ref.length) {
                console.log('解析到 ref:', data.ref);
                refList.value = data.ref;
              }
              // 处理thinking
              if (typeof data.thinking === 'string' && data.thinking) {
                if (!thinkingStart.value) thinkingStart.value = Date.now();
                thinkingList.value.push(data.thinking);
              }
              if (data.thinkingEnd === true) {
                thinkingEnd.value = Date.now();
              }
              if (data.end === true) {
                console.log('流式输出结束');
                done = true;
                break;
              }
            }
          } catch (e) {
            // 非json行忽略
          }
        }
      }
    }
  }).catch(() => {
    answer.value = '请求失败，请重试';
    refList.value = [];
  });

  // 等待bochaai接口完成
  await bochaaiPromise;
}

onMounted(() => {
  const queryParam = route.query.query;
  if (queryParam) {
    searchInput.value = queryParam;
    onSearch(); // 如果query不为空，则调用搜索
  }
});
</script>

<style>
.advanced-result-wrapper {
  position: fixed;
  top: 0; 
  left: 0; 
  right: 0; 
  bottom: 0;
  background: linear-gradient(180deg, #f8e6e6 0%, #e6e6fa 100%);
  min-height: 100vh;
  padding: 16px 8px 60px 8px;
  box-sizing: border-box;
  overflow-y: auto;
}

.search-bar-row {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  padding: 8px 12px;
  margin-bottom: 12px;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 18px;
  background: transparent;
  padding: 8px 0;
}

.search-btn {
  display: flex;
  align-items: center;
  color: #1677ff;
  background: none;
  border: none;
  font-size: 18px;
  font-weight: 600;
  margin-left: 8px;
  cursor: pointer;
  padding: 0 8px;
  height: 36px;
}

.search-divider {
  width: 1px;
  height: 24px;
  background: #e5e5e5;
  margin: 0 8px;
  display: inline-block;
  vertical-align: middle;
}

.tab-row {
  display: flex;
  align-items: flex-end;
  margin-bottom: 0;
  padding: 0 2px;
  background: #fff;
  border-radius: 16px 16px 0 0;
  overflow-x: auto;
  position: relative;
  z-index: 2;
  border-bottom: 1.5px solid #f0f0f0;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: none;
  padding: 8px 18px 8px 16px;
  font-size: 16px;
  color: #888;
  cursor: pointer;
  font-weight: 500;
  border-radius: 14px 14px 0 0;
  background: #fff;
  margin-left: -18px;
  margin-bottom: 0;
  position: relative;
  z-index: 1;
}

.tab-item:first-child {
  margin-left: 0;
}

.tab-item:not(.active) {
  z-index: 1;
  background: #f5f5f5;
  color: #aaa;
}

.tab-item.active {
  color: #1677ff;
  background: #fff;
  border-bottom: 2.5px solid #fff;
  z-index: 10;
}

.tab-icon {
  font-size: 18px;
  margin-right: 2px;
}

.ai-answer-card {
  background: #fff;
  border-radius: 0 0 16px 16px;
  margin: 0 0 12px 0;
  padding: 16px 14px 10px 14px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  border-top: none;
  border-left: 1.5px solid #f0f0f0;
  border-right: 1.5px solid #f0f0f0;
  border-bottom: 1.5px solid #f0f0f0;
  position: relative;
  z-index: 1;
}

.ai-answer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.ai-label {
  font-size: 15px;
  color: #888;
  font-weight: 500;
}

.source-icons {
  display: flex;
  align-items: center;
  position: relative;
  height: 20px;
  margin-right: 2px;
}

.source-icon {
  width: 20px;
  height: 20px;
  position: relative;
  left: 0;
  top: 0;
  margin-left: -6px;
  z-index: auto;
}

.source-icon:first-child {
  margin-left: 0;
}

.source-count {
  font-size: 13px;
  color: #888;
  margin-left: 2px;
  position: relative;
  left: 0;
}

.ai-answer-content {
  font-size: 17px;
  color: #222;
  margin-bottom: 8px;
  line-height: 1.7;
  margin-left: 10px;
}

.ai-answer-content b {
  color: #222;
  font-weight: 700;
}

.ai-answer-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  font-size: 18px;
  color: #bbb;
  margin-top: 2px;
  margin-bottom: 2px;
  min-height: 36px;
}

.action-group,
.action-group-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.result-source {
  font-size: 13px;
  color: #aaa;
  display: flex;
  align-items: center;
  gap: 4px;
}

.action-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.action-group-right {
  margin-left: auto;
  gap: 10px;
  display: flex;
  align-items: center;
}

.action-btn {
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 2px;
  height: 36px;
  transition: background 0.15s;
  border-radius: 6px;
}

.action-btn:hover svg {
  stroke: #1677ff;
}

.action-btn-refresh {
  margin-left: 0;
  margin-right: 2px;
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.result-card {
  background: #fff;
  border-radius: 16px;
  margin-bottom: 7px;
  padding: 12px 12px 8px 12px;
  box-shadow: 0 1px 2px rgba(0,0,0,0.03);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.result-title {
  font-weight: bold;
  font-family: "Microsoft YaHei", "黑体", "Arial", sans-serif;
  color: #222;
  font-size: 17px;
}

.result-desc {
  color: #444;
  font-size: 15px;
  font-family: inherit;
  font-weight: normal;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.7;
  margin-bottom: 2px;
  word-break: break-all;
  white-space: normal;
  min-height: 3.4em;
  max-height: 5.1em;
}

.result-imgs {
  display: flex;
  gap: 8px;
  margin-bottom: 2px;
  flex-direction: row; /* 确保子元素横向排列 */
  overflow-x: auto; 
  width: 100%; /* 确保容器占满可用宽度以便内部滚动生效 */
}

.result-imgs > div { /* 直接子元素（v-if/v-else的容器）也需要flex布局 */
  display: flex;
  flex-direction: row;
  gap: 8px;
}

.img-placeholder {
  width: 80px;
  height: 120px;
  background: #f2f2f2;
  border-radius: 8px;
  object-fit: cover;
}

.result-img {
  width: 80px;
  height: 120px;
  object-fit: cover;
}

.result-source-icon {
  width: 18px;
  height: 18px;
  vertical-align: middle;
  margin-right: 4px;
  border-radius: 4px;
  object-fit: cover;
}

.result-source {
  font-size: 13px;
  color: #aaa;
}

.deving-block {
  margin: 32px 0 0 0;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 180px;
}

.deving-content {
  font-size: 22px;
  color: #bbb;
  letter-spacing: 2px;
  font-weight: 500;
  background: #f7f7f7;
  border-radius: 12px;
  padding: 48px 0;
  width: 100%;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.ai-thinking-bar {
  margin: 8px 0 0 10px;
  cursor: pointer;
  background: #f7f7f7;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 15px;
  color: #888;
  min-height: 24px;
  display: flex;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.marquee {
  width: 100%;
  white-space: nowrap;
  overflow: hidden;
  position: relative;
}

.marquee span {
  display: inline-block;
  padding-left: 100%;
  animation: marquee 6s linear infinite;
}

@keyframes marquee {
  0% { transform: translateX(0); }
  100% { transform: translateX(-100%); }
}

.thinking-finished {
  color: #4caf50;
}

.ai-thinking-detail {
  margin: 5px 0 5px 10px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 6px;
}

.ai-thinking-detail pre {
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
  font-family: inherit;
}
</style>
