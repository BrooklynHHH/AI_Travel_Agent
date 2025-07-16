#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强型流式输出管理器
为LangGraph多智能体系统提供优化的流式输出体验
"""

import time
import json
import sys
from typing import Dict, Any, List, Optional, Union, Generator
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import threading
from collections import defaultdict

# 颜色和样式定义
class Colors:
    """控制台颜色定义"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # 基础颜色
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # 亮色
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    
    # 背景色
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'

class Icons:
    """图标定义"""
    SUPERVISOR = "🎯"
    SEARCH = "🔍"
    PLAN = "📋"
    TRANSPORT = "🚗"
    BUTLER = "🎩"
    
    THINKING = "💭"
    TOOL = "🔧"
    SUCCESS = "✅"
    ERROR = "❌"
    WARNING = "⚠️"
    INFO = "ℹ️"
    
    PROGRESS = "📊"
    TIME = "⏱️"
    TOKEN = "💬"
    CUSTOM = "🔮"

class StreamMode(Enum):
    """流式模式枚举"""
    UPDATES = "updates"
    MESSAGES = "messages"
    CUSTOM = "custom"
    DEBUG = "debug"

@dataclass
class AgentConfig:
    """智能体配置"""
    name: str
    display_name: str
    icon: str
    color: str
    description: str

class AgentRegistry:
    """智能体注册表"""
    
    AGENTS = {
        "supervisor": AgentConfig(
            name="supervisor",
            display_name="旅程总设计师",
            icon=Icons.SUPERVISOR,
            color=Colors.BRIGHT_MAGENTA,
            description="协调和管理多个专业智能体团队"
        ),
        "tour_search_agent": AgentConfig(
            name="tour_search_agent",
            display_name="信息勘探员",
            icon=Icons.SEARCH,
            color=Colors.BRIGHT_BLUE,
            description="搜索景点、美食、文化体验等信息"
        ),
        "day_plan_agent": AgentConfig(
            name="day_plan_agent",
            display_name="行程规划师",
            icon=Icons.PLAN,
            color=Colors.BRIGHT_GREEN,
            description="制定详细的每日行程安排"
        ),
        "live_transport_agent": AgentConfig(
            name="live_transport_agent",
            display_name="后勤调度官",
            icon=Icons.TRANSPORT,
            color=Colors.BRIGHT_YELLOW,
            description="规划交通路线和住宿安排"
        ),
        "travel_butler_agent": AgentConfig(
            name="travel_butler_agent",
            display_name="贴心旅行管家",
            icon=Icons.BUTLER,
            color=Colors.BRIGHT_CYAN,
            description="提供贴心建议和注意事项"
        )
    }
    
    @classmethod
    def get_agent_config(cls, agent_name: str) -> AgentConfig:
        """获取智能体配置"""
        return cls.AGENTS.get(agent_name, AgentConfig(
            name=agent_name,
            display_name=agent_name,
            icon="🤖",
            color=Colors.WHITE,
            description="未知智能体"
        ))

class ProgressBar:
    """进度条组件"""
    
    def __init__(self, total: int = 100, width: int = 20):
        self.total = total
        self.width = width
        self.current = 0
    
    def update(self, value: int):
        """更新进度"""
        self.current = min(value, self.total)
    
    def render(self) -> str:
        """渲染进度条"""
        filled = int(self.width * self.current / self.total)
        bar = "▓" * filled + "░" * (self.width - filled)
        percentage = int(100 * self.current / self.total)
        return f"{bar} {percentage}%"

class TokenStreamer:
    """Token流式显示器"""
    
    def __init__(self):
        self.current_line = ""
        self.token_count = 0
        self.start_time = time.time()
    
    def add_token(self, token: str, agent_name: str = ""):
        """添加token"""
        self.token_count += 1
        self.current_line += token
        
        # 实时显示token（打字机效果）
        print(token, end='', flush=True)
    
    def finish_message(self, agent_name: str = ""):
        """完成消息输出"""
        if self.current_line.strip():
            elapsed = time.time() - self.start_time
            speed = self.token_count / elapsed if elapsed > 0 else 0
            
            print()  # 换行
            print(f"{Colors.DIM}📊 Token统计: {self.token_count} tokens, "
                  f"速度: {speed:.1f} tokens/s{Colors.RESET}")
            
        self.current_line = ""
        self.token_count = 0
        self.start_time = time.time()

class ExecutionTracker:
    """执行跟踪器"""
    
    def __init__(self):
        self.start_time = time.time()
        self.agent_times = {}
        self.current_agent = None
        self.agent_start_time = None
    
    def start_agent(self, agent_name: str):
        """开始执行智能体"""
        if self.current_agent and self.agent_start_time:
            # 结束上一个智能体的计时
            self.agent_times[self.current_agent] = time.time() - self.agent_start_time
        
        self.current_agent = agent_name
        self.agent_start_time = time.time()
    
    def finish_agent(self, agent_name: str):
        """完成智能体执行"""
        if self.current_agent == agent_name and self.agent_start_time:
            self.agent_times[agent_name] = time.time() - self.agent_start_time
            self.current_agent = None
            self.agent_start_time = None
    
    def get_total_time(self) -> float:
        """获取总执行时间"""
        return time.time() - self.start_time
    
    def get_agent_time(self, agent_name: str) -> float:
        """获取智能体执行时间"""
        return self.agent_times.get(agent_name, 0.0)

class EnhancedStreamManager:
    """增强型流式输出管理器"""
    
    def __init__(self, 
                 show_progress: bool = True,
                 show_tokens: bool = True,
                 show_timing: bool = True,
                 verbose_level: int = 1):
        """
        初始化流式输出管理器
        
        Args:
            show_progress: 是否显示进度信息
            show_tokens: 是否显示token流式输出
            show_timing: 是否显示时间统计
            verbose_level: 详细程度 (0=简洁, 1=标准, 2=详细)
        """
        self.show_progress = show_progress
        self.show_tokens = show_tokens
        self.show_timing = show_timing
        self.verbose_level = verbose_level
        
        self.token_streamer = TokenStreamer()
        self.execution_tracker = ExecutionTracker()
        self.progress_bars = {}
        
        self.current_agent = None
        self.message_buffer = []
        
    def print_header(self):
        """打印系统启动头部"""
        print(f"\n{Colors.BOLD}{Colors.BRIGHT_MAGENTA}")
        print("━" * 60)
        print(f"{Icons.SUPERVISOR} 旅程总设计师 - 增强流式输出系统")
        print("━" * 60)
        print(f"{Colors.RESET}")
        print(f"{Colors.DIM}启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}\n")
    
    def print_execution_plan(self, plan_data: Dict[str, Any]):
        """打印执行计划"""
        if self.verbose_level < 1:
            return
            
        print(f"{Colors.BOLD}{Colors.CYAN}📋 执行计划分析{Colors.RESET}")
        print("┌" + "─" * 50)
        
        if "execution_plan" in plan_data:
            for i, step in enumerate(plan_data["execution_plan"], 1):
                agent_name = step.get("agent_name", "unknown")
                task_desc = step.get("task_description", "")
                
                config = AgentRegistry.get_agent_config(agent_name)
                print(f"│ {config.color}{config.icon} {config.display_name}{Colors.RESET}")
                print(f"│   └─ 任务: {task_desc}")
                if i < len(plan_data["execution_plan"]):
                    print("│")
        
        print("└" + "─" * 50)
        print()
    
    def start_agent_execution(self, agent_name: str):
        """开始智能体执行"""
        config = AgentRegistry.get_agent_config(agent_name)
        self.current_agent = agent_name
        self.execution_tracker.start_agent(agent_name)
        
        if self.show_progress:
            print(f"\n{config.color}{config.icon} [{config.display_name}] 开始执行...{Colors.RESET}")
            if self.verbose_level >= 1:
                print(f"{Colors.DIM}   {config.description}{Colors.RESET}")
    
    def handle_tool_call(self, tool_name: str, agent_name: str = ""):
        """处理工具调用"""
        if self.verbose_level >= 1:
            print(f"{Colors.YELLOW}{Icons.TOOL} 调用工具: {tool_name}{Colors.RESET}")
    
    def handle_thinking(self, content: str, agent_name: str = ""):
        """处理思考过程"""
        if self.verbose_level >= 2:
            print(f"{Colors.DIM}{Icons.THINKING} {content[:100]}...{Colors.RESET}")
    
    def handle_token_stream(self, token: str, metadata: Dict[str, Any]):
        """处理token流式输出"""
        if not self.show_tokens:
            return
            
        agent_name = metadata.get("langgraph_node", "")
        
        # 如果是新的智能体开始输出，显示标题
        if agent_name and agent_name != self.current_agent:
            if self.current_agent:
                self.token_streamer.finish_message(self.current_agent)
            
            config = AgentRegistry.get_agent_config(agent_name)
            print(f"\n{config.color}{Icons.TOKEN} [{config.display_name}] {Colors.RESET}", end="")
            self.current_agent = agent_name
        
        self.token_streamer.add_token(token, agent_name)
    
    def handle_custom_data(self, data: Any, agent_name: str = ""):
        """处理自定义数据"""
        if self.verbose_level >= 1:
            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"{Colors.CYAN}{Icons.CUSTOM} {key}: {value}{Colors.RESET}")
            else:
                print(f"{Colors.CYAN}{Icons.CUSTOM} {str(data)}{Colors.RESET}")
    
    def finish_agent_execution(self, agent_name: str, success: bool = True):
        """完成智能体执行"""
        config = AgentRegistry.get_agent_config(agent_name)
        self.execution_tracker.finish_agent(agent_name)
        
        if self.show_timing:
            elapsed = self.execution_tracker.get_agent_time(agent_name)
            status_icon = Icons.SUCCESS if success else Icons.ERROR
            status_color = Colors.GREEN if success else Colors.RED
            
            print(f"\n{status_color}{status_icon} [{config.display_name}] "
                  f"{'完成' if success else '失败'} "
                  f"(耗时: {elapsed:.1f}秒){Colors.RESET}")
    
    def print_summary(self):
        """打印执行总结"""
        if not self.show_timing:
            return
            
        total_time = self.execution_tracker.get_total_time()
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}✅ 执行完成{Colors.RESET}")
        print("┌" + "─" * 40)
        print(f"│ 总耗时: {total_time:.1f}秒")
        
        for agent_name, elapsed in self.execution_tracker.agent_times.items():
            config = AgentRegistry.get_agent_config(agent_name)
            print(f"│ {config.icon} {config.display_name}: {elapsed:.1f}秒")
        
        print("└" + "─" * 40)
    
    def process_stream_chunk(self, chunk: Dict[str, Any], stream_mode: str = ""):
        """处理流式数据块"""
        try:
            # 处理updates模式
            if stream_mode == StreamMode.UPDATES.value or "updates" in str(chunk):
                self._handle_updates_chunk(chunk)
            
            # 处理messages模式
            elif stream_mode == StreamMode.MESSAGES.value or "messages" in str(chunk):
                self._handle_messages_chunk(chunk)
            
            # 处理custom模式
            elif stream_mode == StreamMode.CUSTOM.value or "custom" in str(chunk):
                self._handle_custom_chunk(chunk)
            
            # 处理其他类型的chunk
            else:
                self._handle_generic_chunk(chunk)
                
        except Exception as e:
            print(f"{Colors.RED}{Icons.ERROR} 处理流式数据时出错: {str(e)}{Colors.RESET}")
    
    def _handle_updates_chunk(self, chunk: Dict[str, Any]):
        """处理updates类型的chunk"""
        for node_name, data in chunk.items():
            if node_name in AgentRegistry.AGENTS:
                self.start_agent_execution(node_name)
                
                # 处理消息数据
                if isinstance(data, dict) and "messages" in data:
                    messages = data["messages"]
                    if isinstance(messages, list):
                        for msg in messages:
                            if hasattr(msg, 'content') and msg.content:
                                self._display_agent_output(msg.content, node_name)
                
                self.finish_agent_execution(node_name)
    
    def _handle_messages_chunk(self, chunk: Dict[str, Any]):
        """处理messages类型的chunk"""
        # chunk应该是(token, metadata)的格式
        if isinstance(chunk, tuple) and len(chunk) == 2:
            token, metadata = chunk
            if hasattr(token, 'content') and token.content:
                self.handle_token_stream(token.content, metadata)
    
    def _handle_custom_chunk(self, chunk: Dict[str, Any]):
        """处理custom类型的chunk"""
        self.handle_custom_data(chunk)
    
    def _handle_generic_chunk(self, chunk: Dict[str, Any]):
        """处理通用类型的chunk"""
        if self.verbose_level >= 2:
            print(f"{Colors.DIM}{Icons.INFO} 收到数据: {str(chunk)[:100]}...{Colors.RESET}")
    
    def _display_agent_output(self, content: str, agent_name: str):
        """显示智能体输出内容"""
        config = AgentRegistry.get_agent_config(agent_name)
        
        # 分行显示长内容
        lines = content.split('\n')
        for line in lines:
            if line.strip():
                print(f"{config.color}│ {line}{Colors.RESET}")
    
    def stream_supervisor_execution(self, supervisor_graph, input_data: Dict[str, Any], 
                                  stream_modes: List[str] = None) -> Generator[Dict[str, Any], None, None]:
        """
        流式执行supervisor并提供增强输出
        
        Args:
            supervisor_graph: LangGraph supervisor图
            input_data: 输入数据
            stream_modes: 流式模式列表，默认["updates", "messages", "custom"]
            
        Yields:
            处理后的流式数据
        """
        if stream_modes is None:
            stream_modes = ["updates", "messages", "custom"]
        
        self.print_header()
        
        try:
            # 使用多模式流式输出
            for stream_mode, chunk in supervisor_graph.stream(
                input_data, 
                stream_mode=stream_modes
            ):
                # 处理流式数据
                self.process_stream_chunk(chunk, stream_mode)
                
                # 返回原始数据供其他处理
                yield {
                    "stream_mode": stream_mode,
                    "chunk": chunk,
                    "processed": True
                }
                
        except Exception as e:
            print(f"{Colors.RED}{Icons.ERROR} 执行过程中出错: {str(e)}{Colors.RESET}")
            yield {
                "error": str(e),
                "processed": False
            }
        
        finally:
            # 完成token输出
            if self.current_agent:
                self.token_streamer.finish_message(self.current_agent)
            
            # 打印执行总结
            self.print_summary()


# 便捷函数
def create_enhanced_stream_manager(verbose_level: int = 1, 
                                 show_tokens: bool = True,
                                 show_progress: bool = True,
                                 show_timing: bool = True) -> EnhancedStreamManager:
    """
    创建增强型流式输出管理器的便捷函数
    
    Args:
        verbose_level: 详细程度 (0=简洁, 1=标准, 2=详细)
        show_tokens: 是否显示token流式输出
        show_progress: 是否显示进度信息
        show_timing: 是否显示时间统计
        
    Returns:
        配置好的EnhancedStreamManager实例
    """
    return EnhancedStreamManager(
        verbose_level=verbose_level,
        show_tokens=show_tokens,
        show_progress=show_progress,
        show_timing=show_timing
    )


def simple_stream_output(supervisor_graph, input_data: Dict[str, Any], 
                        verbose_level: int = 1) -> List[Dict[str, Any]]:
    """
    简单的流式输出函数，适合快速使用
    
    Args:
        supervisor_graph: LangGraph supervisor图
        input_data: 输入数据
        verbose_level: 详细程度
        
    Returns:
        所有流式数据的列表
    """
    manager = create_enhanced_stream_manager(verbose_level=verbose_level)
    results = []
    
    for result in manager.stream_supervisor_execution(supervisor_graph, input_data):
        results.append(result)
    
    return results
