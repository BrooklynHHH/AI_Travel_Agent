"""
批量路线规划工具
支持批量查询多个地点之间的路线，并包含重试机制
"""

import time
import logging
from typing import List, Tuple, Optional, Dict, Any
from langchain_core.tools import tool
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API密钥 - 需要从环境变量或配置文件中获取
AMAP_API_KEY = "cc4f161a65645cb8009739ee9fdda460"

class BatchAmapRouteAPI:
    """批量高德地图路线规划API调用类"""
    
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
        
        # 配置重试会话
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def batch_route_planning(self, 
                           locations: List[Tuple[str, str]], 
                           route_type: str = 'driving',
                           max_retries: int = 3,
                           delay_between_requests: float = 0.5,
                           **kwargs) -> List[Dict[str, Any]]:
        """
        批量路线规划 - 计算列表中每两个相邻地点之间的路线
        
        Args:
            locations: 地点列表，格式为 [(地点名称, "经度,纬度"), ...]
            route_type: 路线类型 ('driving', 'walking', 'bicycling', 'electrobike', 'transit')
            max_retries: 最大重试次数
            delay_between_requests: 请求间隔时间（秒）
            **kwargs: 其他路线规划参数
            
        Returns:
            List[Dict]: 路线规划结果列表
        """
        results = []
        
        for i in range(len(locations) - 1):
            origin_name, origin_coord = locations[i]
            dest_name, dest_coord = locations[i + 1]
            
            route_info = {
                'origin_name': origin_name,
                'destination_name': dest_name,
                'origin_coord': origin_coord,
                'destination_coord': dest_coord,
                'route_type': route_type,
                'success': False,
                'result': None,
                'error': None,
                'retry_count': 0
            }
            
            # 重试机制
            for retry in range(max_retries):
                try:
                    route_info['retry_count'] = retry + 1
                    
                    # 根据路线类型调用相应的API
                    if route_type == 'driving':
                        result = self._driving_route(origin_coord, dest_coord, **kwargs)
                    elif route_type == 'walking':
                        result = self._walking_route(origin_coord, dest_coord, **kwargs)
                    elif route_type == 'bicycling':
                        result = self._bicycling_route(origin_coord, dest_coord, **kwargs)
                    elif route_type == 'electrobike':
                        result = self._electrobike_route(origin_coord, dest_coord, **kwargs)
                    elif route_type == 'transit':
                        result = self._transit_route(origin_coord, dest_coord, **kwargs)
                    else:
                        raise ValueError(f"不支持的路线类型: {route_type}")
                    
                    if result and result.get('status') == '1':
                        route_info['success'] = True
                        route_info['result'] = result
                        logger.info(f"成功获取路线: {origin_name} → {dest_name}")
                        break
                    else:
                        error_msg = result.get('info', '未知错误') if result else 'API返回空结果'
                        logger.warning(f"路线规划失败 (尝试 {retry + 1}/{max_retries}): {origin_name} → {dest_name}, 错误: {error_msg}")
                        route_info['error'] = error_msg
                        
                except Exception as e:
                    error_msg = str(e)
                    logger.warning(f"请求异常 (尝试 {retry + 1}/{max_retries}): {origin_name} → {dest_name}, 错误: {error_msg}")
                    route_info['error'] = error_msg
                
                # 如果不是最后一次重试，等待一段时间
                if retry < max_retries - 1:
                    time.sleep(delay_between_requests * (retry + 1))  # 递增延迟
            
            results.append(route_info)
            
            # 请求间隔
            if i < len(locations) - 2:  # 不是最后一个请求
                time.sleep(delay_between_requests)
        
        return results
    
    def batch_matrix_route_planning(self, 
                                  locations: List[Tuple[str, str]], 
                                  route_type: str = 'driving',
                                  max_retries: int = 3,
                                  delay_between_requests: float = 0.5,
                                  **kwargs) -> List[Dict[str, Any]]:
        """
        批量矩阵路线规划 - 计算所有地点之间的路线（N×N矩阵）
        
        Args:
            locations: 地点列表，格式为 [(地点名称, "经度,纬度"), ...]
            route_type: 路线类型
            max_retries: 最大重试次数
            delay_between_requests: 请求间隔时间（秒）
            **kwargs: 其他路线规划参数
            
        Returns:
            List[Dict]: 路线规划结果列表
        """
        results = []
        total_requests = len(locations) * (len(locations) - 1)  # 不包括自己到自己
        current_request = 0
        
        for i, (origin_name, origin_coord) in enumerate(locations):
            for j, (dest_name, dest_coord) in enumerate(locations):
                if i == j:  # 跳过自己到自己
                    continue
                
                current_request += 1
                logger.info(f"处理路线 {current_request}/{total_requests}: {origin_name} → {dest_name}")
                
                route_info = {
                    'origin_name': origin_name,
                    'destination_name': dest_name,
                    'origin_coord': origin_coord,
                    'destination_coord': dest_coord,
                    'route_type': route_type,
                    'success': False,
                    'result': None,
                    'error': None,
                    'retry_count': 0
                }
                
                # 重试机制
                for retry in range(max_retries):
                    try:
                        route_info['retry_count'] = retry + 1
                        
                        # 根据路线类型调用相应的API
                        if route_type == 'driving':
                            result = self._driving_route(origin_coord, dest_coord, **kwargs)
                        elif route_type == 'walking':
                            result = self._walking_route(origin_coord, dest_coord, **kwargs)
                        elif route_type == 'bicycling':
                            result = self._bicycling_route(origin_coord, dest_coord, **kwargs)
                        elif route_type == 'electrobike':
                            result = self._electrobike_route(origin_coord, dest_coord, **kwargs)
                        elif route_type == 'transit':
                            result = self._transit_route(origin_coord, dest_coord, **kwargs)
                        else:
                            raise ValueError(f"不支持的路线类型: {route_type}")
                        
                        if result and result.get('status') == '1':
                            route_info['success'] = True
                            route_info['result'] = result
                            break
                        else:
                            error_msg = result.get('info', '未知错误') if result else 'API返回空结果'
                            route_info['error'] = error_msg
                            
                    except Exception as e:
                        error_msg = str(e)
                        route_info['error'] = error_msg
                    
                    # 如果不是最后一次重试，等待一段时间
                    if retry < max_retries - 1:
                        time.sleep(delay_between_requests * (retry + 1))
                
                results.append(route_info)
                
                # 请求间隔
                if current_request < total_requests:
                    time.sleep(delay_between_requests)
        
        return results
    
    def _driving_route(self, origin: str, destination: str, **kwargs) -> Dict[str, Any]:
        """驾车路线规划"""
        params = {
            'key': self.api_key,
            'origin': origin,
            'destination': destination,
            'strategy': kwargs.get('strategy', 32),
            'cartype': kwargs.get('cartype', 0),
            'ferry': kwargs.get('ferry', 0)
        }
        
        if kwargs.get('waypoints'):
            params['waypoints'] = kwargs['waypoints']
        if kwargs.get('avoidpolygons'):
            params['avoidpolygons'] = kwargs['avoidpolygons']
        if kwargs.get('plate'):
            params['plate'] = kwargs['plate']
            
        return self._make_request('driving', params)
    
    def _walking_route(self, origin: str, destination: str, **kwargs) -> Dict[str, Any]:
        """步行路线规划"""
        params = {
            'key': self.api_key,
            'origin': origin,
            'destination': destination,
            'isindoor': kwargs.get('isindoor', 0)
        }
        
        if kwargs.get('alternative_route'):
            params['alternative_route'] = kwargs['alternative_route']
            
        return self._make_request('walking', params)
    
    def _bicycling_route(self, origin: str, destination: str, **kwargs) -> Dict[str, Any]:
        """骑行路线规划"""
        params = {
            'key': self.api_key,
            'origin': origin,
            'destination': destination
        }
        
        if kwargs.get('alternative_route'):
            params['alternative_route'] = kwargs['alternative_route']
            
        return self._make_request('bicycling', params)
    
    def _electrobike_route(self, origin: str, destination: str, **kwargs) -> Dict[str, Any]:
        """电动车路线规划"""
        params = {
            'key': self.api_key,
            'origin': origin,
            'destination': destination
        }
        
        if kwargs.get('alternative_route'):
            params['alternative_route'] = kwargs['alternative_route']
            
        return self._make_request('electrobike', params)
    
    def _transit_route(self, origin: str, destination: str, **kwargs) -> Dict[str, Any]:
        """公交路线规划"""
        params = {
            'key': self.api_key,
            'origin': origin,
            'destination': destination,
            'strategy': kwargs.get('strategy', 0),
            'city1': kwargs.get('city1', '010'),
            'city2': kwargs.get('city2', '010'),
            'AlternativeRoute': kwargs.get('alternative_route', 5),
            'nightflag': kwargs.get('nightflag', 0)
        }
        
        return self._make_request('transit', params)
    
    def _make_request(self, route_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送HTTP请求"""
        try:
            response = self.session.get(
                self.base_urls[route_type],
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            return {'error': f'请求失败: {str(e)}', 'status': 'error'}
        except Exception as e:
            return {'error': f'解析失败: {str(e)}', 'status': 'error'}
    
    def format_batch_results(self, results: List[Dict[str, Any]], show_details: bool = True) -> str:
        """
        格式化批量路线规划结果
        
        Args:
            results: 批量路线规划结果
            show_details: 是否显示详细信息
            
        Returns:
            str: 格式化的结果字符串
        """
        if not results:
            return "❌ 没有路线规划结果"
        
        output = []
        success_count = sum(1 for r in results if r['success'])
        total_count = len(results)
        
        output.append(f"📊 批量路线规划结果概览")
        output.append(f"✅ 成功: {success_count}/{total_count} 条路线")
        output.append(f"❌ 失败: {total_count - success_count}/{total_count} 条路线")
        output.append("")
        
        # 显示每条路线的结果
        for i, result in enumerate(results, 1):
            route_type_icon = {
                'driving': '🚗',
                'walking': '🚶',
                'bicycling': '🚴',
                'electrobike': '⚡',
                'transit': '🚌'
            }.get(result['route_type'], '🚗')
            
            output.append(f"{i}. {route_type_icon} {result['origin_name']} → {result['destination_name']}")
            
            if result['success']:
                # 解析路线信息
                route_data = result['result'].get('route', {})
                
                if result['route_type'] == 'transit':
                    transits = route_data.get('transits', [])
                    if transits:
                        transit = transits[0]  # 取第一个方案
                        distance = transit.get('distance', 'N/A')
                        cost = transit.get('cost', {})
                        duration = cost.get('duration', 'N/A') if cost else 'N/A'
                        transit_fee = cost.get('transit_fee', 'N/A') if cost else 'N/A'
                        
                        # 转换时间（秒转分钟）
                        if str(duration).isdigit():
                            duration_min = round(int(duration) / 60, 1)
                        else:
                            duration_min = duration
                        
                        output.append(f"   ✅ 距离: {distance}米, 耗时: {duration_min}分钟, 费用: {transit_fee}元")
                        
                        # 如果显示详细信息，添加换乘信息
                        if show_details:
                            segments = transit.get('segments', [])
                            transfer_info = []
                            for segment in segments:
                                bus = segment.get('bus', {})
                                if bus:
                                    buslines = bus.get('buslines', [])
                                    for busline in buslines:
                                        line_name = busline.get('name', 'N/A')
                                        line_type = busline.get('type', 'N/A')
                                        departure_stop = busline.get('departure_stop', {}).get('name', 'N/A')
                                        arrival_stop = busline.get('arrival_stop', {}).get('name', 'N/A')
                                        
                                        # 根据线路类型显示不同图标
                                        if '地铁' in line_type:
                                            icon = "🚇"
                                        elif '火车' in line_type or '高铁' in line_type or '动车' in line_type:
                                            icon = "🚄"
                                        elif '轻轨' in line_type:
                                            icon = "🚈"
                                        else:
                                            icon = "🚌"
                                        
                                        transfer_info.append(f"{icon} {line_name}: {departure_stop} → {arrival_stop}")
                            
                            if transfer_info:
                                output.append(f"   🔄 换乘路线: {' | '.join(transfer_info[:3])}")  # 最多显示3个换乘
                else:
                    paths = route_data.get('paths', [])
                    if paths:
                        path = paths[0]  # 取第一个路线
                        distance = path.get('distance', 'N/A')
                        
                        # 根据路线类型获取时间和费用信息
                        if result['route_type'] in ['bicycling', 'electrobike']:
                            duration = path.get('duration', 'N/A')
                            tolls = 'N/A'  # 骑行和电动车没有过路费
                        else:
                            cost = path.get('cost', {})
                            duration = cost.get('duration', 'N/A') if cost else 'N/A'
                            tolls = cost.get('tolls', 'N/A') if cost else 'N/A'
                        
                        # 转换时间（秒转分钟）
                        if str(duration).isdigit():
                            duration_min = round(int(duration) / 60, 1)
                        else:
                            duration_min = duration
                        
                        if result['route_type'] == 'driving':
                            output.append(f"   ✅ 距离: {distance}米, 耗时: {duration_min}分钟, 过路费: {tolls}元")
                        else:
                            output.append(f"   ✅ 距离: {distance}米, 耗时: {duration_min}分钟")
                
                if show_details and result['retry_count'] > 1:
                    output.append(f"   🔄 重试次数: {result['retry_count']}")
            else:
                output.append(f"   ❌ 失败: {result['error']}")
                output.append(f"   🔄 重试次数: {result['retry_count']}")
            
            output.append("")
        
        return "\n".join(output)


# 创建全局的批量路线规划API实例
batch_amap_route_api = BatchAmapRouteAPI(AMAP_API_KEY)


# ==================== 批量路线规划工具 ====================

@tool("batch_driving_route_tool", parse_docstring=True)
def batch_driving_route_planning(
    locations: List[Tuple[str, str]],
    strategy: int = 32,
    max_retries: int = 3,
    delay_between_requests: float = 0.5,
    show_details: bool = True,
    matrix_mode: bool = False
) -> str:
    """
    批量驾车路线规划工具
    
    Args:
        locations (List[Tuple[str, str]]): 地点列表，格式为 [("地点名称", "经度,纬度"), ...]
        strategy (int): 驾车策略，默认32（高德推荐）
        max_retries (int): 最大重试次数，默认3次
        delay_between_requests (float): 请求间隔时间（秒），默认0.5秒
        show_details (bool): 是否显示详细信息，默认True
        matrix_mode (bool): 是否使用矩阵模式（计算所有地点之间的路线），默认False（只计算相邻地点）
    
    Returns:
        str: 格式化的批量驾车路线信息
    """
    try:
        if matrix_mode:
            results = batch_amap_route_api.batch_matrix_route_planning(
                locations=locations,
                route_type='driving',
                max_retries=max_retries,
                delay_between_requests=delay_between_requests,
                strategy=strategy
            )
            print("批量驾车路线工具调用成功")
        else:
            results = batch_amap_route_api.batch_route_planning(
                locations=locations,
                route_type='driving',
                max_retries=max_retries,
                delay_between_requests=delay_between_requests,
                strategy=strategy
            )
            print("批量驾车路线工具调用成功")
        return batch_amap_route_api.format_batch_results(results, show_details)
    except Exception as e:
        logger.error(f"批量驾车路线规划失败: {str(e)}")
        return f"❌ 批量驾车路线规划失败: {str(e)}"


@tool("batch_walking_route_tool", parse_docstring=True)
def batch_walking_route_planning(
    locations: List[Tuple[str, str]],
    alternative_route: Optional[int] = None,
    max_retries: int = 3,
    delay_between_requests: float = 0.5,
    show_details: bool = True,
    matrix_mode: bool = False
) -> str:
    """
    批量步行路线规划工具
    
    Args:
        locations (List[Tuple[str, str]]): 地点列表，格式为 [("地点名称", "经度,纬度"), ...]
        alternative_route (int): 返回路线条数 1-3，可选
        max_retries (int): 最大重试次数，默认3次
        delay_between_requests (float): 请求间隔时间（秒），默认0.5秒
        show_details (bool): 是否显示详细信息，默认True
        matrix_mode (bool): 是否使用矩阵模式，默认False
    
    Returns:
        str: 格式化的批量步行路线信息
    """
    try:
        if matrix_mode:
            results = batch_amap_route_api.batch_matrix_route_planning(
                locations=locations,
                route_type='walking',
                max_retries=max_retries,
                delay_between_requests=delay_between_requests,
                alternative_route=alternative_route
            )
            print("批量步行路线工具调用成功")
        else:
            results = batch_amap_route_api.batch_route_planning(
                locations=locations,
                route_type='walking',
                max_retries=max_retries,
                delay_between_requests=delay_between_requests,
                alternative_route=alternative_route
            )
            print("批量步行路线工具调用成功")
        return batch_amap_route_api.format_batch_results(results, show_details)
    except Exception as e:
        logger.error(f"批量步行路线规划失败: {str(e)}")
        return f"❌ 批量步行路线规划失败: {str(e)}"


@tool("batch_bicycling_route_tool", parse_docstring=True)
def batch_bicycling_route_planning(
    locations: List[Tuple[str, str]],
    alternative_route: Optional[int] = None,
    max_retries: int = 3,
    delay_between_requests: float = 0.5,
    show_details: bool = True,
    matrix_mode: bool = False
) -> str:
    """
    批量骑行路线规划工具
    
    Args:
        locations (List[Tuple[str, str]]): 地点列表，格式为 [("地点名称", "经度,纬度"), ...]
        alternative_route (int): 返回路线条数 1-3，可选
        max_retries (int): 最大重试次数，默认3次
        delay_between_requests (float): 请求间隔时间（秒），默认0.5秒
        show_details (bool): 是否显示详细信息，默认True
        matrix_mode (bool): 是否使用矩阵模式，默认False
    
    Returns:
        str: 格式化的批量骑行路线信息
    """
    try:
        if matrix_mode:
            results = batch_amap_route_api.batch_matrix_route_planning(
                locations=locations,
                route_type='bicycling',
                max_retries=max_retries,
                delay_between_requests=delay_between_requests,
                alternative_route=alternative_route
            )
            print("批量骑行路线工具调用成功")
        else:
            results = batch_amap_route_api.batch_route_planning(
                locations=locations,
                route_type='bicycling',
                max_retries=max_retries,
                delay_between_requests=delay_between_requests,
                alternative_route=alternative_route
            )
            print("批量骑行路线工具调用成功")
        return batch_amap_route_api.format_batch_results(results, show_details)
    except Exception as e:
        logger.error(f"批量骑行路线规划失败: {str(e)}")
        return f"❌ 批量骑行路线规划失败: {str(e)}"


@tool("batch_electrobike_route_tool", parse_docstring=True)
def batch_electrobike_route_planning(
    locations: List[Tuple[str, str]],
    alternative_route: Optional[int] = None,
    max_retries: int = 3,
    delay_between_requests: float = 0.5,
    show_details: bool = True,
    matrix_mode: bool = False
) -> str:
    """
    批量电动车路线规划工具
    
    Args:
        locations (List[Tuple[str, str]]): 地点列表，格式为 [("地点名称", "经度,纬度"), ...]
        alternative_route (int): 返回路线条数 1-3，可选
        max_retries (int): 最大重试次数，默认3次
        delay_between_requests (float): 请求间隔时间（秒），默认0.5秒
        show_details (bool): 是否显示详细信息，默认True
        matrix_mode (bool): 是否使用矩阵模式，默认False
    
    Returns:
        str: 格式化的批量电动车路线信息
    """
    try:
        if matrix_mode:
            results = batch_amap_route_api.batch_matrix_route_planning(
                locations=locations,
                route_type='electrobike',
                max_retries=max_retries,
                delay_between_requests=delay_between_requests,
                alternative_route=alternative_route
            )
            print("批量电动车路线工具调用成功")
        else:
            results = batch_amap_route_api.batch_route_planning(
                locations=locations,
                route_type='electrobike',
                max_retries=max_retries,
                delay_between_requests=delay_between_requests,
                alternative_route=alternative_route
            )
            print("批量电动车路线工具调用成功")
        return batch_amap_route_api.format_batch_results(results, show_details)
    except Exception as e:
        logger.error(f"批量电动车路线规划失败: {str(e)}")
        return f"❌ 批量电动车路线规划失败: {str(e)}"


@tool("batch_transit_route_tool", parse_docstring=True)
def batch_transit_route_planning(
    locations: List[Tuple[str, str]],
    strategy: int = 0,
    city1: str = "010",
    city2: str = "010",
    max_retries: int = 3,
    delay_between_requests: float = 0.5,
    show_details: bool = True,
    matrix_mode: bool = False
) -> str:
    """
    批量公交路线规划工具
    
    Args:
        locations (List[Tuple[str, str]]): 地点列表，格式为 [("地点名称", "经度,纬度"), ...]
        strategy (int): 换乘策略 0推荐/1经济/2少换乘/3少步行/4舒适/5不乘地铁/6地铁图/7地铁优先/8时间短
        city1 (str): 起点城市代码，默认"010"（北京）
        city2 (str): 终点城市代码，默认"010"（北京）
        max_retries (int): 最大重试次数，默认3次
        delay_between_requests (float): 请求间隔时间（秒），默认0.5秒
        show_details (bool): 是否显示详细路线信息，默认True
        matrix_mode (bool): 是否使用矩阵模式，默认False
    
    Returns:
        str: 格式化的批量公交路线信息，包含详细换乘信息
    """
    try:
        if matrix_mode:
            results = batch_amap_route_api.batch_matrix_route_planning(
                locations=locations,
                route_type='transit',
                max_retries=max_retries,
                delay_between_requests=delay_between_requests,
                strategy=strategy,
                city1=city1,
                city2=city2
            )
            print("批量公交路线工具调用成功")
        else:
            results = batch_amap_route_api.batch_route_planning(
                locations=locations,
                route_type='transit',
                max_retries=max_retries,
                delay_between_requests=delay_between_requests,
                strategy=strategy,
                city1=city1,
                city2=city2
            )
            print("批量公交路线工具调用成功")
        return batch_amap_route_api.format_batch_results(results, show_details)
    except Exception as e:
        logger.error(f"批量公交路线规划失败: {str(e)}")
        return f"❌ 批量公交路线规划失败: {str(e)}"


# ==================== 使用示例 ====================

def example_usage():
    """
    批量路线规划工具使用示例
    """
    # 示例地点列表
    locations = [
        ("北京天安门", "116.397128,39.916527"),
        ("北京故宫", "116.397128,39.916527"),
        ("北京颐和园", "116.275179,39.999617"),
        ("北京天坛", "116.407394,39.883171")
    ]
    
    print("=== 批量驾车路线规划示例 ===")
    result = batch_driving_route_planning(locations)
    print(result)
    
    print("\n=== 批量步行路线规划示例 ===")
    result = batch_walking_route_planning(locations)
    print(result)
    
    print("\n=== 批量公交路线规划示例 ===")
    result = batch_transit_route_planning(locations)
    print(result)
    
    print("\n=== 矩阵模式驾车路线规划示例 ===")
    result = batch_driving_route_planning(locations, matrix_mode=True)
    print(result)


if __name__ == "__main__":
    example_usage()
