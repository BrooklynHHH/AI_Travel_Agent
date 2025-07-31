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
    <div v-if="activeTab === '博查搜索'">
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
          v-for="item in resultListMap['博查搜索']"
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
          </div>
          <div class="result-source">
            <img v-if="item.icon" :src="item.icon" class="result-source-icon" />
            {{ item.source }}
          </div>
        </div>
      </div>
    </div>
    <!-- 其他tab複刻AI區塊，接口待替換 -->
    <div v-if="activeTab === '百度基础搜索'">
      <div class="ai-answer-card">
        <!-- TODO: 百度接口數據，請在此處替換為百度相關接口 -->
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
          v-for="item in resultListMap['百度基础搜索']"
          :key="item.title + item.source"
          @click="onResultCardClick(item.url)"
          style="cursor: pointer;"
        >
          <div class="result-title">{{ item.title }}</div>
          <div class="result-desc">{{ item.desc }}</div>
          <div class="result-imgs">
            <div v-if="item.images && item.images.length">
              <img v-for="img in item.images" :key="img" :src="img.url" class="img-placeholder result-img" />
            </div>
          </div>
          <div class="result-source">
            <img v-if="item.icon" :src="item.icon" class="result-source-icon" />
            {{ item.source }}
          </div>
        </div>
      </div>
    </div>
    <div v-if="activeTab === '百度AI搜索'">
      <div class="ai-answer-card">
        <!-- TODO: 百度AI接口數據，請在此處替換為百度AI相關接口 -->
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
          v-for="item in resultListMap['百度AI搜索']"
          :key="item.title + item.source"
          @click="onResultCardClick(item.url)"
          style="cursor: pointer;"
        >
          <div class="result-title">{{ item.title }}</div>
          <div class="result-desc">{{ item.desc }}</div>
          <div class="result-imgs">
            <div v-if="item.images && item.images.length">
              <img v-for="img in item.images" :key="img" :src="img.url" class="img-placeholder result-img" />
            </div>
          </div>
          <div class="result-source">
            <img v-if="item.icon" :src="item.icon" class="result-source-icon" />
            {{ item.source }}
          </div>
        </div>
      </div>
    </div>
    <div v-if="activeTab === '百度图片搜索'">
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
      <div class="image-gallery">
        <div
          class="image-card"
          v-for="item in resultListMap['百度图片搜索']"
          :key="item.url"
          @click="showFullscreenImage(item.images[0])"
          style="cursor: pointer;"
        >
          <div class="image-container">
            <img :src="item.images[0]" :alt="item.title" class="gallery-image" />
          </div>
        </div>
      </div>
    </div>
    <div v-if="activeTab === '豆包联网问答Agent'">
      <div class="ai-answer-card">
        <!-- TODO: 豆包接口數據，請在此處替換為豆包相關接口 -->
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
          v-for="(item, index) in resultListMap['豆包联网问答Agent']"
          :key="item.url || (item.title + item.source + index)"
        >
          <!-- 天气卡片 -->
          <div v-if="item.type === 'weather'" class="weather-card">
            <div class="weather-header">
              <div class="weather-city">{{ item.weatherData.city.name }}</div>
              <div class="weather-temp">{{ item.weatherData.condition.temp }}°C</div>
            </div>
            
            <div class="weather-main">
              <div class="weather-condition">
                <div class="weather-desc">{{ item.weatherData.condition.weather }}</div>
                <div class="weather-details">
                  <span>体感 {{ item.weatherData.condition.real_feel }}°C</span>
                  <span>湿度 {{ item.weatherData.condition.humidity }}%</span>
                  <span>{{ item.weatherData.condition.wind_dir }} {{ item.weatherData.condition.wind_level }}级</span>
                </div>
              </div>
            </div>

            <div class="weather-aqi">
              <div class="aqi-header">空气质量</div>
              <div class="aqi-content">
                <div class="aqi-value" :class="getAqiClass(item.weatherData.aqi.aqi)">
                  {{ item.weatherData.aqi.aqi }}
                </div>
                <div class="aqi-level">{{ item.weatherData.aqi.quality_level }}</div>
              </div>
            </div>

            <div class="weather-forecast">
              <div class="forecast-header">7天预报</div>
              <div class="forecast-list">
                <div 
                  v-for="(day, dayIndex) in item.weatherData.seven_forecast_data.slice(0, 7)" 
                  :key="dayIndex"
                  class="forecast-item"
                >
                  <div class="forecast-date">{{ formatDate(day.predict_date) }}</div>
                  <div class="forecast-weather">{{ day.weather_day }}</div>
                  <div class="forecast-temp">
                    <span class="temp-high">{{ day.temp_high }}°</span>
                    <span class="temp-low">{{ day.temp_low }}°</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="weather-source">
              <img v-if="item.icon" :src="item.icon" class="result-source-icon" />
              {{ item.source }}
            </div>
          </div>

          <!-- 普通卡片 -->
          <div
            v-else
            class="result-card"
            @click="onResultCardClick(item.url)"
            style="cursor: pointer;"
          >
            <div class="result-title">{{ item.title }}</div>
            <div class="result-desc">{{ item.desc }}</div>
            <div class="result-imgs">
              <div v-if="item.images && item.images.length">
                <img v-for="img in item.images" :key="img" :src="img" class="img-placeholder result-img" />
              </div>
            </div>
            <div class="result-source">
              <img v-if="item.icon" :src="item.icon" class="result-source-icon" />
              {{ item.source }}
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- <div v-if="activeTab === '豆包融合信息搜索Agent'">
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
          v-for="item in resultListMap['豆包融合信息搜索Agent']"
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
          </div>
          <div class="result-source">
            <img v-if="item.icon" :src="item.icon" class="result-source-icon" />
            {{ item.source }}
          </div>
        </div>
      </div>
    </div> -->
    <div v-if="activeTab === '豆包融合信息搜索Agent'">
      <div class="ai-answer-card">
        <!-- TODO: 豆包接口數據，請在此處替換為豆包相關接口 -->
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
          v-for="(item, index) in resultListMap['豆包融合信息搜索Agent']"
          :key="item.url || (item.title + item.source + index)"
        >
          <!-- 天气卡片 -->
          <div v-if="item.type === 'weather'" class="weather-card">
            <div class="weather-header">
              <div class="weather-city">{{ item.weatherData.city.name }}</div>
              <div class="weather-temp">{{ item.weatherData.condition.temp }}°C</div>
            </div>
            
            <div class="weather-main">
              <div class="weather-condition">
                <div class="weather-desc">{{ item.weatherData.condition.weather }}</div>
                <div class="weather-details">
                  <span>体感 {{ item.weatherData.condition.real_feel }}°C</span>
                  <span>湿度 {{ item.weatherData.condition.humidity }}%</span>
                  <span>{{ item.weatherData.condition.wind_dir }} {{ item.weatherData.condition.wind_level }}级</span>
                </div>
              </div>
            </div>

            <div class="weather-aqi">
              <div class="aqi-header">空气质量</div>
              <div class="aqi-content">
                <div class="aqi-value" :class="getAqiClass(item.weatherData.aqi.aqi)">
                  {{ item.weatherData.aqi.aqi }}
                </div>
                <div class="aqi-level">{{ item.weatherData.aqi.quality_level }}</div>
              </div>
            </div>

            <div class="weather-forecast">
              <div class="forecast-header">7天预报</div>
              <div class="forecast-list">
                <div 
                  v-for="(day, dayIndex) in item.weatherData.seven_forecast_data.slice(0, 7)" 
                  :key="dayIndex"
                  class="forecast-item"
                >
                  <div class="forecast-date">{{ formatDate(day.predict_date) }}</div>
                  <div class="forecast-weather">{{ day.weather_day }}</div>
                  <div class="forecast-temp">
                    <span class="temp-high">{{ day.temp_high }}°</span>
                    <span class="temp-low">{{ day.temp_low }}°</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="weather-source">
              <img v-if="item.icon" :src="item.icon" class="result-source-icon" />
              {{ item.source }}
            </div>
          </div>

          <!-- 普通卡片 -->
          <div
            v-else
            class="result-card"
            @click="onResultCardClick(item.url)"
            style="cursor: pointer;"
          >
            <div class="result-title">{{ item.title }}</div>
            <div class="result-desc">{{ item.desc }}</div>
            <div class="result-imgs">
              <div v-if="item.images && item.images.length">
                <img v-for="img in item.images" :key="img" :src="img" class="img-placeholder result-img" />
              </div>
            </div>
            <div class="result-source">
              <img v-if="item.icon" :src="item.icon" class="result-source-icon" />
              {{ item.source }}
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="!['博查搜索','百度基础搜索','百度AI搜索','百度图片搜索','豆包联网问答Agent','豆包融合信息搜索Agent'].includes(activeTab)">
      <div class="deving-block">
        <div class="deving-content">开发中</div>
      </div>
    </div>

    <!-- 全屏图片模态框 -->
    <div v-if="fullscreenImage" class="fullscreen-modal" @click="closeFullscreenImage">
      <div class="fullscreen-content">
        <img :src="fullscreenImage" class="fullscreen-image" @click.stop />
        <button class="close-btn" @click="closeFullscreenImage">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watchEffect, computed, onMounted, watch } from 'vue'; // 引入 watch
import { useRoute } from 'vue-router'; // 引入 useRoute
import { marked } from 'marked';

const route = useRoute(); // 获取路由实例

// 辅助函数：安全地获取URL的hostname，兼容URL编码
function getHostnameFromUrl(url) {
  if (!url) return '';
  try {
    // 先尝试解码URL
    const decodedUrl = decodeURIComponent(url);
    return (new URL(decodedUrl)).hostname;
  } catch (e) {
    try {
      // 如果解码失败，直接使用原URL
      return (new URL(url)).hostname;
    } catch (e2) {
      // 如果都失败了，返回空字符串
      return '';
    }
  }
}

const searchInput = ref(''); // 删除默认文字
const lastSearchQuery = ref(); // 記錄上次搜索詞，避免重複調用AI接口
const tabs = [
  { name: '博查搜索', icon: '🤖' },
  { name: '百度基础搜索', icon: '🌐' },
  { name: '百度AI搜索', icon: '🦊' }, // 原搜狗tab改名
  { name: '百度图片搜索', icon: '🖼️' }, // 新增百度图片搜索tab
  { name: '豆包联网问答Agent', icon: '🟢' }, // 原360改為豆包
  { name: '豆包融合信息搜索Agent', icon: '🔍' }, // 新增第五个标签页
];
const activeTab = ref('博查搜索');
// const resultList = ref([]); // 已不再使用，移除

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

// AQI等级判断函数
function getAqiClass(aqi) {
  if (aqi <= 50) return 'aqi-good';
  if (aqi <= 100) return 'aqi-moderate';
  if (aqi <= 150) return 'aqi-unhealthy-sensitive';
  if (aqi <= 200) return 'aqi-unhealthy';
  if (aqi <= 300) return 'aqi-very-unhealthy';
  return 'aqi-hazardous';
}

// 日期格式化函数
function formatDate(dateStr) {
  const date = new Date(dateStr);
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(today.getDate() + 1);
  
  if (date.toDateString() === today.toDateString()) {
    return '今天';
  } else if (date.toDateString() === tomorrow.toDateString()) {
    return '明天';
  } else {
    const month = date.getMonth() + 1;
    const day = date.getDate();
    return `${month}/${day}`;
  }
}

// 全屏图片显示相关
const fullscreenImage = ref('');

function showFullscreenImage(imageUrl) {
  fullscreenImage.value = imageUrl;
}

function closeFullscreenImage() {
  fullscreenImage.value = '';
}

// 定義每個tab對應的網頁卡片接口
const tabApiMap = {
  '博查搜索': {
    url: 'https://api.bochaai.com/v1/web-search',
    method: 'POST',
    headers: {
      'Authorization': 'Bearer sk-bb67b69442e7458cae6e7bca308487dd',
      'Content-Type': 'application/json'
    },
    body: (query) => JSON.stringify({ query, freshness: 'noLimit', summary: true, count: 20 }),
    adapt: (data) => {
      if (data && data.code === 200 && data.data && data.data.webPages && Array.isArray(data.data.webPages.value)) {
        const imagesArr = (data.data.images && Array.isArray(data.data.images.value)) ? data.data.images.value : [];
        return data.data.webPages.value.map(item => {
          let images = [];
          if (imagesArr.length && item.url) {
            images = imagesArr.filter(img => img.hostPageUrl === item.url).map(img => img.contentUrl).filter(Boolean);
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
      }
      return [];
    }
  },
  '百度图片搜索': {
    url: 'http://staging-llm.search.miui.srv/agent-api/qianfan-image-search',
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: (query) => JSON.stringify({ query }),
    adapt: (data) => {
      console.log('百度图片搜索API原始数据：', data);
      if (data && data.answer) {
        try {
          // 如果answer是字符串，需要先解析为数组
          let imageUrls = data.answer;
          if (typeof data.answer === 'string') {
            // Python风格的字符串，将单引号替换为双引号后解析
            const jsonString = data.answer.replace(/'/g, '"');
            imageUrls = JSON.parse(jsonString);
          }
          
          if (Array.isArray(imageUrls)) {
            const adaptedData = imageUrls.map((imageUrl, index) => {
              if (imageUrl && typeof imageUrl === 'string') {
                return {
                  title: `图片 ${index + 1}`,
                  desc: '',
                  source: '百度图片',
                  icon: '',
                  images: [imageUrl],
                  url: imageUrl,
                  type: 'image'
                };
              }
              return null;
            }).filter(Boolean);
            console.log('百度图片搜索API适配后数据：', adaptedData);
            return adaptedData;
          }
        } catch (e) {
          console.error('百度图片搜索API数据解析失败：', e);
          // 如果JSON解析失败，尝试使用正则表达式提取URL
          try {
            if (typeof data.answer === 'string') {
              const urlRegex = /https?:\/\/[^\s'",\]]+/g;
              const urls = data.answer.match(urlRegex) || [];
              const adaptedData = urls.map((imageUrl, index) => ({
                title: `图片 ${index + 1}`,
                desc: '',
                source: '百度图片',
                icon: '',
                images: [imageUrl],
                url: imageUrl,
                type: 'image'
              }));
              console.log('百度图片搜索API正则提取后数据：', adaptedData);
              return adaptedData;
            }
          } catch (regexError) {
            console.error('正则表达式提取URL失败：', regexError);
          }
        }
      }
      console.log('百度图片搜索API数据格式不正确或为空');
      return [];
    }
  },
  '百度基础搜索': {
    url: 'http://staging-llm.search.miui.srv/agent-api/baidu-ai', // 本地開發用代理解決CORS
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: (query) => JSON.stringify({ q: query, type: 'base' }),
    adapt: (data) => {
      console.log('百度API原始数据：', data);
      console.log('百度API数据类型：', typeof data);
      console.log('百度API是否有references：', data && data.references);
      console.log('百度API references类型：', data && typeof data.references);
      console.log('百度API references是否为数组：', data && Array.isArray(data.references));
      
      if (data && Array.isArray(data.references)) {
        console.log('百度API references长度：', data.references.length);
        const adaptedData = data.references.map(item => {
          if (item.type === 'image' && item.image) {
            // 圖片卡片
            return {
              title: item.title || '',
              desc: item.content || '',
              source: getHostnameFromUrl(item.url),
              icon: item.icon,
              images: [item.image],
              url: item.url
            };
          } else if (item.type === 'video' && item.video) {
            // 視頻卡片（可根據實際字段擴展）
            return {
              title: item.title || '',
              desc: item.content || '',
              source: getHostnameFromUrl(item.url),
              icon: item.icon,
              images: [], // 可根據接口擴展視頻封面
              url: item.url,
              video: item.video
            };
          } else {
            // 普通網頁卡片
            return {
              title: item.title || '',
              desc: item.content || '',
              source: getHostnameFromUrl(item.url),
              icon: item.icon,
              images: item.image ? [item.image] : [],
              url: item.url
            };
          }
        });
        console.log('百度API适配后数据：', adaptedData);
        return adaptedData;
      }
      console.log('百度API数据格式不正确或为空，data:', data);
      return [];
    },
  },
  '百度AI搜索': {
    url: 'http://staging-llm.search.miui.srv/agent-api/baidu-ai',
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: (query) => JSON.stringify({ q: query, type: '' }),
    adapt: (data) => {
      console.log('百度AI API原始数据：', data);
      if (data && Array.isArray(data.references)) {
        const adaptedData = data.references.map(item => {
          if (item.type === 'image' && item.image) {
            // 圖片卡片
            return {
              title: item.title || '',
              desc: item.content || '',
              source: getHostnameFromUrl(item.url),
              icon: item.icon,
              images: [item.image],
              url: item.url
            };
          } else if (item.type === 'video' && item.video) {
            // 視頻卡片（可根據實際字段擴展）
            return {
              title: item.title || '',
              desc: item.content || '',
              source: getHostnameFromUrl(item.url),
              icon: item.icon,
              images: [], // 可根據接口擴展視頻封面
              url: item.url,
              video: item.video
            };
          } else {
            // 普通網頁卡片
            return {
              title: item.title || '',
              desc: item.content || '',
              source: getHostnameFromUrl(item.url),
              icon: item.icon,
              images: item.image ? [item.image] : [],
              url: item.url
            };
          }
        });
        console.log('百度API适配后数据：', adaptedData);
        return adaptedData;
      }
      console.log('百度AI API数据格式不正确或为空');
      return [];
    }
  },
  '豆包联网问答Agent': {
    url: 'http://staging-llm.search.miui.srv/agent-api/doubao-agent', // 使用相對路徑，支持前後端分離和線上部署    url: 'http://localhost:3001/api/doubao-agent', // 使用本地智能體代理

    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: (query) => JSON.stringify({ query }),
    adapt: (data) => {
      // 1. 參考資料卡片（references）
      let cards = [];
      if (data && Array.isArray(data.references)) {
        cards = data.references.map(item => ({
          title: item.title || '',
          desc: '',
          source: item.site_name || '',
          icon: '',
          images: item.cover_image && item.cover_image.url ? [item.cover_image.url] : [],
          url: item.url || ''
        }));
      }
      
      // 2. 多模態卡片（cards）- 先处理weather卡片，确保它们在最前面
      let weatherCards = [];
      let otherCards = [];
      
      if (data && Array.isArray(data.cards)) {
        data.cards.forEach(card => {
          if (card.card_type === 'weather' && card.weather_card) {
            const weatherData = card.weather_card.moji_weather_card;
            weatherCards.push({
              type: 'weather',
              title: `${weatherData.city.name}天气`,
              desc: `${weatherData.condition.weather} ${weatherData.condition.temp}°C`,
              source: '墨迹天气',
              icon: '',
              weatherData: weatherData,
              url: ''
            });
          } else if (card.card_type === 'image' && card.image_card) {
            otherCards.push({
              title: card.image_card.title || '',
              desc: '',
              source: card.image_card.site_name || '',
              icon: '',
              images: card.image_card.image_url ? [card.image_card.image_url] : [],
              url: card.image_card.source_image_url || ''
            });
          } else if (card.card_type === 'video' && card.video_card) {
            otherCards.push({
              title: card.video_card.title || '',
              desc: '',
              source: card.video_card.site_name || '',
              icon: '',
              images: card.video_card.cover_image && card.video_card.cover_image.url ? [card.video_card.cover_image.url] : [],
              url: card.video_card.url || ''
            });
          }
        });
      }
      
      // 将weather卡片放在最前面，然后是其他卡片，最后是references
      return [...weatherCards, ...otherCards, ...cards];
    }
  },
  '豆包融合信息搜索Agent': {
    url: 'http://staging-llm.search.miui.srv/agent-api/doubao-search',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: (query) => JSON.stringify({ 
      query: query, 
      searchType: "web" 
    }),
    adapt: (data) => {
      console.log('豆包融合信息搜索Agent API原始数据：', data);
      if (data && data.Result && Array.isArray(data.Result.WebResults)) {
        const adaptedData = data.Result.WebResults.map(item => {
          return {
            title: item.Title || '',
            desc: item.Snippet || '',
            source: item.SiteName || '',
            icon: item.LogoUrl || '',
            images: [],
            url: item.Url || ''
          }
        });
        console.log('豆包融合信息搜索Agent API适配后数据：', adaptedData);
        return adaptedData;
      }
      console.log('豆包融合信息搜索Agent API数据格式不正确或为空');
      return [];
    }
  }
};

const resultListMap = ref({
  '博查搜索': [],
  '百度基础搜索': [],
  '百度AI搜索': [],
  '百度图片搜索': [],
  '豆包联网问答Agent': [],
  '豆包融合信息搜索Agent': []
});

async function onSearch() {
  const isFirstSearch = !answer.value && !refList.value.length;
  const searchQueryChanged = searchInput.value !== lastSearchQuery.value;
  
  if (isFirstSearch || searchQueryChanged) {
    answer.value = '';
    refList.value = [];
    thinkingList.value = [];
    thinkingStart.value = 0;
    thinkingEnd.value = false;
    thinkingExpand.value = false;
    lastSearchQuery.value = searchInput.value;

    // AI接口不變，所有tab都保留
    const body = {
      content: searchInput.value,
      oaid: "014764227945ac18",
      chatType: "SUMMARY",
      searchId: "MTk0NzA4MzI3Mw==1735626267349",
      miId: "M2U0N2Y5ODRmMzg3OTE5ZjQ5NDYxMjcxMTk2YTA3MjA=",
      tzData: "566f419916348dcc",
      tzResultData: "...",
      tzErrorCode: "2",
      tzErrorMsg: "不支持Tz验签",
      rawLastQueryList: [],
      model: "DOUBAO",
      isDeepThinking: route.query.isdeep === 'true'
    };

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
          if (line.startsWith('data:')) {
            line = line.slice(5).trim();
          }
          if (!line) continue;
          try {
            const data = JSON.parse(line);
            if (data.code === 200 && data.responseType === 'ANSWER') {
              if (data.answer) {
                answer.value += data.answer;
                await nextTick();
              }
              if (Array.isArray(data.ref) && data.ref.length) {
                refList.value = data.ref;
              }
              if (typeof data.thinking === 'string' && data.thinking) {
                if (!thinkingStart.value) thinkingStart.value = Date.now();
                thinkingList.value.push(data.thinking);
              }
              if (data.thinkingEnd === true) {
                thinkingEnd.value = Date.now();
              }
              if (data.end === true) {
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
  }

  // 每個tab下方的網頁卡片都調用對應接口，並存入resultListMap
  const tab = activeTab.value;
  const tabApi = tabApiMap[tab];
  if (tabApi) {
    console.log(`开始请求${tab} API，URL：`, tabApi.url);
    await fetch(tabApi.url, {
      method: tabApi.method,
      headers: tabApi.headers,
      body: tabApi.body(searchInput.value)
    })
      .then(res => {
        console.log(`${tab} API响应状态：`, res.status, res.statusText);
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      })
      .then(data => {
        console.log(`${tab} API返回数据：`, data);
        const adapted = tabApi.adapt(data);
        console.log(`${tab} API适配后数据：`, adapted);
        resultListMap.value[tab] = adapted;
        
        // 强制触发响应式更新
        nextTick(() => {
          console.log(`${tab} resultListMap更新后：`, resultListMap.value[tab]);
        });
      })
      .catch((e) => {
        console.error(`【${tab}API请求失败】`, e);
        console.error(`【${tab}API请求失败】错误详情：`, e.message);
        resultListMap.value[tab] = [];
      });
  } else {
    console.log(`${tab} tab没有对应的API配置`);
    resultListMap.value[tab] = [];
  }
}

// 監聽tab切換，只更新對應tab的網頁卡片，不重複調用AI接口
watch(activeTab, () => {
  if (searchInput.value) {
    // 只調用當前tab的網頁卡片接口，不重複調用AI接口
    const tab = activeTab.value;
    const tabApi = tabApiMap[tab];
    if (tabApi) {
      console.log(`切换到${tab} tab，开始请求API，URL：`, tabApi.url);
      fetch(tabApi.url, {
        method: tabApi.method,
        headers: tabApi.headers,
        body: tabApi.body(searchInput.value)
      })
        .then(res => {
          console.log(`切换到${tab} tab，API响应状态：`, res.status, res.statusText);
          if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
          }
          return res.json();
        })
        .then(data => {
          console.log(`切换到${tab} tab，API返回：`, data);
          const adapted = tabApi.adapt(data);
          console.log(`切换到${tab} tab，适配后：`, adapted);
          resultListMap.value[tab] = adapted;
          
          // 强制触发响应式更新
          nextTick(() => {
            console.log(`切换到${tab} tab，resultListMap更新后：`, resultListMap.value[tab]);
          });
        })
        .catch((e) => {
          console.error(`【切换到${tab} tab API请求失败】`, e);
          console.error(`【切换到${tab} tab API请求失败】错误详情：`, e.message);
          resultListMap.value[tab] = [];
        });
    } else {
      console.log(`切换到${tab} tab没有对应的API配置`);
      resultListMap.value[tab] = [];
    }
  }
});

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

/* 天气卡片样式 */
.weather-card {
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  border-radius: 16px;
  margin-bottom: 7px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(116, 185, 255, 0.3);
  color: white;
  position: relative;
  overflow: hidden;
}

.weather-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  pointer-events: none;
}

.weather-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.weather-city {
  font-size: 20px;
  font-weight: bold;
  color: white;
}

.weather-temp {
  font-size: 32px;
  font-weight: bold;
  color: white;
}

.weather-main {
  margin-bottom: 16px;
}

.weather-condition {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.weather-desc {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.weather-details {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.weather-details span {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.1);
  padding: 4px 8px;
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

.weather-aqi {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 16px;
  backdrop-filter: blur(10px);
}

.aqi-header {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 8px;
}

.aqi-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.aqi-value {
  font-size: 24px;
  font-weight: bold;
  padding: 8px 12px;
  border-radius: 8px;
  min-width: 60px;
  text-align: center;
}

.aqi-good {
  background: #00b894;
  color: white;
}

.aqi-moderate {
  background: #fdcb6e;
  color: white;
}

.aqi-unhealthy-sensitive {
  background: #e17055;
  color: white;
}

.aqi-unhealthy {
  background: #d63031;
  color: white;
}

.aqi-very-unhealthy {
  background: #a29bfe;
  color: white;
}

.aqi-hazardous {
  background: #6c5ce7;
  color: white;
}

.aqi-level {
  font-size: 16px;
  color: white;
  font-weight: 500;
}

.weather-forecast {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 16px;
  backdrop-filter: blur(10px);
}

.forecast-header {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 12px;
}

.forecast-list {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.forecast-item {
  flex: none;
  min-width: 70px;
  text-align: center;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 8px 6px;
  backdrop-filter: blur(5px);
}

.forecast-date {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 4px;
}

.forecast-weather {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.forecast-temp {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.temp-high {
  font-size: 14px;
  font-weight: bold;
  color: white;
}

.temp-low {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.weather-source {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  display: flex;
  align-items: center;
  gap: 4px;
}

.weather-source .result-source-icon {
  filter: brightness(0) invert(1);
  opacity: 0.7;
}

/* 图片画廊样式 */
.image-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
  padding: 0;
}

.image-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  cursor: pointer;
}

.image-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}

.image-container {
  width: 100%;
  height: 150px;
  overflow: hidden;
  position: relative;
}

.gallery-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.2s ease;
}

.image-card:hover .gallery-image {
  transform: scale(1.05);
}

.image-info {
  padding: 8px 12px;
}

.image-title {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.image-source {
  font-size: 12px;
  color: #888;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 全屏图片模态框样式 */
.fullscreen-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  cursor: pointer;
}

.fullscreen-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fullscreen-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
}

.close-btn {
  position: absolute;
  top: -50px;
  right: -50px;
  background: rgba(0, 0, 0, 0.5);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s ease;
}

.close-btn:hover {
  background: rgba(0, 0, 0, 0.7);
}

.close-btn svg {
  stroke: white;
}
</style>
