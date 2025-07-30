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
          <div class="category-items" style="margin-top: 12px;">
            <div class="category-item" @click="handleFeature('图片翻译')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
              </div>
              <div class="item-label">图片翻译</div>
            </div>
          </div>
        </div>
      </div>
      <div class="category-row">
        <div class="category-box">
          <h3 class="category-title">创作</h3>
          <div class="category-items">
            <div class="category-item" @click="handleFeature('千帆视频')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 7l-7 5 7 5V7z"></path><rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect></svg>
              </div>
              <div class="item-label">千帆视频</div>
            </div>
            <div class="category-item" @click="handleFeature('AI生图')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M12 16v-4"></path><path d="M12 8h.01"></path></svg>
              </div>
              <div class="item-label">AI生图</div>
            </div>
            <div class="category-item" @click="handleFeature('播客')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18V5l12-2v13"></path><circle cx="6" cy="18" r="3"></circle><circle cx="18" cy="16" r="3"></circle></svg>
              </div>
              <div class="item-label">播客</div>
            </div>
          </div>
          <div class="category-items" style="margin-top: 12px;">
            <div class="category-item" @click="handleFeature('视频生成')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect><line x1="7" y1="2" x2="7" y2="22"></line><line x1="17" y1="2" x2="17" y2="22"></line><line x1="2" y1="12" x2="22" y2="12"></line><line x1="2" y1="7" x2="7" y2="7"></line><line x1="2" y1="17" x2="7" y2="17"></line><line x1="17" y1="17" x2="22" y2="17"></line><line x1="17" y1="7" x2="22" y2="7"></line></svg>
              </div>
              <div class="item-label">视频生成</div>
            </div>
            <div class="category-item" style="visibility: hidden;">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></svg>
              </div>
              <div class="item-label"></div>
            </div>
            <div class="category-item" style="visibility: hidden;">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></svg>
              </div>
              <div class="item-label"></div>
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
            <div class="category-item" @click="handleFeature('算命')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M12 1v6m0 6v6m11-7h-6m-6 0H1m15.5-6.5L17 7l-1.5-1.5M7 17l-1.5 1.5M17 17l1.5 1.5M7 7L5.5 5.5"></path></svg>
              </div>
              <div class="item-label">算命</div>
            </div>
            <div class="category-item" @click="handleFeature('法行宝')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8h1a4 4 0 0 1 0 8h-1"></path><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path><line x1="6" y1="1" x2="6" y2="4"></line><line x1="10" y1="1" x2="10" y2="4"></line><line x1="14" y1="1" x2="14" y2="4"></line></svg>
              </div>
              <div class="item-label">法行宝</div>
            </div>
          </div>
          <div class="category-items" style="margin-top: 12px;">
            <div class="category-item" @click="handleFeature('旅游规划')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path></svg>
              </div>
              <div class="item-label">旅游规划</div>
            </div>
            <div class="category-item" @click="handleFeature('全国物流查询')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 3h5v5M21 3l-7 7M8 3H3v5M3 3l7 7M16 21h5v-5M21 21l-7-7M8 21H3v-5M3 21l7-7"></path></svg>
              </div>
              <div class="item-label">全国物流查询<br>(阿里mcp)</div>
            </div>
            <div class="category-item" @click="handleFeature('股票实时查询')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 3h5v5M21 3l-7 7M8 3H3v5M3 3l7 7M16 21h5v-5M21 21l-7-7M8 21H3v-5M3 21l7-7"></path></svg>
              </div>
              <div class="item-label">股票实时查询<br>(阿里mcp)</div>
            </div>
          </div>
      </div>

      </div>
      
      <!-- 阿里云分类区域 -->
      <div class="category-row">
        <div class="category-box aliyun-category">
          <h3 class="category-title">阿里云</h3>
          <div class="category-items">
            <div class="category-item" @click="handleFeature('天气预报MCP')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"></path></svg>
              </div>
              <div class="item-label">天气预报MCP</div>
            </div>
            <div class="category-item" @click="handleFeature('夸克搜索MCP')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><path d="M21 21l-4.35-4.35"></path></svg>
              </div>
              <div class="item-label">夸克搜索MCP</div>
            </div>
            <div class="category-item" @click="handleFeature('VIN码车架号查询MCP')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"></path><path d="M17 17m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"></path><path d="M5 17h-2v-6l2-5h9l4 5h1a2 2 0 0 1 2 2v4h-2"></path></svg>
              </div>
              <div class="item-label">VIN码车架号查询MCP</div>
            </div>
          </div>
          <div class="category-items" style="margin-top: 12px;">
            <div class="category-item" @click="handleFeature('企业基本工商信息查询MCP')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21h18"></path><path d="M5 21V7l8-4v18"></path><path d="M19 21V11l-6-4"></path><path d="M9 9v.01"></path><path d="M9 12v.01"></path><path d="M9 15v.01"></path><path d="M9 18v.01"></path></svg>
              </div>
              <div class="item-label">企业基本工商信息查询MCP</div>
            </div>
            <div class="category-item" @click="handleFeature('汇率查询转换MCP')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M12 1v6m0 6v6"></path><path d="M21 12h-6m-6 0H3"></path></svg>
              </div>
              <div class="item-label">汇率查询转换MCP</div>
            </div>
            <div class="category-item" @click="handleFeature('商品条码查询MCP')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 5v14"></path><path d="M8 5v14"></path><path d="M12 5v14"></path><path d="M17 5v14"></path><path d="M21 5v14"></path></svg>
              </div>
              <div class="item-label">商品条码查询MCP</div>
            </div>
          </div>
          <div class="category-items" style="margin-top: 12px;">
            <div class="category-item" @click="handleFeature('墨迹天气MCP')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"></path><path d="M16 14l-2-2-2 2"></path></svg>
              </div>
              <div class="item-label">墨迹天气MCP</div>
            </div>
            <div class="category-item" @click="handleFeature('发票真伪查询MCP')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline><path d="M9 5l2 2 4-4"></path></svg>
              </div>
              <div class="item-label">发票真伪查询MCP</div>
            </div>
            <div class="category-item" @click="handleFeature('ISBN书号查询MCP')">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
              </div>
              <div class="item-label">ISBN书号查询MCP</div>
            </div>
          </div>
        </div>
        <div class="category-box">
          <h3 class="category-title">更多功能</h3>
          <div class="category-items">
            <div class="category-item" style="visibility: hidden;">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></svg>
              </div>
              <div class="item-label"></div>
            </div>
            <div class="category-item" style="visibility: hidden;">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></svg>
              </div>
              <div class="item-label"></div>
            </div>
            <div class="category-item" style="visibility: hidden;">
              <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></svg>
              </div>
              <div class="item-label"></div>
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
    name: '高级搜索结果', // 跳转到AdvancedResultView界面
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
  
  // 拍照搜题功能跳转到OCR页面
  if (feature === '拍照搜题') {
    router.push({
      name: 'ocr'
    });
  } else if (feature === '旅游规划') {
    // 旅游规划功能跳转到旅游页面
    router.push('/travel');
  } else if (feature === '视频生成') {
    // 视频生成功能跳转到视频生成页面
    router.push('/video');
  } else if (feature === '播客') {
    // 播客功能跳转到播客页面
    router.push('/podcast');
  } else if (feature === '算命') {
    // 算命功能跳转到算命页面
    router.push('/fortune');
  } else if (feature === '全国物流查询') {
    // 全国物流查询功能跳转到指定页面
    router.push('/quanguo-kuaidi-wuliu-mcp');
  } else if (feature === '股票实时查询') {
    // 股票实时查询功能跳转到指定页面
    router.push('/aliyun-mcp-stocks');
  } else if (feature === '天气预报MCP') {
    // 天气预报MCP功能跳转到指定页面
    router.push('/aliyun-mcp-weather');
  } else if (feature === '夸克搜索MCP') {
    // 夸克搜索MCP功能跳转到指定页面
    router.push('/aliyun-mcp-quark-search');
  } else if (feature === 'VIN码车架号查询MCP') {
    // VIN码车架号查询MCP功能跳转到指定页面
    router.push('/aliyun-mcp-vin');
  } else if (feature === '企业基本工商信息查询MCP') {
    // 企业基本工商信息查询MCP功能跳转到指定页面
    router.push('/aliyun-mcp-company-info');
  } else if (feature === '汇率查询转换MCP') {
    // 汇率查询转换MCP功能跳转到指定页面
    router.push('/aliyun-mcp-exchange-rate');
  } else if (feature === '商品条码查询MCP') {
    // 商品条码查询MCP功能跳转到指定页面
    router.push('/aliyun-mcp-barcode');
  } else if (feature === '墨迹天气MCP') {
    // 墨迹天气MCP功能跳转到指定页面
    router.push('/aliyun-mcp-moji-weather');
  } else if (feature === '发票真伪查询MCP') {
    // 发票真伪查询MCP功能跳转到指定页面
    router.push('/aliyun-mcp-invoice-checker');
  } else if (feature === 'ISBN书号查询MCP') {
    // ISBN书号查询MCP功能跳转到指定页面
    router.push('/aliyun-mcp-isbn');
  } else if (feature === '图片翻译'){
    // 图片翻译功能跳转至图片翻译界面
    router.push('/pic-translate');
  } else if (feature === 'AI生图') {
    // AI生图功能跳转到图像生成页面
    router.push('/image');
  } else if (feature === '千帆视频') {
    // 千帆视频功能跳转到千帆页面
    router.push('/qianfan');
  } else if (feature === '法行宝') {
    // 百度法行宝功能跳转至百度法行宝界面
    router.push('/baidu-faxingbao');
  } else {
    // 其他功能正常跳转到结果页
    router.push({
      name: '高级搜索结果', // 跳转到AdvancedResultView界面
      query: { 
        query: feature, // 将被点中项的内容设置给query
        isdeep: false // isdeep为false
      }
    });
  }
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

/* 阿里云分类特殊样式 */
.aliyun-category {
  background: linear-gradient(135deg, #ff6a00 0%, #ff8533 100%);
  border: 1px solid #ff6a00;
  color: white;
}

.aliyun-category .category-title {
  color: white;
  font-weight: 600;
}

.aliyun-category .item-label {
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.aliyun-category .item-icon {
  color: white;
}

.aliyun-category .category-item:hover .item-icon {
  transform: scale(1.1);
  transition: transform 0.2s ease;
}

.aliyun-category .category-item:hover .item-label {
  color: white;
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
