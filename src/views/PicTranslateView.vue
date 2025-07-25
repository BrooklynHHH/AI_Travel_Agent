<template>
  <div class="container">
    <h1>多平台图片翻译</h1>

    <div class="upload-area">
      <input type="file" accept="image/*" @change="handleFileChange" />
      <div>
        <label for="targetLang">目标语言: </label>
        <select v-model="targetLang" id="targetLang">
          <option value="en">英语</option>
          <option value="zh">中文</option>
          <option value="ja">日语</option>
          <option value="ko">韩语</option>
          <option value="fr">法语</option>
          <option value="de">德语</option>
        </select>
      </div>
      <button :disabled="!file" @click="startTranslation">开始翻译</button>
    </div>

    <div class="results">
      <div class="platform-result">
        <h3>原图</h3>
        <div class="image-container">
          <img 
            v-if="originalImage" 
            :src="originalImage" 
            class="result-image clickable-image"
            @click="showImageViewer(originalImage, '原图')"
            alt=""
          />
          <div v-else class="placeholder">请上传图片</div>
        </div>
      </div>

      <div
          v-for="platform in platforms"
          :key="platform.name"
          class="platform-result"
      >
        <h3>{{ platform.display }}</h3>
        <div class="image-container">
          <div v-if="platform.loading" class="loading">处理中...</div>
          <img
              v-else-if="platform.image"
              :src="platform.image"
              class="result-image clickable-image"
              @click="showImageViewer(platform.image, platform.display)"
              alt=""
          />
          <div v-else class="placeholder">等待翻译</div>
        </div>
        <p v-if="platform.time" class="time-info">
          处理时间: {{ platform.time }}ms
        </p>
      </div>
    </div>

    <!-- 图片查看器 -->
    <ImageViewer
      v-model:show="imageViewerShow"
      :images="currentImages"
      :current-index="currentImageIndex"
      :keyword="currentImageTitle"
      @update:current-index="currentImageIndex = $event"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { translateImage } from '@/api/pic-translate'
import ImageViewer from '@/components/modals/ImageViewer.vue'

const file = ref(null)
const originalImage = ref(null)
const targetLang = ref('en')

// 图片查看器相关
const imageViewerShow = ref(false)
const currentImages = ref([])
const currentImageIndex = ref(0)
const currentImageTitle = ref('')

const platforms = ref([
  { name: 'aliyun', display: '阿里云翻译', image: null, time: null, loading: false },
  { name: 'baidu', display: '百度翻译', image: null, time: null, loading: false },
  { name: 'volc', display: '火山翻译', image: null, time: null, loading: false }
])

// 显示图片查看器
function showImageViewer(imageUrl, title) {
  currentImages.value = [{ url: imageUrl, keyword: title }]
  currentImageIndex.value = 0
  currentImageTitle.value = title
  imageViewerShow.value = true
}

function handleFileChange(event) {
  const selected = event.target.files[0]
  if (selected) {
    file.value = selected
    const reader = new FileReader()
    reader.onload = e => {
      originalImage.value = e.target.result
    }
    reader.readAsDataURL(selected)
  }
}

async function startTranslation() {
  if (!file.value) return

  platforms.value.forEach(p => {
    p.loading = true
    p.image = null
    p.time = null
  })

  const promises = platforms.value.map(async p => {
    const start = performance.now()
    try {
      const data = await translateImage(p.name, file.value, targetLang.value)
      p.image = 'data:image/jpeg;base64,' + data
      p.time = Math.round(performance.now() - start)
    } catch (e) {
      p.image = null
    } finally {
      p.loading = false
    }
  })

  await Promise.all(promises)
}
</script>

<style scoped>
body {
  font-family: 'Arial', sans-serif;
  max-width: 2000px;
  margin: 0 auto;
  padding: 20px;
}

.upload-area {
  border: 2px dashed #ccc;
  padding: 20px;
  text-align: center;
  margin-bottom: 20px;
  border-radius: 5px;
}

.results {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.platform-result {
  flex: 1;
  min-width: 250px;
  border: 1px solid #eee;
  padding: 15px;
  border-radius: 5px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.platform-result img {
  max-width: 100%;
  margin-top: 10px;
  border-radius: 4px;
}

.time-info {
  color: #666;
  font-size: 0.9em;
  margin-top: 5px;
}

select,
button {
  padding: 8px 15px;
  margin: 10px 5px;
  border-radius: 4px;
}

button {
  background-color: #4caf50;
  color: white;
  border: none;
  cursor: pointer;
}

button:disabled {
  background-color: #cccccc;
}

.loading {
  color: #666;
  font-style: italic;
}

.clickable-image {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.clickable-image:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>
