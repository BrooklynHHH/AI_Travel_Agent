# AI Travel Assistant

一个基于AI的智能旅行助手系统，集成了多种AI功能，包括天气查询、汇率转换、二维码识别、搜索服务等。

## 功能特性

- 🌤️ **天气查询**：实时天气信息和预报
- 💱 **汇率转换**：支持多种货币实时汇率查询
- 📱 **二维码识别**：扫描和生成二维码
- 🔍 **智能搜索**：多平台搜索服务集成
- 📝 **OCR识别**：图片文字识别功能
- 🎙️ **播客生成**：AI自动生成播客内容
- 🎨 **现代化UI**：响应式设计，支持移动端

## 技术架构

### 前端技术栈
- Vue 3 (Composition API)
- Vue Router
- Tailwind CSS
- Element Plus
- WebSocket (实时通信)

### 后端技术栈
- Python 3.6+
- Flask
- WebSocket
- PyDub (音频处理)
- FFmpeg (音频拼接)

### 第三方服务
- 豆包TTS API (语音合成)
- 阿里云DashScope API
- 博查搜索API
- 百度搜索API

## 安装和运行

### 1. 安装依赖

```bash
# 安装前端依赖
npm install

# 安装Python依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

在相应的配置文件中替换API密钥：

#### 前端配置
在以下文件中替换API密钥：
- `src/views/MojiWeatherMcpView.vue`
- `src/views/BarCodeMcpView.vue`
- `src/views/QuarkSearchMcpView.vue`
- `src/views/ExchangeRateMcpView.vue`
- `src/views/AdvancedResultView.vue`

将以下内容替换为你的实际API密钥：
```javascript
const appId = 'YOUR_APP_ID_HERE';
const apiKey = 'YOUR_API_KEY_HERE';
```

#### 后端配置
在 `src/scripts/podcast/` 目录下的配置文件中替换：
- `single_podcast_generator.py`
- `podcast_generator.py`

将以下内容替换为你的实际配置：
```yaml
appid: "YOUR_APP_ID_HERE"
token: "YOUR_TOKEN_HERE"
```

### 3. 启动服务

```bash
# 启动前端服务
npm run serve

# 启动后端服务
python server.py
```

## 项目结构

```
AI_travel/
├── src/                        # 前端代码
│   ├── views/                  # 页面组件
│   │   ├── MojiWeatherMcpView.vue    # 天气查询
│   │   ├── ExchangeRateMcpView.vue   # 汇率转换
│   │   ├── BarCodeMcpView.vue        # 二维码识别
│   │   ├── QuarkSearchMcpView.vue    # 搜索服务
│   │   ├── AdvancedResultView.vue    # 高级搜索结果
│   │   └── OcrView.vue               # OCR识别
│   ├── scripts/                # 脚本文件
│   │   └── podcast/            # 播客生成相关
│   ├── components/             # 通用组件
│   ├── router/                 # 路由配置
│   └── App.vue                 # 主应用组件
├── travel/                     # 旅行相关功能
│   ├── agent_V5.ipynb         # AI代理测试
│   └── simple_multi_turn_system/ # 多轮对话系统
├── server/                     # 后端服务
├── package.json                # 前端依赖
├── requirements.txt            # Python依赖
└── README.md                   # 项目说明
```

## 主要功能模块

### 1. 天气查询 (MojiWeatherMcpView)
- 实时天气信息获取
- 天气预报功能
- 多城市天气对比

### 2. 汇率转换 (ExchangeRateMcpView)
- 实时汇率查询
- 多货币支持
- 历史汇率趋势

### 3. 二维码识别 (BarCodeMcpView)
- 二维码扫描
- 二维码生成
- 多种码制支持

### 4. 智能搜索 (QuarkSearchMcpView)
- 多平台搜索集成
- 搜索结果优化
- 实时搜索建议

### 5. OCR识别 (OcrView)
- 图片文字识别
- 多语言支持
- 识别结果编辑

### 6. 播客生成
- 单人播客生成
- 双人对话播客
- 音频文件处理

## 开发说明

### API密钥配置
所有API密钥都已替换为占位符，使用前需要：
1. 申请相应的API服务
2. 获取API密钥
3. 在配置文件中替换占位符

### 环境要求
- Node.js 14+
- Python 3.6+
- FFmpeg (音频处理)

### 部署说明
项目支持Docker部署，相关文件：
- `Dockerfile`
- `docker-compose.yml`
- `docker-deploy.sh`

## 注意事项

1. 确保所有API密钥已正确配置
2. 音频处理需要安装FFmpeg
3. 建议在生产环境使用HTTPS
4. 注意API调用频率限制

## 许可证

MIT License 