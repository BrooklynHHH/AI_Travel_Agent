    <template>
  <div class="video-gen-page">
    <div class="container">
      <!-- 输入区域 -->
      <div class="input-section">
        <div class="input-card">
          <h2>视频生成</h2>
          
          <!-- 提示词输入 -->
          <div class="form-group">
            <label>提示词 *</label>
            <textarea 
              v-model="prompt" 
              placeholder="请输入视频生成的提示词描述..."
              rows="4"
              class="prompt-input"
            ></textarea>
          </div>

          <!-- 图片上传（可选） -->
          <div class="form-group">
            <label>参考图片（可选）</label>
            <div class="upload-area" @click="triggerFileInput">
              <input 
                ref="fileInput" 
                type="file" 
                accept="image/*" 
                @change="handleImageUpload" 
                style="display: none"
              >
              <div v-if="!referenceImage" class="upload-placeholder">
                <div class="upload-icon">📷</div>
                <p>点击上传参考图片（图生视频）</p>
                <p class="upload-hint">支持 JPG、PNG 格式</p>
              </div>
              <div v-else class="uploaded-image">
                <img :src="referenceImage" alt="参考图片" />
                <button @click.stop="removeImage" class="remove-btn">×</button>
              </div>
            </div>
          </div>

          <!-- 参数选择区域 - 一行四个布局 -->
          <div class="form-group-grid">
            <!-- 第一行 -->
            <div class="form-group">
              <label>分辨率</label>
              <select v-model="resolution" class="param-select">
                <option value="480p">480p</option>
                <option value="720p">720p</option>
                <option value="1080p">1080p</option>
              </select>
            </div>

            <div class="form-group">
              <label>宽高比</label>
              <select v-model="ratio" class="param-select">
                <option value="16:9">16:9</option>
                <option value="9:16">9:16</option>
                <option value="1:1">1:1</option>
                <option value="21:9">21:9 (仅火山支持)</option>
                <option value="4:3">4:3 (仅火山支持)</option>
                <option value="3:4">3:4 (仅火山支持)</option>
                <option value="9:21">9:21 (仅火山支持)</option>
                <option value="keep_ratio">keep_ratio (仅火山支持)</option>
                <option value="adaptive">adaptive (仅火山支持)</option>
              </select>
            </div>

            <div class="form-group">
              <label>时长（秒）</label>
              <select v-model="duration" class="param-select">
                <option value="5">5秒</option>
                <option value="10">10秒</option>
              </select>
            </div>

            <div class="form-group">
              <label>帧率 <span class="unsupported-label">(可灵不支持)</span></label>
              <select v-model="framepersecond" class="param-select">
                <option value="24">24fps</option>
              </select>
            </div>
            
            <!-- 第二行 -->
            <div class="form-group">
              <label>水印设置 <span class="unsupported-label">(可灵不支持)</span></label>
              <select v-model="watermark" class="param-select">
                <option :value="false">无水印</option>
                <option :value="true">带水印</option>
              </select>
            </div>

            <div class="form-group">
              <label>种子值 <span class="unsupported-label">(可灵不支持)</span></label>
              <input 
                v-model.number="seed" 
                type="number" 
                class="param-input"
                placeholder="输入种子值，-1为随机"
              />
            </div>

            <div class="form-group">
              <label>摄像头设置 <span class="unsupported-label">(可灵不支持)</span></label>
              <select v-model="camerafixed" class="param-select">
                <option :value="false">摄像头移动</option>
                <option :value="true">摄像头固定</option>
              </select>
            </div>
          </div>

          <!-- 生成按钮 -->
          <button 
            @click="generateVideos" 
            :disabled="!prompt || isGenerating"
            class="generate-btn"
          >
            {{ isGenerating ? '生成中...' : '开始生成视频' }}
          </button>
        </div>
      </div>

      <!-- 结果展示区域 -->
      <div class="results-section">
        <!-- 上排：豆包模型 -->
        <div class="models-row">
          <h3>豆包模型</h3>
          <div class="models-grid">
            <div 
              v-for="model in volcModels" 
              :key="model.modelId"
              class="model-card"
            >
              <div class="model-header">
                <div>
                  <h4>{{ model.displayName }}</h4>
                  <span class="model-id">ID: {{ model.id || model.modelId || model.model_id || model.name }}</span>
                </div>
                <span v-if="model.responseTime" class="time-info">{{ (model.responseTime / 1000).toFixed(2) }}秒</span>
              </div>
              
              <div class="model-content">
                <div v-if="model.loading" class="loading-state">
                  <div class="spinner"></div>
                  <p>生成中...</p>
                </div>
                
                <div v-else-if="model.error" class="error-state">
                  <div class="error-icon">❌</div>
                  <p>{{ model.error }}</p>
                  <button @click="testSingleModel(model, 'volc')" class="test-btn">重新测试</button>
                </div>
                
              <div v-else-if="model.videoUrl" class="video-result">
                  <video :src="model.videoUrl" controls class="result-video"></video>
                  <div class="model-info">
                    <p><strong>任务ID:</strong> {{ model.taskId }}</p>
                    <p><strong>状态:</strong> {{ model.status }}</p>
                    <p v-if="model.tokens"><strong>Token数量:</strong> {{ model.tokens }}</p>
                  </div>
                  <button @click="testSingleModel(model, 'volc')" class="test-btn">重新测试</button>
                </div>
                
                <div v-else class="waiting-state">
                  <div v-if="model.exampleUrl" class="example-video">
                    <video :src="model.exampleUrl" controls class="result-video"></video>
                    <p class="example-label">示例视频</p>
                  </div>
                  <div v-else>
                    <div class="waiting-icon">⏳</div>
                    <p>等待生成</p>
                  </div>
                  <button @click="testSingleModel(model, 'volc')" class="test-btn">测试此模型</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 下排：可灵模型 -->
        <div class="models-row">
          <h3>可灵模型</h3>
          <div class="models-grid">
            <div 
              v-for="model in klingModels" 
              :key="model.modelId"
              class="model-card"
            >
              <div class="model-header">
                <div>
                  <h4>{{ model.displayName }}</h4>
                  <span class="model-id">ID: {{ model.id || model.modelId || model.model_id || model.name }}</span>
                </div>
                <span v-if="model.responseTime" class="time-info">{{ (model.responseTime / 1000).toFixed(2) }}秒</span>
              </div>
              
              <div class="model-content">
                <div v-if="model.loading" class="loading-state">
                  <div class="spinner"></div>
                  <p>生成中...</p>
                </div>
                
                <div v-else-if="model.error" class="error-state">
                  <div class="error-icon">❌</div>
                  <p>{{ model.error }}</p>
                  <button @click="testSingleModel(model, 'kling')" class="test-btn">重新测试</button>
                </div>
                
                <div v-else-if="model.videoUrl" class="video-result">
                  <video :src="model.videoUrl" controls class="result-video"></video>
                  <div class="model-info">
                    <p><strong>任务ID:</strong> {{ model.taskId }}</p>
                    <p><strong>状态:</strong> {{ model.status }}</p>
                    <p v-if="model.duration"><strong>视频时长:</strong> {{ model.duration }}秒</p>
                    <p v-if="model.createdAt"><strong>创建时间:</strong> {{ new Date(model.createdAt).toLocaleString() }}</p>
                  </div>
                  <button @click="testSingleModel(model, 'kling')" class="test-btn">重新测试</button>
                </div>
                
                <div v-else class="waiting-state">
                  <div v-if="model.exampleUrl" class="example-video">
                    <video :src="model.exampleUrl" controls class="result-video"></video>
                    <p class="example-label">示例视频</p>
                  </div>
                  <div v-else>
                    <div class="waiting-icon">⏳</div>
                    <p>等待生成</p>
                  </div>
                  <button @click="testSingleModel(model, 'kling')" class="test-btn">测试此模型</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { 
  getVolcModels, 
  getKlingModels, 
  generateVolcVideo, 
  generateKlingVideo,
  queryVolcTask,
  queryKlingTask
} from '../api/video-gen'

// 响应式数据
const prompt = ref('一只绒毛柔软的家猫,直立在后腿上,模仿人类敬礼动作。右前爪笔直抬起至额头,手指(爪尖)分明,动作干净利落,对着镜头做眨眼的搞怪表情;然后缓缓放下。猫咪神情专注,眼神坚定。')
const referenceImage = ref(null)
const referenceImageFile = ref(null)
const resolution = ref('1080p')
const ratio = ref('16:9')
const duration = ref(5)
const framepersecond = ref(24)
const watermark = ref(false)
const seed = ref(-1)
const camerafixed = ref(false)
const isGenerating = ref(false)

const volcModels = ref([])
const klingModels = ref([])

const fileInput = ref(null)

// 生命周期
onMounted(async () => {
  await loadModels()
})

// 方法
async function loadModels() {
  try {
    // 加载豆包模型
    const volcModelList = await getVolcModels()
    volcModels.value = volcModelList.map(model => ({
      ...model,
      loading: false,
      error: null,
      videoUrl: null,
      taskId: null,
      status: null,
      responseTime: null
    }))

    // 加载可灵模型
    const klingModelList = await getKlingModels()
    klingModels.value = klingModelList.map(model => ({
      ...model,
      loading: false,
      error: null,
      videoUrl: null,
      taskId: null,
      status: null,
      responseTime: null
    }))
  } catch (error) {
    console.error('加载模型列表失败:', error)
  }
}

function triggerFileInput() {
  fileInput.value?.click()
}

function handleImageUpload(event) {
  const file = event.target.files[0]
  if (file) {
    referenceImageFile.value = file
    const reader = new FileReader()
    reader.onload = (e) => {
      referenceImage.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

function removeImage() {
  referenceImage.value = null
  referenceImageFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

async function generateVideos() {
  if (!prompt.value.trim()) {
    alert('请输入提示词')
    return
  }

  isGenerating.value = true

  // 重置所有模型状态
  volcModels.value = volcModels.value.map(model => ({
    ...model,
    loading: true,
    error: null,
    videoUrl: null,
    taskId: null,
    status: null,
    responseTime: null
  }))
  
  klingModels.value = klingModels.value.map(model => ({
    ...model,
    loading: true,
    error: null,
    videoUrl: null,
    taskId: null,
    status: null,
    responseTime: null
  }))

  // 并行生成视频
  const promises = [
    ...volcModels.value.map(model => generateVideoForModel(model, 'volc')),
    ...klingModels.value.map(model => generateVideoForModel(model, 'kling'))
  ]

  await Promise.allSettled(promises)
  isGenerating.value = false
}

// 测试单个模型
async function testSingleModel(model, platform) {
  if (!prompt.value.trim()) {
    alert('请输入提示词')
    return
  }
  
  // 重置当前模型状态
  model.loading = true
  model.error = null
  model.videoUrl = null
  model.taskId = null
  model.status = null
  model.responseTime = null
  
  // 生成视频
  await generateVideoForModel(model, platform)
}

async function generateVideoForModel(model, platform) {
  const startTime = Date.now()
  model.startTime = startTime // 保存开始时间
  
  try {
    let request, result
    
    // 获取模型ID，尝试不同的可能字段名
    const modelId = model.id || model.modelId || model.model_id || model.name;
    
    if (platform === 'volc') {
      request = {
        prompt: prompt.value,
        resolution: resolution.value,
        ratio: ratio.value,
        duration: duration.value,
        framepersecond: framepersecond.value,
        watermark: watermark.value,
        seed: seed.value,
        camerafixed: camerafixed.value,
        model: modelId
      }
      result = await generateVolcVideo(request, referenceImageFile.value)
    } else {
      request = {
        prompt: prompt.value,
        resolution: resolution.value,
        ratio: ratio.value,
        duration: duration.value,
        framepersecond: framepersecond.value,
        watermark: watermark.value,
        seed: seed.value,
        camerafixed: camerafixed.value,
        model: modelId
      }
      result = await generateKlingVideo(request, referenceImageFile.value)
    }

    // 保存任务ID，确保使用正确的字段名
    console.log(`${platform} 生成结果:`, result);
    
    if (platform === 'volc') {
      // 火山平台直接返回任务ID
      if (result.taskId) {
        model.taskId = result.taskId;
      } else if (result.task_id) {
        model.taskId = result.task_id;
      } else if (typeof result === 'string' && result.includes('cgt-')) {
        // 直接返回的是任务ID字符串
        model.taskId = result;
      } else if (typeof result === 'object' && JSON.stringify(result).includes('cgt-')) {
        // 尝试从结果对象中提取任务ID
        const resultStr = JSON.stringify(result);
        const match = resultStr.match(/cgt-[0-9]+-[a-z0-9]+/);
        if (match) {
          model.taskId = match[0];
        } else {
          console.error('未找到火山任务ID:', result);
          throw new Error('未找到火山任务ID');
        }
      } else {
        console.error('未找到火山任务ID:', result);
        throw new Error('未找到火山任务ID');
      }
    } else {
      // 可灵平台返回的是data对象中的task_id
      if (result.data && result.data.task_id) {
        model.taskId = result.data.task_id;
      } else if (result.taskId) {
        model.taskId = result.taskId;
      } else if (result.task_id) {
        model.taskId = result.task_id;
      } else {
        console.error('未找到可灵任务ID:', result);
        throw new Error('未找到可灵任务ID');
      }
    }
    
    console.log(`${platform} 生成成功，任务ID: ${model.taskId}`);
    // 不在这里设置responseTime，而是在任务完成时设置

    // 开始轮询任务状态
    pollTaskStatus(model, platform);

  } catch (error) {
    model.loading = false;
    model.error = error.message || '生成失败';
    model.responseTime = Date.now() - model.startTime; // 计算从开始到失败的总时间
  }
}

async function pollTaskStatus(model, platform) {
  const maxAttempts = 60 // 最多轮询60次（5分钟）
  let attempts = 0

  const poll = async () => {
    if (attempts >= maxAttempts) {
      model.loading = false
      model.error = '生成超时'
      return
    }

    try {
      if (!model.taskId) {
        model.loading = false
        model.error = '任务ID为空'
        return
      }
      
      console.log(`查询任务状态，平台: ${platform}，任务ID: ${model.taskId}`)
      
      let result
      if (platform === 'volc') {
        // 确保传递正确的任务ID格式
        const taskId = model.taskId.toString().trim()
        result = await queryVolcTask(taskId)
        
        // 尝试解析结果（如果是字符串）
        let parsedResult = result;
        if (typeof result === 'string') {
          try {
            // 检查是否是特殊格式的响应（GetContentGenerationTaskResponse）
            if (result.includes('GetContentGenerationTaskResponse')) {
              // 提取各个字段
              const idMatch = result.match(/id='([^']+)'/);
              const statusMatch = result.match(/status='([^']+)'/);
              const videoUrlMatch = result.match(/videoUrl='([^']+)'/);
              const completionTokensMatch = result.match(/completionTokens=(\d+)/);
              
              parsedResult = {
                id: idMatch ? idMatch[1] : null,
                status: statusMatch ? statusMatch[1] : null,
                content: {
                  videoUrl: videoUrlMatch ? videoUrlMatch[1] : null
                },
                usage: {
                  completionTokens: completionTokensMatch ? parseInt(completionTokensMatch[1]) : null
                }
              };
            }
            // 如果是JSON字符串，尝试解析
            else if (result.includes('{') && result.includes('}')) {
              try {
                // 尝试提取JSON部分
                const jsonMatch = result.match(/\{.*\}/s);
                if (jsonMatch) {
                  parsedResult = JSON.parse(jsonMatch[0]);
                }
              } catch (e) {
                console.error('解析JSON响应失败:', e);
              }
            }
          } catch (e) {
            console.error('解析火山响应失败:', e);
          }
        }
        
        // 根据火山平台的响应格式处理状态
        model.status = parsedResult.status
        
        // 火山平台状态映射
        // queued：排队中
        // running：任务运行中
        // cancelled：取消任务
        // succeeded：任务成功
        // failed：任务失败
        
        if (parsedResult.status === 'succeeded') {
          model.loading = false
          // 从content对象中获取视频URL
          if (parsedResult.content) {
            if (parsedResult.content.video_url) {
              model.videoUrl = parsedResult.content.video_url;
            } else if (parsedResult.content.videoUrl) {
              model.videoUrl = parsedResult.content.videoUrl;
            }
            
            // 提取token使用情况
            if (parsedResult.usage) {
              if (parsedResult.usage.completion_tokens) {
                model.tokens = parsedResult.usage.completion_tokens;
              } else if (parsedResult.usage.completionTokens) {
                model.tokens = parsedResult.usage.completionTokens;
              } else if (parsedResult.usage.total_tokens) {
                model.tokens = parsedResult.usage.total_tokens;
              }
            }
            
            // 计算总耗时（从开始到成功的总时间）
            model.responseTime = Date.now() - model.startTime;
          } else {
            model.error = '视频URL不存在';
            model.responseTime = Date.now() - model.startTime;
          }
        } else if (result.status === 'failed') {
          model.loading = false
          model.error = result.error ? (typeof result.error === 'object' ? JSON.stringify(result.error) : result.error) : '生成失败'
        } else if (result.status === 'cancelled') {
          model.loading = false
          model.error = '任务已取消'
        } else {
          // queued 或 running 状态，继续轮询
          attempts++
          setTimeout(poll, 5000) // 5秒后再次查询
        }
      } else {
        // 可灵平台查询
        const taskId = model.taskId.toString().trim()
        // 根据是否有参考图片设置正确的类型
        const type = referenceImageFile.value ? 'image2video' : 'text2video'
        result = await queryKlingTask(taskId, type)
        
        console.log('可灵平台查询结果:', result)
        
        // 可灵平台返回的数据结构
        // data: {
        //   task_id: 任务ID
        //   task_status: 任务状态 (submitted/processing/succeed/failed)
        //   task_status_msg: 任务状态信息
        //   task_result: { videos: [{ id, url, duration }] }
        //   created_at: 创建时间
        //   updated_at: 更新时间
        // }
        
        if (result.data) {
          // 保存任务状态
          model.status = result.data.task_status || '未知状态'
          
          if (result.data.task_status === 'succeed') {
            model.loading = false
            
            // 从task_result中获取视频信息
            if (result.data.task_result && 
                result.data.task_result.videos && 
                result.data.task_result.videos.length > 0) {
              
              const videoInfo = result.data.task_result.videos[0]
              model.videoUrl = videoInfo.url
              model.duration = videoInfo.duration
              model.createdAt = result.data.created_at
              
              // 计算总耗时（从开始到成功的总时间）
              model.responseTime = Date.now() - model.startTime;
            } else {
              model.error = '视频信息不存在'
              model.responseTime = Date.now() - model.startTime;
            }
          } else if (result.data.task_status === 'failed') {
            model.loading = false
            model.error = result.data.task_status_msg || '生成失败'
            model.responseTime = Date.now() - model.startTime;
          } else if (result.data.task_status === 'submitted' || result.data.task_status === 'processing') {
            // 继续轮询
            attempts++
            setTimeout(poll, 5000) // 5秒后再次查询
          } else {
            model.loading = false
            model.error = `未知状态: ${result.data.task_status}`
          }
        } else {
          // 兼容旧版API返回格式
          model.status = result.status || '未知状态'
          
          if (result.status === 'completed' || result.status === 'success') {
            model.loading = false
            model.videoUrl = result.videoUrl || result.video_url
            model.responseTime = Date.now() - model.startTime;
          } else if (result.status === 'failed' || result.status === 'error') {
            model.loading = false
            model.error = result.error || '生成失败'
            model.responseTime = Date.now() - model.startTime;
          } else {
            // 继续轮询
            attempts++
            setTimeout(poll, 5000) // 5秒后再次查询
          }
        }
      }
    } catch (error) {
      attempts++
      if (attempts >= maxAttempts) {
        model.loading = false
        model.error = '查询状态失败'
      } else {
        setTimeout(poll, 5000)
      }
    }
  }

  poll()
}
</script>

<style scoped>
.video-gen-page {
  height: 100vh; /* 改为 height */
  overflow-y: auto; /* 允许垂直滚动 */
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px 20px 150px;
}

.container {
  margin: 0 auto;
  min-width: 1800px;
  padding: 0;
}

.input-section {
  margin-bottom: 30px;
}

.input-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.input-card h2 {
  margin: 0 0 25px 0;
  color: #333;
  font-size: 24px;
  font-weight: 600;
}

.form-group {
  margin-bottom: 20px;
}

.form-group-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

@media (max-width: 1200px) {
  .form-group-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .form-group-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .form-group-grid {
    grid-template-columns: 1fr;
  }
}

.prompt-input {
  width: 100%;
  padding: 12px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 14px;
  resize: vertical;
  transition: border-color 0.3s;
}

.prompt-input:focus {
  outline: none;
  border-color: #667eea;
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.upload-area:hover {
  border-color: #667eea;
  background-color: #f8fafc;
}

.upload-placeholder .upload-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.upload-placeholder p {
  margin: 5px 0;
  color: #666;
}

.upload-hint {
  font-size: 12px;
  color: #999;
}

.uploaded-image {
  position: relative;
  display: inline-block;
}

.uploaded-image img {
  max-width: 200px;
  max-height: 150px;
  border-radius: 8px;
}

.remove-btn {
  position: absolute;
  top: -10px;
  right: -10px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #ff4757;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
}

.param-select, .param-input {
  width: 100%;
  padding: 12px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  transition: border-color 0.3s;
}

.param-select:focus, .param-input:focus {
  outline: none;
  border-color: #667eea;
}

.unsupported-label {
  font-size: 12px;
  color: #ff6b6b;
  font-weight: normal;
  font-style: italic;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

.generate-btn {
  width: 100%;
  padding: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.results-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.models-row {
  margin-bottom: 40px;
}

.models-row:last-child {
  margin-bottom: 0;
}

.models-row h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 20px;
  font-weight: 600;
  border-bottom: 2px solid #667eea;
  padding-bottom: 10px;
}

.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.model-card {
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
}

.model-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.model-header {
  background: #f8fafc;
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e1e5e9;
}

.model-header h4 {
  margin: 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.time-info {
  font-size: 12px;
  color: #666;
  background: #e1e5e9;
  padding: 4px 8px;
  border-radius: 4px;
}

.model-content {
  padding: 20px;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.loading-state, .error-state, .waiting-state {
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon, .waiting-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.video-result {
  width: 100%;
}

.result-video {
  width: 100%;
  max-height: 200px;
  border-radius: 8px;
  margin-bottom: 15px;
}

.model-info {
  text-align: left;
  font-size: 12px;
  color: #666;
}

.model-info p {
  margin: 5px 0;
}

.model-id {
  display: block;
  font-size: 12px;
  color: #888;
  margin-top: 4px;
}

.test-btn {
  margin-top: 10px;
  padding: 8px 16px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.test-btn:hover {
  background: #764ba2;
  transform: translateY(-2px);
}

.example-video {
  width: 100%;
  margin-bottom: 15px;
}

.example-label {
  font-size: 12px;
  color: #666;
  margin-top: 5px;
  font-style: italic;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .video-gen-page {
    padding: 10px;
  }
  
  .input-card {
    padding: 20px;
  }
  
  .models-grid {
    grid-template-columns: 1fr;
  }
  
  .results-section {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .input-card h2 {
    font-size: 20px;
  }
  
  .models-row h3 {
    font-size: 18px;
  }
}
</style>