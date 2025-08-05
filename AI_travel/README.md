# AI Travel Agent

一个基于AI的智能旅游代理系统，专门为用户提供个性化的旅游规划服务。

## 功能特性

- 🗺️ **智能旅游规划**：根据用户需求生成个性化旅游行程
- 🏞️ **景点搜索推荐**：智能搜索和推荐旅游景点
- 📅 **行程安排**：自动规划每日行程和时间安排
- 🚗 **交通规划**：提供景点间交通路线和时间
- 🏨 **住宿推荐**：根据预算和偏好推荐住宿
- 🍽️ **美食推荐**：推荐当地特色美食和餐厅
- 💰 **预算管理**：帮助用户控制旅游预算
- 🎨 **现代化UI**：响应式设计，支持移动端

## 技术架构

### 前端技术栈
- Vue 3 (Composition API)
- Vue Router
- Tailwind CSS
- WebSocket (实时通信)

### 后端技术栈
- Python 3.6+
- LangGraph (工作流管理)
- OpenAI API (AI对话)
- WebSocket (实时通信)

### 核心组件
- **旅游规划智能体**：负责整体旅游规划
- **景点搜索智能体**：专门搜索和推荐景点
- **行程安排智能体**：规划每日具体行程
- **交通规划智能体**：提供交通路线建议
- **旅游管家智能体**：提供综合旅游服务

## 安装和运行

### 1. 安装依赖

```bash
# 安装前端依赖
npm install

# 安装Python依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

在 `src/config/api.config.js` 中配置OpenAI API密钥：

```javascript
export const API_CONFIG = {
  OPENAI_API_KEY: 'YOUR_OPENAI_API_KEY_HERE'
}
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
├── travel/                     # 旅游代理核心代码
│   ├── test_stream_data_logger.py    # 流式数据测试
│   ├── agent_V5.ipynb               # 旅游代理演示
│   ├── README_stream_test.md         # 测试说明
│   ├── simple_multi_turn_system/     # 多轮对话系统
│   └── stream_test_logs/             # 测试日志
├── src/                        # 前端代码
│   ├── views/                  # 页面组件
│   │   ├── TravelView.vue            # 旅游主界面
│   │   ├── TravelPlanning.vue        # 旅游规划界面
│   │   └── travel/                   # 旅游相关组件
│   ├── components/             # 通用组件
│   │   ├── AgentCard.vue             # 智能体卡片
│   │   └── modals/                   # 模态框组件
│   ├── utils/                  # 工具函数
│   │   ├── streamUtils.js            # 流式数据处理
│   │   ├── searchContentParser.js    # 搜索内容解析
│   │   └── contentFormatter.js       # 内容格式化
│   └── config/                 # 配置文件
│       └── api.config.js             # API配置
├── agent-server/               # 后端服务
├── requirements.txt            # Python依赖
└── README.md                  # 项目说明
```

## 使用说明

1. **启动应用**：访问 `http://localhost:8080/travel`
2. **输入需求**：在对话框中描述您的旅游需求
3. **获取规划**：系统会自动生成个性化旅游规划
4. **查看详情**：点击行程卡片查看详细信息
5. **实时对话**：与AI旅游代理进行实时对话

## 开发说明

- 前端使用Vue 3 Composition API开发
- 后端使用Python LangGraph框架
- 支持流式响应，提供实时交互体验
- 模块化设计，易于扩展和维护

## 许可证

MIT License 