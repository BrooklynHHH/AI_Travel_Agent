<template>
  <div class="travel-container">
    <!-- 浮层组件 -->
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

      <!-- Loading state -->
      <div v-if="isLoading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>正在为您生成行程规划...</p>
      </div>
      
      <!-- Results area (only shown when we have results) -->
      <div v-if="dayPlan && !isLoading" class="results-container">
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
      <div v-if="!dayPlan && !isLoading" class="empty-state">
        <div class="empty-state-icon">🧭</div>
        <h3>开始您的旅行规划</h3>
        <p>输入您的旅游需求，我们将为您生成个性化的旅行计划</p>
        <div class="suggestion-chips">
          <button class="suggestion-chip" @click="useSearchSuggestion('南京三日游')">南京三日游</button>
          <button class="suggestion-chip" @click="useSearchSuggestion('杭州亲子游')">杭州亲子游</button>
          <button class="suggestion-chip" @click="useSearchSuggestion('北京五日游')">北京五日游</button>
          <button class="suggestion-chip" @click="useSearchSuggestion('云南七日游')">云南七日游</button>
        </div>
      </div>
      
      <!-- Site details section (only shown when we have results) -->
      <div v-if="dayPlan && !isLoading && siteDetails.length > 0" class="site-details-section">
        <h2>景点详情</h2>
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
              <div class="overview-text">总天数: {{ dayPlanKeys.length }}天</div>
            </div>
            <div class="overview-item">
              <div class="overview-icon">🕒</div>
              <div class="overview-text">总游览时间: {{ formatMinutes(totalTripTime) }}</div>
            </div>
            <div class="overview-item">
              <div class="overview-icon">🏞️</div>
              <div class="overview-text">景点数量: {{ totalAttractions }}个</div>
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
import { ref, onMounted, nextTick, computed, watch } from 'vue';
import ImageViewer from '../components/modals/ImageViewer.vue';
import ProductWindow from '../components/modals/ProductWindow.vue';
import SettingsModal from '../components/modals/SettingsModal.vue';

// Dify Workflow Client class
class DifyWorkflowClient {
  constructor(apiKey, baseUrl = "https://mify-be.pt.xiaomi.com/api/v1") {
    if (!apiKey) {
      throw new Error("API Key 不能为空");
    }
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

    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        method: "POST",
        headers: this.headers,
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API error: ${response.status} - ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Workflow run failed:", error);
      throw error;
    }
  }
}

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
    apiKeyInput.value = 'app-8oBdrBQ32V1h9fTZAzI6Zfu9';
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
  
  // Set loading state
  isLoading.value = true;
  headerTitle.value = userInput.value;
  
  try {
    // Get API key from cookie or use default__MIFY_API_KEY
    const savedApiKey = 'app-8oBdrBQ32V1h9fTZAzI6Zfu9';
    
    // Create client
    const client = new DifyWorkflowClient(savedApiKey);
    
    // Call API
    const response = await client.runWorkflow(
      { user_question: userInput.value },
      "user-" + Math.random().toString(36).substring(2, 10)
    );
    
    console.log('API Response:', response);
    
    // Process response
    if (response && response.data && response.data.outputs) {
      console.log('Raw API response:', response.data.outputs);
      
      // Parse dayplan data
      const parsedDayPlan = parseDayPlan(response.data.outputs);
      if (parsedDayPlan) {
        dayPlan.value = parsedDayPlan;
        console.log('Parsed day plan:', dayPlan.value);
      } else {
        console.error('Failed to parse dayplan data');
      }
      
      // Process site details
      if (response.data.outputs.site_detail && Array.isArray(response.data.outputs.site_detail)) {
        siteDetails.value = response.data.outputs.site_detail;
        console.log('Site details:', siteDetails.value);
      } else {
        console.error('No site details found or invalid format');
      }
      
      // Process site photos
      if (response.data.outputs.site_photos && Array.isArray(response.data.outputs.site_photos)) {
        sitePhotos.value = response.data.outputs.site_photos;
        console.log('Site photos:', sitePhotos.value);
      } else {
        console.error('No site photos found or invalid format');
      }
    }
  } catch (error) {
    console.error('Error generating travel plan:', error);
    alert('生成旅行计划时出错，请稍后再试');
  } finally {
    isLoading.value = false;
  }
};

// Use search suggestion
const useSearchSuggestion = (suggestion) => {
  userInput.value = suggestion;
  generateTravelPlan();
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
  
  const sitePhoto = sitePhotos.value.find(photo => 
    photo.name.includes(siteName) || siteName.includes(photo.name)
  );
  
  return sitePhoto ? sitePhoto.photos : [];
};

// Open image viewer
const openImageViewer = (images, index, siteName) => {
  viewerImages.value = images;
  currentImageIndex.value = index;
  currentImageKeyword.value = siteName;
  showImageViewer.value = true;
};

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
  margin-bottom: 20px;
}

.site-details-section h2 {
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
  border-radius: 20px;
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
  margin-top: 16px;
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
  margin-bottom: 20px;
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
</style>
