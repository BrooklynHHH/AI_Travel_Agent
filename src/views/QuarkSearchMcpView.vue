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
    <SettingsModal
      v-model:show="showSettingsModal"
      :apiKey="apiKeyInput"
      @save="saveApiKey"
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
              <!-- 思考面板移到message-bubble内部，放在response-text上方 -->
              <div v-if="message.thinkContent || message.streaming" class="think-panel">
                <details :open="message.thinkingOpen">
                  <summary>已深度思考</summary>
                  <div v-if="message.streaming" class="think-content">
                    <div v-html="renderMarkdown(message.thinkContent)"></div><span class="cursor">|</span>
                  </div>
                  <div v-else class="think-content" v-html="renderMarkdown(message.thinkContent)"></div>
                </details>
              </div>
              <div v-if="message.streaming" class="response-text">
                <div v-html="renderMarkdown(message.content)"></div><span class="cursor">|</span>
              </div>
              <div v-else class="response-text" v-html="renderMarkdown(message.content)"></div>
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
        />
        <div class="voice-button" @click="sendMessage">
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
import ImageViewer from '../components/modals/ImageViewer.vue';
import ProductWindow from '../components/modals/ProductWindow.vue';
import SettingsModal from '../components/modals/SettingsModal.vue';
import VideoPlayer from '../components/modals/VideoPlayer.vue';
import MarkdownIt from 'markdown-it';
import markdownItKatex from 'markdown-it-katex';
// 已在main.js全局导入，此处移除: import 'katex/dist/katex.min.css';
import { createWorker, createScheduler } from 'tesseract.js';
import FabricCanvas from '../components/FabricCanvas.vue';

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
  conversationId.value = `ocr_${timestamp}`;
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
      streaming: true,
      thinkingOpen: false // 初始化思考面板为关闭状态
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
    
    // 处理流式输出
    // 用于跟踪思考状态
    let inThinkingMode = false;
    let thinkingContent = '';
    let visibleContent = '';
    
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
      
      // 处理可能包含多个<think>和</think>标签的情况
      let remainingText = newText;
      
      while (remainingText.length > 0) {
        // 检查是否包含<think>标签
        const thinkStartIndex = remainingText.indexOf('<think>');
        // 检查是否包含</think>标签
        const thinkEndIndex = remainingText.indexOf('</think>');
        
        // 情况1: 没有<think>和</think>标签
        if (thinkStartIndex === -1 && thinkEndIndex === -1) {
          // 如果在思考模式中，添加到思考内容
          if (inThinkingMode) {
            thinkingContent += remainingText;
            // 实时更新思考内容到消息对象，实现流式效果
            messages.value[lastIndex].thinkContent = thinkingContent;
          } else {
            // 否则添加到可见内容
            visibleContent += remainingText;
          }
          break;
        }
        
        // 情况2: 只有<think>标签
        else if (thinkStartIndex !== -1 && thinkEndIndex === -1) {
          // <think>标签之前的内容
          if (thinkStartIndex > 0) {
            if (inThinkingMode) {
              thinkingContent += remainingText.substring(0, thinkStartIndex);
              // 实时更新思考内容到消息对象，实现流式效果
              messages.value[lastIndex].thinkContent = thinkingContent;
            } else {
              visibleContent += remainingText.substring(0, thinkStartIndex);
            }
          }
          
          // 进入思考模式
          inThinkingMode = true;
          console.log('开始思考模式');
          
          // 设置思考面板为展开状态
          messages.value[lastIndex].thinkingOpen = true;
          
          // <think>标签之后的内容添加到思考内容
          thinkingContent += remainingText.substring(thinkStartIndex + 7);
          break;
        }
        
        // 情况3: 只有</think>标签
        else if (thinkStartIndex === -1 && thinkEndIndex !== -1) {
          // </think>标签之前的内容
          if (thinkEndIndex > 0) {
            if (inThinkingMode) {
              thinkingContent += remainingText.substring(0, thinkEndIndex);
              // 实时更新思考内容到消息对象，实现流式效果
              messages.value[lastIndex].thinkContent = thinkingContent;
            } else {
              visibleContent += remainingText.substring(0, thinkEndIndex);
            }
          }
          
          // 如果在思考模式中，保存思考内容
          if (inThinkingMode) {
            console.log('结束思考模式');
            
            // 保存思考内容到消息对象
            messages.value[lastIndex].thinkContent = thinkingContent;
            
            // 设置思考面板为关闭状态
            messages.value[lastIndex].thinkingOpen = false;
            
            // 重置思考状态
            inThinkingMode = false;
            thinkingContent = '';
          }
          
          // </think>标签之后的内容添加到可见内容
          visibleContent += remainingText.substring(thinkEndIndex + 8);
          break;
        }
        
        // 情况4: 同时有<think>和</think>标签
        else {
          // 先处理<think>标签
          if (thinkStartIndex < thinkEndIndex) {
            // <think>标签之前的内容
            if (thinkStartIndex > 0) {
              if (inThinkingMode) {
                thinkingContent += remainingText.substring(0, thinkStartIndex);
                // 实时更新思考内容到消息对象，实现流式效果
                messages.value[lastIndex].thinkContent = thinkingContent;
              } else {
                visibleContent += remainingText.substring(0, thinkStartIndex);
              }
            }
            
            // 进入思考模式
            inThinkingMode = true;
            console.log('开始思考模式');
            
            // 设置思考面板为展开状态
            messages.value[lastIndex].thinkingOpen = true;
            
            // 更新剩余文本，继续处理
            remainingText = remainingText.substring(thinkStartIndex + 7);
          }
          // 先处理</think>标签
          else {
            // </think>标签之前的内容
            if (thinkEndIndex > 0) {
              if (inThinkingMode) {
                thinkingContent += remainingText.substring(0, thinkEndIndex);
                // 实时更新思考内容到消息对象，实现流式效果
                messages.value[lastIndex].thinkContent = thinkingContent;
              } else {
                visibleContent += remainingText.substring(0, thinkEndIndex);
              }
            }
            
            // 如果在思考模式中，保存思考内容
            if (inThinkingMode) {
              console.log('结束思考模式');
              
              // 保存思考内容到消息对象
              messages.value[lastIndex].thinkContent = thinkingContent;
              
              // 设置思考面板为关闭状态
              messages.value[lastIndex].thinkingOpen = false;
              
              // 重置思考状态
              inThinkingMode = false;
              thinkingContent = '';
            }
            
            // 更新剩余文本，继续处理
            remainingText = remainingText.substring(thinkEndIndex + 8);
          }
          
          // 如果剩余文本为空，跳出循环
          if (remainingText.length === 0) {
            break;
          }
          
          // 继续处理剩余文本
          continue;
        }
      }
      
      // 更新消息内容
      streamingContent = visibleContent;
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

// Markdown 渲染
const md = new MarkdownIt({ 
  html: true, 
  linkify: true, 
  typographer: true, 
  breaks: true 
});
// 配置KaTeX选项，确保公式正确渲染
md.use(markdownItKatex, {
  throwOnError: false,
  errorColor: '#cc0000',
  macros: {
    // 添加常用宏命令支持
    "\\boldsymbol": "\\mathbf"
  },
  delimiters: [
    {left: '$$', right: '$$', display: true},
    {left: '$', right: '$', display: false},
    {left: '\\(', right: '\\)', display: false},
    {left: '\\[', right: '\\]', display: true}
  ]
});

// 处理<think>标签并提取思考内容
const processThinkTags = (content) => {
  if (!content) return { content: '', thinkContent: '' };
  
  // 使用正则表达式匹配<think>和</think>之间的内容
  const thinkRegex = /<think>([\s\S]*?)<\/think>/g;
  let thinkContent = '';
  
  // 提取所有思考内容并从原内容中移除
  const processedContent = content.replace(thinkRegex, (match, content) => {
    console.log('找到思考内容:', content.substring(0, 50) + '...');
    thinkContent += content + '\n\n';
    return '';
  });
  
  return {
    content: processedContent.trim(),
    thinkContent: thinkContent.trim()
  };
};

const renderMarkdown = (content) => {
  if (!content) return '';
  
  // 先处理<think>标签，提取思考内容
  const { content: processedContent } = processThinkTags(content);
  
  // 处理LaTeX分隔符 \( \) 转换为 $ $ 以确保正确渲染
  let latexProcessedContent = processedContent
    .replace(/\\\(/g, '$')
    .replace(/\\\)/g, '$');
  
  // 使用正则表达式检测非分隔符内的\boldsymbol并转换为\mathbf
  // 这是因为有些KaTeX版本不支持\boldsymbol，但支持\mathbf
  latexProcessedContent = latexProcessedContent.replace(/(\$.*?)\\boldsymbol(\{.*?\})(.*?\$)/g, "$1\\mathbf$2$3");
  
  // 然后渲染Markdown
  return md.render(latexProcessedContent);
};

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
const showSettingsModal = ref(false);
const apiKeyInput = ref('');
const showVideoPlayer = ref(false);
const videoUrl = ref('');
const videoTitle = ref('');
const videoAvatar = ref('');
const videoLikeCount = ref(0);
const videoCommentCount = ref(0);
const videoDescription = ref('');
const isStreaming = ref(false);

// 写死 DashScope appId 和 apiKey
const appId = '68014bd632a34bbc999b4ccfe6d4f4eb'; // TODO: 替换为你的AppId
const apiKey = 'sk-d889c439ee5c44d080cb769a5e4bda53'; // TODO: 替换为你的API Key

// 保存API密钥
const saveApiKey = (key) => {
  console.log('保存API密钥:', key);
  apiKeyInput.value = key;
  showSettingsModal.value = false;
};

// 发送消息
const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return;

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: userInput.value
  });

  const userMessage = userInput.value;
  userInput.value = '';
  isLoading.value = true;

  try {
    // 创建占位AI消息
    const lastIndex = messages.value.push({
      role: 'assistant',
      content: '正在查询，请稍候...'
    }) - 1;

    // 构造请求
    const response = await fetch(`https://dashscope.aliyuncs.com/api/v1/apps/${appId}/completion`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        input: { prompt: userMessage },
        parameters: {},
        debug: {}
      })
    });

    if (!response.ok) throw new Error('API请求失败');

    const result = await response.json();
    // 假设返回内容在 result.output.text
    messages.value[lastIndex].content = result.output?.text || '未获取到回复';

  } catch (e) {
    messages.value.push({
      role: 'assistant',
      content: '查询失败，请稍后重试。'
    });
  } finally {
    isLoading.value = false;
  }
};
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

/* 深度思考面板样式 */
:deep(.think-panel) {
  margin: 10px 0;
  border-radius: 8px;
  overflow: hidden;
  background-color: #f5f7fa;
}

:deep(.think-panel details) {
  width: 100%;
}

:deep(.think-panel summary) {
  padding: 10px 15px;
  background-color: #e8edf3;
  cursor: pointer;
  font-weight: 500;
  color: #4a5568;
  display: flex;
  align-items: center;
  position: relative;
}

:deep(.think-panel summary::before) {
  content: "▶";
  margin-right: 8px;
  font-size: 12px;
  transition: transform 0.3s;
}

:deep(.think-panel details[open] summary::before) {
  transform: rotate(90deg);
}

:deep(.think-panel .think-content) {
  padding: 15px;
  color: #2d3748;
  line-height: 1.6;
}
</style>
