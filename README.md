# AI Travel Agent - 智能旅游规划系统

一个基于多智能体协作的AI旅游规划系统，通过智能对话为用户提供个性化的旅游规划服务。

## 🎬 操作演示

![AI Travel Agent 操作演示](./ai_travel.mp4)

## 📋 产品方案

### 🎯 产品定位
AI Travel Agent 是一个基于多智能体协作的智能旅游规划系统，通过自然语言对话理解用户需求，自动生成个性化的旅游方案。

### 🚀 核心功能

#### 1. 智能需求收集
- **多轮对话理解**：通过自然语言对话收集用户旅游需求
- **需求结构化**：自动识别目的地、时长、预算、人员构成等关键信息
- **需求补充引导**：智能识别缺失信息并引导用户补充

#### 2. 多智能体协作规划
- **景点搜索智能体**：负责搜索和推荐旅游景点、美食、文化活动
- **行程规划智能体**：制定详细的每日行程安排和时间规划
- **交通规划智能体**：提供交通路线、住宿推荐和后勤安排
- **旅游管家智能体**：提供安全提醒、礼仪建议、打包清单等增值服务

#### 3. 实时流式输出
- **实时响应**：支持流式数据输出，用户可实时看到规划进度
- **多轮对话**：支持多轮对话优化和调整旅游方案
- **焦点区域**：重要信息可在焦点区域突出显示

#### 4. 个性化推荐
- **预算匹配**：根据用户预算推荐合适的住宿和交通方案
- **偏好学习**：基于用户反馈优化推荐策略
- **季节适配**：考虑旅游季节和天气因素调整方案

### 🎨 用户体验设计

#### 移动端优先设计
- **响应式布局**：适配各种屏幕尺寸
- **触摸优化**：针对移动设备优化的交互体验
- **离线支持**：支持离线查看已生成的旅游方案

#### 直观的界面设计
- **卡片式布局**：每个智能体以卡片形式展示
- **状态指示**：实时显示各智能体的工作状态
- **进度可视化**：直观显示规划进度和完成状态

## 🏗️ 技术架构

### 前端技术栈

#### 核心框架
- **Vue 3**：使用 Composition API 构建响应式界面
- **Vue Router**：单页面应用路由管理
- **Element Plus**：现代化UI组件库

#### 样式和交互
- **Tailwind CSS**：原子化CSS框架，快速构建界面
- **Vue3 Video Play**：视频播放组件
- **KaTeX**：数学公式渲染

#### 实时通信
- **WebSocket**：与后端实时通信
- **流式数据处理**：实时显示AI生成内容

### 后端技术栈

#### 核心框架
- **Python 3.6+**：主要开发语言
- **Flask**：轻量级Web框架
- **Flask-CORS**：跨域资源共享支持

#### AI和智能体
- **LangGraph**：多智能体工作流管理
- **OpenAI API**：大语言模型接口
- **LangChain**：AI应用开发框架

#### 数据处理
- **PyYAML**：配置文件处理
- **WebSockets**：实时双向通信
- **Pydub**：音频处理（预留功能）

### 系统架构设计

#### 1. 前端架构
```
src/
├── views/                    # 页面组件
│   ├── TravelView.vue       # 旅游主界面（移动端优化）
│   └── TravelPlanning.vue   # 多轮对话规划界面
├── components/               # 通用组件
│   └── AgentCard.vue        # 智能体卡片组件
├── utils/                    # 工具函数
│   └── travelPlanningAPI.js # API通信封装
├── config/                   # 配置文件
│   └── api.config.js        # API配置
└── router/                   # 路由配置
    └── index.js             # 路由定义
```

#### 2. 后端架构
```
travel/
├── agent_V5.ipynb           # 智能体演示和测试
├── test_stream_data_logger.py # 流式数据测试工具
├── simple_multi_turn_system/ # 多轮对话系统
│   ├── agent_v5.py          # 智能体实现
│   └── test_api.ipynb       # API测试
└── stream_test_logs/         # 测试日志
```

#### 3. 智能体协作流程
```
用户输入 → 需求分析 → 智能体调度 → 并行处理 → 结果整合 → 流式输出
    ↓
多轮对话 → 方案优化 → 个性化调整 → 最终方案
```

### 核心智能体设计

#### 1. 景点搜索智能体 (tour_search_agent)
- **职责**：搜索和推荐旅游景点、美食、文化活动
- **输入**：用户目的地和偏好
- **输出**：景点列表、详细信息、推荐理由

#### 2. 行程规划智能体 (day_plan_agent)
- **职责**：制定详细的每日行程安排
- **输入**：景点信息和用户需求
- **输出**：每日行程表、时间安排、活动建议

#### 3. 交通规划智能体 (live_transport_agent)
- **职责**：规划交通路线和住宿安排
- **输入**：行程安排和预算信息
- **输出**：交通方案、住宿推荐、费用估算

#### 4. 旅游管家智能体 (travel_butler_agent)
- **职责**：提供增值服务和贴心建议
- **输入**：完整旅游方案
- **输出**：安全提醒、礼仪建议、打包清单

## 🚀 执行方案

### 1. 环境准备

#### 前端环境
```bash
# 安装Node.js依赖
cd AI_travel
npm install

# 启动开发服务器（端口3001）
npm run serve
```

#### 后端环境
```bash
# 安装Python依赖
pip install -r requirements.txt

# 配置环境变量
export OPENAI_API_KEY="your_api_key"
export AMAP_API_KEY="your_amap_key"
```

### 2. 配置说明

#### API配置 (src/config/api.config.js)
```javascript
export const API_CONFIG = {
  BASE_URL: 'http://staging-llm.search.miui.srv',
  ENDPOINTS: {
    STREAM: '/agent-api/stream',
    HEALTH: '/agent-api/health',
    SESSIONS: '/agent-api/sessions'
  },
  TIMEOUT: 30000,
  RETRY: {
    MAX_ATTEMPTS: 3,
    DELAY: 1000
  }
}
```

#### 智能体配置 (travel/simple_multi_turn_system/agent_v5.py)
```python
# LLM配置
llm = ChatOpenAI(
    temperature=0.0,
    base_url='https://mify-be.pt.xiaomi.com/open/api/v1',
    api_key=REACT_API_KEY,
    streaming=True
)

# 智能体协作配置
supervisor = create_supervisor(
    agents=[tour_search_agent, day_plan_agent, live_transport_agent, travel_butler_agent],
    model=llm,
    handoff_tool_prefix="next_step"
)
```

### 3. 部署方案

#### 开发环境
- **前端**：Vue CLI 开发服务器 (端口3001)
- **后端**：Flask 开发服务器 (端口5000)
- **数据库**：本地文件存储

#### 生产环境
- **前端**：Nginx + Vue 构建产物
- **后端**：Gunicorn + Flask
- **负载均衡**：Nginx 反向代理
- **监控**：Prometheus + Grafana

### 4. 测试方案

#### 单元测试
```bash
# 前端测试
npm run test:unit

# 后端测试
python -m pytest tests/
```

#### 集成测试
```bash
# 流式数据测试
cd travel
python test_stream_data_logger.py --mode batch
```

#### 性能测试
- **并发用户**：支持100+并发用户
- **响应时间**：平均响应时间 < 2秒
- **流式输出**：实时性 < 100ms

## 📊 数据流程

### 1. 用户交互流程
```
用户输入 → 前端验证 → API调用 → 后端处理 → 智能体协作 → 流式返回 → 前端渲染
```

### 2. 智能体协作流程
```
需求分析 → 任务分解 → 并行执行 → 结果整合 → 质量检查 → 输出优化
```

### 3. 数据存储流程
```
会话管理 → 状态保存 → 历史记录 → 用户偏好 → 方案缓存 → 性能优化
```

## 🔧 开发指南

### 1. 代码规范
- **前端**：ESLint + Prettier
- **后端**：Black + Flake8
- **提交规范**：Conventional Commits

### 2. 文档规范
- **API文档**：OpenAPI 3.0
- **组件文档**：Vue Style Guide
- **架构文档**：Mermaid 图表

### 3. 安全规范
- **API密钥**：环境变量管理
- **输入验证**：前后端双重验证
- **CORS配置**：严格跨域控制

## 🚀 未来规划

### 短期目标 (1-3个月)
- [ ] 小程序版本开发
- [ ] 移动端APP开发
- [ ] 多语言支持
- [ ] 离线模式优化

### 中期目标 (3-6个月)
- [ ] 语音交互功能
- [ ] AR景点导览
- [ ] 社交分享功能
- [ ] 个性化推荐算法优化

### 长期目标 (6-12个月)
- [ ] 全球旅游数据集成
- [ ] 实时天气和交通信息
- [ ] 智能客服机器人
- [ ] 企业级解决方案

## 📞 技术支持

### 联系方式
- **项目维护**：BrooklynHHH
- **技术支持**：通过GitHub Issues
- **文档更新**：定期更新README和Wiki

### 贡献指南
1. Fork 项目
2. 创建功能分支
3. 提交代码变更
4. 发起 Pull Request

---

**AI Travel Agent** - 让每一次旅行都成为完美的回忆 ✈️ 