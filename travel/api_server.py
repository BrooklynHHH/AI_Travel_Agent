"""
FastAPI 服务器 - 基于 main.py 逻辑的简化版本
提供旅游规划的核心API接口
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import json
import uuid
from datetime import datetime
import logging
from contextlib import asynccontextmanager
import time

# 导入新的日志配置
from log_config import (
    get_logger_manager, 
    get_planning_logger, 
    get_optimization_logger,
    get_api_logger,
    log_planning_step,
    log_optimization_step,
    log_planning_error,
    log_optimization_error
)

# 导入 supervisor_agent 模块
from supervisor_agent import (
    run_travel_planning,
    run_travel_planning_flexible
)

# 导入需求收集智能体（从main.py复制）
import requests
from langchain_core.tools import tool
import time
import os
from requests.packages.urllib3.util.retry import Retry
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json_repair

# 初始化LLM和需求收集智能体
load_dotenv()
react_api_key = os.getenv("REACT_API_KEY")
llm = ChatOpenAI(temperature=0.0, base_url='https://mify-be.pt.xiaomi.com/open/api/v1', api_key=react_api_key)

need_collect_agent = create_react_agent(
    model=llm,
    prompt="""
角色：
旅游规划顾问，通过友好的对话方式了解用户的旅游需求，逐步收集完整的旅行信息。

任务：
通过自然对话的方式，逐步了解并确认用户的旅游需求，判断当前收集状态，决定是否继续询问或开始制定计划。

核心收集信息：
必需信息（缺一不可）：
- 🎯 目的地
- ⏰ 出行时长

重要信息（影响规划质量）：
- 🚗 出行方式
- 👥 人员构成
- 💰 预算范围
- 📅 出行时间

补充信息（优化体验）：
- 🎯 主要目的：休闲放松/观光打卡/美食体验/历史文化/购物
- 🏨 住宿偏好
- 🍜 饮食偏好
- ✨ 特殊需求

状态判断逻辑：
- **CONTINUE** - 当满足以下条件时：
  - 缺少任一必需信息
  - 或者必需信息已收集完，但重要信息缺失较多（3项中缺2项以上）

- **END** - 当满足以下条件时：
  - 所有必需信息已收集
  - 且重要信息至少收集2项以上
  - 或者用户明确表示信息已足够

回复格式要求：
只输出JSON格式，包含以下字段：
```json
{
  "status": "CONTINUE/END",
  "confirm_need": ["已确认的需求项1", "已确认的需求项2", ...],
  "need": ["友好的自然语言询问1", "友好的自然语言询问2", ...]
}
```

注意事项：
- need字段中的询问要友好自然，像真人对话
- 每次询问不超过2个问题
- 优先询问必需信息
- END状态时，need字段询问是否开始制定行程

使用示例：

用户："我想要去南京三日游"

回复：
```json
{
  "status": "CONTINUE",
  "confirm_need": ["目的地:南京", "出行时长:3天"],
  "need": ["您打算什么时候出发呢？具体的日期或者大概的时间段都可以", "这次是和谁一起去？比如是独自旅行、情侣出游、还是和朋友家人一起？"]
}
```

用户："下个月15号左右，和女朋友一起去"

回复：
```json
{
  "status": "END",
  "confirm_need": ["目的地:南京", "出行时长:3天", "出行时间:下个月15号左右", "人员构成:情侣"],
  "need": ["这些信息已经足够制定行程了，您希望我现在就开始为您规划详细的南京3日游行程吗？还是想先补充一下预算范围或者特别想去的地方？"]
}
```

""",
    tools=[],
    name="need_collect_agent"
)

# 配置日志 - 使用新的日志系统
logger_manager = get_logger_manager()
logger = get_api_logger()

# 记录服务启动
logger.info("=== 旅游规划API服务器日志系统初始化完成 ===")

# 全局会话存储
sessions: Dict[str, Dict] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时的初始化
    logger.info("旅游规划API服务器启动")
    yield
    # 关闭时的清理
    logger.info("旅游规划API服务器关闭")

# 创建 FastAPI 应用
app = FastAPI(
    title="智能旅游规划 API",
    description="基于main.py逻辑的旅游规划服务",
    version="2.0.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型
class NeedCollectionRequest(BaseModel):
    user_input: str
    session_id: Optional[str] = None

class TravelPlanningRequest(BaseModel):
    user_request: str
    session_id: Optional[str] = None

class TravelOptimizeRequest(BaseModel):
    user_feedback: str
    travel_plan_draft: str
    session_id: Optional[str] = None

# 响应模型
class NeedCollectionResponse(BaseModel):
    status: str  # "CONTINUE" 或 "END"
    confirm_need: List[str]
    need: List[str]
    session_id: str

class TravelPlanningResponse(BaseModel):
    status: str
    result: Optional[str] = None
    session_id: str
    error: Optional[str] = None

# 工具函数
def create_session() -> str:
    """创建新的会话ID"""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "created_at": datetime.now(),
        "user_input_history": [],
        "is_first_round": True,
        "travel_plan_draft": None,
        "status": "active"
    }
    return session_id

def get_session(session_id: str) -> Dict:
    """获取会话信息"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="会话不存在")
    return sessions[session_id]

def serialize_message(obj):
    """序列化消息对象，处理 LangChain 消息类型"""
    if hasattr(obj, 'content'):
        # 处理 LangChain 消息对象
        return {
            "type": obj.__class__.__name__,
            "content": obj.content,
            "role": getattr(obj, 'type', 'unknown')
        }
    elif isinstance(obj, dict):
        # 递归处理字典
        return {k: serialize_message(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        # 递归处理列表
        return [serialize_message(item) for item in obj]
    else:
        # 其他类型直接返回
        return obj

async def stream_generator(session_id: str, generator):
    """流式响应生成器"""
    try:
        for chunk in generator:
            if isinstance(chunk, dict):
                # 检查是否是新的事件格式
                if "event" in chunk:
                    # 新格式：直接使用事件数据
                    event_data = {
                        "event": chunk.get("event", "unknown"),
                        "data": serialize_message(chunk.get("data", {})),
                        "step": chunk.get("step", 0),
                        "timestamp": chunk.get("timestamp", datetime.now().isoformat()),
                        "session_id": session_id
                    }
                else:
                    # 旧格式：包装为 supervisor_output 事件
                    serialized_chunk = serialize_message(chunk)
                    event_data = {
                        "event": "supervisor_output",
                        "data": serialized_chunk,
                        "timestamp": datetime.now().isoformat(),
                        "session_id": session_id
                    }
                
                # 使用 ensure_ascii=True 避免中文字符编码问题
                json_str = json.dumps(event_data, ensure_ascii=True)
                yield f"data: {json_str}\n\n"
            else:
                # 处理非字典类型的数据
                event_data = {
                    "event": "raw_output",
                    "data": {"content": str(chunk)},
                    "timestamp": datetime.now().isoformat(),
                    "session_id": session_id
                }
                json_str = json.dumps(event_data, ensure_ascii=True)
                yield f"data: {json_str}\n\n"
        
    except Exception as e:
        logger.error(f"流式响应错误: {e}")
        error_event = {
            "event": "error",
            "data": {"error": str(e)},
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id
        }
        json_str = json.dumps(error_event, ensure_ascii=True)
        yield f"data: {json_str}\n\n"

# API 路由

@app.get("/")
async def root():
    """根路径"""
    return {"message": "智能旅游规划 API 服务正在运行", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(sessions),
        "version": "2.0.0"
    }

@app.post("/api/need-collection", response_model=NeedCollectionResponse)
async def collect_needs(request: NeedCollectionRequest):
    """需求收集接口 - 完全按照main.py逻辑实现"""
    try:
        # 创建或获取会话
        session_id = request.session_id or create_session()
        session = get_session(session_id)
        
        # 更新输入历史
        session["user_input_history"].append(request.user_input)
        
        logger.info(f"会话 {session_id}: 需求收集，输入历史: {session['user_input_history']}")
        
        # 调用需求收集智能体 - 按照main.py逻辑
        # 将输入历史转换为字符串格式
        user_input_str = str(session["user_input_history"])
        
        result = need_collect_agent.invoke({
            "messages": [("user", user_input_str)]
        })
        
        # 解析结果 - 获取最后一条消息的内容
        if result and "messages" in result and len(result["messages"]) > 0:
            last_message = result["messages"][-1]
            # 处理不同类型的消息对象
            if hasattr(last_message, 'content'):
                content = last_message.content
            elif isinstance(last_message, dict) and 'content' in last_message:
                content = last_message['content']
            else:
                content = str(last_message)
        else:
            content = "无法获取需求收集结果"
            
        logger.info(f"需求收集原始结果: {content}")
        
        # 尝试解析 JSON 响应
        try:
            need_data = json_repair.loads(content)
        except Exception as e:
            logger.error(f"解析需求收集结果失败: {e}")
            # 提供默认响应
            need_data = {
                "status": "CONTINUE",
                "confirm_need": [f"用户输入: {request.user_input}"],
                "need": ["请提供更多详细信息以便为您制定旅游方案"]
            }
        
        # 更新会话状态
        session["last_need_collection"] = need_data
        
        return NeedCollectionResponse(
            status=need_data.get("status", "CONTINUE"),
            confirm_need=need_data.get("confirm_need", []),
            need=need_data.get("need", []),
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"需求收集错误: {e}")
        raise HTTPException(status_code=500, detail=f"需求收集失败: {str(e)}")

@app.post("/api/travel-planning")
async def plan_travel(request: TravelPlanningRequest):
    """第一轮旅游规划接口 - 按照main.py逻辑"""
    try:
        # 创建或获取会话
        session_id = request.session_id or create_session()
        session = get_session(session_id)
        
        logger.info(f"会话 {session_id}: 开始第一轮旅游规划")
        
        # 调用第一轮规划 - 按照main.py逻辑
        planning_results = []
        for chunk in run_travel_planning(request.user_request):
            planning_results.append(chunk)
        
        # 获取最后的结果作为draft
        if planning_results:
            last_chunk = planning_results[-1]
            if "supervisor" in last_chunk and "messages" in last_chunk["supervisor"]:
                draft = last_chunk["supervisor"]["messages"][-1].content
            else:
                draft = str(last_chunk)
        else:
            draft = "规划完成，但未收到具体内容"
        
        # 更新会话状态
        session["travel_plan_draft"] = draft
        session["is_first_round"] = False
        session["planning_results"] = planning_results
        
        return TravelPlanningResponse(
            status="success",
            result=draft,
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"第一轮旅游规划错误: {e}")
        return TravelPlanningResponse(
            status="error",
            session_id=session_id,
            error=str(e)
        )

@app.post("/api/travel-planning-stream")
async def plan_travel_stream(request: TravelPlanningRequest):
    """第一轮旅游规划接口（流式）- 按照main.py逻辑"""
    start_time = time.time()
    
    try:
        # 创建或获取会话
        session_id = request.session_id or create_session()
        session = get_session(session_id)
        
        # 记录会话开始
        logger_manager.log_session_start(
            'planning', 
            session_id, 
            'travel_planning_stream',
            user_request=request.user_request[:100] + "..." if len(request.user_request) > 100 else request.user_request,
            request_length=len(request.user_request)
        )
        
        # 准备流式响应
        def planning_generator():
            step_start_time = time.time()
            try:
                draft = None
                step_count = 0
                
                # 记录开始事件
                log_planning_step(session_id, step_count, "发送规划开始事件", 
                                user_request_preview=request.user_request[:50] + "...")
                
                # 发送开始事件
                yield {
                    "event": "planning_start",
                    "data": {
                        "message": "开始旅游规划...",
                        "user_request": request.user_request
                    },
                    "step": step_count
                }
                
                # 记录开始调用规划函数
                planning_start_time = time.time()
                log_planning_step(session_id, step_count + 1, "开始调用run_travel_planning函数")
                
                for chunk in run_travel_planning(request.user_request):
                    step_count += 1
                    chunk_start_time = time.time()
                    
                    # 详细记录每个步骤
                    logger_manager.log_step_debug(
                        'planning', 
                        session_id, 
                        step_count, 
                        f"处理规划chunk", 
                        data=chunk
                    )
                    
                    # 记录步骤处理时间
                    step_duration = (time.time() - chunk_start_time) * 1000
                    logger_manager.log_performance('planning', session_id, f"步骤{step_count}处理", step_duration)
                    
                    # 发送中间步骤事件
                    yield {
                        "event": "planning_step",
                        "data": chunk,
                        "step": step_count,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # 保存最后的结果作为draft
                    if "supervisor" in chunk and "messages" in chunk["supervisor"]:
                        messages = chunk["supervisor"]["messages"]
                        if messages and len(messages) > 0:
                            last_message = messages[-1]
                            if hasattr(last_message, 'content'):
                                draft = last_message.content
                                log_planning_step(session_id, step_count, "提取到规划内容", 
                                                content_length=len(draft))
                            elif isinstance(last_message, dict) and 'content' in last_message:
                                draft = last_message['content']
                                log_planning_step(session_id, step_count, "提取到规划内容(dict)", 
                                                content_length=len(draft))
                
                # 记录规划完成
                total_planning_time = (time.time() - planning_start_time) * 1000
                logger_manager.log_performance('planning', session_id, "完整规划流程", total_planning_time)
                
                log_planning_step(session_id, step_count + 1, "规划流程完成", 
                                total_steps=step_count, 
                                has_draft=draft is not None,
                                draft_length=len(draft) if draft else 0)
                
                # 发送完成事件
                yield {
                    "event": "planning_complete",
                    "data": {
                        "message": "旅游规划完成",
                        "draft": draft,
                        "total_steps": step_count
                    },
                    "step": step_count + 1
                }
                
                # 更新会话状态
                session["travel_plan_draft"] = draft
                session["is_first_round"] = False
                
                # 记录会话完成
                logger_manager.log_session_complete(
                    'planning', 
                    session_id, 
                    'travel_planning_stream', 
                    step_count + 1,
                    draft_generated=draft is not None,
                    draft_length=len(draft) if draft else 0
                )
                    
            except Exception as e:
                log_planning_error(session_id, f"规划生成器错误: {str(e)}", e)
                yield {
                    "event": "planning_error",
                    "data": {"error": str(e)},
                    "step": step_count + 1
                }
        
        # 返回流式响应
        return StreamingResponse(
            stream_generator(session_id, planning_generator()),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )
        
    except Exception as e:
        # 记录总体错误
        total_time = (time.time() - start_time) * 1000
        logger_manager.log_error('planning', session_id if 'session_id' in locals() else 'unknown', 
                               f"流式第一轮旅游规划错误 (耗时: {total_time:.3f}ms): {str(e)}", e)
        raise HTTPException(status_code=500, detail=f"流式规划失败: {str(e)}")

@app.post("/api/travel-optimize")
async def optimize_travel(request: TravelOptimizeRequest):
    """后续轮次方案优化接口 - 按照main.py逻辑"""
    try:
        # 创建或获取会话
        session_id = request.session_id or create_session()
        session = get_session(session_id)
        
        logger.info(f"会话 {session_id}: 开始方案优化")
        
        # 调用后续轮次优化 - 按照main.py逻辑
        optimization_results = []
        for chunk in run_travel_planning_flexible(
            request.user_feedback,
            request.travel_plan_draft
        ):
            optimization_results.append(chunk)
        
        # 获取最后的结果作为新的draft
        if optimization_results:
            last_chunk = optimization_results[-1]
            if "supervisor" in last_chunk and "messages" in last_chunk["supervisor"]:
                new_draft = last_chunk["supervisor"]["messages"][-1].content
            else:
                new_draft = str(last_chunk)
        else:
            new_draft = "优化完成，但未收到具体内容"
        
        # 更新会话状态
        session["travel_plan_draft"] = new_draft
        session["optimization_results"] = optimization_results
        
        return TravelPlanningResponse(
            status="success",
            result=new_draft,
            session_id=session_id
        )
        
    except Exception as e:
        logger.error(f"方案优化错误: {e}")
        return TravelPlanningResponse(
            status="error",
            session_id=session_id,
            error=str(e)
        )

@app.post("/api/travel-optimize-stream")
async def optimize_travel_stream(request: TravelOptimizeRequest):
    """后续轮次方案优化接口（流式）- 按照main.py逻辑"""
    start_time = time.time()
    
    try:
        # 创建或获取会话
        session_id = request.session_id or create_session()
        session = get_session(session_id)
        
        # 记录会话开始
        logger_manager.log_session_start(
            'optimization', 
            session_id, 
            'travel_optimize_stream',
            user_feedback=request.user_feedback[:100] + "..." if len(request.user_feedback) > 100 else request.user_feedback,
            feedback_length=len(request.user_feedback),
            original_plan_length=len(request.travel_plan_draft)
        )
        
        # 准备流式响应
        def optimization_generator():
            step_start_time = time.time()
            try:
                new_draft = None
                step_count = 0
                
                # 记录开始事件
                log_optimization_step(session_id, step_count, "发送优化开始事件", 
                                    feedback_preview=request.user_feedback[:50] + "...",
                                    original_plan_preview=request.travel_plan_draft[:50] + "...")
                
                # 发送开始事件
                yield {
                    "event": "optimization_start",
                    "data": {
                        "message": "开始方案优化...",
                        "user_feedback": request.user_feedback,
                        "original_plan": request.travel_plan_draft[:200] + "..." if len(request.travel_plan_draft) > 200 else request.travel_plan_draft
                    },
                    "step": step_count
                }
                
                # 记录开始调用优化函数
                optimization_start_time = time.time()
                log_optimization_step(session_id, step_count + 1, "开始调用run_travel_planning_flexible函数")
                
                for chunk in run_travel_planning_flexible(
                    request.user_feedback,
                    request.travel_plan_draft
                ):
                    step_count += 1
                    chunk_start_time = time.time()
                    
                    # 详细记录每个步骤
                    logger_manager.log_step_debug(
                        'optimization', 
                        session_id, 
                        step_count, 
                        f"处理优化chunk", 
                        data=chunk
                    )
                    
                    # 记录步骤处理时间
                    step_duration = (time.time() - chunk_start_time) * 1000
                    logger_manager.log_performance('optimization', session_id, f"优化步骤{step_count}处理", step_duration)
                    
                    # 发送中间步骤事件
                    yield {
                        "event": "optimization_step",
                        "data": chunk,
                        "step": step_count,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # 保存最后的结果作为新的draft
                    if "supervisor" in chunk and "messages" in chunk["supervisor"]:
                        messages = chunk["supervisor"]["messages"]
                        if messages and len(messages) > 0:
                            last_message = messages[-1]
                            if hasattr(last_message, 'content'):
                                new_draft = last_message.content
                                log_optimization_step(session_id, step_count, "提取到优化内容", 
                                                    content_length=len(new_draft))
                            elif isinstance(last_message, dict) and 'content' in last_message:
                                new_draft = last_message['content']
                                log_optimization_step(session_id, step_count, "提取到优化内容(dict)", 
                                                    content_length=len(new_draft))
                
                # 记录优化完成
                total_optimization_time = (time.time() - optimization_start_time) * 1000
                logger_manager.log_performance('optimization', session_id, "完整优化流程", total_optimization_time)
                
                log_optimization_step(session_id, step_count + 1, "优化流程完成", 
                                    total_steps=step_count, 
                                    has_new_draft=new_draft is not None,
                                    new_draft_length=len(new_draft) if new_draft else 0,
                                    original_length=len(request.travel_plan_draft))
                
                # 发送完成事件
                yield {
                    "event": "optimization_complete",
                    "data": {
                        "message": "方案优化完成",
                        "new_draft": new_draft,
                        "total_steps": step_count
                    },
                    "step": step_count + 1
                }
                
                # 更新会话状态
                session["travel_plan_draft"] = new_draft
                
                # 记录会话完成
                logger_manager.log_session_complete(
                    'optimization', 
                    session_id, 
                    'travel_optimize_stream', 
                    step_count + 1,
                    new_draft_generated=new_draft is not None,
                    new_draft_length=len(new_draft) if new_draft else 0,
                    optimization_successful=new_draft is not None and len(new_draft) > 0
                )
                    
            except Exception as e:
                log_optimization_error(session_id, f"优化生成器错误: {str(e)}", e)
                yield {
                    "event": "optimization_error",
                    "data": {"error": str(e)},
                    "step": step_count + 1
                }
        
        # 返回流式响应
        return StreamingResponse(
            stream_generator(session_id, optimization_generator()),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
            }
        )
        
    except Exception as e:
        # 记录总体错误
        total_time = (time.time() - start_time) * 1000
        logger_manager.log_error('optimization', session_id if 'session_id' in locals() else 'unknown', 
                               f"流式方案优化错误 (耗时: {total_time:.3f}ms): {str(e)}", e)
        raise HTTPException(status_code=500, detail=f"流式优化失败: {str(e)}")

@app.get("/api/sessions/{session_id}")
async def get_session_info(session_id: str):
    """获取会话信息"""
    try:
        session = get_session(session_id)
        return {
            "session_id": session_id,
            "created_at": session["created_at"].isoformat(),
            "user_input_history": session["user_input_history"],
            "is_first_round": session["is_first_round"],
            "status": session["status"],
            "has_travel_plan_draft": session["travel_plan_draft"] is not None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会话信息错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    try:
        if session_id in sessions:
            del sessions[session_id]
            return {"message": "会话已删除", "session_id": session_id}
        else:
            raise HTTPException(status_code=404, detail="会话不存在")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除会话错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions")
async def list_sessions():
    """列出所有会话"""
    try:
        session_list = []
        for session_id, session_data in sessions.items():
            session_list.append({
                "session_id": session_id,
                "created_at": session_data["created_at"].isoformat(),
                "status": session_data["status"],
                "input_count": len(session_data["user_input_history"]),
                "is_first_round": session_data["is_first_round"]
            })
        return {"sessions": session_list, "total": len(session_list)}
    except Exception as e:
        logger.error(f"列出会话错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 错误处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"全局异常: {exc}")
    return {"error": "服务器内部错误", "detail": str(exc)}

if __name__ == "__main__":
    import uvicorn
    
    # 启动服务器
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
