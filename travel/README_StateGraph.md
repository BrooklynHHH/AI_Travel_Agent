# StateGraph旅游规划系统

基于LangGraph StateGraph架构的旅游规划系统，参考`zhongketianta.py`的设计模式，实现严格按顺序执行的旅游规划流程。

## 🌟 系统特点

### 核心优势
- **流程可控**: 严格按照预定义顺序执行，确保每个步骤都完成
- **状态传递**: 前一步的输出作为后一步的输入，数据流清晰
- **错误处理**: 每个节点都有完善的异常处理机制
- **可扩展性**: 容易添加新的处理步骤或修改现有流程

### 工作流程
```
用户输入 → 需求收集 → 景点检索 → 行程规划 → 交通安排 → 旅行建议 → 完整攻略
```

## 📁 文件结构

```
agent-mi/travel/
├── supervisor_agent_stategraph.py  # 主要实现文件
├── stategraph_api.py              # API接口封装
├── test_stategraph.py             # 测试文件
└── README_StateGraph.md           # 说明文档
```

## 🚀 快速开始

### 1. 基本使用

```python
from supervisor_agent_stategraph import run_travel_planning_blocking

# 阻塞模式 - 等待完整结果
result = run_travel_planning_blocking("我想去南京三日游")
print(result['final_travel_guide'])
```

### 2. 流式输出

```python
from supervisor_agent_stategraph import run_travel_planning_stategraph

# 流式模式 - 实时查看进度
for event in run_travel_planning_stategraph("我想去南京三日游"):
    print(f"当前步骤: {event}")
```

### 3. 使用API接口

```python
from stategraph_api import travel_api

# 使用封装好的API
result = travel_api.plan_travel_complete("我想去杭州两日游")
if result['success']:
    print(result['travel_guide'])
else:
    print(f"错误: {result['error']}")
```

## 🔧 系统架构

### 状态定义
```python
class TravelPlanningState(TypedDict):
    user_input: str                    # 用户原始输入
    collected_needs: dict              # 需求收集结果
    search_results: dict               # 景点搜索结果
    day_plan: dict                     # 行程规划结果
    transport_plan: dict               # 交通住宿安排
    butler_suggestions: dict           # 旅行建议和注意事项
    final_travel_guide: str            # 最终完整攻略
    status: str                        # 当前处理状态
    error_message: str                 # 错误信息
```

### 工作流节点

1. **need_collect_node**: 需求收集
   - 分析用户输入
   - 提取关键信息（目的地、时长等）

2. **tour_search_node**: 景点搜索
   - 根据需求搜索相关景点
   - 获取景点详情和攻略

3. **day_plan_node**: 行程规划
   - 制定详细的每日行程
   - 考虑景点间距离和时间

4. **transport_node**: 交通住宿
   - 安排交通路线
   - 推荐住宿选择

5. **butler_node**: 旅行建议
   - 提供天气、美食建议
   - 当地注意事项

6. **final_integration_node**: 最终整合
   - 整合所有信息
   - 生成完整旅游攻略

## 🛠️ 配置说明

### 环境变量
```bash
# .env 文件
REACT_API_KEY=your_api_key
AMAP_API_KEY=your_amap_key
```

### 依赖包
```bash
pip install langchain-openai
pip install langgraph
pip install requests
pip install python-dotenv
```

## 🧪 测试

### 运行测试
```bash
python test_stategraph.py
```

### 测试用例
- 南京三日游（历史文化）
- 杭州两日游（西湖美景+美食）
- 北京五日游（亲子游，轻松行程）

## 📊 与原系统对比

| 特性 | 原Supervisor系统 | 新StateGraph系统 |
|------|------------------|------------------|
| 执行顺序 | 智能体自主决定 | 严格按预定义顺序 |
| 状态管理 | 消息传递 | 结构化状态对象 |
| 错误处理 | 分散在各智能体 | 集中在节点函数 |
| 可调试性 | 较难追踪 | 每步状态可查看 |
| 扩展性 | 需修改Supervisor | 添加节点即可 |

## 🔄 集成到现有系统

### 替换原有函数
```python
# 原来的调用方式
from supervisor_agent_new import run_travel_planning

# 新的调用方式
from supervisor_agent_stategraph import run_travel_planning_blocking as run_travel_planning
```

### API服务器集成
```python
# 在api_server.py中添加新的路由
from stategraph_api import travel_api

@app.route('/api/travel/stategraph', methods=['POST'])
def travel_planning_stategraph():
    user_request = request.json.get('user_request')
    result = travel_api.plan_travel_complete(user_request)
    return jsonify(result)
```

## 🎯 使用场景

### 适用场景
- 需要严格控制执行顺序的旅游规划
- 要求每个步骤都必须完成的场景
- 需要详细状态跟踪的应用
- 对结果一致性要求较高的系统

### 不适用场景
- 需要智能体自主决策执行顺序
- 某些步骤可以跳过的灵活场景
- 对性能要求极高的实时应用

## 🚀 未来扩展

### 可能的改进方向
1. **并行处理**: 某些独立步骤可以并行执行
2. **条件分支**: 根据用户需求选择不同的处理路径
3. **缓存机制**: 缓存常用景点和路线信息
4. **用户反馈**: 支持用户对中间结果的修改
5. **多语言支持**: 支持不同语言的旅游规划

### 扩展示例
```python
# 添加新的处理节点
def weather_check_node(state: TravelPlanningState) -> TravelPlanningState:
    """天气检查节点"""
    # 实现天气检查逻辑
    pass

# 在工作流中添加节点
workflow.add_node("weather_check", weather_check_node)
workflow.add_edge("day_plan", "weather_check")
workflow.add_edge("weather_check", "transport")
```

## 📝 开发日志

### v1.0.0 (2025-06-30)
- ✅ 实现基础StateGraph架构
- ✅ 完成六个核心处理节点
- ✅ 添加完善的错误处理
- ✅ 提供流式和阻塞两种模式
- ✅ 创建API接口封装
- ✅ 编写测试用例和文档

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件
- 项目讨论区

---

*最后更新: 2025-06-30*
