"""
StateGraph旅游规划系统API接口
提供简单的API接口供其他模块调用
"""

from supervisor_agent_stategraph import run_travel_planning_stategraph, run_travel_planning_blocking
import json
import time
from typing import Dict, Generator, Any

class TravelPlanningStateGraphAPI:
    """StateGraph旅游规划系统API类"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.description = "基于StateGraph的旅游规划系统"
    
    def plan_travel_stream(self, user_request: str) -> Generator[Dict[str, Any], None, None]:
        """
        流式生成旅游规划
        
        Args:
            user_request (str): 用户需求
            
        Yields:
            dict: 包含步骤信息的字典
        """
        try:
            for event in run_travel_planning_stategraph(user_request):
                # 格式化输出
                formatted_event = {
                    "timestamp": time.time(),
                    "event": event,
                    "status": "processing"
                }
                yield formatted_event
                
        except Exception as e:
            yield {
                "timestamp": time.time(),
                "error": str(e),
                "status": "error"
            }
    
    def plan_travel_complete(self, user_request: str) -> Dict[str, Any]:
        """
        完整生成旅游规划（阻塞模式）
        
        Args:
            user_request (str): 用户需求
            
        Returns:
            dict: 完整的旅游规划结果
        """
        try:
            result = run_travel_planning_blocking(user_request)
            
            # 格式化返回结果
            return {
                "success": True,
                "timestamp": time.time(),
                "user_request": user_request,
                "result": result,
                "travel_guide": result.get("final_travel_guide", ""),
                "status": result.get("status", "unknown"),
                "error": result.get("error_message", "")
            }
            
        except Exception as e:
            return {
                "success": False,
                "timestamp": time.time(),
                "user_request": user_request,
                "error": str(e),
                "status": "error"
            }
    
    def get_system_info(self) -> Dict[str, str]:
        """获取系统信息"""
        return {
            "version": self.version,
            "description": self.description,
            "workflow_steps": [
                "1. 需求收集",
                "2. 景点搜索", 
                "3. 行程规划",
                "4. 交通住宿",
                "5. 旅行建议",
                "6. 最终整合"
            ]
        }

# 创建全局API实例
travel_api = TravelPlanningStateGraphAPI()

# 便捷函数
def plan_travel(user_request: str, stream: bool = False):
    """
    便捷的旅游规划函数
    
    Args:
        user_request (str): 用户需求
        stream (bool): 是否使用流式输出
        
    Returns:
        Generator or Dict: 根据stream参数返回不同类型
    """
    if stream:
        return travel_api.plan_travel_stream(user_request)
    else:
        return travel_api.plan_travel_complete(user_request)

# 示例使用
if __name__ == "__main__":
    # 测试API
    api = TravelPlanningStateGraphAPI()
    
    print("系统信息:")
    print(json.dumps(api.get_system_info(), indent=2, ensure_ascii=False))
    
    print("\n测试旅游规划:")
    result = api.plan_travel_complete("我想去苏州两日游")
    print(f"规划结果: {result['success']}")
    if result['success']:
        print(f"攻略长度: {len(result['travel_guide'])}")
    else:
        print(f"错误信息: {result['error']}")
