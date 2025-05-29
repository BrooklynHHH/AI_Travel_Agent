<template>
  <div class="travel-container">
    <!-- 浮层组件11111222222333333333444444-->
    <ImageViewer
      v-model:show="showImageViewer"
      :images="viewerImages"
      v-model:currentIndex="currentImageIndex"
      :keyword="currentImageKeyword"
    />
    <ProductWindow
      v-model:show="showProductWindow"
      :productName="productName"
      :productUrl="productUrl"
      v-model:isFullscreen="isFullscreen"
      v-model:windowHeight="windowHeight"
      :isLoading="isLoading"
      :iframeKey="iframeKey"
      @iframe-load="onIframeLoad"
    />
    <SettingsModal
      v-model:show="showSettingsModal"
      :apiKey="apiKeyInput"
      @save="saveApiKey"
    />

    <!-- Progress bar (visible when loading) -->
    <div v-if="isLoading" class="progress-container top-progress">
      <div class="progress-bar"></div>
    </div>
    
    <!-- Mobile header -->
    <div class="mobile-header">
      <div class="status-bar">
        <div class="time">{{ currentTime }}</div>
        <div class="status-icons">
          <span class="signal">●●●●</span>
          <span class="wifi">●</span>
          <span class="battery">●</span>
        </div>
      </div>
      <div class="travel-header">
        <div class="back-button" @click="goBack">
          <i class="back-icon">←</i>
        </div>
        <div class="header-title">小米AI搜索</div>
        <div class="more-button">
          <i class="more-icon">⋮</i>
        </div>
      </div>
    </div>

    <!-- Settings Button -->
    <button class="settings-button" @click="openSettingsModal">
      <span class="settings-icon">⚙️</span>
    </button>
    
    <!-- Travel content -->
    <div class="travel-content" ref="travelContent">

      <!-- Generation Phases (always shown when available) -->
      <div v-if="generationPhases.length > 0 || isLoading" class="generation-phases-container">
        <div class="generation-phases">
          <!-- Loading spinner (integrated with thinking container) -->
          <div v-if="isLoading" class="thinking-container loading-active">
            <div class="thinking-header">
              <div class="thinking-icon">🧠</div>
              <div class="thinking-title">正在为您生成行程规划...</div>
              <div class="loading-spinner-small"></div>
            </div>
          </div>
          
          <!-- Regular thinking container when not loading -->
          <div v-else class="thinking-container" @click="toggleThinkingExpanded">
            <div class="thinking-header">
              <div class="thinking-icon">🧠</div>
              <div class="thinking-title">思考中...</div>
              <div class="thinking-expand-icon">{{ isThinkingExpanded ? '▼' : '▶' }}</div>
            </div>
          </div>
          
          <!-- 展开的思考内容 -->
          <div v-if="isThinkingExpanded" class="thinking-content">
            <!-- 景点讲解内容 -->
            <div 
              v-for="(phase, index) in filteredPhases" 
              :key="index" 
              class="phase-container" 
              :class="{ 'important-phase': phase.isImportant, 'active-phase': currentPhase === phase.phase, 'explain-site-phase': phase.phase === 'explain_site' }"
            >
              <div class="phase-header" @click="togglePhaseExpanded(phase.phase)">
                <div class="phase-title">{{ getPhaseDisplayName(phase.phase) }}</div>
                <div class="phase-status-indicator" v-if="currentPhase === phase.phase">
                  <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
                <div class="phase-expand-icon">{{ expandedPhases.includes(phase.phase) ? '▼' : '▶' }}</div>
              </div>
              <div v-if="expandedPhases.includes(phase.phase)" class="phase-content">
                <div v-if="phase.phase === 'json_search'" class="search-terms-container">
                  <div v-for="(term, termIndex) in formatSearchTerms(phase.content)" :key="termIndex" class="search-term-item">
                    {{ term }}
                  </div>
                </div>
                <div v-else-if="phase.phase === 'title_summary'" class="search-results-container">
                  <div v-for="(result, resultIndex) in formatSearchResults(phase.content)" :key="resultIndex" class="search-result-item">
                    <a :href="result.url" target="_blank" class="search-result-link">{{ result.title }}</a>
                  </div>
                </div>
                <div v-else-if="phase.phase === 'site_name_address_description'" class="tour-guide-container site-summary-container">
                  <div class="tour-guide-header">
                    <div class="tour-guide-icon">🏞️</div>
                    <div class="tour-guide-title">景点总结</div>
                  </div>
                  <div class="tour-guide-content">
                    <div class="tour-guide-messages">
                      <div v-for="(message, msgIndex) in tourGuideMessages" :key="msgIndex" class="message-wrapper">
                        <!-- User message -->
                        <div v-if="message.role === 'user'" class="message-container user-message">
                          <div class="message-bubble">
                            {{ message.content }}
                          </div>
                        </div>
                        <!-- Bot message -->
                        <div v-else-if="message.role === 'assistant'" class="message-container bot-message">
                          <div class="mi-logo">
                            <div class="mi-logo-text">MI</div>
                          </div>
                          <div class="message-bubble main-response">
                            <div v-if="message.streaming" class="response-text">
                              <div v-html="renderMarkdown(message.content)"></div><span class="cursor">|</span>
                            </div>
                            <div v-else class="response-text" v-html="renderMarkdown(message.content)"></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <pre v-else>{{ phase.content }}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Site details section (shown when site details are available) -->
      <div v-if="siteDetails.length > 0" class="site-details-section">
        <h2>为您选择了以下景点</h2>
        <div class="site-cards-grid">
          <div 
            v-for="(site, index) in siteDetails" 
            :key="index"
            class="site-card"
          >
            <div class="site-header">
              <div class="site-name">{{ site.name }}</div>
            </div>
            <div class="site-photos" v-if="getSitePhotos(site.name).length > 0">
              <div class="site-photos-grid">
                <div 
                  v-for="(photo, photoIndex) in getSitePhotos(site.name)" 
                  :key="photoIndex"
                  class="site-photo"
                  @click="openImageViewer(getSitePhotos(site.name), photoIndex, site.name)"
                >
                  <img :src="photo" alt="景点照片" />
                </div>
              </div>
            </div>
            <div class="site-details-content">
              <div class="site-address">
                <span class="detail-label">地址：</span>{{ site.address }}
              </div>
              <div class="site-description scrollable-content">
                <span class="detail-label">描述：</span>{{ site.description }}
              </div>
              <div class="site-tags">
                <span 
                  v-for="(tag, tagIndex) in site.source_keywords" 
                  :key="tagIndex"
                  class="site-tag"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Results area (shown when day plan is available) -->
      <div v-if="dayPlan" class="results-container">
        <h2>为您制定了以下旅游规划</h2>
        <!-- Day plan tabs -->
        <div class="day-tabs">
        <button 
          v-for="(day, index) in dayPlanKeys" 
          :key="index"
          class="day-tab-button"
          :class="{ 'active': selectedDay === day }"
          @click="selectDay(day)"
        >
          {{ day.replace('Day_', '第') }}天
        </button>
        <button 
          v-if="currentDayPlan && currentDayPlan.attractions && currentDayPlan.attractions.length > 1"
          class="map-button"
          @click="showRouteMap()"
        >
          查看地图路线
        </button>
        </div>
        
      <!-- 地图容器 -->
      <div id="map-container" v-show="showMap" class="map-container">
        <div id="container"></div>
        <div id="panel"></div>
        <button class="close-map-button" @click="closeMap">关闭地图</button>
      </div>

      <!-- Selected day plan -->
      <div class="day-plan-container">
          <div class="day-plan-header">
            <h2>{{ selectedDay.replace('Day_', '第') }}天 - {{ currentDayPlan.theme_or_area }}</h2>
            <div class="day-time-info">
              <div class="time-item">
                <span class="time-label">景点游览时间：</span>
                <span class="time-value">{{ formatMinutes(currentDayPlan.estimated_attraction_time_minutes) }}</span>
              </div>
              <div class="time-item">
                <span class="time-label">交通时间：</span>
                <span class="time-value">{{ formatMinutes(currentDayPlan.estimated_travel_time_minutes) }}</span>
              </div>
            </div>
          </div>
          
          <!-- Activities for the day -->
          <div class="activities-container">
            <div 
              v-for="(activity, index) in currentDayPlan.attractions" 
              :key="index" 
              class="activity-item"
              @click="showSiteDetail(activity.site_name)"
            >
              <div class="activity-number">{{ index + 1 }}</div>
              <div class="activity-content">
                <div class="activity-details">
                  <div class="activity-name">{{ activity.site_name }}</div>
                  <div class="activity-time">游览时间: {{ formatMinutes(activity.estimated_visit_duration_minutes) }}</div>
                </div>
                <div v-if="activity.travel_to_next_minutes" class="travel-info">
                  <div class="travel-time">{{ formatMinutes(activity.travel_to_next_minutes) }}</div>
                  <div class="travel-arrow">↓</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Reason for the plan -->
          <div class="plan-reason">
            <div class="reason-header">行程安排理由</div>
            <div class="reason-content">{{ currentDayPlan.day_reasoning }}</div>
          </div>
        </div>
      </div>

      <!-- Empty state (when no search has been performed) -->
      <div v-if="!dayPlan && !siteDetails.length && !isLoading" class="empty-state">
        <div class="empty-state-icon">🧭</div>
        <h3>开启您的专属旅程</h3>
        <p>告诉我您的旅行偏好,我将为您量身定制完美行程。</p>
        <div class="suggestion-chips">
          <button class="suggestion-chip" @click="useSearchSuggestion('南京三日游之特种兵版')">南京三日游之特种兵版</button>
          <button class="suggestion-chip" @click="useSearchSuggestion('杭州亲子游')">杭州亲子游</button>
          <button class="suggestion-chip" @click="useSearchSuggestion('北京五日游')">北京五日游</button>
          <button class="suggestion-chip" @click="useSearchSuggestion('云南七日游')">云南七日游</button>
        </div>
      </div>
      
      <!-- Trip Planning Overview Section -->
      <div v-if="dayPlan && !isLoading" class="trip-overview-section">
        <h2>行程规划概览</h2>
        <div class="trip-overview-card" @click="toggleTripDetails">
          <div class="overview-header">
            <div class="overview-title">{{ dayPlan.trip_name || userInput }}</div>
            <div class="overview-expand-icon">{{ showTripDetails ? '▼' : '▶' }}</div>
          </div>
          
          <div class="overview-summary">
            <div class="overview-item">
              <div class="overview-icon">📅</div>
              <div class="overview-text">总天数: <span>{{ dayPlanKeys.length }}</span>天</div>
            </div>
            <div class="overview-item">
              <div class="overview-icon">🕒</div>
              <div class="overview-text">总游览时间: <span>{{ formatMinutes(totalTripTime) }}</span></div>
            </div>
            <div class="overview-item">
              <div class="overview-icon">🏞️</div>
              <div class="overview-text">景点数量: <span>{{ totalAttractions }}</span>个</div>
            </div>
          </div>
          
          <div v-if="showTripDetails" class="trip-details">
            <div 
              v-for="(day, index) in dayPlanKeys" 
              :key="index"
              class="trip-day-item"
            >
              <div class="trip-day-header">
                <div class="trip-day-title">{{ day.replace('Day_', '第') }}天 - {{ dayPlan.daily_itinerary[day].theme_or_area }}</div>
                <div class="trip-day-time">{{ formatMinutes(dayPlan.daily_itinerary[day].estimated_attraction_time_minutes) }}</div>
              </div>
              
              <div class="trip-day-attractions">
                <div 
                  v-for="(attraction, attrIndex) in dayPlan.daily_itinerary[day].attractions" 
                  :key="attrIndex"
                  class="trip-attraction-item"
                >
                  <div class="attraction-bullet">•</div>
                  <div class="attraction-name">{{ attraction.site_name }}</div>
                  <div class="attraction-time">{{ formatMinutes(attraction.estimated_visit_duration_minutes) }}</div>
                </div>
              </div>
              
              <div class="trip-day-reasoning">
                <div class="reasoning-label">安排理由:</div>
                <div class="reasoning-text">{{ dayPlan.daily_itinerary[day].day_reasoning }}</div>
              </div>
              
              <div v-if="index < dayPlanKeys.length - 1" class="trip-day-divider"></div>
            </div>
          </div>
        </div>
      </div>
    </div>


    <!-- Fixed search input at bottom -->
    <div class="fixed-search-container">
      <div class="search-input-wrapper">
        <input 
          type="text" 
          placeholder="南京有什么好玩的地方" 
          v-model="userInput"
          @keyup.enter="generateTravelPlan"
        />
        <button class="search-button" @click="generateTravelPlan">
          <span class="search-icon">🔍</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed, watch, onBeforeUnmount } from 'vue';
import ImageViewer from '../components/modals/ImageViewer.vue';
import ProductWindow from '../components/modals/ProductWindow.vue';
import SettingsModal from '../components/modals/SettingsModal.vue';
import { handleStreamingResponse } from '../utils/streamUtils';
import MarkdownIt from 'markdown-it';

// Initialize markdown-it renderer
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true
});

// Markdown renderer function
const renderMarkdown = (content) => {
  if (!content) return '';
  return md.render(content);
};

// Dify Workflow Client class
class DifyWorkflowClient {
  constructor(apiKey, baseUrl = "https://mify-be.pt.xiaomi.com/api/v1") {
    if (!apiKey) {
      throw new Error("API Key 不能为空");
    }
    console.log(`创建DifyWorkflowClient，API密钥: ${apiKey.substring(0, 8)}...，baseUrl: ${baseUrl}`);
    this.apiKey = apiKey;
    this.baseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
    this.headers = {
      "Authorization": `Bearer ${this.apiKey}`,
      "Content-Type": "application/json"
    };
  }

  async runWorkflow(inputs, user, responseMode = "blocking") {
    const endpoint = "/workflows/run";
    const payload = {
      inputs,
      response_mode: responseMode,
      user
    };

    console.log(`准备调用工作流，endpoint: ${this.baseUrl}${endpoint}，payload:`, JSON.stringify(payload).substring(0, 100) + "...");

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: "POST",
        headers: this.headers,
        body: JSON.stringify(payload)
      });

      console.log(`收到响应，状态码: ${response.status}`);

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`API错误: ${response.status} - ${errorText}`);
        throw new Error(`API error: ${response.status} - ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("工作流调用失败:", error);
      throw error;
    }
  }
  
  async runWorkflowStreaming(inputs, user, onUpdate) {
    const endpoint = "/workflows/run";
    const payload = {
      inputs,
      response_mode: "streaming",
      user
    };

    console.log(`准备调用流式工作流，endpoint: ${this.baseUrl}${endpoint}，payload:`, JSON.stringify(payload).substring(0, 100) + "...");

    try {
      console.log("发送请求...");
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: "POST",
        headers: this.headers,
        body: JSON.stringify(payload)
      });

      console.log(`收到响应，状态码: ${response.status}`);

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`API错误: ${response.status} - ${errorText}`);
        throw new Error(`API error: ${response.status} - ${errorText}`);
      }

      // 手动处理流
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let result = { data: { outputs: {} } };
      
      // 用于跟踪当前正在生成的阶段
      let currentPhase = null;
      const phaseContent = {};
      
      // 关注的特定节点类型
      const importantNodeTypes = [
        "json_search", 
        "title_summary",
        "site_name_address_description",
        "get_photos", 
        "day_plan"
      ];

      let isReading = true;
      while (isReading) {
        const { done, value } = await reader.read();
        if (done) {
          isReading = false;
          break;
        }
        
        buffer += decoder.decode(value, { stream: true });
        
        // 处理完整的 JSON 对象
        let boundary = 0;
        while (boundary !== -1) {
          // 查找 "data: " 前缀
          const dataPrefix = "data: ";
          const dataStart = buffer.indexOf(dataPrefix, boundary);
          if (dataStart === -1) break;
          
          // 查找消息结束的双换行符
          const messageEnd = buffer.indexOf("\n\n", dataStart);
          if (messageEnd === -1) break;
          
          // 提取 JSON 数据
          const jsonStart = dataStart + dataPrefix.length;
          const jsonData = buffer.substring(jsonStart, messageEnd).trim();
          
          // 更新 buffer
          buffer = buffer.substring(messageEnd + 2);
          boundary = 0;
          
          if (!jsonData) continue;
          if (jsonData === "event: ping") continue; // 忽略心跳事件
          
          try {
            const data = JSON.parse(jsonData);
            console.log('Stream Event:', data);
            
            // 处理不同类型的事件
            if (data.event === 'workflow_started') {
              // 工作流开始
              if (onUpdate) {
                onUpdate({
                  event: 'workflow_started',
                  data: { 
                    outputs: { 
                      current_step: '初始化工作流' 
                    } 
                  }
                });
              }
            } else if (data.event === 'node_started') {
              // 节点开始执行
              const nodeTitle = data.data?.title || '执行节点';
              currentPhase = nodeTitle;
              
              // 初始化当前阶段的内容
              if (!phaseContent[currentPhase]) {
                phaseContent[currentPhase] = '';
              }
              
              if (onUpdate) {
                onUpdate({
                  event: 'node_started',
                  data: { 
                    outputs: { 
                      current_step: currentPhase,
                      generation_phases: Object.entries(phaseContent).map(([phase, content]) => ({
                        phase,
                        content,
                        isImportant: importantNodeTypes.includes(phase)
                      }))
                    } 
                  }
                });
              }
            } else if (data.event === 'text_chunk') {
              // 文本块事件，包含生成的内容
              if (currentPhase && data.data && data.data.text) {
                // 将文本块添加到当前阶段的内容中
                phaseContent[currentPhase] += data.data.text;
                
                // 特殊处理day_plan节点，尝试提取JSON内容
                if (currentPhase === "day_plan") {
                  // 尝试检测是否已经接收到完整的JSON
                  const jsonMatch = phaseContent[currentPhase].match(/```json\n([\s\S]*?)\n```/);
                  if (jsonMatch && jsonMatch[1]) {
                    try {
                      // 尝试解析JSON以验证完整性
                      JSON.parse(jsonMatch[1]); // 只验证JSON是否有效，不需要存储结果
                      // 如果解析成功，可以提前更新dayplan
                      if (onUpdate) {
                        onUpdate({
                          event: 'text_chunk',
                          data: { 
                            outputs: { 
                              current_step: currentPhase,
                              generation_phases: Object.entries(phaseContent).map(([phase, content]) => ({
                                phase,
                                content,
                                isImportant: importantNodeTypes.includes(phase)
                              })),
                              dayplan: phaseContent[currentPhase]
                            } 
                          }
                        });
                      }
                      continue;
                    } catch (e) {
                      // JSON不完整，继续接收
                    }
                  }
                }
                
                if (onUpdate) {
                  onUpdate({
                    event: 'text_chunk',
                    data: { 
                      outputs: { 
                        current_step: currentPhase,
                        generation_phases: Object.entries(phaseContent).map(([phase, content]) => ({
                          phase,
                          content,
                          isImportant: importantNodeTypes.includes(phase)
                        }))
                      } 
                    }
                  });
                }
              }
            } else if (data.event === 'node_finished') {
              // 节点执行完成
              const nodeTitle = data.data?.title || currentPhase;
              
              // 检查是否是重要节点
              const isImportantNode = importantNodeTypes.includes(nodeTitle);
              
              if (data.data && data.data.outputs) {
                // 合并节点输出到结果中
                result.data.outputs = { ...result.data.outputs, ...data.data.outputs };
                
                // 如果是重要节点，保存其输出内容
                if (isImportantNode && data.data.outputs) {
              // 处理特定节点的输出
              if (nodeTitle === "site_name_address_description" && data.data.outputs.site_detail) {
                // 景点详情节点，保存景点信息
                phaseContent[nodeTitle] = JSON.stringify(data.data.outputs.site_detail, null, 2);
              } else if (nodeTitle === "day_plan" && data.data.outputs.dayplan) {
                // 行程规划节点，保存行程信息
                phaseContent[nodeTitle] = data.data.outputs.dayplan;
              } else if (nodeTitle === "title_summary" && data.data.outputs.show_content) {
                // 检索结果列表，累积所有迭代的结果
                if (!phaseContent[nodeTitle]) {
                  phaseContent[nodeTitle] = JSON.stringify(data.data.outputs.show_content, null, 2);
                } else {
                  // 尝试合并当前结果与之前的结果
                  try {
                    const existingResults = JSON.parse(phaseContent[nodeTitle]);
                    const newResults = data.data.outputs.show_content;
                    // 合并结果并去重
                    const mergedResults = [...existingResults, ...newResults].filter((item, index, self) => 
                      index === self.findIndex(t => t.title === item.title && t.url === item.url)
                    );
                    phaseContent[nodeTitle] = JSON.stringify(mergedResults, null, 2);
                  } catch (e) {
                    // 如果解析失败，直接追加
                    phaseContent[nodeTitle] += "\n" + JSON.stringify(data.data.outputs.show_content, null, 2);
                  }
                }
              } else {
                // 其他节点，将输出转换为字符串
                const outputContent = JSON.stringify(data.data.outputs, null, 2);
                if (!phaseContent[nodeTitle]) {
                  phaseContent[nodeTitle] = outputContent;
                } else {
                  phaseContent[nodeTitle] += "\n" + outputContent;
                }
              }
                }
                
                // 添加生成阶段信息
                result.data.outputs.generation_phases = Object.entries(phaseContent).map(([phase, content]) => ({
                  phase,
                  content,
                  isImportant: importantNodeTypes.includes(phase)
                }));
                
                if (onUpdate) {
                  onUpdate({
                    event: 'node_finished',
                    data: { outputs: result.data.outputs }
                  });
                }
              }
              
              // 重置当前阶段，但保留内容
              if (currentPhase === nodeTitle) {
                currentPhase = null;
              }
            } else if (data.event === 'workflow_finished') {
              // 工作流完成
              if (data.data && data.data.outputs) {
                result.data.outputs = { ...result.data.outputs, ...data.data.outputs };
                
                // 添加生成阶段信息
                result.data.outputs.generation_phases = Object.entries(phaseContent).map(([phase, content]) => ({
                  phase,
                  content,
                  isImportant: importantNodeTypes.includes(phase)
                }));
              }
              isReading = false;
            } else if (data.event === 'ping') {
              // 心跳事件，忽略
            }
          } catch (e) {
            console.error('Error parsing streaming chunk:', e, jsonData);
          }
        }
      }
      
      return result;
    } catch (error) {
      console.error("Workflow streaming failed:", error);
      throw error;
    }
  }
}

// 地图相关状态
const showMap = ref(false);
const mapInitialized = ref(false);

// User input for search
const userInput = ref('');
const headerTitle = ref('旅行规划助手');

// Day plan data
const dayPlan = ref(null);
const siteDetails = ref([]);
const sitePhotos = ref([]);

// Product window state
const showProductWindow = ref(false);
const productName = ref('');
const productUrl = ref('');
const isFullscreen = ref(false);
const windowHeight = ref(50); // Default height is 50%
const iframeKey = ref(0); // 用于强制重新加载iframe
const isLoading = ref(false); // 加载状态

// iframe加载事件处理
const onIframeLoad = () => {
  console.log('Iframe加载完成');
  isLoading.value = false;
};

/** 浮层图片查看器状态 */
const showImageViewer = ref(false);
const viewerImages = ref([]);
const currentImageIndex = ref(0);
const currentImageKeyword = ref('');

// Settings state
const showSettingsModal = ref(false);
const apiKeyInput = ref('');

// Settings functions
const openSettingsModal = () => {
  // Load existing API key from cookie if available
  const savedApiKey = getCookie('api_key');
  if (savedApiKey) {
    apiKeyInput.value = savedApiKey;
  } else {
    // Set default API key if none is saved
    apiKeyInput.value = 'app-6dBwf3lXyFG7jNLFJpSA7deK';          
  }
  showSettingsModal.value = true;
};

const saveApiKey = () => {
  // Validate the API key format (app-xxxx or abc-123)
  if (!apiKeyInput.value || !apiKeyInput.value.match(/^(app|abc)-[a-zA-Z0-9]+$/)) {
    alert('请输入正确格式的API Key (例如: abc-123)');
    return;
  }
  
  // Save to cookie
  setCookie('api_key', apiKeyInput.value);
  
  // Close the settings modal
  showSettingsModal.value = false;
  
  // Provide feedback to user
  alert('API Key 已保存');
};

// Cookie utility functions
const setCookie = (name, value, days = 365) => {
  const d = new Date();
  d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
  const expires = "expires=" + d.toUTCString();
  document.cookie = name + "=" + value + ";" + expires + ";path=/";
};

const getCookie = (name) => {
  const cookieName = name + "=";
  const decodedCookie = decodeURIComponent(document.cookie);
  const cookieArray = decodedCookie.split(';');
  
  for (let i = 0; i < cookieArray.length; i++) {
    let cookie = cookieArray[i].trim();
    if (cookie.indexOf(cookieName) === 0) {
      return cookie.substring(cookieName.length, cookie.length);
    }
  }
  return "";
};

// Data
const currentTime = ref('');
const travelContent = ref(null);
const expandedSites = ref([]);
const showTripDetails = ref(false);
const streamingSteps = ref([]);
const generationPhases = ref([]);
const currentPhase = ref('');
const isThinkingExpanded = ref(true); // 默认展开思考内容
const expandedPhases = ref([]); // 跟踪哪些阶段是展开的

// Tour guide messages
const tourGuideMessages = ref([]);
const tourGuideLoading = ref(false);
const tourGuideStreaming = ref(false);
const tourGuideStreamingMessage = ref('');
const tourGuideGenerated = ref(false); // 添加标志变量，确保景点总结只生成一次

// 滚动到消息底部
const scrollToBottom = () => {
  const tourGuideMessagesEl = document.querySelector('.tour-guide-messages');
  if (tourGuideMessagesEl) {
    tourGuideMessagesEl.scrollTop = tourGuideMessagesEl.scrollHeight;
  }
};

// Generate tour guide content
const generateTourGuide = async (siteContent) => {
  // 如果已经生成过或正在加载中，则不再重复生成
  if (tourGuideLoading.value || tourGuideGenerated.value) return;
  
  try {
    // Set loading state
    tourGuideLoading.value = true;
    tourGuideStreamingMessage.value = '';
    
    // Create placeholder for assistant response
    const lastIndex = tourGuideMessages.value.push({
      role: 'assistant',
      content: '',
      streaming: true
    }) - 1;
    
    // Set streaming state to true
    tourGuideStreaming.value = true;
    
    // Call Xiaomi API
    const url = 'https://mify-be.pt.xiaomi.com/api/v1/chat-messages';
    
    const headers = {
      'Authorization': 'Bearer app-fgOwYlqI5vQGTiMgEYH8CRkX',
      'Content-Type': 'application/json'
    };
    
    const body = {
      inputs: {},
      query: siteContent, // 直接使用siteDetails的JSON字符串
      response_mode: "streaming",
      user: "test-user"
    };
    
    // Use fetch with streaming
    const response = await fetch(url, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(body)
    });
    
    // Use streamUtils to handle the streaming response
    await handleStreamingResponse(response, {
      debug: true,
      onStart: () => {
        console.log('Tour guide streaming response started');
      },
      onData: (data) => {
        // Handle message event (contains answer content)
        if (data.event === "message" && data.answer) {
          let newContent = data.answer;
          
          // Add the new content to the streaming message
          tourGuideStreamingMessage.value += newContent;
          
          // Update the message content
          tourGuideMessages.value[lastIndex].content = tourGuideStreamingMessage.value;
          
          // Scroll to bottom with new content
          nextTick(() => {
            scrollToBottom();
          });
        }
      },
      onComplete: () => {
        console.log('Tour guide streaming response completed');
        
        // Mark streaming as complete
        tourGuideMessages.value[lastIndex].streaming = false;
        
        // Set streaming state to false
        tourGuideStreaming.value = false;
        
        // 标记为已生成，避免重复生成
        tourGuideGenerated.value = true;
      },
      onError: (error) => {
        console.error('Tour guide streaming error:', error);
      },
      // Define events that should end the stream
      endEvents: ['workflow_finished']
    });
    
  } catch (error) {
    console.error('Error generating tour guide:', error);
    
    // Remove the streaming message placeholder
    if (tourGuideMessages.value.length > 0 && tourGuideMessages.value[tourGuideMessages.value.length - 1].streaming) {
      tourGuideMessages.value.pop();
    }
    
    // Add error message
    tourGuideMessages.value.push({
      role: 'assistant',
      content: '抱歉，我遇到了一些问题，无法生成景点讲解。',
      error: true
    });
    
  } finally {
    // Reset loading and streaming states
    tourGuideLoading.value = false;
    tourGuideStreaming.value = false;
    
    // Scroll to bottom
    nextTick(() => {
      scrollToBottom();
    });
  }
};

// 切换思考容器的展开/折叠状态
const toggleThinkingExpanded = () => {
  isThinkingExpanded.value = !isThinkingExpanded.value;
};

// 切换单个阶段的展开/折叠状态
const togglePhaseExpanded = (phaseName) => {
  if (expandedPhases.value.includes(phaseName)) {
    // 如果已经展开，则折叠
    expandedPhases.value = expandedPhases.value.filter(p => p !== phaseName);
  } else {
    // 如果已经折叠，则展开
    expandedPhases.value.push(phaseName);
  }
};

// Parse dayplan data from API response
const parseDayPlan = (data) => {
  try {
    // Extract dayplan from the response
    if (data && data.dayplan) {
      // The dayplan is a string containing JSON, so we need to parse it
      const dayplanStr = data.dayplan;
      // Extract the JSON part from the markdown code block
      const jsonMatch = dayplanStr.match(/```json\n([\s\S]*?)\n```/);
      if (jsonMatch && jsonMatch[1]) {
        return JSON.parse(jsonMatch[1]);
      } else {
        // 尝试直接解析，可能是纯JSON字符串
        try {
          return JSON.parse(dayplanStr);
        } catch (e) {
          console.error('Failed to parse dayplan as direct JSON:', e);
        }
      }
    }
    return null;
  } catch (error) {
    console.error('Error parsing dayplan data:', error);
    return null;
  }
};

// Format minutes to hours and minutes
const formatMinutes = (minutes) => {
  if (!minutes) return '0分钟';
  
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  
  if (hours > 0) {
    return `${hours}小时${mins > 0 ? ` ${mins}分钟` : ''}`;
  } else {
    return `${mins}分钟`;
  }
};

// Generate travel plan
const generateTravelPlan = async () => {
  if (!userInput.value.trim() || isLoading.value) return;
  
  // Reset data
  dayPlan.value = null;
  siteDetails.value = [];
  sitePhotos.value = [];
  streamingSteps.value = [];
  tourGuideMessages.value = []; // 清空景点讲解消息
  tourGuideGenerated.value = false; // 重置景点讲解生成标志
  
  // Set loading state
  isLoading.value = true;
  headerTitle.value = userInput.value;
  
  // 添加初始加载消息
  streamingSteps.value.push('正在开始生成行程规划...');
  
  try {
    console.log('开始生成旅行计划，用户输入:', userInput.value);
    
    // Get API key from cookie or use default
    const savedApiKey = getCookie('api_key') || 'app-6dBwf3lXyFG7jNLFJpSA7deK';
    console.log('使用API密钥:', savedApiKey);
    
    // Create client
    const client = new DifyWorkflowClient(savedApiKey);
    
    // Generate a unique user ID for this session
    const userId = "user-" + Math.random().toString(36).substring(2, 10);
    console.log('生成用户ID:', userId);
    
    
    console.log('开始调用travel_V2工作流...');
    
    // Call API with streaming mode
    await client.runWorkflowStreaming(
      { user_question: userInput.value },
      userId,
      (partialResponse) => {
        console.log('收到部分响应:', partialResponse.event);
        // Process partial response
        if (partialResponse && partialResponse.data && partialResponse.data.outputs) {
          const outputs = partialResponse.data.outputs;
          console.log('Partial response:', outputs);
          
          // 添加流式步骤消息
          if (outputs.current_step && outputs.current_step !== currentPhase.value) {
            streamingSteps.value.push(`正在${outputs.current_step}...`);
          }
          
          // Update current phase
          if (outputs.current_step) {
            currentPhase.value = outputs.current_step;
          }
          
// Process generation phases if available
if (outputs.generation_phases && Array.isArray(outputs.generation_phases)) {
  generationPhases.value = outputs.generation_phases;
  console.log('Generation phases:', generationPhases.value);
  
  // 自动展开explain_site节点
  const explainSitePhase = outputs.generation_phases.find(phase => phase.phase === 'explain_site');
  if (explainSitePhase && !expandedPhases.value.includes('explain_site')) {
    expandedPhases.value.push('explain_site');
  }
  
  // 自动展开site_name_address_description节点
  const siteDetailPhase = outputs.generation_phases.find(phase => phase.phase === 'site_name_address_description');
  if (siteDetailPhase && !expandedPhases.value.includes('site_name_address_description')) {
    expandedPhases.value.push('site_name_address_description');
  }
  
  // 不再自动展开阶段，让用户手动点击展开
  // 只有当阶段不是json_search或title_summary时才自动展开
  const importantPhases = outputs.generation_phases.filter(phase => 
    phase.isImportant && 
    phase.phase !== 'json_search' && 
    phase.phase !== 'title_summary' &&
    phase.phase !== 'explain_site' && // 已经单独处理了explain_site
    phase.phase !== 'site_name_address_description' // 已经单独处理了site_name_address_description
  );
  
  if (importantPhases.length > 0 && !expandedPhases.value.includes(importantPhases[0].phase)) {
    expandedPhases.value.push(importantPhases[0].phase);
  }
}
          
// Parse dayplan data if available
if (outputs.dayplan) {
  const parsedDayPlan = parseDayPlan(outputs);
  if (parsedDayPlan) {
    dayPlan.value = parsedDayPlan;
    console.log('Parsed day plan (partial):', dayPlan.value);
    
    // 设置默认选中的天数
    if (dayPlan.value.daily_itinerary && Object.keys(dayPlan.value.daily_itinerary).length > 0) {
      selectedDay.value = Object.keys(dayPlan.value.daily_itinerary)[0];
    }
  }
}
          
// Process site details if available
if (outputs.site_detail && Array.isArray(outputs.site_detail)) {
  siteDetails.value = outputs.site_detail;
  console.log('Site details (partial):', siteDetails.value);
  
  // 不再在这里立即生成景点讲解，而是等待DOM渲染后再生成
}
          
// Process site photos if available
if (outputs.site_photos) {
  if (Array.isArray(outputs.site_photos)) {
    sitePhotos.value = outputs.site_photos;
    console.log('Site photos (array):', sitePhotos.value);
  } else if (typeof outputs.site_photos === 'object') {
    // 如果是对象格式，转换为数组格式
    const photosArray = [];
    for (const [name, photos] of Object.entries(outputs.site_photos)) {
      if (Array.isArray(photos)) {
        photosArray.push({ name, photos });
      }
    }
    if (photosArray.length > 0) {
      sitePhotos.value = photosArray;
      console.log('Site photos (converted from object):', sitePhotos.value);
    }
  }
}
        }
      }
    );
    
    // Add completion message to streaming steps
    streamingSteps.value.push('行程规划已完成！');
    console.log('Streaming completed');
    
    // 确保在数据处理完成后再关闭加载状态
    if (dayPlan.value) {
      console.log('Day plan loaded successfully:', dayPlan.value);
    } else {
      console.warn('No day plan data received');
      streamingSteps.value.push('未能获取到行程数据，请重试');
    }
    
  } catch (error) {
    console.error('Error generating travel plan:', error);
    streamingSteps.value.push('生成行程时出错，请稍后再试');
    alert('生成旅行计划时出错，请稍后再试');
  } finally {
    // 延迟关闭加载状态，确保用户能看到最终消息
    setTimeout(() => {
      isLoading.value = false;
    }, 1000);
  }
};


// Use search suggestion
const useSearchSuggestion = (suggestion) => {
  userInput.value = suggestion;
  generateTravelPlan();
};

// Computed properties for generation phases
const filteredPhases = computed(() => {
  // 显示json_search、title_summary、site_name_address_description和explain_site这四个阶段
  return generationPhases.value.filter(phase => 
    phase.phase === 'json_search' || 
    phase.phase === 'title_summary' || 
    phase.phase === 'site_name_address_description' ||
    phase.phase === 'explain_site'
  );
});

// Helper methods for generation phases
const getPhaseDisplayName = (phaseName) => {
  const displayNames = {
    "json_search": "生成检索句",
    "title_summary": "检索结果列表",
    "site_name_address_description": "景点总结",
    "get_photos": "景点图片获取",
    "day_plan": "行程规划生成",
    "explain_site": "景点讲解"
  };
  return displayNames[phaseName] || phaseName;
};

// eslint-disable-next-line no-unused-vars
const isValidJson = (str) => {
  try {
    JSON.parse(str);
    return true;
  } catch (e) {
    return false;
  }
};

// eslint-disable-next-line no-unused-vars
const formatJsonContent = (content) => {
  try {
    const jsonObj = JSON.parse(content);
    // 格式化景点信息
    if (Array.isArray(jsonObj)) {
      let formattedContent = `🏞️ 【景点信息汇总】\n\n`;
      
      jsonObj.forEach((site, index) => {
        formattedContent += `📍 ${index + 1}. 【${site.name}】\n`;
        formattedContent += `   📌 地址: ${site.address}\n`;
        formattedContent += `   📝 描述: ${site.description}\n`;
        formattedContent += `   🏷️ 标签: ${site.source_keywords.join('、')}\n`;
        
        if (index < jsonObj.length - 1) {
          formattedContent += `\n${'-'.repeat(40)}\n\n`;
        }
      });
      
      return formattedContent;
    }
    
    // 移除usage信息
    if (jsonObj.text && jsonObj.usage) {
      return `${jsonObj.text}`;
    }
    
    // 如果不是数组，尝试格式化其他类型的JSON
    const formattedContent = Object.entries(jsonObj)
      .filter(([key]) => key !== 'usage') // 过滤掉usage字段
      .map(([key, value]) => {
        if (typeof value === 'object' && value !== null) {
          return `${key}: ${JSON.stringify(value, null, 2).replace(/\n/g, '\n  ')}`;
        }
        return `${key}: ${value}`;
      })
      .join('\n\n');
    
    return formattedContent;
  } catch (e) {
    return content;
  }
};

// eslint-disable-next-line no-unused-vars
const formatDayPlanContent = (content) => {
  try {
    // 提取JSON部分
    const jsonMatch = content.match(/```json\n([\s\S]*?)\n```/);
    if (jsonMatch && jsonMatch[1]) {
      const jsonObj = JSON.parse(jsonMatch[1]);
      
      // 格式化行程规划
      let formattedContent = `🗺️ 【${jsonObj.summary.total_planned_days}日旅游行程规划】\n\n`;
      
      // 添加行程概览
      formattedContent += `📋 【行程概览】\n`;
      formattedContent += `${'-'.repeat(40)}\n`;
      formattedContent += `📅 总天数: ${jsonObj.summary.total_planned_days}天\n`;
      formattedContent += `⏱️ 行程节奏: ${jsonObj.summary.overall_pace === 'moderate' ? '适中' : 
                            jsonObj.summary.overall_pace === 'relaxed' ? '轻松' : 
                            jsonObj.summary.overall_pace === 'packed' ? '紧凑' : 
                            jsonObj.summary.overall_pace}\n`;
      if (jsonObj.summary.notes_or_unassigned) {
        formattedContent += `📝 备注: ${jsonObj.summary.notes_or_unassigned}\n`;
      }
      formattedContent += `${'-'.repeat(40)}\n\n`;
      
      // 添加每日行程
      Object.entries(jsonObj.daily_itinerary).forEach(([day, details]) => {
        formattedContent += `🔶 【${day.replace('Day_', '第')}天 - ${details.theme_or_area}】\n`;
        formattedContent += `${'-'.repeat(40)}\n`;
        formattedContent += `⏰ 时间安排:\n`;
        formattedContent += `  • 景点游览: ${formatMinutes(details.estimated_attraction_time_minutes)}\n`;
        formattedContent += `  • 交通时间: ${formatMinutes(details.estimated_travel_time_minutes)}\n`;
        formattedContent += `  • 总时长: ${formatMinutes(details.estimated_attraction_time_minutes + details.estimated_travel_time_minutes)}\n\n`;
        
        formattedContent += `🏛️ 景点行程:\n`;
        
        details.attractions.forEach((attraction, index) => {
          const siteName = attraction.site_name.replace(/北京市\s+/, '');
          formattedContent += `  ${index + 1}. ${siteName} (${formatMinutes(attraction.estimated_visit_duration_minutes)})\n`;
          
          if (attraction.travel_to_next_minutes) {
            formattedContent += `     ↓ ${formatMinutes(attraction.travel_to_next_minutes)} ↓\n`;
          }
        });
        
        formattedContent += `\n💡 安排理由:\n  ${details.day_reasoning}\n\n`;
      });
      
      return formattedContent;
    }
    return content;
  } catch (e) {
    console.error('Error formatting day plan:', e);
    return content;
  }
};

// Computed properties
const dayPlanKeys = computed(() => {
  if (!dayPlan.value) return [];
  return Object.keys(dayPlan.value.daily_itinerary || {});
});

// Selected day (default to first day)
const selectedDay = ref('');

// Watch dayPlanKeys and set selectedDay to first day when available
watch(dayPlanKeys, (newKeys) => {
  if (newKeys.length > 0 && !selectedDay.value) {
    selectedDay.value = newKeys[0];
  }
}, { immediate: true });

// Current day plan based on selected day
const currentDayPlan = computed(() => {
  if (!dayPlan.value || !dayPlan.value.daily_itinerary || !selectedDay.value) {
    return { attractions: [], day_reasoning: '' };
  }
  return dayPlan.value.daily_itinerary[selectedDay.value] || { attractions: [], day_reasoning: '' };
});

// Computed properties for trip overview
const totalTripTime = computed(() => {
  if (!dayPlan.value || !dayPlan.value.daily_itinerary) return 0;
  
  let totalMinutes = 0;
  Object.values(dayPlan.value.daily_itinerary).forEach(day => {
    if (day.estimated_attraction_time_minutes) {
      totalMinutes += day.estimated_attraction_time_minutes;
    }
    if (day.estimated_travel_time_minutes) {
      totalMinutes += day.estimated_travel_time_minutes;
    }
  });
  
  return totalMinutes;
});

const totalAttractions = computed(() => {
  if (!dayPlan.value || !dayPlan.value.daily_itinerary) return 0;
  
  let count = 0;
  Object.values(dayPlan.value.daily_itinerary).forEach(day => {
    if (day.attractions && Array.isArray(day.attractions)) {
      count += day.attractions.length;
    }
  });
  
  return count;
});

// 地图相关方法
const showRouteMap = async () => {
  showMap.value = true;
  
  // 等待DOM更新后初始化地图
  await nextTick();
  
  // 每次显示地图时都重新初始化，确保路线正确显示
  mapInitialized.value = false;
  initMap();
};

const closeMap = () => {
  showMap.value = false;
};

const initMap = () => {
  // 添加安全密钥配置
  if (!window._AMapSecurityConfig) {
    window._AMapSecurityConfig = {
      securityJsCode: "ab6be27976f6495b5eefd19c89f2f425", // 这里应该使用你申请的安全密钥
    };
  }
  
  // 如果已经加载了AMapLoader，直接使用
  if (window.AMapLoader) {
    loadMap();
  } else {
    // 动态加载AMapLoader
    const script = document.createElement('script');
    script.src = 'https://webapi.amap.com/loader.js';
    script.async = true;
    script.onload = () => {
      loadMap();
    };
    document.head.appendChild(script);
  }
};

const loadMap = () => {
  // 使用AMapLoader加载高德地图API
  window.AMapLoader.load({
    key: "b7e2044eae5d5b47d9fe9500789f969f", // 使用您的高德地图API密钥
    version: "2.0",
    plugins: ['AMap.Driving'], // 需要使用的插件
  })
  .then((AMap) => {
    // 创建地图实例
    const map = new AMap.Map("container", {
      viewMode: '2D',
      resizeEnable: true,
      zoom: 13, // 地图显示的缩放级别
      center: [116.397428, 39.90923], // 默认中心点
    });
    
    // 标记地图已初始化
    mapInitialized.value = true;
    
    // 绘制路线
    drawRoute(map, AMap);
  })
  .catch((e) => {
    console.error("地图加载失败:", e);
  });
};

const drawRoute = (map, AMap) => {
  console.log('开始绘制路线...');
  
  if (!map) {
    console.error('地图实例不存在，无法绘制路线');
    return;
  }
  
  // 获取当前选中日期的景点
  const attractions = currentDayPlan.value.attractions;
  if (!attractions || attractions.length < 2) {
    console.error('景点数量不足，无法绘制路线');
    return;
  }
  
  console.log('当天景点数量：', attractions.length);
  
  try {
    // 创建驾车导航实例
    const driving = new AMap.Driving({
      map: map,
      panel: "panel"
    });
    
    // 构建搜索点数组
    const searchPoints = [];
    
    // 添加所有景点作为路线点
    for (let i = 0; i < attractions.length; i++) {
      searchPoints.push({
        keyword: attractions[i].site_name
      });
    }
    
    console.log('路线规划点：', searchPoints);
    
    // 搜索驾车路线
    driving.search(searchPoints, function(status, result) {
      if (status === 'complete') {
        console.log('绘制驾车路线完成');
        // 调整地图视野以包含所有路线点
        map.setFitView();
      } else {
        console.error('获取驾车数据失败：', result);
      }
    });
  } catch (error) {
    console.error('绘制路线时发生错误：', error);
  }
};

// 在组件卸载前清理地图资源
onBeforeUnmount(() => {
  if (mapInitialized.value) {
    // 获取地图实例并销毁
    const mapDiv = document.getElementById("container");
    if (mapDiv && mapDiv.__amap_map_instance) {
      mapDiv.__amap_map_instance.destroy();
    }
  }
});

// Methods
const updateTime = () => {
  const now = new Date();
  const hours = now.getHours();
  const minutes = now.getMinutes().toString().padStart(2, '0');
  currentTime.value = `${hours}:${minutes}`;
};

const goBack = () => {
  // Handle back navigation
  console.log('Back button clicked');
};

const selectDay = (day) => {
  selectedDay.value = day;
  // Scroll to top of day plan
  nextTick(() => {
    if (travelContent.value) {
      const dayPlanContainer = travelContent.value.querySelector('.day-plan-container');
      if (dayPlanContainer) {
        dayPlanContainer.scrollIntoView({ behavior: 'smooth' });
      }
    }
    
    // 如果地图已经显示，重新绘制路线
    if (showMap.value && mapInitialized.value) {
      // 获取地图实例
      const mapDiv = document.getElementById("container");
      if (mapDiv && mapDiv.__amap_map_instance) {
        // 清除之前的路线
        mapDiv.__amap_map_instance.clearMap();
        // 重新绘制路线
        drawRoute(mapDiv.__amap_map_instance);
      } else {
        // 如果没有找到地图实例，重新初始化地图
        initMap();
      }
    }
  });
};

// This function is no longer needed since site details are always shown
// We're keeping the expandedSites ref for compatibility with other parts of the code

const showSiteDetail = (activityName) => {
  // Find the site that matches the activity name
  const site = siteDetails.value.find(site => 
    site.name.includes(activityName) || activityName.includes(site.name)
  );
  
  if (site) {
    // Find the index of the site
    const siteIndex = siteDetails.value.findIndex(s => s.name === site.name);
    
    // Expand the site card
    if (!expandedSites.value.includes(siteIndex)) {
      expandedSites.value.push(siteIndex);
    }
    
    // Scroll to the site card
    nextTick(() => {
      if (travelContent.value) {
        const siteCard = travelContent.value.querySelector(`.site-card:nth-child(${siteIndex + 1})`);
        if (siteCard) {
          siteCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }
    });
  }
};

// Toggle trip details visibility
const toggleTripDetails = () => {
  showTripDetails.value = !showTripDetails.value;
};

// Get photos for a specific site
const getSitePhotos = (siteName) => {
  if (!sitePhotos.value || !sitePhotos.value.length) return [];
  
  // 尝试找到完全匹配的景点
  let sitePhoto = sitePhotos.value.find(photo => photo.name === siteName);
  
  // 如果没有完全匹配，尝试部分匹配
  if (!sitePhoto) {
    sitePhoto = sitePhotos.value.find(photo => 
      photo.name.includes(siteName) || siteName.includes(photo.name)
    );
  }
  
  return sitePhoto ? sitePhoto.photos : [];
};

// 格式化检索句
const formatSearchTerms = (content) => {
  try {
    // 尝试解析JSON
    let terms = [];
    if (content.includes('show_content')) {
      // 如果包含show_content字段，尝试提取
      const jsonObj = JSON.parse(content);
      if (jsonObj.show_content && Array.isArray(jsonObj.show_content)) {
        terms = jsonObj.show_content;
      }
    } else if (isValidJson(content)) {
      // 直接尝试解析为数组
      const jsonObj = JSON.parse(content);
      if (Array.isArray(jsonObj)) {
        terms = jsonObj;
      } else if (jsonObj.search_sentence && Array.isArray(jsonObj.search_sentence)) {
        terms = jsonObj.search_sentence;
      }
    } else {
      // 尝试从文本中提取
      const matches = content.match(/\[(.*?)\]/g);
      if (matches) {
        terms = matches.map(m => m.replace(/[[\]"']/g, '').trim());
      }
    }
    
    // 过滤空字符串
    return terms.filter(term => term && term.trim() !== '');
  } catch (e) {
    console.error('Error formatting search terms:', e);
    return [];
  }
};

// 格式化检索结果
const formatSearchResults = (content) => {
  try {
    // 尝试解析JSON
    let results = [];
    if (content.includes('show_content')) {
      // 如果包含show_content字段，尝试提取
      const jsonObj = JSON.parse(content);
      if (jsonObj.show_content && Array.isArray(jsonObj.show_content)) {
        results = jsonObj.show_content.map(item => ({
          title: item.title || '未知标题',
          url: item.url || '#'
        }));
      }
    } else if (isValidJson(content)) {
      // 直接尝试解析
      const jsonObj = JSON.parse(content);
      if (Array.isArray(jsonObj)) {
        results = jsonObj.map(item => ({
          title: item.title || item.name || '未知标题',
          url: item.url || '#'
        }));
      }
    }
    
    return results;
  } catch (e) {
    console.error('Error formatting search results:', e);
    return [];
  }
};


// Open image viewer
const openImageViewer = (images, index, siteName) => {
  // 将字符串数组转换为对象数组
  const formattedImages = images.map(image => ({
    url: image,
    keyword: siteName
  }));
  viewerImages.value = formattedImages;
  currentImageIndex.value = index;
  currentImageKeyword.value = siteName;
  showImageViewer.value = true;
};

// 监听siteDetails变化，当它有值时，等待DOM渲染后再生成景点总结
watch(siteDetails, (newVal) => {
  if (newVal.length > 0 && !tourGuideGenerated.value && !tourGuideLoading.value) {
    // 使用nextTick确保DOM已经更新
    nextTick(() => {
      // 生成景点总结
      generateTourGuide(JSON.stringify(newVal));
    });
  }
});

// Lifecycle hooks
onMounted(() => {
  updateTime();
  setInterval(updateTime, 60000);
  
  // Expand the first site by default
  if (siteDetails.value.length > 0) {
    expandedSites.value.push(0);
  }
});
</script>

<style scoped>
/* 旅行容器样式 */
.travel-container {
  position: fixed;
  display: grid;
  grid-template-rows: 1fr auto;
  height: 100vh;
  width: 100vw;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  margin: 0;
  padding: 0;
  overflow: hidden;
  background-color: #f5f7fa;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* 移动端头部样式 */
.mobile-header {
  background-color: #f7f8fc;
  padding-top: env(safe-area-inset-top, 10px);
  z-index: 100;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  width: 100%;
}

.status-bar {
  display: flex;
  justify-content: space-between;
  padding: 4px 16px;
  font-size: 12px;
  color: #333;
}

.status-icons {
  display: flex;
  gap: 4px;
}

.travel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.back-button, .more-button {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #333;
  cursor: pointer;
}

.back-icon, .more-icon {
  font-size: 20px;
}

/* 旅行内容区域样式 */
.travel-content {
  grid-row: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0 16px 100px 16px;
  -webkit-overflow-scrolling: touch;
  width: 100%;
  display: flex;
  flex-direction: column;
}

/* 日期选项卡样式 */
.day-tabs {
  display: flex;
  overflow-x: auto;
  padding: 16px 0;
  gap: 10px;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none; /* Firefox */
}

.day-tabs::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Edge */
}

.day-tab-button {
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 12px;
  padding: 8px 16px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  flex-shrink: 0;
}

.day-tab-button.active {
  background-color: #ff6700;
  color: white;
  border-color: #ff6700;
}

/* 日程计划容器样式 */
.day-plan-container {
  background-color: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.day-plan-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px 0;
}

/* 活动列表样式 */
.activities-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.activity-item {
  display: flex;
  align-items: center;
  background-color: #f8f8f8;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.activity-item:hover {
  background-color: #f0f0f0;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.activity-item:active {
  background-color: #e8e8e8;
  transform: translateY(0);
}

.activity-number {
  width: 24px;
  height: 24px;
  background-color: #ff6700;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  margin-right: 12px;
}

.activity-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.activity-name {
  font-size: 15px;
  color: #333;
}

.activity-arrow {
  color: #999;
  font-size: 16px;
}

/* 行程理由样式 */
.plan-reason {
  background-color: #f8f8f8;
  border-radius: 8px;
  padding: 12px;
}

.reason-header {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.reason-content {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

/* 景点详情区域样式 */
.site-details-section {
  margin: 20px auto;
  max-width: 1200px;
  width: 100%;
  background-color: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.site-details-section h2, .results-container h2, .trip-overview-section h2 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px 0;
}

.site-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

@media (max-width: 767px) {
  .site-cards-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
}

@media (max-width: 480px) {
  .site-cards-grid {
    grid-template-columns: 1fr;
  }
}

.site-card {
  background-color: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  height: 100%;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.site-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.site-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background-color: #f8f8f8;
  border-bottom: 2px solid #ff6700;
}

.site-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.site-photos {
  width: 100%;
  overflow: hidden;
}

.site-photos-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 4px;
}

.site-photo {
  position: relative;
  padding-top: 75%; /* 4:3 aspect ratio */
  overflow: hidden;
  cursor: pointer;
}

.site-photo img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.site-photo:hover img {
  transform: scale(1.05);
}

.site-details-content {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.scrollable-content {
  max-height: 200px;
  overflow-y: auto;
  padding: 8px;
  background-color: #f9f9f9;
  border-radius: 8px;
  margin-top: 8px;
}

.site-address {
  margin-bottom: 12px;
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #eaeaea;
}

.site-description {
  margin-bottom: 12px;
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #eaeaea;
  max-height: 180px;
  overflow-y: auto;
}

.site-description::-webkit-scrollbar {
  width: 6px;
}

.site-description::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.site-description::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 3px;
}

.site-description::-webkit-scrollbar-thumb:hover {
  background: #ccc;
}

.detail-label {
  font-weight: 600;
  color: #333;
}

.site-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.site-tag {
  background-color: #f0f0f0;
  border-radius: 12px;
  padding: 4px 12px;
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

/* 底部导航栏样式 */
.bottom-nav {
  grid-row: 2;
  display: flex;
  justify-content: space-around;
  align-items: center;
  background-color: white;
  padding: 12px 0;
  padding-bottom: calc(env(safe-area-inset-bottom, 16px) + 12px);
  border-top: 1px solid #eee;
  box-shadow: 0 -1px 3px rgba(0, 0, 0, 0.05);
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #999;
  font-size: 12px;
}

.nav-item.active {
  color: #ff6700;
}

.nav-icon {
  font-size: 20px;
  margin-bottom: 4px;
}

/* 设置按钮样式 */
.settings-button {
  position: fixed;
  top: 16px;
  right: 16px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: white;
  border: 1px solid #eee;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 100;
  transition: all 0.2s ease;
}

.settings-button:hover {
  transform: scale(1.05);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
}

.settings-icon {
  font-size: 20px;
}

/* 搜索输入区域样式 */
.search-container {
  margin: 16px 0;
}

.search-input-wrapper {
  display: flex;
  background-color: white;
  border-radius: 24px;
  padding: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.search-input-wrapper input {
  flex: 1;
  border: none;
  padding: 12px 16px;
  font-size: 15px;
  outline: none;
  background: transparent;
}

.search-button {
  background-color: #ff6700;
  color: white;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  margin-right: 4px;
}

.search-icon {
  font-size: 18px;
}

/* 加载状态样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 3px solid rgba(255, 103, 0, 0.1);
  border-top-color: #ff6700;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-container p {
  color: #666;
  font-size: 16px;
}

.loading-container .streaming-status {
  margin-top: 16px;
  max-width: 600px;
  text-align: center;
}

.loading-message {
  color: #666;
  font-size: 14px;
  margin-top: 12px;
  padding: 8px 16px;
  background-color: #f8f8f8;
  border-radius: 8px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 生成阶段样式 */
.generation-phases-container {
  display: flex;
  justify-content: center;
  width: 100%;
  margin: 20px auto;
  max-width: 1200px;
}

.generation-phases {
  width: 100%;
  background-color: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* 思考容器样式 */
.thinking-container {
  background-color: #f5f5f5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 16px;
}

.thinking-container:hover {
  background-color: #f0f0f0;
}

.thinking-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
}

.thinking-icon {
  font-size: 18px;
  margin-right: 10px;
}

.thinking-title {
  flex: 1;
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.thinking-expand-icon {
  font-size: 12px;
  color: #666;
}

.thinking-content {
  padding: 8px;
  background-color: #fafafa;
  border-radius: 8px;
  margin-top: 8px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 阶段容器样式 */
.phase-container {
  margin-bottom: 16px;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
  background-color: #f9f9f9;
}

.phase-container:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.important-phase {
  background-color: #fffaf5;
  box-shadow: 0 2px 6px rgba(255, 103, 0, 0.08);
}

.active-phase {
  border: 2px solid #ff6700;
  box-shadow: 0 4px 12px rgba(255, 103, 0, 0.15);
}

.important-phase .phase-header {
  background-color: #fff0e6;
  border-bottom: 1px solid #ffcca8;
}

.active-phase .phase-header {
  background-color: #ffe4d1;
  border-bottom: 2px solid #ff6700;
}

.phase-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #f8f8f8;
  cursor: pointer;
}

.phase-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.active-phase .phase-title {
  color: #ff6700;
}

.phase-status-indicator {
  margin-right: 10px;
}

.phase-expand-icon {
  font-size: 12px;
  color: #666;
}

/* 打字指示器样式 */
.typing-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
}

.typing-indicator span {
  height: 6px;
  width: 6px;
  margin: 0 2px;
  background-color: #ff6700;
  border-radius: 50%;
  display: inline-block;
  opacity: 0.7;
}

.typing-indicator span:nth-child(1) {
  animation: typing 1.5s infinite 0s;
}

.typing-indicator span:nth-child(2) {
  animation: typing 1.5s infinite 0.3s;
}

.typing-indicator span:nth-child(3) {
  animation: typing 1.5s infinite 0.6s;
}

@keyframes typing {
  0% { transform: scale(1); opacity: 0.7; }
  50% { transform: scale(1.5); opacity: 1; }
  100% { transform: scale(1); opacity: 0.7; }
}

.phase-content {
  padding: 16px;
  background-color: #fafafa;
  max-height: 500px;
  overflow-y: auto;
  border-radius: 0 0 8px 8px;
  animation: slideDown 0.3s ease;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.03);
}

@keyframes slideDown {
  from { max-height: 0; opacity: 0; }
  to { max-height: 500px; opacity: 1; }
}

.phase-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
}

/* 特殊样式用于景点总结内容 */
.phase-container[class*="景点总结"] .phase-content pre {
  background-color: #f0f8ff;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #4a90e2;
  font-size: 14px;
  line-height: 1.7;
  color: #333;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* 特殊样式用于景点图片获取内容 */
.phase-container[class*="景点图片"] .phase-content pre {
  background-color: #f5f5f5;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #9e9e9e;
  font-size: 14px;
  line-height: 1.7;
  color: #333;
}

/* 景点讲解容器样式 */
.explain-site-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.explain-site-content {
  background-color: #f0f8ff;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 14px;
  color: #4a6fa5;
  line-height: 1.6;
  border: 1px solid #d0e1f9;
  transition: all 0.2s ease;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.explain-site-content:hover {
  background-color: #e6f2ff;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(74, 111, 165, 0.15);
}

.explain-site-phase .phase-header {
  background-color: #f8f8f8;
  border-bottom: 1px solid #eaeaea;
}

.explain-site-phase .phase-title::before {
  content: "🎙️ ";
}

/* Tour Guide Container Styles */
.tour-guide-container {
  display: flex;
  flex-direction: column;
  background-color: #f9f9f9;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid #e8e8e8;
}

.tour-guide-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eaeaea;
}

.tour-guide-icon {
  font-size: 24px;
  margin-right: 10px;
  color: #ff6700;
}

.tour-guide-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.tour-guide-content {
  flex: 1;
}

.tour-guide-empty {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.tour-guide-button {
  background-color: #ff6700;
  color: white;
  border: none;
  border-radius: 20px;
  padding: 8px 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tour-guide-button:hover {
  background-color: #ff8533;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(255, 103, 0, 0.2);
}

.tour-guide-messages {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 350px;
  overflow-y: auto;
  padding: 12px;
  border-radius: 10px;
  background-color: #f5f5f5;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
  border: 1px solid #eaeaea;
}

.message-wrapper {
  width: 100%;
}

.message-container {
  display: flex;
  margin-bottom: 12px;
  position: relative;
  width: 100%;
  min-width: 0;
  flex-shrink: 0;
}

.message-container.user-message {
  display: flex;
  justify-content: flex-end;
  width: 100%;
}

.user-message {
  justify-content: flex-end;
  width: 100%;
  display: flex;
}

.bot-message {
  justify-content: flex-start;
  align-items: flex-start;
  width: 100%;
}

.message-bubble {
  max-width: 90%;
  min-width: 0;
  padding: 14px 18px;
  border-radius: 18px;
  word-break: break-word;
  line-height: 1.5;
  overflow-wrap: break-word;
  transition: transform 0.2s ease;
}

.user-message .message-bubble {
  background-color: #e6f0ff;
  color: #333;
  border-top-right-radius: 4px;
  max-width: 80%;
  margin-left: auto;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  border: 1px solid #d0e1f9;
}

.bot-message .message-bubble {
  background-color: white;
  color: #333;
  border-top-left-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  border: 1px solid #eaeaea;
}

.message-bubble:hover {
  transform: translateY(-2px);
}

.mi-logo {
  width: 32px;
  height: 32px;
  margin-left: 0;
  margin-right: 8px;
  border-radius: 4px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #ff6700;
}

.mi-logo-text {
  color: white;
  font-weight: bold;
  font-size: 14px;
  letter-spacing: -1px;
}

.main-response {
  padding: 16px;
  font-size: 15px;
}

.response-text {
  line-height: 1.5;
}

.cursor {
  display: inline-block;
  font-weight: bold;
  transition: opacity 0.3s;
}


/* 特别为LLM 3节点添加样式 */
.llm3-phase .phase-content pre {
  background-color: #fff8f0;
  padding: 20px;
  border-radius: 10px;
  border-left: 4px solid #ff6700;
  font-size: 15px;
  line-height: 1.7;
  color: #333;
  box-shadow: 0 2px 6px rgba(255,103,0,0.1);
}

/* 添加特殊样式用于格式化的内容 */
.phase-content pre em {
  font-style: italic;
  color: #555;
}

.phase-content pre strong {
  font-weight: bold;
  color: #000;
}

/* 为格式化的内容添加特殊样式 */
.phase-content pre {
  position: relative;
}

/* 为emoji添加特殊样式 */
.phase-content pre span.emoji {
  font-size: 1.2em;
  margin-right: 0.2em;
  vertical-align: middle;
}

/* 为分隔线添加特殊样式 */
.phase-content pre hr {
  border: none;
  border-top: 1px dashed #ddd;
  margin: 12px 0;
}

/* 为LLM 3节点添加特殊标记 */
.llm3-phase .phase-header .phase-title {
  color: #ff6700;
  font-weight: 700;
}

.llm3-phase .phase-header .phase-title::before {
  content: "🗺️ ";
}

/* 空状态样式 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.empty-state-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.empty-state p {
  color: #666;
  margin-bottom: 24px;
  line-height: 1.5;
}

.suggestion-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.suggestion-chip {
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 12px;
  padding: 8px 16px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: all 0.2s ease;
}

.suggestion-chip:hover {
  background-color: #e9e9e9;
  transform: translateY(-2px);
}

/* 结果区域样式 */
.results-container {
  margin: 20px auto;
  max-width: 1200px;
  width: 100%;
  background-color: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* 日期选项卡样式 */
.day-tabs {
  display: flex;
  overflow-x: auto;
  padding: 16px 0;
  gap: 10px;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none; /* Firefox */
}

.day-tabs::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Edge */
}

.day-tab-button {
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 20px;
  padding: 8px 16px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  flex-shrink: 0;
}

.day-tab-button.active {
  background-color: #ff6700;
  color: white;
  border-color: #ff6700;
}

/* 日程计划容器样式 */
.day-plan-container {
  background-color: white;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.day-plan-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.day-time-info {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
  background-color: #f8f8f8;
  padding: 8px 12px;
  border-radius: 8px;
}

.time-item {
  display: flex;
  align-items: center;
}

.time-label {
  font-size: 13px;
  color: #666;
  margin-right: 4px;
}

.time-value {
  font-size: 13px;
  font-weight: 600;
  color: #333;
}

/* 活动列表样式 */
.activities-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}


.activity-item {
  display: flex;
  align-items: flex-start;
  background-color: #f8f8f8;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.activity-item:hover {
  background-color: #f0f0f0;
  transform: translateY(-2px);
}

.activity-number {
  width: 24px;
  height: 24px;
  background-color: #ff6700;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  margin-right: 12px;
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.activity-details {
  flex: 1;
}

.activity-name {
  font-size: 15px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.activity-time {
  font-size: 13px;
  color: #666;
}

.travel-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-left: 12px;
}

.travel-time {
  font-size: 12px;
  color: #666;
  background-color: #eee;
  padding: 2px 8px;
  border-radius: 12px;
  margin-bottom: 4px;
}

.travel-arrow {
  color: #999;
  font-size: 16px;
}

/* 行程理由样式 */
.plan-reason {
  background-color: #f8f8f8;
  border-radius: 8px;
  padding: 12px;
}

.reason-header {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.reason-content {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

/* 景点详情区域样式 */
.site-details-section {
  margin-bottom: 20px;
}

.site-details-section h2 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px 0;
}

.site-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.site-card {
  background-color: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.site-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  cursor: pointer;
}

.site-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.site-expand-icon {
  color: #999;
  font-size: 14px;
}

.site-details {
  padding: 0 16px 16px 16px;
  border-top: 1px solid #eee;
}

.site-address, .site-description {
  margin-bottom: 12px;
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.detail-label {
  font-weight: 600;
  color: #333;
}

.site-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.site-tag {
  background-color: #f0f0f0;
  border-radius: 16px;
  padding: 4px 12px;
  font-size: 12px;
  color: #666;
}

/* 行程规划概览区域样式 */
.trip-overview-section {
  margin: 20px auto;
  max-width: 1200px;
  width: 100%;
  background-color: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.trip-overview-section h2 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px 0;
}

.trip-overview-card {
  background-color: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  cursor: pointer;
}

.overview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.overview-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.overview-expand-icon {
  color: #999;
  font-size: 14px;
}

.overview-summary {
  display: flex;
  flex-wrap: wrap;
  padding: 16px;
  gap: 16px;
  background-color: #f8f8f8;
}

.overview-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.overview-icon {
  font-size: 18px;
}

.overview-text {
  font-size: 14px;
  color: #333;
}

.overview-text span {
  font-weight: 700;
  color: #ff6700;
  font-size: 18px;
}

.trip-details {
  padding: 16px;
  border-top: 1px solid #eee;
}

.trip-day-item {
  margin-bottom: 20px;
}

.trip-day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.trip-day-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
}

.trip-day-time {
  font-size: 13px;
  color: #666;
  background-color: #f0f0f0;
  padding: 4px 8px;
  border-radius: 12px;
}

.trip-day-attractions {
  margin-bottom: 12px;
}

.trip-attraction-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px dashed #eee;
}

.attraction-bullet {
  color: #ff6700;
  font-size: 18px;
  margin-right: 8px;
}

.attraction-name {
  flex: 1;
  font-size: 14px;
  color: #333;
}

.attraction-time {
  font-size: 12px;
  color: #666;
}

.trip-day-reasoning {
  background-color: #f8f8f8;
  padding: 12px;
  border-radius: 8px;
  margin-top: 12px;
}

.reasoning-label {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.reasoning-text {
  font-size: 13px;
  color: #666;
  line-height: 1.5;
}

.trip-day-divider {
  height: 1px;
  background-color: #eee;
  margin: 16px 0;
}

/* 进度条样式 */
.progress-container {
  width: 100%;
  height: 4px;
  margin: 12px 0;
  background-color: #f0f0f0;
  border-radius: 2px;
  overflow: hidden;
}

.top-progress {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  margin: 0;
  height: 3px;
  background-color: transparent;
  border-radius: 0;
}

.progress-bar {
  height: 100%;
  width: 30%;
  background-color: #ff6700;
  border-radius: 2px;
  animation: progress-animation 1.5s infinite ease-in-out;
}

@keyframes progress-animation {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(400%);
  }
}

/* 底部固定搜索框样式 */
.fixed-search-container {
  position: fixed;
  bottom: 20px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  padding: 0 16px;
  z-index: 100;
}

.fixed-search-container .search-input-wrapper {
  width: 100%;
  max-width: 500px;
  background-color: #fff;
  border-radius: 24px;
  padding: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  border: 2px solid #ff6700;
}

.fixed-search-container input {
  flex: 1;
  border: none;
  padding: 12px 16px;
  font-size: 15px;
  outline: none;
  background: transparent;
}

.fixed-search-container .search-button {
  background-color: #ff6700;
  color: white;
  border: none;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  margin-right: 2px;
  transition: all 0.2s ease;
}

.fixed-search-container .search-button:hover {
  background-color: #ff8533;
  transform: scale(1.05);
}

.fixed-search-container .search-icon {
  font-size: 20px;
}

/* 加载旋转器样式 */
.loading-spinner-small {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid rgba(255, 103, 0, 0.1);
  border-top-color: #ff6700;
  animation: spin 1s linear infinite;
  margin-left: 10px;
}

/* 加载状态下的思考容器样式 */
.loading-active {
  background-color: #fff0e6;
  border: 1px solid #ffcca8;
  cursor: default;
}

.loading-active:hover {
  background-color: #fff0e6;
  transform: none;
}

/* 检索词容器样式 */
.search-terms-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.search-term-item {
  background-color: #f0f8ff;
  border-radius: 12px;
  padding: 6px 20px;
  font-size: 13px;
  color: #4a6fa5;
  display: flex;
  align-items: center;
}

.search-term-item::before {
  content: "🔍";
  margin-right: 6px;
  font-size: 14px;
}

/* 检索结果容器样式 */
.search-results-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.search-result-item {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 12px;
  transition: all 0.2s ease;
  border-bottom: 1px solid #e0e0e0;
  margin-bottom: 2px;
  border: 1px solid #eaeaea;
}

.search-result-item:hover {
  background-color: #f0f0f0;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.search-result-item:active {
  background-color: #e8e8e8;
  transform: translateY(0);
}

.search-result-link {
  color: #333;
  text-decoration: none;
  font-size: 14px;
  display: block;
  line-height: 1.4;
}

.search-result-link:hover {
  color: #ff6700;
  text-decoration: underline;
}

/* 地图容器样式 */
.map-container {
  position: relative;
  width: 100%;
  height: 500px;
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

#container {
  width: 100%;
  height: 100%;
}

#panel {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 280px;
  max-height: 90%;
  overflow-y: auto;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.close-map-button {
  position: absolute;
  top: 10px;
  left: 10px;
  background-color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 100;
  transition: all 0.2s ease;
}

.close-map-button:hover {
  background-color: #f0f0f0;
  transform: translateY(-2px);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
}

.map-button {
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 20px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.map-button::before {
  content: "🗺️";
}

.map-button:hover {
  background-color: #45a049;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}
</style>
