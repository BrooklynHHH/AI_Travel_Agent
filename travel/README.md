# 🧳 智能旅游规划系统

基于多智能体系统（MAS）的智能旅游规划解决方案，将 Python 后端与 Vue.js 前端完美结合。

## 📋 系统架构

```
智能旅游规划系统
├── 后端 (Python FastAPI)
│   ├── supervisor_agent.py     # 多智能体系统核心
│   ├── api_server.py          # FastAPI Web服务器
│   ├── workflow_client.py     # 工作流客户端
│   └── start_server.py        # 启动脚本
└── 前端 (Vue.js)
    ├── SupervisorAgent.vue    # 主界面组件
    └── travelPlanningAPI.js   # API客户端
```

## 🚀 快速开始

### 1. 环境准备

确保您的系统已安装：
- Python 3.8+
- Node.js 14+
- npm 或 yarn

### 2. 后端设置

#### 安装依赖
```bash
cd agent-mi/travel
pip install -r requirements.txt
```

#### 配置环境变量
创建 `.env` 文件：
```env
# AI模型API密钥
REACT_API_KEY=your_openai_api_key

# 高德地图API密钥
AMAP_API_KEY=your_amap_api_key

# 工作流API密钥（可选）
WORKFLOW_API_KEY=your_workflow_key
```

#### 启动后端服务
```bash
# 方式1：使用启动脚本（推荐）
python start_server.py

# 方式2：直接使用uvicorn
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后，访问：
- API服务：http://localhost:8000
- API文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

### 3. 前端设置

#### 安装依赖
```bash
cd agent-mi
npm install
```

#### 启动前端服务
```bash
npm run serve
```

前端服务启动后，访问：http://localhost:8080

### 4. 访问系统

在浏览器中打开：http://localhost:8080/supervisor-agent

## 🤖 智能体介绍

系统包含以下专业智能体：

### 1. 需求收集智能体 (need_collect_agent)
- **职责**：分析用户输入，收集旅游需求
- **功能**：
  - 识别目的地、时长、人员构成等关键信息
  - 判断信息完整性
  - 引导用户补充必要信息

### 2. 景点搜索智能体 (tour_search_agent)
- **职责**：搜索目的地相关信息
- **功能**：
  - 景点推荐与详情获取
  - 美食文化信息搜索
  - 旅游攻略收集

### 3. 行程规划智能体 (day_plan_agent)
- **职责**：制定详细行程安排
- **功能**：
  - 地理编码查询
  - 景点间距离计算
  - 最优路线规划
  - 时间安排优化

### 4. 交通住宿智能体 (live_transport_agent)
- **职责**：规划交通和住宿
- **功能**：
  - 住宿推荐（酒店、民宿）
  - 交通方案（公交、地铁、打车）
  - 成本预算计算

### 5. 旅行管家智能体 (travel_butler_agent)
- **职责**：提供贴心旅行建议
- **功能**：
  - 天气穿衣建议
  - 美食推荐
  - 注意事项提醒
  - 应急方案

## 🔧 API 接口

### 需求收集
```http
POST /api/need-collection
Content-Type: application/json

{
  "user_input": "我想去北京三日游",
  "session_id": "optional_session_id",
  "input_history": []
}
```

### 旅游规划（非流式）
```http
POST /api/travel-planning
Content-Type: application/json

{
  "user_request": "请制定北京三日游方案",
  "session_id": "optional_session_id",
  "confirmed_needs": []
}
```

### 旅游规划（流式）
```http
POST /api/travel-planning-stream
Content-Type: application/json

{
  "user_request": "请制定北京三日游方案",
  "session_id": "optional_session_id"
}
```

### 方案优化
```http
POST /api/travel-optimize
Content-Type: application/json

{
  "user_feedback": "行程太紧张了，希望放松一些",
  "travel_plan_draft": "原方案内容...",
  "session_id": "optional_session_id"
}
```

## 🎯 功能特性

### 智能对话
- 自然语言理解
- 上下文记忆
- 多轮对话支持

### 实时规划
- 流式输出
- 实时反馈
- 动态调整

### 个性化定制
- 需求分析
- 偏好学习
- 方案优化

### 数据集成
- 高德地图API
- 实时地理信息
- 距离时间计算

## 🛠️ 开发指南

### 添加新智能体

1. 在 `supervisor_agent.py` 中定义新智能体：
```python
new_agent = create_react_agent(
    model=llm,
    prompt="智能体提示词...",
    tools=[tool1, tool2],
    name="new_agent"
)
```

2. 将智能体添加到supervisor：
```python
supervisor = create_supervisor(
    agents=[existing_agents, new_agent],
    model=llm,
    prompt="supervisor提示词..."
)
```

### 添加新工具

1. 定义工具函数：
```python
@tool("tool_name", parse_docstring=True)
def new_tool(param1: str, param2: int):
    """
    工具描述
    
    Args:
        param1: 参数1描述
        param2: 参数2描述
    
    Returns:
        返回值描述
    """
    # 工具实现
    return result
```

2. 将工具添加到智能体：
```python
agent = create_react_agent(
    model=llm,
    tools=[existing_tools, new_tool],
    # ...
)
```

### 自定义API端点

在 `api_server.py` 中添加新端点：
```python
@app.post("/api/new-endpoint")
async def new_endpoint(request: RequestModel):
    # 端点实现
    return response
```

## 🔍 故障排除

### 常见问题

1. **API密钥错误**
   - 检查 `.env` 文件配置
   - 确认密钥有效性

2. **依赖安装失败**
   - 更新pip：`pip install --upgrade pip`
   - 使用虚拟环境：`python -m venv venv`

3. **端口占用**
   - 修改端口：`--port 8001`
   - 检查进程：`lsof -i :8000`

4. **前后端连接失败**
   - 检查后端服务状态
   - 确认API地址配置

### 日志查看

后端日志会显示详细的执行信息：
```bash
# 启动时会显示
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 📈 性能优化

### 后端优化
- 使用连接池
- 缓存频繁查询
- 异步处理

### 前端优化
- 组件懒加载
- 请求防抖
- 结果缓存

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [LangChain](https://langchain.com/) - AI应用开发框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Web框架
- [Vue.js](https://vuejs.org/) - 渐进式前端框架
- [高德地图](https://lbs.amap.com/) - 地理信息服务

---

如有问题或建议，请提交 Issue 或联系开发团队。
