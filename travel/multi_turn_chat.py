#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多轮对话旅游规划系统
基于 agent_V4.ipynb 中的代码逻辑实现
"""

import sys
import os
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage

# 添加路径以导入相关模块
sys.path.append('agent-mi/travel')

try:
    from supervisor_agent import (
        llm, tour_search_agent, day_plan_agent, 
        live_transport_agent, travel_butler_agent
    )
    from langgraph_supervisor import create_supervisor
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保相关模块文件存在并且路径正确")
    sys.exit(1)

class MultiTurnChat:
    """多轮对话系统"""
    
    def __init__(self):
        """初始化系统"""
        print("🚀 初始化多轮对话旅游规划系统...")
        
        # 创建主管智能体
        self.supervisor = create_supervisor(
            agents=[tour_search_agent, day_plan_agent, live_transport_agent, travel_butler_agent],
            model=llm,
            prompt="""
**# 角色定位**
你是一位**“旅程总设计师”（Master Planner）**，一个顶级的Supervisor智能体。你的核心职责是分析用户的旅行需求，将其拆解为一系列结构化的任务，并精准地调度下属的专家智能体团队来协同完成。最终，你将整合所有产出，形成一份无缝衔接、高度个性化且可迭代优化的旅行解决方案。

**# 专家智能体团队介绍**
你领导以下四个高度专业化的智能体：
1.  **tour_search_agent (信息勘探员)**: 负责勘探和收集所有“原材料”，包括景点、美食、文化体验、活动等。
2.  **day_plan_agent (行程规划师)**: 负责将“原材料”组织排序，设计详尽的每日行程（What & When）。
3.  **live_transport_agent (后勤调度官)**: 负责解决交通和住宿问题（How & Where）。
4.  **travel_butler_agent (贴心旅行管家)**: 负责提供打包、安全、礼仪等增值服务，完善旅行体验。

**# Guiding Principles (行动指导原则)**
你的所有决策都必须遵循以下核心原则：
1.  **渐进式信息补充**: 不要期望用户一次性提供所有信息。你的任务是根据现有信息采取行动，并自然地引导用户补充下一步所需的关键信息。
2.  **依赖驱动执行**: 严格遵守智能体之间的任务依赖关系。例如，必须先由`tour_search_agent`提供素材，`day_plan_agent`才能开始规划。
3.  **精准任务调度**: 针对用户的具体反馈或单一问题，只调用最相关的智能体进行局部更新，避免不必要的资源浪费。
4.  **主动冲突识别**: 当发现用户的需求存在内在矛盾时（如预算过低与期望过高），你的首要任务是**中断规划并向用户澄清**，而不是生成一个不可行的方案。

**# 动态规划与决策逻辑**
你将根据用户需求的**完备层级**来决定执行何种规划流程：

**第一阶段：基础构建 (处理L1基础需求: 目的地, 时长)**
*   **触发条件**: 用户仅提供模糊想法，缺少**目的地**或**时长**。
*   **行动指令**:
    *   若无`目的地`：调用 **`tour_search_agent`**，任务是“基于用户偏好推荐2-3个目的地选项”。
    *   若有`目的地`但无`时长`等信息：调用 **`tour_search_agent`**，任务是“围绕该目的地，广泛推荐其核心景点与体验，为用户提供规划灵感”。
    *   **目标**: 引导用户确定规划的“时空坐标”。

**第二阶段：框架规划 (处理L2重要信息: 预算, 人员, 方式等)**
*   **触发条件**: 用户已提供**目的地**和**时长**，并给出了预算、人员等核心信息。这是**最常见的核心规划流程**。
*   **行动指令 (序列化与并行)**:
    1.  **首先**，调用 **`tour_search_agent`** 深度搜索符合用户偏好和风格的“原材料”。
    2.  **然后**，**并行调用**以下两个智能体：
        *   **`day_plan_agent`**: 接收`tour_search_agent`的输出，开始构建每日行程框架。
        *   **`live_transport_agent`**: 根据预算和人员构成，开始规划交通方案并筛选住宿选项。
    *   **目标**: 生成一份包含行程、交通、住宿的结构化**初稿**。

**第三阶段：个性化与迭代优化 (处理L3补充信息及反馈)**
*   **触发条件1 (首次完善)**: 核心行程**初稿**已制定完成。
*   **行动指令1**: 调用 **`travel_butler_agent`**，将初稿作为输入，为其添加所有必要的贴心建议和注意事项，完成**首次完整交付**。

*   **触发条件2 (用户反馈)**: 用户对方案的**特定部分**提出修改意见。
*   **行动指令2 (精准再激活)**:
    *   若用户想“调整景点” -> **只调用 `tour_search_agent`**。
    *   若用户想“调整行程节奏” -> **只调用 `day_plan_agent`**。
    *   若用户想“调整酒店或预算” -> **只调用 `live_transport_agent`**。
    *   若用户需要“更多建议或美食” -> **只调用 `travel_butler_agent`**。
    *   **目标**: 高效响应用户反馈，实现方案的快速迭代优化。

**# 特定任务处理**
*   **触发条件**: 用户的需求非常具体，只涉及单一领域（例如“推荐酒店”、“查询交通”)。
*   **行动指令**: **只调用最相关的智能体**（如`live_transport_agent`），直接提供精准答案。

**# 输出格式要求**
在调用智能体之前，你必须生成一份结构化的执行计划，格式如下：
```json
{
  "execution_plan": [
    {
      "agent_name": "被调用的智能体名称",
      "task_description": "一句清晰、明确的任务指令",
      "input_data": {
        "confirm_need": ["相关需求1", "相关需求2"],
        "inferred_style": ["相关风格推断1"]
      }
    }
  ],
  "synthesis_instruction": "在所有智能体完成任务后，你需要如何整合他们的结果，形成最终的交付物。"
}
```
"""
        ).compile()
        
        # 对话历史
        self.conversation_messages = []
        
        print("✅ 系统初始化完成！")
    
    def chat(self, user_input: str) -> Dict[str, Any]:
        """
        处理用户输入并返回系统响应
        
        Args:
            user_input: 用户输入
            
        Returns:
            包含系统响应和消息历史的字典
        """
        print(f"\n💬 用户输入: {user_input}")
        print("-" * 50)
        
        try:
            # 如果是第一轮对话，直接使用用户输入
            if not self.conversation_messages:
                input_messages = [{"role": "user", "content": user_input}]
            else:
                # 后续轮次，将用户输入添加到历史消息中
                self.conversation_messages.append(HumanMessage(content=user_input))
                input_messages = [{"role": "user", "content": str(self.conversation_messages)}]
            
            # 调用主管智能体
            result_chunks = []
            for chunk in self.supervisor.stream({"messages": input_messages}):
                result_chunks.append(chunk)
                print(f"📊 处理中: {list(chunk.keys())}")
            
            # 获取最终结果
            if result_chunks:
                final_chunk = result_chunks[-1]
                if "supervisor" in final_chunk:
                    messages = final_chunk["supervisor"]["messages"]
                    
                    # 更新对话历史
                    self.conversation_messages = messages
                    
                    # 提取系统响应
                    system_response = ""
                    for msg in messages:
                        if hasattr(msg, 'content'):
                            system_response += msg.content + "\n"
                    
                    print("✅ 处理完成！")
                    
                    return {
                        "status": "success",
                        "response": system_response.strip(),
                        "messages": messages,
                        "chunks": result_chunks
                    }
            
            return {
                "status": "error",
                "response": "处理过程中没有收到有效结果"
            }
            
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            return {
                "status": "error",
                "response": f"处理您的输入时出现错误: {str(e)}"
            }
    
    def get_conversation_history(self) -> List:
        """获取对话历史"""
        return self.conversation_messages
    
    def reset_conversation(self):
        """重置对话历史"""
        self.conversation_messages = []
        print("🔄 对话历史已重置")

def main():
    """主函数 - 演示多轮对话流程"""
    print("🎯 多轮对话旅游规划系统演示")
    print("=" * 50)
    
    # 创建对话系统
    chat_system = MultiTurnChat()
    
    # 第一轮对话
    print("\n🔥 第一轮对话")
    user_input_1 = "周末出去兜兜风"
    result_1 = chat_system.chat(user_input_1)
    
    if result_1["status"] == "success":
        print(f"\n🤖 系统响应:")
        print(result_1["response"])
        
        # 获取第一轮的消息历史
        round_1_messages = result_1["messages"]
        print(f"\n📝 第一轮消息数量: {len(round_1_messages)}")
        
        # 第二轮对话 - 用户反馈
        print("\n🔥 第二轮对话")
        user_input_2 = "去北京周边"
        result_2 = chat_system.chat(user_input_2)
        
        if result_2["status"] == "success":
            print(f"\n🤖 系统响应:")
            print(result_2["response"])
            
            # 获取第二轮的消息历史
            round_2_messages = result_2["messages"]
            print(f"\n📝 第二轮消息数量: {len(round_2_messages)}")
            
            # 第三轮对话 - 进一步细化
            print("\n🔥 第三轮对话")
            user_input_3 = "预算5000元，两个人，想要轻松一点的行程"
            result_3 = chat_system.chat(user_input_3)
            
            if result_3["status"] == "success":
                print(f"\n🤖 系统响应:")
                print(result_3["response"])
                
                print(f"\n📝 第三轮消息数量: {len(result_3['messages'])}")
            else:
                print(f"❌ 第三轮对话失败: {result_3['response']}")
        else:
            print(f"❌ 第二轮对话失败: {result_2['response']}")
    else:
        print(f"❌ 第一轮对话失败: {result_1['response']}")
    
    print("\n🎉 演示完成！")

def interactive_chat():
    """交互式对话模式"""
    print("🎯 交互式多轮对话模式")
    print("=" * 50)
    print("输入 'quit' 退出，输入 'reset' 重置对话历史")
    
    chat_system = MultiTurnChat()
    
    while True:
        try:
            user_input = input("\n👤 您: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 再见！")
                break
            elif user_input.lower() == 'reset':
                chat_system.reset_conversation()
                continue
            elif not user_input:
                print("请输入有效内容")
                continue
            
            result = chat_system.chat(user_input)
            
            if result["status"] == "success":
                print(f"\n🤖 系统: {result['response']}")
            else:
                print(f"\n❌ 错误: {result['response']}")
                
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")

if __name__ == "__main__":
    # 可以选择运行演示模式或交互模式
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_chat()
    else:
        main()
