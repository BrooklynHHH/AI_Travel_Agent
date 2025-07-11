# 简化多轮对话系统

基于用户输入历史的流式多轮对话旅游规划系统，严格按照用户需求实现 `/api/stream` 接口。

## 🎯 系统特点

- **严格按需求实现**: 完全按照用户的接口规范实现
- **多轮对话支持**: 基于 `user_input_history` 实现上下文记忆
- **流式输出**: 实时流式响应，支持 Server-Sent Events (SSE)
- **会话管理**: 自动会话管理和过期清理
- **差异化展示**: 根据接口数据字段类型进行内容格式化
- **简化架构**: 清晰的模块化设计，易于理解和维护

## 📁 项目结构

```
simple_multi_turn_system/
├── __init__.py                 # 包初始化
├── config.py                   # 配置文件
├── requirements.txt            # 依赖列表
├── simple_multi_turn_api.py    # 核心API服务器
├── multi_turn_session.py       # 会话管理模块
├── content_formatter.py        # 内容格式化模块
├── start_server.py            # 启动脚本
├── test_simple_api.py         # 测试脚本
├── README.md                  # 说明文档
└── utils/                     # 工具模块
    ├── __init__.py
    ├── logger.py              # 日志工具
    └── stream_handler.py      # 流式处理工具
```

## 🚀 快速开始

### 1. 环境准备

确保您的环境中有以下目录结构：
```
agent_mi_V2/
├── simple_multi_turn_system/  # 本系统
└── agent-mi/travel/           # 智能体模块
    ├── supervisor_agent.py
    └── enhanced_stream_api_V1.py
```

### 2. 安装依赖

```bash
cd simple_multi_turn_system
pip install -r requirements.txt
```

### 3. 启动服务器

**方式一：使用启动脚本（推荐）**
```bash
python start_server.py
```

**方式二：直接启动**
```bash
python simple_multi_turn_api.py
```

### 4. 测试系统

```bash
python test_simple_api.py
```

## 📋 API接口

### 核心接口：POST /api/stream

这是系统的核心接口，完全按照用户需求实现：

**请求格式：**
```bash
curl -X POST http://localhost:5000/api/stream \
  -H "Content-Type: application/json" \
  -d '{"user_input": "推荐风景"}'
```

**请求参数：**
- `user_input` (必需): 用户输入内容
- `session_id` (可选): 会话ID，不提供则自动创建

**响应格式：**
流式 Server-Sent Events (SSE) 响应，包含以下类型的数据：

1. **开始处理**
```json
{
  "type": "start",
  "message": "开始处理请求",
  "session_id": "uuid",
  "timestamp": "2025-07-11T12:00:00"
}
```

2. **智能体开始工作**
```json
{
  "type": "agent_start",
  "agent": "supervisor",
  "agent_name": "总控智能体",
  "timestamp": "2025-07-11T12:00:01"
}
```

3. **内容更新**
```json
{
  "type": "content_update",
  "agent": "tour_search_agent",
  "agent_name": "景点搜索专家",
  "content": "为您推荐以下风景名胜...",
  "content_type": "recommendation",
  "timestamp": "2025-07-11T12:00:02"
}
```

4. **处理完成**
```json
{
  "type": "done",
  "message": "处理完成",
  "final_response": "完整的回复内容",
  "agents_used": ["supervisor", "tour_search_agent"],
  "timestamp": "2025-07-11T12:00:10"
}
```

### 其他接口

- `GET /api/health` - 健康检查
- `GET /api/status` - 服务状态
- `GET /api/sessions` - 列出所有会话
- `GET /api/sessions/<id>` - 获取会话信息
- `DELETE /api/sessions/<id>` - 删除会话
- `POST /api/sessions/<id>/clear` - 清空会话历史

## 🔄 多轮对话逻辑

系统严格按照用户需求实现多轮对话：

1. **接受用户输入** → 将用户输入添加到 `user_input_history`
2. **构建上下文** → 将 `user_input_history` 传入 `user_input` 参数
3. **调用接口** → 使用流式输出实现实时响应
4. **差异化展示** → 根据接收到的信息类型进行不同展示
5. **循环处理** → 重复以上步骤实现多轮对话

### 示例多轮对话

**第1轮：**
```bash
curl -X POST http://localhost:5000/api/stream \
  -H "Content-Type: application/json" \
  -d '{"user_input": "推荐风景"}'
```

**第2轮（使用相同session_id）：**
```bash
curl -X POST http://localhost:5000/api/stream \
  -H "Content-Type: application/json" \
  -d '{"user_input": "我想去北京", "session_id": "your-session-id"}'
```

系统会自动构建包含历史的上下文：
```
用户输入历史:
1. 推荐风景
2. 我想去北京

当前用户输入: 我想去北京
```

## 🎨 内容格式化

系统根据接口数据字段类型进行差异化展示：

- **start**: 开始处理消息 🚀
- **agent_start**: 智能体开始工作 🤖
- **content_update**: 内容更新 📝
- **done**: 处理完成 ✅
- **error**: 错误信息 ❌

每种类型都有对应的图标、颜色和显示样式。

## 📊 会话管理

- **自动会话创建**: 不提供session_id时自动创建
- **历史记录管理**: 自动维护用户输入历史
- **过期清理**: 自动清理过期会话（默认1小时）
- **长度限制**: 历史记录长度限制（默认10轮）

## 🔧 配置说明

主要配置项在 `config.py` 中：

```python
# API配置
API_HOST = '0.0.0.0'
API_PORT = 5000

# 会话配置
MAX_HISTORY_LENGTH = 10      # 最大历史长度
SESSION_TIMEOUT = 3600       # 会话超时时间（秒）

# 智能体配置
SUPERVISOR_CONFIG = {
    'verbose_level': 1,
    'show_tokens': True,
    'show_progress': True,
    'show_timing': True
}
```

## 📝 日志记录

系统提供详细的日志记录：

- 用户输入记录
- 系统响应记录
- 流式数据处理记录
- 会话事件记录
- 错误信息记录

日志文件：`simple_multi_turn.log`

## 🧪 测试

运行测试脚本验证系统功能：

```bash
python test_simple_api.py
```

测试内容包括：
- 健康检查
- 单次流式API调用
- 多轮对话测试
- 会话管理功能
- 状态接口测试

## 🔍 故障排除

### 常见问题

1. **导入模块失败**
   - 确保 `agent-mi/travel` 目录存在
   - 检查必需文件是否存在

2. **依赖安装失败**
   - 使用 `pip install -r requirements.txt` 安装依赖
   - 检查Python版本兼容性

3. **端口占用**
   - 修改 `config.py` 中的 `API_PORT` 配置
   - 或停止占用5000端口的其他服务

4. **流式响应异常**
   - 检查网络连接
   - 确认客户端支持SSE

### 调试模式

启动时设置调试模式：
```python
DEBUG_MODE = True  # 在config.py中设置
```

## 📈 性能优化

- 使用流式处理减少内存占用
- 自动清理过期会话
- 异步处理提高并发性能
- 智能缓冲减少网络开销

## 🤝 扩展开发

系统采用模块化设计，易于扩展：

1. **添加新的内容类型**: 修改 `content_formatter.py`
2. **扩展会话功能**: 修改 `multi_turn_session.py`
3. **添加新接口**: 在 `simple_multi_turn_api.py` 中添加路由
4. **自定义流式处理**: 修改 `utils/stream_handler.py`

## 📄 许可证

本项目仅供学习和研究使用。

## 🙋‍♂️ 支持

如有问题，请检查：
1. 日志文件 `simple_multi_turn.log`
2. 控制台输出信息
3. 测试脚本结果

---

**🎯 核心目标**: 严格按照用户需求实现基于 `user_input_history` 的多轮对话流式接口系统。
