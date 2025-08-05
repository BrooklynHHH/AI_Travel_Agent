# AI Travel Assistant - 快速启动指南

## 🚀 快速开始

### 1. 环境准备

确保你的系统已安装：
- Node.js 14+
- Python 3.6+
- FFmpeg

### 2. 克隆项目

```bash
git clone <your-repo-url>
cd AI_travel
```

### 3. 安装依赖

```bash
# 安装前端依赖
npm install

# 安装Python依赖
pip install -r requirements.txt
```

### 4. 配置API密钥

#### 前端API配置

编辑以下文件，替换API密钥：

**src/views/MojiWeatherMcpView.vue**
```javascript
const appId = 'YOUR_APP_ID_HERE';
const apiKey = 'YOUR_API_KEY_HERE';
```

**src/views/BarCodeMcpView.vue**
```javascript
const appId = 'YOUR_APP_ID_HERE';
const apiKey = 'YOUR_API_KEY_HERE';
```

**src/views/QuarkSearchMcpView.vue**
```javascript
const appId = 'YOUR_APP_ID_HERE';
const apiKey = 'YOUR_API_KEY_HERE';
```

**src/views/ExchangeRateMcpView.vue**
```javascript
const appId = 'YOUR_APP_ID_HERE';
const apiKey = 'YOUR_API_KEY_HERE';
```

**src/views/AdvancedResultView.vue**
```javascript
'Authorization': 'Bearer YOUR_API_KEY_HERE',
```

#### 后端API配置

**src/scripts/podcast/single_podcast_generator.py**
```python
default_config = {
    "appid": "YOUR_APP_ID_HERE",
    "token": "YOUR_TOKEN_HERE",
    # ... 其他配置
}
```

**src/scripts/podcast/podcast_generator.py**
```python
default_config = {
    "appid": "YOUR_APP_ID_HERE",
    "token": "YOUR_TOKEN_HERE",
    # ... 其他配置
}
```

### 5. 启动服务

```bash
# 启动前端服务
npm run serve

# 启动后端服务（新终端）
python server.py
```

### 6. 访问应用

打开浏览器访问：`http://localhost:8080`

## 🔧 功能测试

### 天气查询
1. 点击"天气查询"模块
2. 输入城市名称
3. 查看实时天气信息

### 汇率转换
1. 点击"汇率转换"模块
2. 选择源货币和目标货币
3. 输入金额查看转换结果

### 二维码识别
1. 点击"二维码识别"模块
2. 上传二维码图片或扫描二维码
3. 查看识别结果

### 智能搜索
1. 点击"智能搜索"模块
2. 输入搜索关键词
3. 查看多平台搜索结果

### OCR识别
1. 点击"OCR识别"模块
2. 上传包含文字的图片
3. 查看识别结果

### 播客生成
1. 点击"播客生成"模块
2. 输入播客主题
3. 选择单人/双人模式
4. 等待生成完成

## 🐛 常见问题

### Q: API密钥配置错误
A: 确保所有API密钥都已正确替换，检查密钥格式是否正确

### Q: 音频生成失败
A: 确保已安装FFmpeg，检查音频输出目录权限

### Q: 前端无法连接后端
A: 检查后端服务是否正常启动，确认端口配置

### Q: 搜索功能无结果
A: 检查网络连接，确认搜索API配置正确

## 📞 技术支持

如遇到问题，请检查：
1. 控制台错误信息
2. 网络连接状态
3. API密钥配置
4. 依赖安装完整性

## 🎯 下一步

- 自定义UI主题
- 添加更多AI功能
- 优化性能
- 部署到生产环境 