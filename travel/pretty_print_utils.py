"""
美化打印工具模块
用于美化显示流式代理输出
"""

from langchain_core.messages import convert_to_messages


def pretty_print_message(message, indent=False):
    """
    美化打印单个消息
    
    Args:
        message: 要打印的消息对象
        indent: 是否缩进显示
    """
    pretty_message = message.pretty_repr(html=True)
    if not indent:
        print(pretty_message)
        return

    indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
    print(indented)


def pretty_print_messages(update, last_message=False):
    """
    美化打印流式代理输出的消息
    
    Args:
        update: 代理更新对象，可能是元组或字典
        last_message: 是否只显示最后一条消息
    """
    is_subgraph = False
    if isinstance(update, tuple):
        ns, update = update
        # 在打印输出中跳过父图更新
        if len(ns) == 0:
            return

        graph_id = ns[-1].split(":")[0]
        print(f"来自子图 {graph_id} 的更新:")
        print("\n")
        is_subgraph = True

    for node_name, node_update in update.items():
        update_label = f"来自节点 {node_name} 的更新:"
        if is_subgraph:
            update_label = "\t" + update_label

        print(update_label)
        print("\n")

        messages = convert_to_messages(node_update["messages"])
        if last_message:
            messages = messages[-1:]

        for m in messages:
            pretty_print_message(m, indent=is_subgraph)
        print("\n")


def pretty_print_stream_output(stream, show_only_last=False):
    """
    美化打印整个流式输出
    
    Args:
        stream: 流式输出迭代器
        show_only_last: 是否只显示每个更新的最后一条消息
    """
    print("=" * 60)
    print("🚀 开始流式代理输出")
    print("=" * 60)
    
    for update in stream:
        pretty_print_messages(update, last_message=show_only_last)
        print("-" * 40)
    
    print("=" * 60)
    print("✅ 流式输出结束")
    print("=" * 60)


def pretty_print_travel_planning(stream):
    """
    专门为旅游规划系统设计的美化打印函数
    
    Args:
        stream: 旅游规划系统的流式输出
    """
    print("🌟" * 20)
    print("🧳 旅游规划系统启动")
    print("🌟" * 20)
    
    step_count = 0
    agent_outputs = {}  # 存储每个智能体的完整输出
    
    for update in stream:
        step_count += 1
        print(f"\n📍 步骤 {step_count}")
        print("─" * 50)
        
        # 检查是否是子图更新
        is_subgraph = False
        if isinstance(update, tuple):
            ns, update = update
            if len(ns) == 0:
                continue
            graph_id = ns[-1].split(":")[0]
            print(f"🔄 子图更新: {graph_id}")
            is_subgraph = True
        
        # 处理每个节点的更新
        for node_name, node_update in update.items():
            # 根据节点名称添加相应的图标
            node_icons = {
                "need_collect_agent": "📝",
                "tour_search_agent": "🔍", 
                "day_plan_agent": "📅",
                "live_transport_agent": "🚗",
                "travel_butler_agent": "🎩",
                "supervisor": "👨‍💼",
                "attraction_explorer": "🎯",
                "itinerary_planner": "📅",
                "travel_butler": "🎩",
                "transport_planner": "🚗"
            }
            
            icon = node_icons.get(node_name, "🤖")
            
            if is_subgraph:
                print(f"\t{icon} {node_name}:")
            else:
                print(f"{icon} {node_name}:")
            
            # 处理消息
            if "messages" in node_update:
                messages = convert_to_messages(node_update["messages"])
                for message in messages[-1:]:  # 只显示最新消息
                    content = message.content
                    
                    # 保存完整输出到agent_outputs
                    if hasattr(message, 'name') and message.name:
                        agent_outputs[message.name] = content
                    else:
                        agent_outputs[node_name] = content
                    
                    # 显示内容预览（前500字符）
                    display_content = content
                    if len(content) > 500:
                        display_content = content[:500] + "\n\n... [内容较长，已截断显示] ..."
                    
                    if is_subgraph:
                        print(f"\t  💬 {display_content}")
                    else:
                        print(f"  💬 {display_content}")
        
        print()
    
    print("🌟" * 20)
    print("🎉 旅游规划完成！")
    print("🌟" * 20)
    
    # 显示完整的最终结果
    print("\n" + "="*80)
    print("📋 完整旅游规划方案")
    print("="*80)
    
    for agent_name, output in agent_outputs.items():
        print(f"\n🔸 {agent_name} 输出:")
        print("-" * 60)
        print(output)
        print("-" * 60)
    
    return agent_outputs
