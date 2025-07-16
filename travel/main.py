from supervisor_agent import run_travel_planning,run_travel_planning_flexible


import requests
from langchain_core.tools import tool
import time
import os
from requests.packages.urllib3.util.retry import Retry
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
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

# 初始化标记，表示是否是第一轮
import json_repair

is_first_round = True
user_input_history = []
while True:
    user_input = input("请输入你的需求:")
    if user_input == "exit":
        break
    user_input_history.append(user_input)   
    # 根据是否是第一轮选择不同的函数
    if is_first_round:
        need_result = need_collect_agent.invoke({"messages": [{"role": "user", "content": str(user_input_history)}]})
        need_result = need_result["messages"][-1].content
        need_result = json_repair.loads(need_result)
        status = need_result["status"]
        confirm_need = need_result["confirm_need"]
        need = need_result["need"]
        query = f"已经确认的需求如下：{confirm_need}\n待确认的需求如下：{need}\n请帮我规划一下行程"
        print(query)
        # 第一轮使用 run_travel_planning
        for chunk in run_travel_planning(query):
            print(chunk)
            print("\n" + "="*50 + "\n")
        draft = chunk["supervisor"]["messages"][-1].content
        # 第一轮结束后，设置标记为False
        
        is_first_round = False
    else:
        # 后续轮次使用 run_travel_planning_flexible
        for chunk in run_travel_planning_flexible(user_input,draft):
            print(chunk)
            print("\n" + "="*50 + "\n")
        draft = chunk["supervisor"]["messages"][-1].content
    print("=====规划完成=====")