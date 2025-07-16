"""
StateGraph旅游规划系统演示脚本
展示如何使用新的基于StateGraph的旅游规划系统
"""

import time
from supervisor_agent_stategraph import run_travel_planning_blocking, run_travel_planning_stategraph
from stategraph_api import travel_api

def demo_basic_usage():
    """演示基本使用方法"""
    print("🎯 演示1: 基本使用方法")
    print("="*50)
    
    user_request = "我想去苏州两日游，主要想看园林和体验当地美食"
    
    print(f"用户需求: {user_request}")
    print("正在生成旅游攻略...")
    
    start_time = time.time()
    result = run_travel_planning_blocking(user_request)
    end_time = time.time()
    
    print(f"✅ 生成完成! 耗时: {end_time - start_time:.2f}秒")
    print(f"状态: {result.get('status', '未知')}")
    print(f"攻略长度: {len(result.get('final_travel_guide', ''))}")
    
    # 保存结果
    with open("demo_result_basic.md", "w", encoding="utf-8") as f:
        f.write(result.get('final_travel_guide', ''))
    print("结果已保存到 demo_result_basic.md")

def demo_stream_usage():
    """演示流式输出"""
    print("\n🎯 演示2: 流式输出")
    print("="*50)
    
    user_request = "我想去西安三日游，重点是历史文化景点"
    
    print(f"用户需求: {user_request}")
    print("开始流式生成...")
    
    step_count = 0
    for event in run_travel_planning_stategraph(user_request):
        step_count += 1
        print(f"步骤 {step_count}: {list(event.keys())}")
        
        # 只显示前几个步骤，避免输出过多
        if step_count >= 6:
            print("... (后续步骤省略)")
            break
    
    print("✅ 流式输出演示完成")

def demo_api_usage():
    """演示API接口使用"""
    print("\n🎯 演示3: API接口使用")
    print("="*50)
    
    # 获取系统信息
    system_info = travel_api.get_system_info()
    print("系统信息:")
    print(f"版本: {system_info['version']}")
    print(f"描述: {system_info['description']}")
    print("工作流步骤:")
    for step in system_info['workflow_steps']:
        print(f"  - {step}")
    
    # 使用API生成攻略
    user_request = "我想去青岛两日游，想看海景和吃海鲜"
    print(f"\n用户需求: {user_request}")
    print("使用API生成攻略...")
    
    result = travel_api.plan_travel_complete(user_request)
    
    if result['success']:
        print("✅ API调用成功!")
        print(f"攻略长度: {len(result['travel_guide'])}")
        
        # 保存结果
        with open("demo_result_api.md", "w", encoding="utf-8") as f:
            f.write(result['travel_guide'])
        print("结果已保存到 demo_result_api.md")
    else:
        print(f"❌ API调用失败: {result['error']}")

def demo_error_handling():
    """演示错误处理"""
    print("\n🎯 演示4: 错误处理")
    print("="*50)
    
    # 测试空输入
    print("测试空输入...")
    result = travel_api.plan_travel_complete("")
    print(f"空输入结果: {'成功' if result['success'] else '失败'}")
    
    # 测试无效输入
    print("测试无效输入...")
    result = travel_api.plan_travel_complete("随便说点什么")
    print(f"无效输入结果: {'成功' if result['success'] else '失败'}")

def main():
    """主演示函数"""
    print("🚀 StateGraph旅游规划系统演示")
    print("="*60)
    
    try:
        # 演示1: 基本使用
        demo_basic_usage()
        
        # 演示2: 流式输出
        demo_stream_usage()
        
        # 演示3: API接口
        demo_api_usage()
        
        # 演示4: 错误处理
        demo_error_handling()
        
        print("\n🎉 所有演示完成!")
        print("="*60)
        print("生成的文件:")
        print("- demo_result_basic.md")
        print("- demo_result_api.md")
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {str(e)}")

if __name__ == "__main__":
    main()
