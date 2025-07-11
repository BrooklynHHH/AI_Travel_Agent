#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强型流式输出API接口
将enhanced_stream_manager封装为API接口形式
"""
# 正确的版本

from typing import Dict, Any, List, Generator
# 导入增强型流式输出管理器
import sys
import os
sys.path.append(os.path.dirname(__file__))

# 由于文件名包含空格，使用importlib动态导入
from enhanced_stream_manager_copy import create_api_response_handler,create_enhanced_stream_manager,StreamAPIAdapter,OutputMessage
# 这里需要导入你的supervisor
# from your_module import supervisor
from supervisor_agent  import create_multi_turn_chat_supervisor
supervisor  = create_multi_turn_chat_supervisor()
import json

# 假设supervisor已经在其他地方定义，这里需要导入
# from your_supervisor_module import supervisor

class EnhancedStreamAPI:
    """增强型流式输出API类"""
    
    def __init__(self, supervisor=None):
        """
        初始化API
        
        Args:
            supervisor: LangGraph supervisor实例
        """
        self.supervisor = supervisor
        
    def run_enhanced_streaming_api(self, user_input: str, 
                                 verbose_level: int = 1,
                                 show_tokens: bool = True,
                                 show_progress: bool = True,
                                 show_timing: bool = True) -> Generator[Dict[str, Any], None, None]:
        """
        运行增强型流式输出API版本
        
        Args:
            user_input: 用户输入
            verbose_level: 详细程度 (0=简洁, 1=标准, 2=详细)
            show_tokens: 是否显示token流式输出
            show_progress: 是否显示进度信息
            show_timing: 是否显示时间统计
            
        Yields:
            Dict[str, Any]: 流式输出结果，与原print(result)中的result格式相同
        """
        # 创建增强型流式输出管理器
        stream_manager = create_enhanced_stream_manager(
            verbose_level=verbose_level,
            show_tokens=show_tokens,
            show_progress=show_progress,
            show_timing=show_timing
        )
        
        # 输入数据
        input_data = {
            "messages": [
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        }
        
        # 流式执行并返回结果
        for result in stream_manager.stream_supervisor_execution(self.supervisor, input_data):
            # 确保返回的结果是可JSON序列化的
            serializable_result = self._make_serializable(result)
            yield serializable_result
    
    def _make_serializable(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """将结果转换为可JSON序列化的格式"""
        return self._convert_to_serializable(result)
    
    def _convert_to_serializable(self, obj):
        """递归转换对象为可JSON序列化的格式"""
        if hasattr(obj, 'to_dict'):
            # 处理有to_dict方法的对象（如OutputMessage）
            dict_obj = obj.to_dict()
            return self._convert_to_serializable(dict_obj)
        elif hasattr(obj, 'value'):
            # 处理枚举对象（如OutputType）
            return obj.value
        elif hasattr(obj, '__dict__'):
            # 处理其他自定义对象
            return {k: self._convert_to_serializable(v) for k, v in obj.__dict__.items()}
        elif isinstance(obj, dict):
            # 处理字典
            return {k: self._convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            # 处理列表和元组
            return [self._convert_to_serializable(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            # 处理基本类型
            return obj
        else:
            # 其他类型转换为字符串
            return str(obj)
    
    def run_enhanced_streaming_api_list(self, user_input: str,
                                      verbose_level: int = 1,
                                      show_tokens: bool = True,
                                      show_progress: bool = True,
                                      show_timing: bool = True) -> List[Dict[str, Any]]:
        """
        运行增强型流式输出API版本（返回完整列表）
        
        Args:
            user_input: 用户输入
            verbose_level: 详细程度
            show_tokens: 是否显示token流式输出
            show_progress: 是否显示进度信息
            show_timing: 是否显示时间统计
            
        Returns:
            List[Dict[str, Any]]: 所有流式输出结果的列表
        """
        results = []
        for result in self.run_enhanced_streaming_api(
            user_input, verbose_level, show_tokens, show_progress, show_timing
        ):
            results.append(result)
        return results


# 便捷函数
def run_enhanced_streaming_api(user_input: str, 
                             supervisor=None,
                             verbose_level: int = 1,
                             show_tokens: bool = True,
                             show_progress: bool = True,
                             show_timing: bool = True) -> Generator[Dict[str, Any], None, None]:
    """
    便捷函数：运行增强型流式输出API
    
    Args:
        user_input: 用户输入
        supervisor: LangGraph supervisor实例
        verbose_level: 详细程度
        show_tokens: 是否显示token流式输出
        show_progress: 是否显示进度信息
        show_timing: 是否显示时间统计
        
    Yields:
        Dict[str, Any]: 流式输出结果
    """
    api = EnhancedStreamAPI(supervisor)
    for result in api.run_enhanced_streaming_api(
        user_input, verbose_level, show_tokens, show_progress, show_timing
    ):
        yield result


def run_enhanced_streaming_api_list(user_input: str,
                                  supervisor=None,
                                  verbose_level: int = 1,
                                  show_tokens: bool = True,
                                  show_progress: bool = True,
                                  show_timing: bool = True) -> List[Dict[str, Any]]:
    """
    便捷函数：运行增强型流式输出API（返回完整列表）
    
    Args:
        user_input: 用户输入
        supervisor: LangGraph supervisor实例
        verbose_level: 详细程度
        show_tokens: 是否显示token流式输出
        show_progress: 是否显示进度信息
        show_timing: 是否显示时间统计
        
    Returns:
        List[Dict[str, Any]]: 所有流式输出结果的列表
    """
    api = EnhancedStreamAPI(supervisor)
    return api.run_enhanced_streaming_api_list(
        user_input, verbose_level, show_tokens, show_progress, show_timing
    )


# Flask API示例
def create_flask_api():
    """创建Flask API示例"""
    from flask import Flask, request, jsonify, Response
    import json
    
    app = Flask(__name__)
    

    
    @app.route('/enhanced_stream', methods=['POST'])
    def enhanced_stream_endpoint():
        """增强型流式输出API端点"""
        try:
            data = request.get_json()
            user_input = data.get('user_input', '')
            verbose_level = data.get('verbose_level', 1)
            show_tokens = data.get('show_tokens', True)
            show_progress = data.get('show_progress', True)
            show_timing = data.get('show_timing', True)
            
            def generate():
                for result in run_enhanced_streaming_api(
                    user_input=user_input,
                    supervisor=supervisor,
                    verbose_level=verbose_level,
                    show_tokens=show_tokens,
                    show_progress=show_progress,
                    show_timing=show_timing
                ):
                    yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"
            
            return Response(generate(), mimetype='text/plain')
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/enhanced_stream_complete', methods=['POST'])
    def enhanced_stream_complete_endpoint():
        """增强型流式输出API端点（返回完整结果）"""
        try:
            data = request.get_json()
            user_input = data.get('user_input', '')
            verbose_level = data.get('verbose_level', 1)
            show_tokens = data.get('show_tokens', True)
            show_progress = data.get('show_progress', True)
            show_timing = data.get('show_timing', True)
            
            results = run_enhanced_streaming_api_list(
                user_input=user_input,
                supervisor=supervisor,
                verbose_level=verbose_level,
                show_tokens=show_tokens,
                show_progress=show_progress,
                show_timing=show_timing
            )
            
            return jsonify({
                "status": "success",
                "results": results,
                "total_count": len(results)
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return app


# FastAPI示例
def create_fastapi_api():
    """创建FastAPI API示例"""
    from fastapi import FastAPI
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel
    import json
    
    app = FastAPI(title="Enhanced Stream API")
    
    class StreamRequest(BaseModel):
        user_input: str
        verbose_level: int = 1
        show_tokens: bool = True
        show_progress: bool = True
        show_timing: bool = True
    

    
    @app.post("/enhanced_stream")
    async def enhanced_stream_endpoint(request: StreamRequest):
        """增强型流式输出API端点"""
        def generate():
            for result in run_enhanced_streaming_api(
                user_input=request.user_input,
                supervisor=supervisor,
                verbose_level=request.verbose_level,
                show_tokens=request.show_tokens,
                show_progress=request.show_progress,
                show_timing=request.show_timing
            ):
                yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(generate(), media_type="text/plain")
    
    @app.post("/enhanced_stream_complete")
    async def enhanced_stream_complete_endpoint(request: StreamRequest):
        """增强型流式输出API端点（返回完整结果）"""
        results = run_enhanced_streaming_api_list(
            user_input=request.user_input,
            supervisor=supervisor,
            verbose_level=request.verbose_level,
            show_tokens=request.show_tokens,
            show_progress=request.show_progress,
            show_timing=request.show_timing
        )
        
        return {
            "status": "success",
            "results": results,
            "total_count": len(results)
        }
    
    return app


# 使用示例
if __name__ == "__main__":
    # 示例1：生成器方式使用
    print("=== 生成器方式使用 ===")
    user_input = "推荐风景"
    from supervisor_agent import create_multi_turn_chat_supervisor
    supervisor = create_multi_turn_chat_supervisor()


    for result in run_enhanced_streaming_api(user_input, supervisor):
        print("API返回结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("-" * 50)
    
    # 示例2：列表方式使用
    print("\n=== 列表方式使用 ===")
    results = run_enhanced_streaming_api_list(user_input, supervisor)
    print(f"总共获得 {len(results)} 个结果")
    for i, result in enumerate(results):
        print(f"结果 {i+1}:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("-" * 30)
