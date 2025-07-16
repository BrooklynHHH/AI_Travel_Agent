"""
增强版打印工具
用于美化多智能体系统的输出
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import re


def enhanced_pretty_print_travel_planning(stream):
    """
    增强版旅游规划打印工具
    
    Args:
        stream: supervisor的流式输出
        
    Returns:
        dict: 整理后的智能体输出结果
    """
    print("🌟 开始旅游规划...")
    print("=" * 60)
    
    agent_outputs = {}
    current_agent = None
    
    try:
        for chunk in stream:
            if isinstance(chunk, dict):
                # 处理不同类型的输出
                for key, value in chunk.items():
                    if key != "__end__":  # 忽略结束标记
                        current_agent = key
                        
                        # 打印智能体标题
                        print(f"\n🤖 【{get_agent_display_name(key)}】正在工作...")
                        print("-" * 40)
                        
                        # 处理智能体输出
                        if isinstance(value, dict):
                            if "messages" in value:
                                messages = value["messages"]
                                if messages and len(messages) > 0:
                                    content = messages[-1].get("content", "")
                                    if content:
                                        formatted_content = format_agent_output(content, key)
                                        print(formatted_content)
                                        
                                        # 保存到结果中
                                        if key not in agent_outputs:
                                            agent_outputs[key] = []
                                        agent_outputs[key].append(content)
                            
                            if "error" in value:
                                print(f"❌ 错误: {value['error']}")
                                if key not in agent_outputs:
                                    agent_outputs[key] = []
                                agent_outputs[key].append(f"错误: {value['error']}")
                        
                        elif isinstance(value, str):
                            formatted_content = format_agent_output(value, key)
                            print(formatted_content)
                            
                            if key not in agent_outputs:
                                agent_outputs[key] = []
                            agent_outputs[key].append(value)
                        
                        print("-" * 40)
    
    except Exception as e:
        print(f"❌ 处理流式输出时出错: {e}")
        return agent_outputs
    
    # 打印总结
    print("\n" + "=" * 60)
    print("✅ 旅游规划完成！")
    print(f"📊 共调用了 {len(agent_outputs)} 个智能体")
    
    for agent_name in agent_outputs.keys():
        print(f"   • {get_agent_display_name(agent_name)}")
    
    print("=" * 60)
    
    return agent_outputs


def get_agent_display_name(agent_name: str) -> str:
    """获取智能体的显示名称"""
    name_mapping = {
        "tour_search_agent": "🔍 景点搜索专家",
        "day_plan_agent": "📅 行程规划师", 
        "live_transport_agent": "🚗 交通住宿顾问",
        "travel_butler_agent": "🎩 旅行管家",
        "need_collect_agent": "📝 需求收集专家"
    }
    return name_mapping.get(agent_name, f"🤖 {agent_name}")


def format_agent_output(content: str, agent_name: str) -> str:
    """格式化智能体输出内容"""
    if not content:
        return "📝 (无输出内容)"
    
    # 根据智能体类型进行特殊格式化
    if agent_name == "tour_search_agent":
        return format_search_output(content)
    elif agent_name == "day_plan_agent":
        return format_planning_output(content)
    elif agent_name == "live_transport_agent":
        return format_transport_output(content)
    elif agent_name == "travel_butler_agent":
        return format_butler_output(content)
    else:
        return format_general_output(content)


def format_search_output(content: str) -> str:
    """格式化搜索输出"""
    # 添加搜索相关的图标和格式
    formatted = content.replace("景点", "🏛️ 景点")
    formatted = formatted.replace("美食", "🍜 美食")
    formatted = formatted.replace("酒店", "🏨 酒店")
    return formatted


def format_planning_output(content: str) -> str:
    """格式化规划输出"""
    # 添加规划相关的图标
    formatted = content.replace("Day", "📅 Day")
    formatted = formatted.replace("行程", "🗺️ 行程")
    formatted = formatted.replace("路线", "🛣️ 路线")
    return formatted


def format_transport_output(content: str) -> str:
    """格式化交通输出"""
    # 添加交通相关的图标
    formatted = content.replace("交通", "🚗 交通")
    formatted = formatted.replace("住宿", "🏨 住宿")
    formatted = formatted.replace("地铁", "🚇 地铁")
    formatted = formatted.replace("公交", "🚌 公交")
    return formatted


def format_butler_output(content: str) -> str:
    """格式化管家输出"""
    # 添加管家服务相关的图标
    formatted = content.replace("天气", "🌤️ 天气")
    formatted = content.replace("注意", "⚠️ 注意")
    formatted = formatted.replace("建议", "💡 建议")
    formatted = formatted.replace("提醒", "🔔 提醒")
    return formatted


def format_general_output(content: str) -> str:
    """格式化通用输出"""
    # 基本的Markdown格式化
    formatted = content
    
    # 处理标题
    formatted = re.sub(r'^# (.*)', r'🎯 \1', formatted, flags=re.MULTILINE)
    formatted = re.sub(r'^## (.*)', r'📋 \1', formatted, flags=re.MULTILINE)
    formatted = re.sub(r'^### (.*)', r'📌 \1', formatted, flags=re.MULTILINE)
    
    # 处理列表
    formatted = re.sub(r'^- (.*)', r'  • \1', formatted, flags=re.MULTILINE)
    formatted = re.sub(r'^\* (.*)', r'  • \1', formatted, flags=re.MULTILINE)
    
    return formatted


def save_results_to_file(agent_outputs: Dict[str, List[str]], filename: Optional[str] = None) -> str:
    """
    保存结果到文件
    
    Args:
        agent_outputs: 智能体输出结果
        filename: 文件名，如果不提供则自动生成
        
    Returns:
        str: 保存的文件路径
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"travel_plan_{timestamp}.md"
    
    # 确保文件扩展名
    if not filename.endswith('.md'):
        filename += '.md'
    
    # 创建输出目录
    output_dir = "travel_plans"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            # 写入文件头
            f.write(f"# 🧳 智能旅游规划方案\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # 写入各智能体的输出
            for agent_name, outputs in agent_outputs.items():
                f.write(f"## {get_agent_display_name(agent_name)}\n\n")
                
                for i, output in enumerate(outputs, 1):
                    if len(outputs) > 1:
                        f.write(f"### 输出 {i}\n\n")
                    f.write(f"{output}\n\n")
                    f.write("---\n\n")
            
            # 写入文件尾
            f.write("## 📝 使用说明\n\n")
            f.write("- 本方案由AI智能体系统自动生成\n")
            f.write("- 请根据实际情况调整行程安排\n")
            f.write("- 如需修改，请提供具体的调整需求\n\n")
            f.write("**祝您旅途愉快！** 🌟\n")
        
        print(f"💾 结果已保存到: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"❌ 保存文件失败: {e}")
        return ""


def print_agent_summary(agent_outputs: Dict[str, List[str]]):
    """打印智能体输出摘要"""
    print("\n📊 智能体输出摘要:")
    print("=" * 50)
    
    for agent_name, outputs in agent_outputs.items():
        print(f"\n{get_agent_display_name(agent_name)}:")
        print(f"  📝 输出数量: {len(outputs)}")
        
        # 计算总字符数
        total_chars = sum(len(output) for output in outputs)
        print(f"  📏 总字符数: {total_chars}")
        
        # 显示第一个输出的前100个字符作为预览
        if outputs:
            preview = outputs[0][:100].replace('\n', ' ')
            if len(outputs[0]) > 100:
                preview += "..."
            print(f"  👀 预览: {preview}")
    
    print("=" * 50)


def export_to_json(agent_outputs: Dict[str, List[str]], filename: Optional[str] = None) -> str:
    """
    导出结果为JSON格式
    
    Args:
        agent_outputs: 智能体输出结果
        filename: 文件名
        
    Returns:
        str: 保存的文件路径
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"travel_plan_{timestamp}.json"
    
    if not filename.endswith('.json'):
        filename += '.json'
    
    output_dir = "travel_plans"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filepath = os.path.join(output_dir, filename)
    
    # 构建JSON数据
    json_data = {
        "generated_at": datetime.now().isoformat(),
        "agent_outputs": agent_outputs,
        "summary": {
            "total_agents": len(agent_outputs),
            "agent_names": list(agent_outputs.keys()),
            "total_outputs": sum(len(outputs) for outputs in agent_outputs.values())
        }
    }
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 JSON结果已保存到: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"❌ 保存JSON文件失败: {e}")
        return ""


# 使用示例
if __name__ == "__main__":
    # 模拟智能体输出
    sample_outputs = {
        "tour_search_agent": [
            "找到了北京的热门景点：故宫、天安门、长城等...",
            "推荐的美食：北京烤鸭、炸酱面、豆汁..."
        ],
        "day_plan_agent": [
            "Day 1: 上午游览天安门广场，下午参观故宫...",
            "Day 2: 前往八达岭长城，下午返回市区..."
        ],
        "live_transport_agent": [
            "推荐住宿：王府井附近的酒店，交通便利...",
            "交通方案：地铁1号线直达各主要景点..."
        ]
    }
    
    # 打印摘要
    print_agent_summary(sample_outputs)
    
    # 保存到文件
    save_results_to_file(sample_outputs, "sample_travel_plan.md")
    
    # 导出JSON
    export_to_json(sample_outputs, "sample_travel_plan.json")
