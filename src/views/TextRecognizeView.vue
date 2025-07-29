<template>
  <div class="ocr-container">
    <!-- 图片上传区域 - 紧凑型设计 -->
    <div class="upload-container">
      <div class="upload-layout">
        <!-- 左侧上传区 -->
        <div
            class="upload-area"
            @dragover.prevent="onDragOver"
            @dragleave.prevent="onDragLeave"
            @drop.prevent="onDrop"
            :class="{ 'drag-over': isDragging }"
        >
          <div class="upload-content">
            <div class="upload-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="17 8 12 3 7 8"></polyline>
                <line x1="12" y1="3" x2="12" y2="15"></line>
              </svg>
            </div>
            <p class="upload-text">拖拽图片或 <label for="file-input" class="upload-link">点击上传</label></p>
            <input
                type="file"
                id="file-input"
                class="file-input"
                accept="image/*"
                @change="onFileSelected"
            />
          </div>
        </div>

        <!-- 右侧预览和按钮 -->
        <div class="image-preview">
          <h1 class="page-title">OCR工具测试界面</h1>
          <img :src="imageUrl" class="preview-image" alt="预览图片" v-if="imageUrl"  />
          <button class="process-button" @click="processImage" :disabled="isProcessing" v-if="imageUrl" >
            <span v-if="isProcessing" class="loading-spinner2"></span>
            <span>{{ isProcessing ? '处理中...' : '开始OCR识别' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- OCR结果展示区域 -->
    <div class="results-container">
      <div v-for="(item, key) in ocrResults" :key="key" class="result-card">
        <div class="card-header">
          <span class="card-title">{{ item.title }}</span>
          <span v-if="item.responseTime !== null" class="response-time">
            响应时间: {{ item.responseTime }}ms
          </span>
        </div>

        <div class="card-body">
          <div v-if="item.loading" class="loading-overlay">
            <div class="loading-spinner2"></div>
          </div>

          <div v-else-if="item.error" class="error-message">
            <div class="error-alert">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
              <span>{{ item.error }}</span>
            </div>
          </div>

          <pre v-else class="result-content">{{ item.result || '暂无结果' }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import {callDoubaoVisionOcr, callAliyunOcr, callBaiduOcr, callRapidOcr, callTencentOcr} from '@/api/ocr'

// 图片上传相关
const imageFile = ref(null)
const imageUrl = ref('')
const isProcessing = ref(false)
const isDragging = ref(false)

// OCR结果
const ocrResults = reactive({
  doubaoVision: {
    title: '豆包视觉模型文字识别',
    result: '',
    loading: false,
    error: '',
    responseTime: null
  },
  aliyunOcr: {
    title: '阿里云OCR',
    result: '',
    loading: false,
    error: '',
    responseTime: null
  },
  baiduOcr: {
    title: '百度OCR',
    result: '',
    loading: false,
    error: '',
    responseTime: null
  },
  rapidOcr: {
    title: 'RapidOCR',
    result: '',
    loading: false,
    error: '',
    responseTime: null
  },
  tencentOcr: {
    title: '腾讯云OCR',
    result: '',
    loading: false,
    error: '',
    responseTime: null
  },
  reservedOcr: {
    title: '预留OCR接口',
    result: '预留OCR接口',
    loading: false,
    error: '',
    responseTime: null
  }
})

// 处理拖拽事件
const onDragOver = () => {
  isDragging.value = true
}

const onDragLeave = () => {
  isDragging.value = false
}

const onDrop = (event) => {
  isDragging.value = false
  const files = event.dataTransfer.files
  if (files.length > 0) {
    handleFile(files[0])
  }
}

// 处理文件选择
const onFileSelected = (event) => {
  const files = event.target.files
  if (files.length > 0) {
    handleFile(files[0])
  }
}

const handleFile = (file) => {
  if (!file.type.match('image.*')) {
    alert('请选择图片文件')
    return
  }

  imageFile.value = file
  imageUrl.value = URL.createObjectURL(file)
}

// 显示错误消息
const showError = (message) => {
  alert(message)
}

// 处理OCR识别
const processImage = async () => {
  if (!imageFile.value) {
    showError('请先选择一张图片')
    return
  }

  isProcessing.value = true

  // 重置所有结果
  Object.keys(ocrResults).forEach(key => {
    if (key !== 'reservedOcr1' && key !== 'reservedOcr2') {
      ocrResults[key].result = ''
      ocrResults[key].loading = true
      ocrResults[key].error = ''
      ocrResults[key].responseTime = null
    }
  })

  // 创建FormData对象
  const formData = new FormData()
  formData.append('image', imageFile.value)

  try {
    // 并行调用所有OCR接口
    await Promise.all([
      callDoubaoVisionOcr(formData).then(response => {
        ocrResults.doubaoVision.result = response.data
        ocrResults.doubaoVision.responseTime = response.time
        ocrResults.doubaoVision.loading = false
      }).catch(error => {
        ocrResults.doubaoVision.error = `请求失败: ${error.message}`
        ocrResults.doubaoVision.loading = false
      }),

      callAliyunOcr(formData).then(response => {
        ocrResults.aliyunOcr.result = response.data
        ocrResults.aliyunOcr.responseTime = response.time
        ocrResults.aliyunOcr.loading = false
      }).catch(error => {
        ocrResults.aliyunOcr.error = `请求失败: ${error.message}`
        ocrResults.aliyunOcr.loading = false
      }),

      callBaiduOcr(formData).then(response => {
        ocrResults.baiduOcr.result = response.data
        ocrResults.baiduOcr.responseTime = response.time
        ocrResults.baiduOcr.loading = false
      }).catch(error => {
        ocrResults.baiduOcr.error = `请求失败: ${error.message}`
        ocrResults.baiduOcr.loading = false
      }),

      callRapidOcr(formData).then(response => {
        ocrResults.rapidOcr.result = response.data
        ocrResults.rapidOcr.responseTime = response.time
        ocrResults.rapidOcr.loading = false
      }).catch(error => {
        ocrResults.rapidOcr.error = `请求失败: ${error.message}`
        ocrResults.rapidOcr.loading = false
      }),

      callTencentOcr(formData).then(response => {
        ocrResults.tencentOcr.result = response.data
        ocrResults.tencentOcr.responseTime = response.time
        ocrResults.tencentOcr.loading = false
      }).catch(error => {
        ocrResults.tencentOcr.error = `请求失败: ${error.message}`
        ocrResults.tencentOcr.loading = false
      }),
    ])
  } catch (error) {
    showError('处理过程中发生错误')
    console.error('处理过程中发生错误:', error)
  } finally {
    isProcessing.value = false
  }
}
</script>

<style scoped>
.ocr-container {
  max-width: 1800px;
  margin: 0 auto;
  padding: 10px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.page-title {
  text-align: center;
  margin: 10px 0;
  color: #333;
  font-size: 1.5rem;
}

.upload-container {
  background-color: white;
  border-radius: 8px;
  padding: 10px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-bottom: 15px;
}

.upload-layout {
  display: flex;
  align-items: center;
  gap: 15px;
}

.upload-area {
  flex: 1;
  border: 2px dashed #dcdfe6;
  border-radius: 6px;
  padding: 10px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  min-height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.upload-area.drag-over {
  border-color: #409eff;
  background-color: rgba(64, 158, 255, 0.06);
}

.upload-icon {
  color: #909399;
  margin-bottom: 5px;
}

.upload-text {
  color: #606266;
  font-size: 14px;
  margin: 0;
}

.upload-link {
  color: #409eff;
  cursor: pointer;
}

.file-input {
  display: none;
}

.image-preview {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.preview-image {
  max-width: 100%;
  max-height: 120px;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 10px;
}

.process-button {
  background-color: #409eff;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: inline-flex;
  align-items: center;
  transition: background-color 0.3s;
}

.process-button:hover {
  background-color: #66b1ff;
}

.process-button:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.results-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
}

.result-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-header {
  padding: 8px 12px;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f5f7fa;
}

.card-title {
  font-weight: bold;
  color: #303133;
  font-size: 14px;
}

.response-time {
  font-size: 12px;
  color: #909399;
}

.card-body {
  position: relative;
  height: 200px; /* 减小高度以适应屏幕 */
}

.result-content {
  height: 100%;
  overflow-y: auto;
  white-space: pre-wrap;
  font-family: monospace;
  font-size: 12px;
  padding: 10px;
  background-color: #f8f8f8;
  margin: 0;
  color: #303133;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.7);
}

.loading-spinner2 {
  display: inline-block;
  width: 16px;
  height: 16px;
  margin-right: 6px;
  border: 2px solid rgba(64, 158, 255, 0.3);
  border-radius: 50%;
  border-top-color: #409eff;
  animation: spin 1s linear infinite;
}

.error-message {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 10px;
}

.error-alert {
  background-color: #fef0f0;
  color: #f56c6c;
  padding: 10px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  font-size: 12px;
}

.error-alert svg {
  margin-right: 8px;
  color: #f56c6c;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .results-container {
    grid-template-columns: 1fr;
  }

  .upload-layout {
    flex-direction: column;
  }
}

</style>
