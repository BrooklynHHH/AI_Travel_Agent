<template>
  <div class="chat-container">
    <!-- 返回按钮 -->
    <div class="back-button" @click="goBack">
      <i class="back-icon">&lt;</i>
    </div>
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
    <VideoPlayer
      v-model:show="showVideoPlayer"
      :videoUrl="videoUrl"
      :videoTitle="videoTitle"
      :videoAvatar="videoAvatar"
      :videoLikeCount="videoLikeCount"
      :videoCommentCount="videoCommentCount"
      :videoDescription="videoDescription"
    />

    <!-- 进度条 -->
    <div v-if="isLoading || isStreaming" class="progress-container top-progress">
      <div class="progress-bar"></div>
    </div>

    <!-- 裁剪弹窗 -->
    <FabricCanvas
      v-if="showCropper"
      :imageUrl="cropTempUrl"
      @confirm="onCropConfirm"
      @cancel="onCropCancel"
    />
    <!-- Chat内容 -->
    <div class="chat-content" ref="chatContent">
      <!-- 其余内容复用 -->
      <div v-for="(message, index) in messages" :key="index" class="message-wrapper" style="width: 100%;">
        <div v-if="message.role === 'user'" class="message-container user-message">
          <div class="message-bubble">
            <div v-if="message.image" class="user-image-container">
              <div style="position: relative; display: inline-block;">
                <img :src="message.image" :ref="el => { if(message.hasOcr) ocrImage = el }" style="max-width: 320px; border: 1px solid #eee;" />
                <canvas
                  v-if="boxes.length && message.hasOcr"
                  :width="imageWidth"
                  :height="imageHeight"
                  ref="ocrCanvas"
                  style="position: absolute; left: 0; top: 0; pointer-events: none;"
                ></canvas>
              </div>
            </div>
            <div v-if="message.content">{{ message.content }}</div>
          </div>
        </div>
        <template v-else-if="message.role === 'assistant'">
          <div class="message-container bot-message">
            <div class="mi-logo">
              <div class="mi-logo-text">MI</div>
            </div>
            <div class="message-bubble main-response">
              <!-- 统一用 marked 渲染 assistant 消息 -->
              <div class="response-text" v-html="renderMarkdown(message.content)"></div>
            </div>
          </div>
        </template>
      </div>
      <div style="height: 20px"></div>
    </div>

    <!-- 输入区 -->
    <div class="chat-input">
      <div class="input-container">
        <!-- 上传图片按钮隐藏，保留但不显示 -->
        <label v-if="false" class="upload-btn" style="margin-right: 8px;">
          <input type="file" accept="image/*" @change="onFileChange" style="display: none;" />
          <i class="plus-icon">📷</i>
        </label>
        <input 
          type="text" 
          placeholder="输入你想问的问题" 
          v-model="userInput"
          @keyup.enter="sendMessage"
          :disabled="isLoading || isStreaming"
        />
        <div class="voice-button" @click="sendMessage" :class="{ 'disabled': isLoading || isStreaming }">
          <i class="send-icon">↑</i>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { handleStreamingResponse } from '../utils/streamUtils';
import ImageViewer from '../base/views/ImageViewer.vue';
import ProductWindow from '../components/modals/ProductWindow.vue';
import VideoPlayer from '../components/modals/VideoPlayer.vue';
// 使用 markdown-it 替代 marked
import MarkdownIt from 'markdown-it';
// 已在main.js全局导入，此处移除: import 'katex/dist/katex.min.css';
import { createWorker, createScheduler } from 'tesseract.js';
import FabricCanvas from '../components/FabricCanvas.vue';

// 初始化 markdown-it 实例
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true // 启用换行符转换为<br>标签
});

const router = useRouter();
const userInput = ref('');
const messages = ref([]);
const imageUrl = ref('');
const showCropper = ref(false);
const cropTempUrl = ref('');
const conversationId = ref('');

// 返回按钮功能
const goBack = () => {
  router.push('/advanced');
};

// 在组件加载时生成会话ID
onMounted(() => {
  const timestamp = new Date().getTime();
  conversationId.value = `baidu_faxingbao_${timestamp}`;
  console.log('生成会话ID:', conversationId.value);
});

// 上传图片到服务器
const uploadImageToServer = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user', 'taoliang1');
    
    const response = await fetch('http://10.18.4.170/v1/files/upload', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer app-KKnaWRUs5gw15CUBHGZkqWd2'
      },
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`上传失败: ${response.status} ${response.statusText}`);
    }
    
    const result = await response.json();
    console.log('上传成功:', result);
    
    // 缓存文件ID
    localStorage.setItem('lastUploadedFileId', result.id);
    
    return result;
  } catch (error) {
    console.error('上传图片出错:', error);
    return null;
  }
};

// 将DataURL转换为Blob
const dataURLtoBlob = (dataURL) => {
  const arr = dataURL.split(',');
  const mime = arr[0].match(/:(.*?);/)[1];
  const bstr = atob(arr[1]);
  let n = bstr.length;
  const u8arr = new Uint8Array(n);
  
  while (n--) {
    u8arr[n] = bstr.charCodeAt(n);
  }
  
  return new Blob([u8arr], { type: mime });
};

// 调用API接口处理图片
const processImageWithAPI = async (fileId) => {
  if (!fileId) return;
  
  try {
    // 设置加载状态
    isLoading.value = true;
    
    // 创建一个占位消息
    const lastIndex = messages.value.push({
      role: 'assistant',
      content: '',
      streaming: true
    }) - 1;
    
    // 设置流式输出状态
    isStreaming.value = true;
    
    // 准备请求数据
    const requestData = {
      inputs: {
        q: {
          transfer_method: "local_file",
          upload_file_id: fileId,
          type: "image"
        },
        query: userInput.value || "",
        con_id: conversationId.value
      },
      response_mode: "streaming",
      user: "taoliang1"
    };
    
    // 调用API
    const response = await fetch('http://10.18.4.170/v1/workflows/run', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer app-KKnaWRUs5gw15CUBHGZkqWd2',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    });
    
    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status} ${response.statusText}`);
    }
    
    // 用于存储流式输出的内容
    let streamingContent = '';
    
    // 定义处理流式文本的函数
    const processStreamingText = (newText) => {
      // 处理换行符，将\n\n替换为\n，将\n替换为Markdown换行符（两个空格加换行）
      if (newText === '\n\n') {
        newText = '\n';
      }
      
      // 将单个\n替换为Markdown换行符（两个空格加换行）
      if (newText === '\n') {
        newText = '  \n';
      }
      
      console.log('处理文本:', newText.substring(0, 50) + (newText.length > 50 ? '...' : ''));
      
      // 移除<think>和</think>标签，直接显示内容
      let processedText = newText
        .replace(/<think>/g, '')
        .replace(/<\/think>/g, '');
      
      // 更新消息内容
      streamingContent += processedText;
      messages.value[lastIndex].content = streamingContent;
      
      // 滚动到底部
      nextTick(() => {
        scrollToBottom();
      });
    };
    
    await handleStreamingResponse(response, {
      debug: true,
      onStart: () => {
        console.log('流式响应开始');
      },
      onData: (data) => {
        // 处理消息事件
        if (data.event === "message" && data.answer) {
          const newText = data.answer;
          processStreamingText(newText);
        }
        // 处理文本块事件
        else if (data.event === "text_chunk" && data.data && data.data.text) {
          const newText = data.data.text;
          processStreamingText(newText);
        }
      },
      onComplete: () => {
        console.log('流式响应完成');
        
        // 标记流式输出完成
        messages.value[lastIndex].streaming = false;
        
        // 设置流式输出状态为false
        isStreaming.value = false;
        
        // 在流式输出完成后，重新渲染内容以正确显示LaTeX公式
        nextTick(() => {
          // 获取当前消息的内容
          const currentContent = messages.value[lastIndex].content;
          // 先清空内容，然后重新设置，触发重新渲染
          messages.value[lastIndex].content = '';
          setTimeout(() => {
            // 重新应用内容并强制刷新
            messages.value[lastIndex].content = currentContent;
            // 强制重新渲染KaTeX公式
            nextTick(() => {
              // 查找所有包含KaTeX公式的元素并应用额外样式
              const katexElements = document.querySelectorAll('.response-text .katex');
              katexElements.forEach(el => {
                el.classList.add('katex-refreshed');
              });
            });
          }, 10);
        });
      },
      onError: (error) => {
        console.error('流式响应错误:', error);
      }
    });
    
  } catch (error) {
    console.error('处理图片API错误:', error);
    
    // 添加错误消息
    messages.value.push({
      role: 'assistant',
      content: '抱歉，处理图片时出现错误。',
      error: true
    });
    
  } finally {
    // 重置加载状态
    isLoading.value = false;
    isStreaming.value = false;
    
    // 滚动到底部
    nextTick(() => {
      scrollToBottom();
    });
  }
};

// 滚动到底部
const scrollToBottom = () => {
  const chatContentEl = document.querySelector('.chat-content');
  if (chatContentEl) {
    chatContentEl.scrollTop = chatContentEl.scrollHeight;
  }
};

// 处理澄清追问选项点击
const handleClarificationOption = (option, event) => {
  console.log('用户选择了澄清选项:', option);
  
  // 获取当前选项元素
  const optionElement = event.target.closest('.clarification-option');
  if (!optionElement) return;
  
  // 切换选中状态
  optionElement.classList.toggle('selected');
  
  // 检查是否为多选模式
  const isMultiple = optionElement.querySelector('.checkbox-multiple');
  if (!isMultiple) {
    // 单选模式：取消其他选项的选中状态
    const allOptions = document.querySelectorAll('.clarification-option');
    allOptions.forEach(opt => {
      if (opt !== optionElement) {
        opt.classList.remove('selected');
      }
    });
  }
  
  // 更新确认按钮状态
  updateConfirmButtonState();
};

// 更新确认按钮状态
const updateConfirmButtonState = () => {
  const selectedElements = document.querySelectorAll('.clarification-option.selected');
  const confirmButton = document.querySelector('.confirm-button');
  
  if (confirmButton) {
    if (selectedElements.length === 0) {
      confirmButton.disabled = true;
      confirmButton.style.opacity = '0.5';
      confirmButton.style.cursor = 'not-allowed';
    } else {
      confirmButton.disabled = false;
      confirmButton.style.opacity = '1';
      confirmButton.style.cursor = 'pointer';
    }
  }
};

// 处理澄清追问确认按钮点击
const handleClarificationConfirm = () => {
  console.log('用户点击了确认按钮');
  
  // 收集所有选中的选项
  const selectedOptions = [];
  const selectedElements = document.querySelectorAll('.clarification-option.selected');
  
  selectedElements.forEach(element => {
    const optionText = element.querySelector('.option-text').textContent;
    selectedOptions.push(optionText);
  });
  
  if (selectedOptions.length === 0) {
    alert('请至少选择一个选项');
    return;
  }
  
  // 将选中的选项作为用户消息发送
  const selectedText = selectedOptions.join('、');
  userInput.value = selectedText;
  sendMessage();
};

// 将处理函数暴露到全局，以便HTML中的onclick可以调用
window.handleClarificationOption = handleClarificationOption;
window.handleClarificationConfirm = handleClarificationConfirm;
window.updateConfirmButtonState = updateConfirmButtonState;


const onCropConfirm = async (box) => {
  console.log('接收到的裁剪区域:', box);
  
  const img = new window.Image();
  img.onload = async () => {
    console.log('原始图片尺寸:', img.width, 'x', img.height);
    
    // 创建一个新的canvas来裁剪图片
    const canvas = document.createElement('canvas');
    canvas.width = box.width;
    canvas.height = box.height;
    const ctx = canvas.getContext('2d');
    
    // 裁剪图片
    ctx.drawImage(
      img,
      box.left, box.top, box.width, box.height,
      0, 0, box.width, box.height
    );
    
    // 将裁剪后的图片转换为DataURL
    const croppedImageUrl = canvas.toDataURL('image/png');
    
    // 将DataURL转换为Blob
    const blob = dataURLtoBlob(croppedImageUrl);
    
    // 创建带时间戳的文件名
    const timestamp = new Date().getTime();
    const fileName = `crop_${timestamp}.png`;
    
    // 创建File对象
    const file = new File([blob], fileName, { type: 'image/png' });
    
    // 上传图片到服务器
    const uploadResult = await uploadImageToServer(file);
    
    // 添加到用户消息中
    messages.value.push({
      role: 'user',
      content: userInput.value || '',
      image: croppedImageUrl,
      hasOcr: true,
      fileId: uploadResult ? uploadResult.id : null
    });
    userInput.value = '';
    
    // 保存图片URL用于OCR
    imageUrl.value = croppedImageUrl;
    showCropper.value = false;
    
    // 更新图片尺寸并执行OCR
    nextTick(() => {
      updateImageSize();
      doOcr();
      
      // 如果上传成功，调用API处理图片
      if (uploadResult && uploadResult.id) {
        processImageWithAPI(uploadResult.id);
      }
    });
  };
  
  // 加载原始图片
  img.src = cropTempUrl.value;
  cropTempUrl.value = '';
};

const onCropCancel = () => {
  cropTempUrl.value = '';
  showCropper.value = false;
};
const boxes = ref([]); // 识别到的题目框 [{x, y, w, h}]
const imageWidth = ref(0);
const imageHeight = ref(0);
const ocrImage = ref(null);
const ocrCanvas = ref(null);

// 处理图片上传
const onFileChange = (e) => {
  const file = e.target.files[0];
  if (!file) return;
  
  // 先重置状态，确保每次上传都能正确显示裁剪界面
  cropTempUrl.value = '';
  showCropper.value = false;
  
  // 使用nextTick确保DOM已更新
  nextTick(() => {
    const reader = new FileReader();
    reader.onload = (ev) => {
      cropTempUrl.value = ev.target.result;
      showCropper.value = true;
    };
    reader.readAsDataURL(file);
  });
  
  // 重置input，确保可以上传相同的文件
  e.target.value = '';
};

// 获取图片实际宽高
const updateImageSize = () => {
  if (ocrImage.value) {
    imageWidth.value = ocrImage.value.naturalWidth;
    imageHeight.value = ocrImage.value.naturalHeight;
  }
};

// OCR识别并画框
const doOcr = async () => {
  boxes.value = [];
  if (!imageUrl.value) return;
  console.log('开始识别...');
  
  try {
    // 创建worker和scheduler
    const worker = await createWorker('chi_sim+eng', { 
      logger: false, // 移除函数日志记录器，改为false禁用日志
      workerPath: 'https://unpkg.com/tesseract.js@v6.0.1/dist/worker.min.js',  // 使用unpkg CDN替代jsdelivr
      corePath: 'https://unpkg.com/tesseract.js-core@v4.0.4/tesseract-core.wasm.js',
      langPath: 'https://tessdata.projectnaptha.com/4.0.0',
    });
    
    const scheduler = createScheduler();
    scheduler.addWorker(worker);
    
    // 使用scheduler进行识别
    const { data } = await scheduler.addJob('recognize', imageUrl.value);
    
    console.log('识别原始结果', data);
    
    // 只简单筛选含有"="或"解"或"题"等关键词的行，作为"题目"
    const questionWords = ['=', '解', '题', '求', '设', '已知', '计算', '证明'];
    const resultBoxes = [];
    
    if (Array.isArray(data.words)) {
      data.words.forEach(word => {
        if (questionWords.some(q => word.text && word.text.includes(q))) {
          resultBoxes.push({
            x: word.bbox.x0,
            y: word.bbox.y0,
            w: word.bbox.x1 - word.bbox.x0,
            h: word.bbox.y1 - word.bbox.y0
          });
        }
      });
    }
    
    console.log('题目框选结果', resultBoxes);
    boxes.value = resultBoxes;
    drawBoxes();
    
    // 释放资源
    await scheduler.terminate();
    
  } catch (error) {
    console.error('OCR识别错误:', error);
  }
};

// 在canvas上画框
const drawBoxes = () => {
  if (!ocrCanvas.value || !ocrImage.value) return;
  const ctx = ocrCanvas.value.getContext('2d');
  ctx.clearRect(0, 0, ocrCanvas.value.width, ocrCanvas.value.height);
  ctx.strokeStyle = 'red';
  ctx.lineWidth = 2;
  boxes.value.forEach(box => {
    ctx.strokeRect(box.x, box.y, box.w, box.h);
  });
};

// Markdown 渲染，自动去除 markdown 代码块包裹
const renderMarkdown = (content) => {
  if (!content) return '';
  // 打印内容便于调试
  console.log('message.content:', JSON.stringify(content));
  
  // 去除 markdown 代码块包裹
  const codeBlockRegex = /^```(?:html)?\n([\s\S]*?)\n```$/i;
  const match = content.match(codeBlockRegex);
  if (match) {
    return match[1]; // 直接返回 HTML
  }
  
  // 检查是否包含HTML标签
  const hasHtmlTags = /<[^>]*>/.test(content);
  
  if (hasHtmlTags) {
    // 如果包含HTML标签，直接返回内容，不进行Markdown解析
    console.log('检测到HTML内容，直接返回');
    return content;
  }
  
  // 对于纯文本内容，使用Markdown解析
  return md.render(content);
};

// 处理<think>标签并提取思考内容

// iframe加载事件处理
const onIframeLoad = () => {
  console.log('Iframe加载完成');
  isLoading.value = false;
};

// 其余状态和方法复用 ChatView
const showImageViewer = ref(false);
const viewerImages = ref([]);
const currentImageIndex = ref(0);
const currentImageKeyword = ref('');
const showProductWindow = ref(false);
const productName = ref('');
const productUrl = ref('');
const isFullscreen = ref(false);
const windowHeight = ref(50);
const iframeKey = ref(0);
const isLoading = ref(false);
const showVideoPlayer = ref(false);
const videoUrl = ref('');
const videoTitle = ref('');
const videoAvatar = ref('');
const videoLikeCount = ref(0);
const videoCommentCount = ref(0);
const videoDescription = ref('');
const isStreaming = ref(false);

// 百度法行宝API配置
const BAIDU_API_URL = 'http://staging-llm.search.miui.srv/agent-api/baidu-faxingbao';

// 消息类型说明
// messageType: 1 - 法律咨询
// messageType: 2 - 案例卡片
// messageType: 6 - 预约律师卡片
// messageType: 9 - 法律咨询（带法规标）
// messageType: 19 - 微服务卡片（对话召回）
// messageType: 26 - 相关法律查询
// messageType: 27 - 澄清追问

// 会话ID管理
const sessionID = ref('');

// 卡片数据存储
const cardData = ref([]);

// 渲染卡片组件
const renderCardComponent = (card) => {
  // 根据设备类型选择合适的链接
  const linkUrl = card.pcLinkUrl || card.mobileLinkUrl || card.linkUrl || '#';
  
  // 根据服务类型确定按钮文本
  const getButtonText = (card) => {
    const name = card.linkName || '';
    if (name.includes('律师费') || name.includes('费用') || name.includes('计算')) {
      return '点击计算';
    } else if (name.includes('咨询') || name.includes('律师')) {
      return '点击咨询';
    } else if (name.includes('查询') || name.includes('搜索')) {
      return '点击查询';
    } else {
      return '点击查看';
    }
  };
  
  const buttonText = getButtonText(card);
  
  return `
    <div class="service-card">
      <div class="service-card-header">
        <div class="service-icon">
          ${card.linkLogo ? `<img src="${card.linkLogo}" alt="服务图标">` : '🔗'}
        </div>
        <div class="service-title">${card.linkName || '相关服务'}</div>
      </div>
      <div class="service-description">
        ${card.linkDesc || '暂无描述'}
      </div>
      <div class="service-action">
        <button class="service-button" onclick="window.open('${linkUrl}', '_blank')">
          ${buttonText}
        </button>
      </div>
    </div>
  `;
};

// 渲染卡片列表
const renderCardList = (cards) => {
  if (!Array.isArray(cards) || cards.length === 0) {
    return '<div class="no-cards">暂无相关服务</div>';
  }
  
  const cardHtml = cards.map(card => renderCardComponent(card)).join('');
  return `
    <div class="service-cards-grid">
      ${cardHtml}
    </div>
  `;
};

// 渲染案例卡片组件
const renderCaseCardComponent = (caseItem) => {
  // 根据设备类型选择合适的链接
  const linkUrl = caseItem.pcLinkUrl || caseItem.mobileLinkUrl || '#';
  
  return `
    <div class="case-card">
      <div class="case-card-header">
        <div class="case-icon">
          📋
        </div>
        <div class="case-title">${caseItem.linkName || '案例标题'}</div>
      </div>
      <div class="case-description">
        ${caseItem.linkDesc || '案例描述'}
      </div>
      <div class="case-action">
        <button class="case-button" onclick="window.open('${linkUrl}', '_blank')">
          查看案例
        </button>
      </div>
    </div>
  `;
};

// 渲染案例卡片列表
const renderCaseCards = (cases) => {
  if (!Array.isArray(cases) || cases.length === 0) {
    return '<div class="no-cards">暂无相关案例</div>';
  }
  
  const caseHtml = cases.map(caseItem => renderCaseCardComponent(caseItem)).join('');
  return `
    <div class="case-cards-grid">
      ${caseHtml}
    </div>
  `;
};

// 渲染法律条款卡片
const renderLawTermCard = (item) => {
  return `
    <div class="law-term-card">
      <div class="law-term-header">
        <div class="law-term-icon">⚖️</div>
        <div class="law-term-title">${item.title || '法规条款'}</div>
      </div>
      <div class="law-term-content">
        <div class="law-term-text">${item.term_content || '暂无内容'}</div>
        <div class="law-term-meta">
          <div class="meta-item">
            <span class="meta-label">法规性质:</span>
            <span class="meta-value">${item.nature || '未知'}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">时效性:</span>
            <span class="meta-value">${item.timeliness || '未知'}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">发布机构:</span>
            <span class="meta-value">${item.issue_authority || '未知'}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">发布日期:</span>
            <span class="meta-value">${item.publish_date || '未知'}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">生效日期:</span>
            <span class="meta-value">${item.effective_date || '未知'}</span>
          </div>
        </div>
      </div>
      <div class="law-term-action">
        <button class="law-term-button">
          查看详情
        </button>
      </div>
    </div>
  `;
};

// 渲染法律查询卡片
const renderLawCards = (laws) => {
  if (!Array.isArray(laws) || laws.length === 0) {
    return '<div class="no-cards">暂无相关法律信息</div>';
  }
  
  let allCardsHtml = '';
  
  laws.forEach(law => {
    if (law.norm_title) {
      allCardsHtml += `<div class="law-section">
        <div class="law-section-header">
          <h3>📋 ${law.norm_title}</h3>
        </div>
        <div class="law-terms-container">`;
      
      if (law.term_info && Array.isArray(law.term_info)) {
        law.term_info.forEach(term => {
          if (term.term_index) {
            allCardsHtml += `<div class="term-group">
              <div class="term-index">${term.term_index}</div>
              <div class="term-cards">`;
            
            if (term.term_list && Array.isArray(term.term_list)) {
              term.term_list.forEach(item => {
                allCardsHtml += renderLawTermCard(item);
              });
            }
            
            allCardsHtml += `</div></div>`;
          }
        });
      }
      
      allCardsHtml += `</div></div>`;
    }
  });
  
  return `
    <div class="law-cards-content">
      ${allCardsHtml}
    </div>
  `;
};

// 渲染澄清追问卡片
const renderClarificationCard = (content) => {
  let optionsHtml = '';
  const isMultiple = content.isMultiple !== false; // 默认为多选
  
  if (content.options && Array.isArray(content.options)) {
    optionsHtml = content.options.map((option) => `
      <div class="clarification-option" onclick="handleClarificationOption('${option}', event)">
        <div class="option-checkbox ${isMultiple ? 'checkbox-multiple' : 'checkbox-single'}">
          <div class="checkbox-inner"></div>
        </div>
        <div class="option-text">${option}</div>
      </div>
    `).join('');
  }
  
  // 确保消息内容不为空
  const message = content.message || '为了更好地回答您的问题，请选择以下选项：';
  
  // 根据是否多选显示不同的文本
  const selectText = isMultiple ? '多选' : '单选';
  
  return `
    <div class="clarification-question">
      <span class="question-text">${message}</span>
      <span class="question-type">
        <span class="type-text">${selectText}</span>
      </span>
    </div>
    <div class="clarification-card">
      <div class="clarification-options">
        ${optionsHtml}
      </div>
      <div class="clarification-confirm">
        <button class="confirm-button" onclick="handleClarificationConfirm()" disabled>确定</button>
      </div>
    </div>
  `;
};

// 新增“法规卡片”渲染函数
const renderLawExtCards = (extArr) => {
  if (!Array.isArray(extArr) || extArr.length === 0) return '';
  return `
    <div class="law-ext-cards-grid">
      ${extArr.map(item => `
        <div class="law-term-card">
          <div class="law-term-header">
            <div class="law-term-icon">⚖️</div>
            <div class="law-term-title">${item.title || ''}</div>
          </div>
          <div class="law-term-content">
            <div class="law-term-text">${item.termContent || item.term_content || ''}</div>
            <div class="law-term-meta">
              <div class="meta-item"><span class="meta-label">时效性:</span><span class="meta-value">${item.timeliness || ''}</span></div>
              <div class="meta-item"><span class="meta-label">索引:</span><span class="meta-value">${item.termIndex || item.term_index || ''}</span></div>
              <div class="meta-item"><span class="meta-label">发布日期:</span><span class="meta-value">${item.publishDate || item.publish_date || ''}</span></div>
              <div class="meta-item"><span class="meta-label">生效日期:</span><span class="meta-value">${item.effectiveDate || item.effective_date || ''}</span></div>
            </div>
          </div>
          ${(item.mobileLinkUrl || item.pcLinkUrl) ? `
            <div class="law-term-action">
              <button class="law-term-button" onclick="window.open('${item.pcLinkUrl || item.mobileLinkUrl}', '_blank')">
                查看原文
              </button>
            </div>
          ` : ''}
        </div>
      `).join('')}
    </div>
  `;
};

// 法律类问题判断接口
const checkLegalQuestion = async (query, historyQuery = '') => {
  try {
    const response = await fetch('https://service.mify.mioffice.cn/api/v1/workflows/run', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer app-knyYuGAXUX37ss2ynsdxLqME',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        inputs: {
          query: query,
          historyquery: historyQuery
        },
        response_mode: "blocking",
        user: "taoliang1",
        custom_id: "legal_check"
      })
    });

    if (!response.ok) {
      throw new Error(`法律类判断接口请求失败: ${response.status} ${response.statusText}`);
    }

    const result = await response.json();
    console.log('法律类判断结果:', result);

    // 检查是否有错误
    if (result.data && result.data.error) {
      throw new Error(`法律类判断接口错误: ${result.data.error}`);
    }

    // 返回判断结果
    if (result.data && result.data.outputs && result.data.outputs.text) {
      return result.data.outputs.text;
    }

    return null;
  } catch (error) {
    console.error('法律类问题判断失败:', error);
    return null;
  }
};

// 发送消息
const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value || isStreaming.value) return;

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: userInput.value
  });

  const userMessage = userInput.value;
  userInput.value = '';
  isLoading.value = true;

  try {
    // 准备历史对话记录用于法律问题判断
    const historyForLegalCheck = [];
    // 获取最近几轮对话作为历史记录（用于法律问题判断）
    const recentMessagesForCheck = messages.value.slice(-6); // 最近3轮对话（6条消息）
    for (let i = 0; i < recentMessagesForCheck.length; i += 2) {
      if (recentMessagesForCheck[i] && recentMessagesForCheck[i + 1]) {
        historyForLegalCheck.push(recentMessagesForCheck[i].content);
        historyForLegalCheck.push(recentMessagesForCheck[i + 1].content);
      }
    }
    
    // 构建历史对话字符串
    const historyQuery = historyForLegalCheck.join('\n');
    
    // 首先判断是否为法律类问题
    console.log('开始判断是否为法律类问题...');
    console.log('当前问题:', userMessage);
    console.log('历史对话:', historyQuery);
    const legalCheckResult = await checkLegalQuestion(userMessage, historyQuery);
    
    if (legalCheckResult === '0' || legalCheckResult === 0) {
      // 不是法律类问题，直接返回提示
      messages.value.push({
        role: 'assistant',
        content: '很抱歉，您的问题不属于法律类，法行宝无法帮助您。'
      });
      isLoading.value = false;
      nextTick(() => {
        scrollToBottom();
      });
      return;
    }
    
    console.log('问题属于法律类，继续处理...');

    // 创建占位AI消息
    const lastIndex = messages.value.push({
      role: 'assistant',
      content: '正在查询，请稍候...',
      streaming: true
    }) - 1;

    // 设置流式输出状态
    isStreaming.value = true;

    // 准备历史对话记录
    const history = [];
    // 获取最近几轮对话作为历史记录
    const recentMessages = messages.value.slice(-6); // 最近3轮对话（6条消息）
    for (let i = 0; i < recentMessages.length; i += 2) {
      if (recentMessages[i] && recentMessages[i + 1]) {
        history.push(recentMessages[i].content);
        history.push(recentMessages[i + 1].content);
      }
    }

    // 构造请求参数
    const requestData = {
      query: userMessage,
      sessionID: sessionID.value || '', // 首次对话传空，后续使用返回的sessionID
      model: 127, // 启用所有模式：1111111 = 127
      history: history
    };

    console.log('发送请求到百度法行宝:', requestData);

    // 调用百度法行宝API
    const response = await fetch(BAIDU_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    });

    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status} ${response.statusText}`);
    }

    // 用于存储流式输出的内容
    let streamingContent = '';
    
    // 用于存储澄清追问数据，等待流式输出完成后显示
    let clarificationData = {
      message: '',
      options: []
    };
    
    // 重置澄清追问数据，确保每次对话都是新的
    clarificationData = {
      message: '',
      options: []
    };

    // 处理流式输出
    await handleStreamingResponse(response, {
      debug: true,
      onStart: () => {
        console.log('百度法行宝流式响应开始');
      },
      onData: (data) => {
        console.log('收到百度法行宝数据:', data);
        
        // 处理不同类型的响应数据
        if (data.sessionID) {
          // 保存sessionID用于后续对话
          sessionID.value = data.sessionID;
          console.log('保存sessionID:', sessionID.value);
        }
        
        // 根据messageType处理不同类型的消息
        const messageType = data.messageType;
        console.log('消息类型:', messageType);
        
        // 如果messageType为undefined，说明是结束消息，直接返回
        if (messageType === undefined) {
          return;
        }
        
        switch (messageType) {
          case 1: // 法律咨询
            if (data.content) {
              // 使用Markdown解析器处理文本内容
              const markdownContent = md.render(data.content);
              const textContent = `
                <div class="text-content-container">
                  <div class="text-content markdown-content">
                    ${markdownContent}
                  </div>
                </div>
              `;
              streamingContent += textContent;
              messages.value[lastIndex].content = streamingContent;
            }
            break;
            
          case 2: // 案例卡片
            if (data.content && Array.isArray(data.content)) {
              // 存储卡片数据
              cardData.value = data.content;
              
              // 渲染案例卡片组件
              const caseCardsHtml = renderCaseCards(data.content);
              
              // 将卡片HTML添加到内容中
              streamingContent += caseCardsHtml;
              messages.value[lastIndex].content = streamingContent;
            }
            break;
            
          case 9: // 法律咨询（带法规标）
            if (data.content) {
              // 使用Markdown解析器处理文本内容
              const markdownContent = md.render(data.content);
              const textContent = `
                <div class="text-content-container">
                  <div class="text-content markdown-content">
                    ${markdownContent}
                  </div>
                </div>
              `;
              streamingContent += textContent;
            }
            // 渲染 ext 法规卡片
            if (data.ext && Array.isArray(data.ext) && data.ext.length > 0) {
              const extCardsHtml = renderLawExtCards(data.ext);
              streamingContent += extCardsHtml;
            }
            messages.value[lastIndex].content = streamingContent;
            break;
            
          case 26: // 相关法律查询
            if (data.content && Array.isArray(data.content)) {
              const lawCardsHtml = renderLawCards(data.content);
              streamingContent += lawCardsHtml;
              messages.value[lastIndex].content = streamingContent;
            }
            break;
            
          case 6: // 预约律师卡片
            if (data.content && typeof data.content === 'object') {
              // 将单个对象转换为数组格式
              const cardArray = [data.content];
              
              // 存储卡片数据
              cardData.value = cardArray;
              
              // 渲染卡片组件
              const cardHtml = renderCardList(cardArray);
              
              // 将卡片HTML添加到内容中
              streamingContent += cardHtml;
              messages.value[lastIndex].content = streamingContent;
            }
            break;
            
          case 19: // 微服务卡片（对话召回）
            if (data.content && typeof data.content === 'object') {
              // 将单个对象转换为数组格式
              const cardArray = [data.content];
              
              // 存储卡片数据
              cardData.value = cardArray;
              
              // 渲染卡片组件
              const cardHtml = renderCardList(cardArray);
              
              // 将卡片HTML添加到内容中
              streamingContent += cardHtml;
              messages.value[lastIndex].content = streamingContent;
            }
            break;
            
          case 27: // 澄清追问
            if (data.content) {
              // 合并澄清追问数据
              if (data.content.message) {
                clarificationData.message += data.content.message;
              }
              if (data.content.options && Array.isArray(data.content.options)) {
                clarificationData.options = data.content.options;
              }
              // 暂时不渲染，等待流式输出完成
            }
            break;
            
          default:
            // 处理其他类型的消息
            if (data.content) {
              if (typeof data.content === 'string') {
                // 使用Markdown解析器处理文本内容
                const markdownContent = md.render(data.content);
                const textContent = `
                  <div class="text-content-container">
                    <div class="text-content markdown-content">
                      ${markdownContent}
                    </div>
                  </div>
                `;
                streamingContent += textContent;
              } else if (typeof data.content === 'object') {
                // 尝试将对象内容渲染为可读格式
                let objectContent = '';
                
                // 如果是数组，尝试渲染为列表
                if (Array.isArray(data.content)) {
                  objectContent = data.content.map(item => {
                    if (typeof item === 'object') {
                      return `- ${JSON.stringify(item)}`;
                    } else {
                      return `- ${item}`;
                    }
                  }).join('\n');
                } else {
                  // 如果是普通对象，尝试提取有用信息
                  const keys = Object.keys(data.content);
                  if (keys.length > 0) {
                    objectContent = keys.map(key => {
                      const value = data.content[key];
                      if (typeof value === 'string') {
                        return `**${key}**: ${value}`;
                      } else {
                        return `**${key}**: ${JSON.stringify(value)}`;
                      }
                    }).join('\n');
                  } else {
                    objectContent = JSON.stringify(data.content, null, 2);
                  }
                }
                
                // 对对象内容进行Markdown解析
                const parsedObjectContent = md.render(objectContent);
                const objectContentHtml = `
                  <div class="text-content-container">
                    <div class="text-content markdown-content">
                      ${parsedObjectContent}
                    </div>
                  </div>
                `;
                streamingContent += objectContentHtml;
              }
              messages.value[lastIndex].content = streamingContent;
            }
            break;
        }
        
        // 滚动到底部
        nextTick(() => {
          scrollToBottom();
        });
      },
      onComplete: () => {
        console.log('百度法行宝流式响应完成');
        
        // 如果有澄清追问数据，在流式输出完成后渲染
        if (clarificationData && (clarificationData.message || clarificationData.options.length > 0)) {
          console.log('渲染澄清追问卡片:', clarificationData);
          const clarificationHtml = renderClarificationCard(clarificationData);
          streamingContent += clarificationHtml;
          messages.value[lastIndex].content = streamingContent;
          
          // 初始化确认按钮状态
          nextTick(() => {
            updateConfirmButtonState();
          });
        }
        
        // 标记流式输出完成
        messages.value[lastIndex].streaming = false;
        
        // 设置流式输出状态为false
        isStreaming.value = false;
        
        // 重置加载状态
        isLoading.value = false;
        
        // 滚动到底部
        nextTick(() => {
          scrollToBottom();
        });
      },
      onError: (error) => {
        console.error('百度法行宝流式响应错误:', error);
        messages.value[lastIndex].content = '抱歉，查询失败，请稍后重试。';
        messages.value[lastIndex].streaming = false;
        isStreaming.value = false;
        isLoading.value = false;
      }
    });

    // 添加超时保护机制，确保即使流式响应没有正确结束，用户也能继续输入
    setTimeout(() => {
      if (isLoading.value || isStreaming.value) {
        console.log('流式响应超时，强制重置状态');
        isLoading.value = false;
        isStreaming.value = false;
        if (messages.value[lastIndex]) {
          messages.value[lastIndex].streaming = false;
        }
      }
    }, 30000); // 30秒超时

  } catch (e) {
    console.error('发送消息失败:', e);
    messages.value.push({
      role: 'assistant',
      content: '查询失败，请稍后重试。'
    });
  } finally {
    // 确保所有状态都被重置
    isLoading.value = false;
    isStreaming.value = false;
  }
};

// 滚动到底部
</script>

<style>
/* 全局KaTeX样式，确保公式正确渲染 */
.katex {
  font-size: 1.2em !important;
  max-width: 100% !important;
  display: inline-block !important;
}

.katex-display {
  margin: 1em 0 !important;
  overflow-x: auto !important;
  overflow-y: hidden !important;
  padding: 5px 0 !important;
  text-align: center !important;
  width: 100% !important;
}

.katex-html {
  max-width: 100% !important;
}

.katex-error {
  color: #cc0000 !important;
}

/* 确保粗体符号正确显示 */
.katex .mathbf {
  font-weight: bold !important;
}

.katex-refreshed {
  animation: katex-refresh 0.1s;
}

@keyframes katex-refresh {
  0% { opacity: 0.99; }
  100% { opacity: 1; }
}

/* 确保LaTeX公式可视 */
.message-bubble .response-text p {
  overflow-wrap: break-word !important;
  word-wrap: break-word !important;
  word-break: break-word !important;
}

/* 确保公式在移动设备上也能正确显示 */
@media (max-width: 768px) {
  .katex-display {
    font-size: 0.9em !important;
  }
}

/* 服务卡片样式 */
.service-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin: 20px 0;
}

.service-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
  position: relative;
}

.service-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  border-color: #3b82f6;
}

.service-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.service-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  border-radius: 8px;
  overflow: hidden;
}

.service-icon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.service-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  flex: 1;
}

.service-description {
  color: #475569;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 20px;
}

.service-action {
  display: flex;
  justify-content: center;
}

.service-button {
  background: #dbeafe;
  color: #1e40af;
  border: none;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
}

.service-button:hover {
  background: #bfdbfe;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(30, 64, 175, 0.2);
}

.service-button:active {
  transform: translateY(0);
}

.no-cards {
  text-align: center;
  color: #64748b;
  font-style: italic;
  padding: 20px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .service-cards-grid {
    grid-template-columns: 1fr;
  }
  
  .service-card {
    padding: 16px;
  }
  
  .service-card-header {
    gap: 8px;
  }
  
  .service-icon {
    width: 32px;
    height: 32px;
    font-size: 18px;
  }
  
  .service-title {
    font-size: 14px;
  }
  
  .service-description {
    font-size: 13px;
  }
  
  .service-button {
    padding: 10px 16px;
    font-size: 14px;
  }
}

/* 案例卡片样式 */
.case-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  margin: 20px 0;
}

.case-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
  position: relative;
}

.case-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  border-color: #0284c7;
}

.case-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.case-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0284c7, #0369a1);
  color: white;
  border-radius: 8px;
}

.case-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  flex: 1;
  line-height: 1.4;
}

.case-description {
  color: #475569;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 20px;
}



.case-action {
  display: flex;
  justify-content: center;
}

.case-button {
  background: #dbeafe;
  color: #1e40af;
  border: none;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
}

.case-button:hover {
  background: #bfdbfe;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(30, 64, 175, 0.2);
}

.case-button:active {
  transform: translateY(0);
}

/* 案例卡片移动端响应式 */
@media (max-width: 768px) {
  .case-cards-grid {
    grid-template-columns: 1fr;
  }
  
  .case-card {
    padding: 16px;
  }
  
  .case-card-header {
    gap: 8px;
  }
  
  .case-icon {
    width: 32px;
    height: 32px;
    font-size: 18px;
  }
  
  .case-title {
    font-size: 14px;
  }
  
  .case-description {
    font-size: 13px;
  }
  
  .case-button {
    padding: 10px 16px;
    font-size: 14px;
  }
  
  .law-term-card {
    padding: 16px;
  }
  
  .law-term-header {
    gap: 8px;
  }
  
  .law-term-icon {
    width: 32px;
    height: 32px;
    font-size: 18px;
  }
  
  .law-term-title {
    font-size: 14px;
  }
  
  .law-term-text {
    font-size: 13px;
  }
  
  .law-term-button {
    padding: 10px 16px;
    font-size: 14px;
  }
  
  .law-ext-cards-grid {
    grid-template-columns: 1fr;
  }
}

/* 法律卡片样式 */
.law-cards-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin: 20px 0;
}

.law-ext-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  margin: 20px 0;
}

.law-section {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border: 1px solid #e2e8f0;
}

.law-section-header {
  background: linear-gradient(135deg, #7c3aed, #6d28d9);
  color: white;
  padding: 12px 16px;
}

.law-section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.law-terms-container {
  padding: 16px;
}

.term-group {
  margin-bottom: 20px;
}

.term-group:last-child {
  margin-bottom: 0;
}

.term-index {
  background: #f3e8ff;
  color: #7c3aed;
  padding: 8px 12px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 12px;
  border-left: 4px solid #7c3aed;
}

.term-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 12px;
}

.law-term-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
  position: relative;
}

.law-term-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  border-color: #7c3aed;
}

.law-term-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.law-term-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #7c3aed, #6d28d9);
  color: white;
  border-radius: 8px;
}

.law-term-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  flex: 1;
}

.law-term-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.law-term-text {
  color: #374151;
  font-size: 14px;
  line-height: 1.5;
  background: #f8fafc;
  padding: 12px;
  border-radius: 6px;
  border-left: 3px solid #7c3aed;
}

.law-term-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.meta-label {
  color: #6b7280;
  font-weight: 500;
  min-width: 60px;
}

.meta-value {
  color: #374151;
  font-weight: 600;
}

.law-term-action {
  display: flex;
  justify-content: center;
}

.law-term-button {
  background: #dbeafe;
  color: #1e40af;
  border: none;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
}

.law-term-button:hover {
  background: #bfdbfe;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(30, 64, 175, 0.2);
}

.law-term-button:active {
  transform: translateY(0);
}

/* 移动端响应式 */
@media (max-width: 768px) {
  .term-cards {
    grid-template-columns: 1fr;
  }
  
  .law-term-meta {
    grid-template-columns: 1fr;
  }
  
  .law-term-card {
    padding: 12px;
  }
  
  .law-term-header {
    gap: 6px;
  }
  
  .law-term-icon {
    width: 28px;
    height: 28px;
    font-size: 16px;
  }
  
  .law-term-title {
    font-size: 13px;
  }
  
  .law-term-text {
    font-size: 12px;
    padding: 10px;
  }
}

/* 文本内容容器样式 */
.text-content-container {
  margin: 4px 0;
}

.text-content {
  color: #2d3748;
  font-size: 16px;
  line-height: 1.6;
  padding: 3px 0;
}

/* Markdown内容样式 */
.markdown-content {
  color: #2d3748;
  font-size: 16px;
  line-height: 1.6;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3,
.markdown-content h4,
.markdown-content h5,
.markdown-content h6 {
  color: #1a202c;
  font-weight: 600;
  margin: 4px 0 2px 0;
  line-height: 1.4;
}

.markdown-content h1 {
  font-size: 24px;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 8px;
}

.markdown-content h2 {
  font-size: 22px;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 6px;
}

.markdown-content h3 {
  font-size: 20px;
  color: #2d3748;
}

.markdown-content h4 {
  font-size: 18px;
  color: #4a5568;
}

.markdown-content h5 {
  font-size: 16px;
  color: #4a5568;
}

.markdown-content h6 {
  font-size: 14px;
  color: #4a5568;
}

.markdown-content p {
  margin: 2px 0;
  line-height: 1.6;
}

.markdown-content ul,
.markdown-content ol {
  margin: 2px 0;
  padding-left: 24px;
}

.markdown-content li {
  margin: 1px 0;
  line-height: 1.5;
}

.markdown-content strong,
.markdown-content b {
  font-weight: 600;
  color: #1a202c;
}

.markdown-content em,
.markdown-content i {
  font-style: italic;
  color: #4a5568;
}

.markdown-content code {
  background: #f7fafc;
  color: #e53e3e;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
}

.markdown-content pre {
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 6px;
  overflow-x: auto;
  margin: 3px 0;
}

.markdown-content pre code {
  background: none;
  color: #2d3748;
  padding: 0;
}

.markdown-content blockquote {
  border-left: 4px solid #3182ce;
  background: #f7fafc;
  margin: 3px 0;
  padding: 4px 8px;
  color: #4a5568;
  font-style: italic;
}

.markdown-content hr {
  border: none;
  border-top: 1px solid #e2e8f0;
  margin: 4px 0;
}

.markdown-content table {
  border-collapse: collapse;
  width: 100%;
  margin: 3px 0;
}

.markdown-content th,
.markdown-content td {
  border: 1px solid #e2e8f0;
  padding: 8px 12px;
  text-align: left;
}

.markdown-content th {
  background: #f7fafc;
  font-weight: 600;
  color: #1a202c;
}

.markdown-content tr:nth-child(even) {
  background: #f9fafb;
}



/* 澄清追问卡片样式 */
.clarification-question {
  margin: 20px 0 12px 0;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.question-text {
  color: #2d3748;
  font-size: 16px;
  line-height: 1.6;
  font-weight: 500;
}

.question-type {
  display: flex;
  align-items: center;
  background: white;
  color: #1e40af;
  border: 2px solid #1e40af;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.type-text {
  font-size: 12px;
}

.clarification-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border: 1px solid #e2e8f0;
  position: relative;
  margin-bottom: 20px;
}

.clarification-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.clarification-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #f8fafc;
}

.clarification-option:hover {
  background: #f1f5f9;
  border-color: #3b82f6;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
}

.option-checkbox {
  width: 20px;
  height: 20px;
  border: 2px solid #cbd5e1;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s ease;
  position: relative;
}

.checkbox-single {
  border-radius: 50%;
}

.checkbox-multiple {
  border-radius: 4px;
}

.clarification-option:hover .option-checkbox {
  border-color: #3b82f6;
}

.clarification-option.selected .option-checkbox {
  border-color: #3b82f6;
  background: #3b82f6;
}

.checkbox-inner {
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.checkbox-multiple .checkbox-inner {
  border-radius: 1px;
}

.clarification-option.selected .checkbox-inner {
  opacity: 1;
}

.option-text {
  flex: 1;
  color: #1e293b;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.4;
}

.clarification-confirm {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.confirm-button {
  background: #dbeafe;
  color: #1e40af;
  border: none;
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
  max-width: none;
}

.confirm-button:hover {
  background: #bfdbfe;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(30, 64, 175, 0.2);
}

.confirm-button:active {
  transform: translateY(0);
}

.confirm-button:disabled {
  background: #e2e8f0;
  color: #94a3b8;
  cursor: not-allowed;
  transform: none;
}

.confirm-button:disabled:hover {
  background: #e2e8f0;
  transform: none;
  box-shadow: none;
}

/* 移动端响应式 */
@media (max-width: 768px) {
  .clarification-question {
    gap: 8px;
  }
  
  .question-text {
    font-size: 14px;
  }
  
  .question-type {
    padding: 3px 6px;
    font-size: 11px;
  }
  
  .type-text {
    font-size: 11px;
  }
  
  .clarification-card {
    padding: 16px;
  }
  
  .clarification-option {
    padding: 10px 12px;
  }
  
  .option-text {
    font-size: 14px;
  }
  
  .confirm-button {
    padding: 10px 16px;
    font-size: 14px;
  }
}
</style>

<style scoped>
/* 返回按钮样式 */
.back-button {
  position: fixed;
  top: 16px;
  left: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  cursor: pointer;
  z-index: 100;
  transition: all 0.2s ease;
}

.back-button:hover {
  opacity: 0.8;
}

.back-icon {
  font-size: 16px;
  font-weight: bold;
  color: #666;
}

.upload-btn {
  cursor: pointer;
  display: flex;
  align-items: center;
}
.plus-icon {
  font-size: 20px;
}



.voice-button {
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background-color: #ff6700;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.voice-button:hover:not(.disabled) {
  background-color: #e65c00;
  transform: scale(1.05);
}

.voice-button.disabled {
  background-color: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}

.send-icon {
  color: white;
  font-size: 16px;
  font-weight: bold;
}
</style>
