"""
多智能体系统代理 (MAS - Multi-Agent System)
从 agent_V1.ipynb 中提取的 supervisor 相关代码
"""
from langgraph.checkpoint.memory import MemorySaver

import requests
from langchain_core.tools import tool
import time
import os
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json_repair
import logging
from typing import Dict, Optional, List, Union
import json
from datetime import datetime
import requests
from langchain_core.tools import tool
import time
import os
from requests.packages.urllib3.util.retry import Retry
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
import os
from langchain_community.utilities import OpenWeatherMapAPIWrapper
from typing import Any, Dict, List, Optional, Union
# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化LLM
REACT_API_KEY = "app-lSno2nv5q12VHg4RpgFKRLe6"
AMAP_API_KEY = "cc4f161a65645cb8009739ee9fdda460"
llm = ChatOpenAI(temperature=0.0, base_url='https://mify-be.pt.xiaomi.com/open/api/v1', api_key=REACT_API_KEY)



# os.environ["OPENWEATHERMAP_API_KEY"] = "ac02f15cae37ee320292cd92abbfe055"

# weather = OpenWeatherMapAPIWrapper()




# ==================== 工具函数定义 ====================

def get_geocode(address, api_key):
    """
    获取地理编码信息
    
    Args:
        address (str): 要查询的地址
        api_key (str): 高德地图API密钥
    
    Returns:
        dict: API响应结果
    """
    url = "https://restapi.amap.com/v3/geocode/geo"
    
    params = {
        'key': api_key,
        'address': address,
        'output': 'JSON'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        json_data = response.json()
        # print(json_data)
        formatted_address = json_data["geocodes"][0]["formatted_address"]
        location = json_data["geocodes"][0]["location"]
        return formatted_address, location
        
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return None

@tool("get_geocodes_tool", parse_docstring=True)
def get_geocodes(addresses: list, max_retries: int = 3):
    """
    获取地址列表的的经纬度
    
    Args:
        addresses (list): 要查询的地址列表，如["北京市海淀区玉渊潭", "北京市海淀区颐和园"]
        max_retries (int): 最大重试次数，默认3次
    
    Returns:
        list: 地址列表的经纬度列表，如[('北京市海淀区玉渊潭', '116.306156,39.918653'), ('北京市海淀区颐和园', '116.275179,39.999617')]
    """
    geocodes = []
    
    for address in addresses:
        retry_count = 0
        success = False
        
        while retry_count < max_retries and not success:
            try:
                geocode = get_geocode(address, AMAP_API_KEY)
                geocodes.append(geocode)
                success = True
                time.sleep(0.1)
            except Exception as e:
                retry_count += 1
                print(f"获取{address}的经纬度失败 (第{retry_count}次尝试): {e}")
                
                if retry_count < max_retries:
                    print(f"等待0.1秒后重试...")
                    time.sleep(0.5)
                else:
                    print(f"获取{address}的经纬度最终失败，已重试{max_retries}次")
                    geocodes.append(None)
    str_geocodes = ""
    for x,y in geocodes:
        if x is None:
            continue
        else:
            str_geocodes += f"{x}的经纬度为:{y}\n"
    return str_geocodes

@tool("get_distance_tool", parse_docstring=True)
def get_distance(locations: list):
    """
    获取景点之间的驾车距离，并返回距离信息
    
    Args:
        locations (list): 景点列表，每个景点包含名称和经纬度，两个或两个以上景点，比如[('北京玉渊潭', '116.306156,39.918653'), ('南京夫子庙', '118.795400,32.061700'), ('新疆大巴扎', '87.627701,43.793026')]
    
    Returns:
        dict: 包含景点之间距离信息的字典
    """
    def get_driving_distance(origin, destination, max_retries=3, retry_delay=1):
        """
        使用高德地图 API 获取两个点之间的驾车距离
        """
        url = "https://restapi.amap.com/v3/distance"
        
        params = {
            'key': AMAP_API_KEY,
            'origins': origin,
            'destination': destination,
            'type': 1,  # 驾车距离
            'output': 'JSON'
        }

        session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=retry_delay,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        for attempt in range(max_retries):
            try:
                response = session.get(url, params=params)
                result = response.json()
                
                if result["status"] == "1":
                    return [(int(r["distance"]), int(r["duration"])) for r in result["results"]]
                else:
                    print(f"API请求错误(尝试 {attempt + 1}/{max_retries})：", result)
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                    
            except Exception as e:
                print(f"请求异常(尝试 {attempt + 1}/{max_retries})：", str(e))
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                
        return None

    DISTANCE = []
    # 计算每个景点之间的驾车距离
    for i in range(len(locations)):
        destination = locations[i][1]
        destination_name = locations[i][0]
        origins = locations[i+1:]
        origins_locations = [o[1] for o in origins]
        oringins_name = [o[0] for o in origins]
        if len(origins_locations) > 0:
                begin = "|".join(origins_locations)
                distance = get_driving_distance(begin, destination)
                DISTANCE += [f"【{destination_name}】距离【{oo}】有{bb[0]}米，开车需要：{bb[1]//60}分钟{bb[1]%60}秒" for bb, oo in zip(distance, oringins_name)]
        time.sleep(0.5)  # 添加请求间隔，避免频繁请求
    return {
        "distance": DISTANCE
    }

class AmapRouteAPI:
    """高德地图路线规划API调用类"""
    
    def __init__(self, api_key: str):
        """
        初始化
        Args:
            api_key (str): 高德地图API密钥
        """
        self.api_key = api_key
        self.base_urls = {
            'driving': 'https://restapi.amap.com/v5/direction/driving',
            'walking': 'https://restapi.amap.com/v5/direction/walking', 
            'bicycling': 'https://restapi.amap.com/v5/direction/bicycling',
            'electrobike': 'https://restapi.amap.com/v5/direction/electrobike',
            'transit': 'https://restapi.amap.com/v5/direction/transit/integrated'
        }
    
    def driving_route(self, 
                     origin: str,
                     destination: str,
                     strategy: int = 32,
                     waypoints: Optional[str] = None,
                     avoidpolygons: Optional[str] = None,
                     plate: Optional[str] = None,
                     cartype: int = 0,
                     ferry: int = 0,
                     show_fields: Optional[str] = None) -> Dict[str, Any]:
        """
        驾车路线规划
        
        Args:
            origin (str): 起点经纬度 "经度,纬度"
            destination (str): 终点经纬度 "经度,纬度"
            strategy (int): 驾车策略，默认32（高德推荐）
            waypoints (str): 途经点，多个用";"分隔
            avoidpolygons (str): 避让区域
            plate (str): 车牌号
            cartype (int): 车辆类型 0普通燃油/1纯电动/2插电混动
            ferry (int): 是否使用轮渡 0使用/1不使用
            show_fields (str): 返回字段控制
            
        Returns:
            dict: API响应结果
        """
        params = {
            'key': self.api_key,
            'origin': origin,
            'destination': destination,
            'strategy': strategy,
            'cartype': cartype,
            'ferry': ferry
        }
        
        # 添加可选参数
        if waypoints:
            params['waypoints'] = waypoints
        if avoidpolygons:
            params['avoidpolygons'] = avoidpolygons
        if plate:
            params['plate'] = plate
        if show_fields:
            params['show_fields'] = show_fields
            
        return self._make_request('driving', params)
    
    def walking_route(self,
                     origin: str,
                     destination: str,
                     alternative_route: Optional[int] = None,
                     isindoor: int = 0,
                     show_fields: Optional[str] = None) -> Dict[str, Any]:
        """
        步行路线规划
        
        Args:
            origin (str): 起点经纬度 "经度,纬度"
            destination (str): 终点经纬度 "经度,纬度"
            alternative_route (int): 返回路线条数 1-3
            isindoor (int): 是否室内算路 0不需要/1需要
            show_fields (str): 返回字段控制
            
        Returns:
            dict: API响应结果
        """
        params = {
            'key': self.api_key,
            'origin': origin,
            'destination': destination,
            'isindoor': isindoor
        }
        
        if alternative_route:
            params['alternative_route'] = alternative_route
        if show_fields:
            params['show_fields'] = show_fields
            
        return self._make_request('walking', params)

    
    def bicycling_route(self,
                       origin: str,
                       destination: str,
                       alternative_route: Optional[int] = None,
                       show_fields: Optional[str] = None) -> Dict[str, Any]:
        """
        骑行路线规划
        
        Args:
            origin (str): 起点经纬度 "经度,纬度"
            destination (str): 终点经纬度 "经度,纬度"
            alternative_route (int): 返回路线条数 1-3
            show_fields (str): 返回字段控制
            
        Returns:
            dict: API响应结果
        """
        params = {
            'key': self.api_key,
            'origin': origin,
            'destination': destination
        }
        
        if alternative_route:
            params['alternative_route'] = alternative_route
        if show_fields:
            params['show_fields'] = show_fields
            
        return self._make_request('bicycling', params)
    
    def electrobike_route(self,
                         origin: str,
                         destination: str,
                         alternative_route: Optional[int] = None,
                         show_fields: Optional[str] = None) -> Dict[str, Any]:
        """
        电动车路线规划
        
        Args:
            origin (str): 起点经纬度 "经度,纬度"
            destination (str): 终点经纬度 "经度,纬度"
            alternative_route (int): 返回路线条数 1-3
            show_fields (str): 返回字段控制
            
        Returns:
            dict: API响应结果
        """
        params = {
            'key': self.api_key,
            'origin': origin,
            'destination': destination
        }
        
        if alternative_route:
            params['alternative_route'] = alternative_route
        if show_fields:
            params['show_fields'] = show_fields
            
        return self._make_request('electrobike', params)
    
    def transit_route(self,
                     origin: str,
                     destination: str,
                     strategy: int = 0,
                     city1: str = "010",
                     city2: str = "010",
                     alternative_route: int = 5,
                     nightflag: int = 0,
                     show_fields: Optional[str] = None) -> Dict[str, Any]:
        """
        公交路线规划
        
        Args:
            origin (str): 起点经纬度 "经度,纬度"
            destination (str): 终点经纬度 "经度,纬度"
            strategy (int): 换乘策略 0推荐/1经济/2少换乘/3少步行/4舒适/5不乘地铁/6地铁图/7地铁优先/8时间短
            alternative_route (int): 返回方案条数 1-10
            nightflag (int): 是否考虑夜班车 0不考虑/1考虑
            show_fields (str): 返回字段控制
            
        Returns:
            dict: API响应结果
        """
        params = {
            'key': self.api_key,
            'origin': origin,
            'destination': destination,
            'strategy': strategy,
            'city1': city1,
            'city2': city2,
            'AlternativeRoute': alternative_route,
            'nightflag': nightflag
        }
        
        if show_fields:
            params['show_fields'] = show_fields
            
        return self._make_request('transit', params)
    
    def _make_request(self, route_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送HTTP请求
        
        Args:
            route_type (str): 路线类型
            params (dict): 请求参数
            
        Returns:
            dict: API响应结果
        """
        try:
            response = requests.get(
                self.base_urls[route_type],
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {'error': f'请求失败: {str(e)}', 'status': 'error'}
        except json.JSONDecodeError as e:
            return {'error': f'JSON解析失败: {str(e)}', 'status': 'error'}
  
    def format_route_info(self, result: Dict[str, Any], route_type: str, show_details: bool = True) -> str:
        """
        格式化路线信息
        
        Args:
            result (dict): API响应结果
            route_type (str): 路线类型
            show_details (bool): 是否显示详细路线信息
            
        Returns:
            str: 格式化的路线信息
        """
        if 'error' in result:
            return f"❌ 错误: {result['error']}"
        
        try:
            status = result.get('status', 'unknown')
            if status != '1':
                return f"❌ 请求失败: {result.get('info', 'unknown error')}"
            
            route = result.get('route', {})
            origin = route.get('origin', 'N/A')
            destination = route.get('destination', 'N/A')
            
            info = f"📍 起点: {origin}\n📍 终点: {destination}\n\n"
            
            if route_type == 'transit':
                transits = route.get('transits', [])
                for i, transit in enumerate(transits[:3]):
                    distance = transit.get('distance', 'N/A')
                    cost = transit.get('cost', {})
                    duration = cost.get('duration', 'N/A') if cost else 'N/A'
                    transit_fee = cost.get('transit_fee', 'N/A') if cost else 'N/A'
                    
                    # 转换时间（秒转分钟）
                    duration_min = round(int(duration) / 60, 1) if str(duration).isdigit() else duration
                    
                    info += f"🚌 方案{i+1}: 距离{distance}米, 耗时{duration_min}分钟, 费用{transit_fee}元\n"
                    
                    # 只对公交路线显示详细信息
                    if show_details:
                        info += self._format_transit_route_details(transit, i+1)
                        info += "\n"
                        
            else:
                paths = route.get('paths', [])
                for i, path in enumerate(paths[:3]):
                    distance = path.get('distance', 'N/A')
                    
                    # 根据路线类型获取时间
                    if route_type in ['bicycling', 'electrobike']:
                        duration = path.get('duration', 'N/A')
                    else:
                        cost = path.get('cost', {})
                        duration = cost.get('duration', 'N/A') if cost else 'N/A'
                    
                    # 转换时间（秒转分钟）
                    duration_min = round(int(duration) / 60, 1) if str(duration).isdigit() else duration
                    
                    # 根据路线类型显示不同信息
                    if route_type == 'driving':
                        cost = path.get('cost', {})
                        tolls = cost.get('tolls', 'N/A') if cost else 'N/A'
                        info += f"🚗 路线{i+1}: 距离{distance}米, 耗时{duration_min}分钟, 过路费{tolls}元\n"
                        # 驾车路线不显示详细信息
                            
                    elif route_type == 'bicycling':
                        info += f"🚴 路线{i+1}: 距离{distance}米, 耗时{duration_min}分钟\n"
                    elif route_type == 'electrobike':
                        info += f"⚡ 路线{i+1}: 距离{distance}米, 耗时{duration_min}分钟\n"
                    else:  # walking
                        info += f"🚶 路线{i+1}: 距离{distance}米, 耗时{duration_min}分钟\n"
            
            return info
            
        except Exception as e:
            return f"❌ 解析响应失败: {str(e)}"

    def _format_transit_route_details(self, transit: Dict[str, Any], route_num: int) -> str:
        """格式化公交路线详细信息 - 只显示地铁、公交、火车等交通工具"""
        details = f"   🚌 方案{route_num}详细路线:\n"
        
        segments = transit.get('segments', [])
        step_counter = 1
        
        for seg_idx, segment in enumerate(segments):
            # 公交段（地铁、公交、火车等）
            bus = segment.get('bus', {})
            if bus:
                buslines = bus.get('buslines', [])
                for busline in buslines:
                    line_name = busline.get('name', 'N/A')
                    line_type = busline.get('type', 'N/A')
                    departure_stop = busline.get('departure_stop', {}).get('name', 'N/A')
                    arrival_stop = busline.get('arrival_stop', {}).get('name', 'N/A')
                    via_num = busline.get('via_num', 0)
                    bus_distance = busline.get('distance', 'N/A')
                    bus_duration = busline.get('cost', {}).get('duration', 'N/A')
                    bus_duration_min = round(int(bus_duration) / 60, 1) if str(bus_duration).isdigit() else bus_duration
                    
                    # 根据线路类型显示不同图标
                    if '地铁' in line_type:
                        icon = "🚇"
                    elif '火车' in line_type or '高铁' in line_type or '动车' in line_type:
                        icon = "🚄"
                    elif '轻轨' in line_type:
                        icon = "🚈"
                    else:
                        icon = "🚌"
                        
                    details += f"      {step_counter}. {icon} {line_name}\n"
                    details += f"         📍 {departure_stop} → {arrival_stop}\n"
                    details += f"         📏 距离: {bus_distance}米 | ⏱️ 耗时: {bus_duration_min}分钟 | 🚏 经过: {via_num}站\n"
                    
                    # 显示主要途经站点
                    via_stops = busline.get('via_stops', [])
                    if via_stops and len(via_stops) > 0:
                        # 智能选择显示的站点数量
                        if len(via_stops) <= 3:
                            via_names = [stop.get('name', '') for stop in via_stops]
                        else:
                            # 显示前2个和后1个站点
                            via_names = [via_stops[0].get('name', ''), via_stops[1].get('name', '')]
                            if len(via_stops) > 3:
                                via_names.append('...')
                            via_names.append(via_stops[-1].get('name', ''))
                        
                        details += f"         🚏 途经站: {' → '.join(filter(None, via_names))}\n"
                    
                    step_counter += 1
                    details += "\n"
            
            # 火车段（如果单独存在）
            railway = segment.get('railway', {})
            if railway:
                railway_steps = railway.get('steps', [])
                for rail_step in railway_steps:
                    details += f"      {step_counter}. 🚄 火车路段\n"
                    # 可以根据需要添加更多火车信息
                    step_counter += 1
        
        return details

    def get_transit_summary(self, result: Dict[str, Any]) -> List[Dict]:
        """
        获取公交路线的交通工具摘要
        
        Args:
            result (dict): API响应结果
            
        Returns:
            list: 每个方案的交通工具摘要列表
        """
        summaries = []
        
        if result.get('status') != '1':
            return summaries
        
        route = result.get('route', {})
        transits = route.get('transits', [])
        
        for i, transit in enumerate(transits):
            summary = {
                'route_number': i + 1,
                'total_distance': transit.get('distance', 'N/A'),
                'total_duration': transit.get('cost', {}).get('duration', 'N/A'),
                'total_cost': transit.get('cost', {}).get('transit_fee', 'N/A'),
                'transport_modes': []
            }
            
            # 转换时间
            if str(summary['total_duration']).isdigit():
                summary['total_duration_min'] = round(int(summary['total_duration']) / 60, 1)
            
            segments = transit.get('segments', [])
            for segment in segments:
                bus = segment.get('bus', {})
                if bus:
                    buslines = bus.get('buslines', [])
                    for busline in buslines:
                        transport_info = {
                            'type': busline.get('type', 'N/A'),
                            'name': busline.get('name', 'N/A'),
                            'from': busline.get('departure_stop', {}).get('name', 'N/A'),
                            'to': busline.get('arrival_stop', {}).get('name', 'N/A'),
                            'stations': busline.get('via_num', 0),
                            'distance': busline.get('distance', 'N/A'),
                            'duration': busline.get('cost', {}).get('duration', 'N/A')
                        }
                        
                        if str(transport_info['duration']).isdigit():
                            transport_info['duration_min'] = round(int(transport_info['duration']) / 60, 1)
                        
                        summary['transport_modes'].append(transport_info)
            
            summaries.append(summary)
        
        return summaries
    




# 创建全局的 AmapRouteAPI 实例
amap_route_api = AmapRouteAPI(AMAP_API_KEY)

# ==================== 高德地图路线规划工具 ====================

@tool("driving_route_tool", parse_docstring=True)
def driving_route_planning(
    origin: str,
    destination: str,
    strategy: int = 32,
    waypoints: Optional[str] = None,
    show_details: bool = True
) -> str:
    """
    驾车路线规划工具
    
    Args:
        origin (str): 起点经纬度 "经度,纬度"
        destination (str): 终点经纬度 "经度,纬度"
        strategy (int): 驾车策略，默认32（高德推荐）
        waypoints (str): 途经点，多个用";"分隔，可选
        show_details (bool): 是否显示详细信息，默认True
    
    Returns:
        str: 格式化的驾车路线信息
    """
    try:
        result = amap_route_api.driving_route(
            origin=origin,
            destination=destination,
            strategy=strategy,
            waypoints=waypoints
        )
        return amap_route_api.format_route_info(result, 'driving', show_details)
    except Exception as e:
        logger.error(f"驾车路线规划失败: {str(e)}")
        return f"❌ 驾车路线规划失败: {str(e)}"

@tool("walking_route_tool", parse_docstring=True)
def walking_route_planning(
    origin: str,
    destination: str,
    alternative_route: Optional[int] = None,
    show_details: bool = True
) -> str:
    """
    步行路线规划工具
    
    Args:
        origin (str): 起点经纬度 "经度,纬度"
        destination (str): 终点经纬度 "经度,纬度"
        alternative_route (int): 返回路线条数 1-3，可选
        show_details (bool): 是否显示详细信息，默认True
    
    Returns:
        str: 格式化的步行路线信息
    """
    try:
        result = amap_route_api.walking_route(
            origin=origin,
            destination=destination,
            alternative_route=alternative_route
        )
        return amap_route_api.format_route_info(result, 'walking', show_details)
    except Exception as e:
        logger.error(f"步行路线规划失败: {str(e)}")
        return f"❌ 步行路线规划失败: {str(e)}"

@tool("bicycling_route_tool", parse_docstring=True)
def bicycling_route_planning(
    origin: str,
    destination: str,
    alternative_route: Optional[int] = None,
    show_details: bool = True
) -> str:
    """
    骑行路线规划工具
    
    Args:
        origin (str): 起点经纬度 "经度,纬度"
        destination (str): 终点经纬度 "经度,纬度"
        alternative_route (int): 返回路线条数 1-3，可选
        show_details (bool): 是否显示详细信息，默认True
    
    Returns:
        str: 格式化的骑行路线信息
    """
    try:
        result = amap_route_api.bicycling_route(
            origin=origin,
            destination=destination,
            alternative_route=alternative_route
        )
        return amap_route_api.format_route_info(result, 'bicycling', show_details)
    except Exception as e:
        logger.error(f"骑行路线规划失败: {str(e)}")
        return f"❌ 骑行路线规划失败: {str(e)}"

@tool("electrobike_route_tool", parse_docstring=True)
def electrobike_route_planning(
    origin: str,
    destination: str,
    alternative_route: Optional[int] = None,
    show_details: bool = True
) -> str:
    """
    电动车路线规划工具
    
    Args:
        origin (str): 起点经纬度 "经度,纬度"
        destination (str): 终点经纬度 "经度,纬度"
        alternative_route (int): 返回路线条数 1-3，可选
        show_details (bool): 是否显示详细信息，默认True
    
    Returns:
        str: 格式化的电动车路线信息
    """
    try:
        result = amap_route_api.electrobike_route(
            origin=origin,
            destination=destination,
            alternative_route=alternative_route
        )
        return amap_route_api.format_route_info(result, 'electrobike', show_details)
    except Exception as e:
        logger.error(f"电动车路线规划失败: {str(e)}")
        return f"❌ 电动车路线规划失败: {str(e)}"

@tool("transit_route_tool", parse_docstring=True)
def transit_route_planning(
    origin: str,
    destination: str,
    strategy: int = 0,
    city1: str = "010",
    city2: str = "010",
    show_details: bool = True
) -> str:
    """
    公交路线规划工具
    
    Args:
        origin (str): 起点经纬度 "经度,纬度"
        destination (str): 终点经纬度 "经度,纬度"
        strategy (int): 换乘策略 0推荐/1经济/2少换乘/3少步行/4舒适/5不乘地铁/6地铁图/7地铁优先/8时间短
        city1 (str): 起点城市代码，默认"010"（北京）
        city2 (str): 终点城市代码，默认"010"（北京）
        show_details (bool): 是否显示详细路线信息，默认True
    
    Returns:
        str: 格式化的公交路线信息，包含详细换乘信息
    """
    try:
        result = amap_route_api.transit_route(
            origin=origin,
            destination=destination,
            strategy=strategy,
            city1=city1,
            city2=city2
        )
        return amap_route_api.format_route_info(result, 'transit', show_details)
    except Exception as e:
        logger.error(f"公交路线规划失败: {str(e)}")
        return f"❌ 公交路线规划失败: {str(e)}"

# 高德地图周边搜索API类
class AmapSearchAPI:
    """高德地图周边搜索API"""
    
    BASE_URL = "https://restapi.amap.com/v3/place/around"
    
    # 常用POI类型代码映射
    COMMON_POI_TYPES = {
        # 住宿
        "住宿": "100000",
        "酒店": "100000",
        "宾馆": "100100",
        "星级酒店": "100101",
        "经济型酒店": "100102",
        "青年旅社": "100104",
        
        # 餐饮
        "餐饮": "050000",
        "美食": "050000",
        "中餐": "050100",
        "西餐": "050200",
        "快餐": "050300",
        "咖啡厅": "050500",
        "茶馆": "050600",
        "甜品": "050900",
        
        # 景点
        "景点": "110000",
        "风景名胜": "110000",
        "公园": "110100",
        "寺庙": "110201",
        "教堂": "110202",
        
        # 其他常用
        "购物": "060000",
        "超市": "060400",
        "医院": "090100",
        "药店": "090500",
        "银行": "160100",
        "ATM": "160300",
        "地铁站": "150500",
        "公交站": "150700",
        "停车场": "150900",
        "加油站": "010100"
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
    
    def search(
        self,
        location: Union[str, tuple],
        types: str,
        radius: int = 1000,
        keywords: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        city: Optional[str] = None,
        max_retries: int = 3
    ) -> Optional[Dict]:
        """搜索周边POI"""
        # 处理坐标格式
        if isinstance(location, tuple):
            location = f"{location[0]},{location[1]}"
        
        # 处理POI类型（支持中文转换）
        type_code = self.COMMON_POI_TYPES.get(types, types)
        
        # 构建请求参数
        params = {
            'key': self.api_key,
            'location': location,
            'types': type_code,
            'radius': min(radius, 50000),
            'offset': min(page_size, 25),
            'page': page,
            'extensions': 'all',
            'output': 'JSON'
        }
        
        if keywords:
            params['keywords'] = keywords
        if city:
            params['city'] = city
        
        # 执行请求（含重试）
        for attempt in range(max_retries):
            try:
                response = self.session.get(
                    self.BASE_URL,
                    params=params,
                    timeout=10
                )
                
                response.raise_for_status()
                data = response.json()
                
                if data.get('status') == '1':
                    return self._parse_response(data)
                else:
                    logger.error(f"API错误：{data.get('info')}")
                    
            except Exception as e:
                logger.warning(f"第{attempt + 1}次请求失败：{e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
        
        return None
    
    def _parse_response(self, data: Dict) -> Dict:
        """解析响应数据"""
        result = {
            'total': int(data.get('count', 0)),
            'items': []
        }
        
        for poi in data.get('pois', []):
            item = {
                'id': poi.get('id'),
                'name': poi.get('name'),
                'type': poi.get('type'),
                'typecode': poi.get('typecode'),
                'address': poi.get('address'),
                'location': poi.get('location'),
                'distance': int(poi.get('distance', 0)),
                'tel': poi.get('tel', ''),
                'rating': poi.get('biz_ext', {}).get('rating', ''),
                'cost': poi.get('biz_ext', {}).get('cost', ''),
                'opentime': poi.get('biz_ext', {}).get('open_time', ''),
                'province': poi.get('pname', ''),
                'city': poi.get('cityname', ''),
                'district': poi.get('adname', '')
            }
            result['items'].append(item)
        
        return result



@tool("search_nearby", parse_docstring=True)
def search_nearby(
    location: str,
    search_type: str,
    radius: int = 1000,
    keywords: Optional[str] = None,
    limit: int = 10
) -> List[Dict]:
    """
    搜索指定位置周边的各类场所（POI）。支持搜索住宿、餐饮、景点等多种类型。
    
    Args:
        location (str): 中心点坐标，格式为"经度,纬度"，如"116.397428,39.90923"
        search_type (str): 搜索类型，支持住宿、餐饮、景点等
        radius (int): 搜索半径，单位为米，默认1000米
        keywords (Optional[str]): 搜索关键词，可选
        limit (int): 返回结果数量限制，默认10个
    
    Returns:
        List[Dict]: POI列表，每个POI包含名称、地址、距离等信息
    """
    try:
        api = AMAP_API_KEY
        result = AmapSearchAPI(api).search(
            location=location,
            types=search_type,
            radius=radius,
            keywords=keywords,
            page_size=min(limit, 25)
        )
        
        if result and result['items']:
            return result['items'][:limit]
        else:
            return []
            
    except Exception as e:
        logger.error(f"搜索失败: {str(e)}")
        return [{"error": f"搜索失败: {str(e)}"}]


from workflow_client import WorkflowClient
from langchain_core.tools import tool

@tool("tour_search_tool", parse_docstring=True)
def tour_search(tour_need:str,had_tour:str =None):
    """
    智能旅游规划工具
    
    Args:
        tour_need: 旅游需求描述，必填
        had_tour: 已经去过的地方，可选
    
    Returns:
        site_detail_result: 检索到的景点详情
        
    Raises:
        ValueError: 当输入参数无效时
        ConnectionError: 当API调用失败时
    """
    tour_search_client = WorkflowClient(api_key="app-qFq7SmUqmn1vv54bD2qKDAY8")
    if had_tour:
        question = f"我之前去过{had_tour}，请帮我规划一下{tour_need}"
    else:
        question = f"请帮我规划一下{tour_need}"
    result = tour_search_client.run_workflow_blocking({
        "user_question": question,}, "test_user")
    site_detail_result = result["data"]["outputs"]["text"]
    
    return site_detail_result

@tool("search_tool", parse_docstring=True)
def search(search_need:str):
    """
    智能旅游行攻略检索工具
    
    Args:
        search_need: 旅游攻略需求描述，必填
    
    Returns:
        travel_itineraries: 网络上检索到的旅游行程攻略
        
    Raises:
        ValueError: 当输入参数无效时
        ConnectionError: 当API调用失败时
    """
    tour_search_client = WorkflowClient(api_key="app-qFq7SmUqmn1vv54bD2qKDAY8")
    question = f"请帮我检索一下{search_need}"
    result = tour_search_client.run_workflow_blocking({
        "user_question": question,}, "test_user")
    travel_itineraries = result["data"]["outputs"]["text"]
    return travel_itineraries


from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os



# ==================== 行程规划系统提示词 ====================

day_plan_sys_prompt = """
**角色：智能行程规划专家**

**核心任务：**
基于用户的旅游意图、景点信息和景点间驾车时间，为用户规划一个合理、高效、个性化的多日游览行程。

**规划原则：**
1. **用户意图优先**：根据用户的兴趣偏好、出行人群特点、特殊需求来选择和排序景点
2. **交通效率**：利用景点间驾车时间数据，将距离近的景点安排在同一天
3. **行程节奏**：根据用户偏好和出行人群调整每日游览强度（轻松/适中/紧凑）
4. **逻辑顺序**：每日行程形成顺畅路线，如有指定起点，第一天必须从该点出发
5. **完整覆盖**：尽量安排所有提供的核心景点，无法安排的需说明原因

**输入信息：**
- 用户意图分析（包含：目标城市、游玩天数、出行人群、兴趣标签、特殊需求、起始点等）
- 景点信息列表（包含：景点名称、描述、标签等）
- 景点间驾车时间数据

**输出格式：**
请用自然语言输出行程规划，包含以下内容：

1. **行程概览**
   - 总天数、整体节奏、起始点说明

2. **每日行程安排**
   - 第X天：[主题/区域]
   - 游览顺序：景点1 → 景点2 → 景点3...
   - 时间安排：各景点建议游览时长、景点间交通时间
   - 安排理由：说明为何如此安排，如何符合用户需求

3. **特别说明**
   - 未能安排的景点及原因（如有）
   - 其他注意事项

**重要限制：**
- 只使用输入数据中提供的景点，不添加新景点
- 严格使用给定的驾车时间数据
- 行程安排要符合用户的具体需求和偏好

**示例输出风格：**
"根据您的需求，我为您规划了3天的南京之旅，整体节奏轻松舒适，从您入住的南京市中心酒店X出发。

第1天：历史文化深度游
路线：南京市中心酒店X → 总统府（2.5小时）→ 玄武湖（2小时）
- 早上从酒店出发，驾车10分钟到达总统府，深入了解中国近代历史
- 中午在附近用餐后，驾车15分钟前往玄武湖休闲漫步
- 安排理由：首日选择历史文化景点，符合您的兴趣偏好，景点间距离近，不会太疲劳

第2天：秦淮风情美食之旅..."
"""

# ==================== 智能体定义 ====================

# 工具列表

# 需求收集智能体
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


# 景点搜索智能体
tour_search_agent = create_react_agent(
    model=llm,
    prompt=f"""
        角色定位：
        你是一个搜索景点信息和景点攻略的智能体。

        核心能力：
        - 精准理解用户的旅游需求和偏好
        - 熟练调用`tour_search`、`tour_strategy`工具进行信息检索
        - 整合并优化景点介绍和旅游攻略内容，保证景点列表和攻略列表能够满足用户的需要

        工作流程：
        1. 分析用户需求（目的地、旅游偏好、时间安排等）
        2. 调用`tour_search`工具检索相关信息，你可以调用多次工具，以便于景点列表和攻略列表能够满足用户的需要
        3. 筛选并整理最相关、最有价值的内容
        4. 按规定格式输出结果

        你最后的输出需要满足以下要求：
        【景点介绍】
        - 景点名称：[具体名称]
        - 基础信息：[地理位置、开放时间、门票价格等]
        - 景点特色：[核心亮点、历史文化背景、独特体验等]
        - 景点攻略：[景点攻略]
        

        质量要求：
        1. 信息准确性：确保所有信息真实可靠、是从检索到的网页中总结出来的，而不是根据自身的知识
        2. 内容实用性：提供切实可行的建议和攻略
        3. 表述清晰性：语言简洁明了，重点突出，便于用户快速获取关键信息
        4. 你的任务是：根据用户的需求，进行景点探索、景点补充、景点更新；攻略的探索、更新，最终形成景点列表和攻略列表，以便于形成规划智能体进行景点规划，不需要你对景点进行规划
        5. 最后返回的内容，要是规定格式。
    """,
    tools=[tour_search,search],
    name="tour_search_agent"
)

# 行程规划智能体
day_plan_agent = create_react_agent(
    model=llm,
    prompt=f"""你是一个专业的旅行行程规划助手，擅长利用高德地图API为用户提供全面的旅行规划服务。

{day_plan_sys_prompt}

你可以：
1. 通过get_geocodes_tool查询任何地址的精确经纬度坐标，支持批量查询多个地点
2. 通过get_distance_tool计算多个景点之间的驾车距离和所需时间，帮助用户合理安排游览顺序


当用户提供地点信息时，你会主动分析并推荐最合理的出行方案。对于多个景点，你会考虑距离、交通便利性和游览时间，提供最优的游览顺序和交通方式。
此外，为了方便其他智能体接受数据，你会在景点旁边添加该景点的经纬，度格式为：景点名称（经纬度：经度，纬度），例如：故宫（经纬度：116.397128,39.916527）
请根据用户的需求，灵活运用这些工具，提供专业、贴心的旅行规划建议。
    """,
    tools=[get_geocodes, get_distance],
    name="day_plan_agent"
)

# 旅行管家智能体
travel_butler_agent = create_react_agent(
    model=llm,
    prompt=f"""
你是私人旅行管家，负责提升旅行品质。

服务范围：
1. 天气穿衣：查询天气，给出具体穿衣建议
2. 美食推荐：使用search_nearby找景点周边500-1000米内的"餐饮|特色美食"
3. 特色体验：推荐当地特色活动、演出、手工艺
4. 购物向导：特产推荐及购买地点

输出格式：
- 天气建议：温度、降水、穿衣指南
- 每日美食：早中晚餐推荐（名称|特色|人均|距离）
- 必尝小吃：当地特色小吃清单
- 体验活动：文化体验、季节限定项目
- 贴心提醒：用餐时间、支付方式、注意事项

语气温暖亲切，让用户感受专属服务。

你可以：
1. 通过get_geocodes_tool查询任何地址的精确经纬度坐标，支持批量查询多个地点
2. 通过search_nearby_tool搜索指定位置周边的酒店、景点、美食、购物等

当用户提供地点信息时，你会主动分析并推荐最合理的出行方案。对于多个景点，你会考虑距离、交通便利性和游览时间，提供最优的游览顺序和交通方式。

请根据用户的需求，灵活运用这些工具，提供专业、贴心的旅行规划建议。

    """,
    tools=[get_geocodes, search_nearby,search],
    name="travel_butler_agent"
)

# 导入批量路线规划工具
from batch_route_tools import (
    batch_driving_route_planning,
    batch_walking_route_planning,
    batch_bicycling_route_planning,
    batch_electrobike_route_planning,
    batch_transit_route_planning
)

# 出行规划智能体
live_transport_agent = create_react_agent(
    model=llm,
    prompt=f"""
# 交通住宿规划专家 Prompt

你是专业的出行规划专家，负责为用户制定详细的交通和住宿方案。

## 核心任务

### 1. 住宿安排
- 使用 `search_nearby` 搜索"酒店|住宿"
- 优先选择地铁站500米范围内的酒店
- 综合考虑位置、价格、评分等因素

### 2. 交通规划
- 为每段行程提供1-2种最优交通方案
- 根据距离和需求选择合适的出行方式
- 提供详细的路线、时间和费用信息

### 3. 成本预算
- 准确计算住宿总费用
- 统计各类交通费用
- 提供总预算参考

## 工作流程

### 第一步：信息识别与处理
从提供的文本中识别已有信息：
- ✅ 已提供的信息：直接使用进行规划
- ❌ 缺失的信息：跳过相关部分，不要询问

**处理原则：**
- 有出发地 → 规划城际交通
- 无出发地 → 跳过城际交通部分
- 有景点信息 → 规划景点间交通
- 有住宿需求 → 搜索推荐酒店
- 无具体日期 → 提供通用方案（不涉及具体班次）

### 第二步：灵活构建行程
根据已有信息构建行程链：
- 完整版：出发地 → 目的地 → 酒店 → 景点 → 酒店 → 返程
- 简化版：酒店 ⇄ 景点（当无出发地信息时）


### 第三步：路线规划
将以上串联的行程按照要求，调用批量路线规划工具。
使用批量路线规划工具（只计算相邻地点之间的出行方式），确保覆盖：
- 城际交通（往返）
- 酒店到每天的第一个景点
- 相邻景点之间的交通
- 每天的最后一个景点返回酒店



## 可用工具

### 批量路线规划工具（优先使用）
1. `batch_transit_route_planning` - 公交地铁方案
2. `batch_driving_route_planning` - 驾车/打车方案
3. `batch_walking_route_planning` - 步行方案（近距离）
4. `batch_bicycling_route_planning` - 骑行方案
5. `batch_electrobike_route_planning` - 电动车方案

### 辅助工具
- `get_geocodes_tool` - 查询地址经纬度（如需补充）
- `search_nearby` - 搜索周边设施

## 输出格式要求

```
【住宿推荐】
酒店名称：XXX酒店
地址：具体地址
特色：近地铁站，性价比高，评分X.X
价格：XXX元/晚，共X晚，总计XXX元

【第一天】出发地（如果用户没有提供，则不进行这部分的规划）→目的地→酒店→景点
1. 城际交通：
   - 方案：[具体交通工具]
   - 路线：[详细路线]
   - 时长：X小时X分钟
   - 费用：XXX元

2. 酒店→景点A：
   - 推荐方案：[交通方式]
   - 路线：[详细路线]
   - 时长：X分钟
   - 费用：X元

3. 景点A→景点B：
   [同上格式]

4. 景点B→酒店：
   [同上格式]

【第二天】酒店→景点→酒店
[重复以上格式]

【第三天】酒店→景点→酒店→返程（如果用户没有提供，则不进行这部分的规划）
[重复以上格式]

【费用汇总】
- 住宿费用：XXX元
- 交通费用：XXX元
  - 城际交通：XXX元
  - 市内交通：XXX元
- 总计：XXX元

【温馨提示】

以上方案基于您提供的景点信息制定
如需城际交通规划，请提供出发城市
费用为参考价格，实际以购买时为准
```

## 重要提醒

## 执行准则

### 必须遵守：
1. **不询问原则**：绝不主动询问缺失信息
2. **灵活应对**：有什么信息就规划什么
3. **标注说明**：在最后简要说明哪些部分因信息不足未能规划
4. **专注可行**：专注于可以规划的部分，做到最好
5. 所有交通信息必须基于工具返回的精确数据，不得臆造
6. 优先推荐性价比高的方案
7. 考虑用户的体力和时间限制
  
### 输出要求：
1. 直接展示可规划的内容
2. 跳过无法规划的部分（不留空白章节）
3. 在末尾用一个简短的"温馨提示"说明情况
4. 保持专业、实用、积极的语气

## 示例对比

❌ 错误做法：
"为了给您制定精确方案，我需要了解您的出发地..."

✅ 正确做法：
"根据您提供的景点信息，我为您规划了以下交通方案：
[直接输出可规划内容]"

请记住：用户找您是为了获得帮助，而不是被询问更多问题。基于现有信息，尽力提供最有价值的规划方案。
    """,
    tools=[get_geocodes, search_nearby, 
           batch_driving_route_planning, batch_walking_route_planning, 
           batch_bicycling_route_planning, batch_electrobike_route_planning, 
           batch_transit_route_planning],
    name="live_transport_agent",
    )

# ==================== 多智能体系统代理 (MAS) ====================

# 导入supervisor创建函数

try:
    from langgraph_supervisor import create_supervisor
except ImportError:
    print("警告：无法导入 langgraph_supervisor，请确保已安装相关依赖")
    create_supervisor = None

def create_travel_supervisor():
    """
    创建旅游多智能体系统的supervisor
    
    Returns:
        supervisor: 编译后的supervisor图
    """
    if create_supervisor is None:
        raise ImportError("无法创建supervisor，请安装 langgraph_supervisor")
    
    supervisor = create_supervisor(
        agents=[tour_search_agent,day_plan_agent, live_transport_agent, travel_butler_agent],
        model=llm,
        prompt=(
            """
# 角色定位
你是一位专业的旅游规划总监，负责协调和管理多个专业智能体团队，为用户提供完整、个性化的旅游解决方案。

# 智能体团队介绍
你管理以下4个专业智能体：
1. **tour_search_agent**（景点搜索）：负责搜索目的地景点、美食、文化等信息
2. **day_plan_agent**（行程规划）：负责制定每日详细行程安排
3. **live_transport_agent**（交通住宿）：负责规划交通路线和住宿安排
4. **travel_butler_agent**（旅行管家）：负责提供贴心建议、注意事项和应急方案

# 工作流程

## 第一阶段：信息收集
按顺序调用各智能体，收集所有相关信息

## 第二阶段：深度融合（核心）
将各智能体的信息按时间线深度融合，形成连贯的旅行故事

# 最终输出示例（时间线融合式）

## 🌟 旅游方案概览
[基本信息汇总]

## 📅 完整行程安排（融合版）

### 第1天：[主题]
**出发**
- 🚄 07:30 从[出发地]乘坐[交通工具]前往[目的地]
- 💡 提醒：提前准备[travel_butler建议的物品]
- 🕐 预计10:30抵达

**入住**
- 🏨 11:00 抵达[酒店名称]办理入住
- 📍 地址：[具体地址]
- 💰 费用：[价格]/晚

**午餐**
- 🍜 12:00 推荐品尝[当地特色美食]
- 📍 推荐餐厅：[名称及位置]
- 💰 人均：[价格]

**下午行程**
- 🎯 14:00 前往[景点A]
  - 🚇 交通：从酒店乘地铁[线路]，约[时长]
  - 🎫 门票：[价格]
  - ⏱️ 建议游览：2小时
  - 📸 推荐：[拍照点/特色体验]
  - ⚠️ 注意：[travel_butler的提醒]

- 🎯 16:30 步行前往[景点B]（距离500米）
  - 🎫 门票：[价格]
  - 🌟 特色：[景点特色介绍]
  - 💡 贴士：[travel_butler的建议]

**晚餐**
- 🍽️ 18:30 推荐[餐厅名称]
- 🚶 从景点B步行10分钟可达
- 🥘 必点：[推荐菜品]

**返回酒店**
- 🚕 20:00 打车返回酒店，约15分钟
- 💰 预计费用：30元

**当日小结**
- 总步数：约15000步
- 总费用：[交通]+[门票]+[餐饮]=[总计]
- 天气：[weather_info]，建议[穿着建议]

### 第2天：[主题]
[按照相同的时间线方式融合各智能体信息]

## 💰 费用汇总
**详细预算表**
| 项目 | 金额 | 备注 |
|------|------|------|
| 交通 | [总额] | 包含城际+市内 |
| 住宿 | [总额] | [X]晚 |
| 门票 | [总额] | 所有景点 |
| 餐饮 | [总额] | 预估 |
| **总计** | **[总额]** | 人均[金额] |

## 🎒 行前准备（融合版）
根据行程特点，建议准备：
- 证件：[清单]
- 衣物：根据[天气情况]准备[具体建议]
- 其他：[根据景点特点的准备物品]

## 📞 实用信息
- 紧急联系：[当地重要电话]
- 注意事项：[文化禁忌、安全提醒等]
- 特别提醒：[基于具体行程的个性化提醒]

## 📝 用户反馈
[待确认信息和修改建议]

# 信息融合原则

## 时间线融合法
1. 以时间为主线，将各智能体信息自然穿插
2. 交通信息紧跟行程节点
3. 贴士建议融入具体场景
4. 费用信息实时标注

## 场景化呈现
- 不是简单罗列，而是讲述一天的旅行故事
- 让用户能够"预见"整个旅程

## 融合示例
❌ 错误（割裂式）：
- 景点：A、B、C
- 交通：地铁、步行
- 建议：注意防晒

✅ 正确（融合式）：
"14:00 从酒店乘地铁2号线前往景点A（约20分钟，3元），今日阳光强烈请注意防晒..."

# 执行检查
整合时确保：
- [ ] 每个时间节点都有完整信息（地点+交通+费用+贴士）
- [ ] 信息按照实际游览顺序自然流动
- [ ] 各智能体的信息都巧妙融入时间线中
- [ ] 形成连贯、可执行的行程指南

记住：你要创造的不是信息列表，而是一份生动的旅行指南，让用户仿佛已经在旅途中。
            """
        )
    ).compile()
    
    return supervisor




def create_travel_supervisor_flexible():
    """
    创建旅游多智能体系统的supervisor
    
    Returns:
        supervisor: 编译后的supervisor图
    """
    if create_supervisor is None:
        raise ImportError("无法创建supervisor，请安装 langgraph_supervisor")
    
    supervisor = create_supervisor(
        agents=[tour_search_agent,day_plan_agent, live_transport_agent, travel_butler_agent],
        model=llm,
        prompt=(
            """
# 角色定位
你是旅游规划总监，负责协调4个专业智能体团队，提供灵活的旅游规划服务。

# 智能体执行链
标准执行顺序：
1. tour_search_agent → 2. day_plan_agent → 3. live_transport_agent → 4. travel_butler_agent

# 灵活起点策略
根据用户需求和已有信息，选择合适的起点：

## 起点判断规则：
1. **从 tour_search_agent 开始**（完整流程）：
   - 用户刚开始规划，需要了解目的地
   - 用户想要探索新的景点或体验
   - 示例："我想去杭州玩"、"杭州有什么好玩的"

2. **从 day_plan_agent 开始**（已有景点信息）：
   - 用户的反馈需要调整行程顺序，或者需要调整景点顺序
   - 示例："我想去西湖、灵隐寺、宋城，怎么安排"

3. **从 live_transport_agent 开始**（已有行程安排）：
   - 用户的反馈需要解决更新或者替换交通和住宿问题
   - 示例："帮我重新规划交通和住宿"

4. **仅调用 travel_butler_agent**（方案优化）：
   - 需要补充建议或注意事项，用户的直接反馈和travel_butler_agent有关
   - 示例："我的行程都安排好了，有什么需要注意的吗"

# 执行原则
1. **识别起点**：分析用户输入，确定从哪个智能体开始
2. **顺序执行**：从起点开始，按顺序调用后续智能体
3. **信息传递**：确保前一个智能体的输出传递给下一个
4. **跳过已完成**：不重复执行用户已经完成的步骤

## 更新原则
- 只改用户要求的部分
- 改动时自动更新关联内容（如换景点→更新交通）
- 用 🔄 标记所有变更

## 输出格式

### 更新概览
- 主要变更：[列出改动]
- 费用变化：[如有]

### 详细行程
**Day X 更新：**
- 🔄 原：[旧内容] → 新：[新内容]
- 原因：[用户反馈]

### 优化说明
根据您的反馈，已完成以下优化：
1. [具体改进1]
2. [具体改进2]

# 执行示例
用户："第二天太累了，故宫不想去"
→ 识别：时间+景点问题
→ 执行：搜索故宫替代 → 减少景点数量 → 优化路线
→ 输出：更新后的第二天行程

记住：保留原方案优点，精准解决用户提出的问题。
     灵活识别起点，但始终保持后续流程的顺序性。
            """
        )
    ).compile()
    
    return supervisor


def run_travel_planning(user_request: str):
    """
    第一轮：直接运行旅游规划多智能体系统，跳过需求收集
    
    Args:
        user_request (str): 用户的旅游需求
        
    Returns:
        generator: 流式输出结果
    """
    supervisor = create_travel_supervisor()
    
    for chunk in supervisor.stream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_request
                }
            ]
        }
    ):
        yield chunk


def run_travel_planning_flexible(user_feedback: str, travel_plan_draft: str):
    """
    后续轮：基于用户反馈和当前方案进行优化
    
    Args:
        user_feedback (str): 用户反馈
        travel_plan_draft (str): 当前旅游方案草稿
        
    Returns:
        generator: 流式输出结果
    """
    supervisor = create_travel_supervisor_flexible()
    
    combined_input = f"""
用户反馈：{user_feedback}

当前方案：
{travel_plan_draft}

请根据用户反馈优化方案。
    """
    
    for chunk in supervisor.stream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": combined_input
                }
            ]
        }
    ):
        yield chunk



# ==================== 示例使用 ====================

# from supervisor_agent import run_travel_planning,run_travel_planning_flexible


import requests
from langchain_core.tools import tool
import time
import os
from requests.packages.urllib3.util.retry import Retry
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os


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
