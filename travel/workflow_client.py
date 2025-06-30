import requests
import json
from typing import Dict, List, Union, Optional, Any, Generator
import logging
import time

class WorkflowClient:
    """
    工作流API客户端
    用于调用Workflow应用API，支持流式和阻塞模式
    """
    
    def __init__(self, api_key: str, base_url: str = "https://mify-be.pt.xiaomi.com/api/v1"):
        """
        初始化工作流客户端
        
        Args:
            api_key: API密钥
            base_url: API基础URL，默认为小米Mify服务
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger(__name__)
    
    def upload_file(self, file_path: str, user: str, file_type: str = "document") -> Optional[str]:
        """
        上传文件到服务器
        
        Args:
            file_path: 文件路径
            user: 用户标识
            file_type: 文件类型，默认为document
            
        Returns:
            上传成功返回文件ID，失败返回None
        """
        upload_url = f"{self.base_url}/files/upload"
        
        try:
            with open(file_path, 'rb') as file:
                files = {
                    'file': (file_path.split('/')[-1], file)
                }
                data = {
                    "user": user,
                    "type": file_type
                }
                
                response = requests.post(upload_url, headers=self.headers, files=files, data=data)
                
                if response.status_code == 201:
                    self.logger.info("文件上传成功")
                    return response.json().get("id")
                else:
                    self.logger.error(f"文件上传失败，状态码: {response.status_code}, 响应: {response.text}")
                    return None
        except Exception as e:
            self.logger.error(f"文件上传过程中发生错误: {str(e)}")
            return None
    
    def run_workflow_blocking(self, inputs: Dict[str, Any], user: str) -> Dict[str, Any]:
        """
        以阻塞模式运行工作流
        
        Args:
            inputs: 工作流输入参数
            user: 用户标识
            
        Returns:
            工作流执行结果
        """
        workflow_url = f"{self.base_url}/workflows/run"
        
        data = {
            "inputs": inputs,
            "response_mode": "blocking",
            "user": user
        }
        
        try:
            response = requests.post(workflow_url, headers=self.headers, json=data)
            
            if response.status_code == 200:
                self.logger.info("工作流执行成功")
                return response.json()
            else:
                error_msg = f"工作流执行失败，状态码: {response.status_code}, 响应: {response.text}"
                self.logger.error(error_msg)
                return {"status": "error", "message": error_msg}
        except Exception as e:
            error_msg = f"工作流执行过程中发生错误: {str(e)}"
            self.logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    def run_workflow_streaming(self, inputs: Dict[str, Any], user: str) -> Generator[Dict[str, Any], None, None]:
        """
        以流式模式运行工作流
        
        Args:
            inputs: 工作流输入参数
            user: 用户标识
            
        Returns:
            生成器，产生工作流执行的流式响应
        """
        workflow_url = f"{self.base_url}/workflows/run"
        
        data = {
            "inputs": inputs,
            "response_mode": "streaming",
            "user": user
        }
        
        try:
            with requests.post(workflow_url, headers=self.headers, json=data, stream=True) as response:
                if response.status_code != 200:
                    error_msg = f"工作流执行失败，状态码: {response.status_code}, 响应: {response.text}"
                    self.logger.error(error_msg)
                    yield {"status": "error", "message": error_msg}
                    return
                
                # 处理SSE流
                buffer = ""
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        buffer += chunk.decode('utf-8')
                        while '\n\n' in buffer:
                            event, buffer = buffer.split('\n\n', 1)
                            if event.startswith('data: '):
                                event_data = event[6:]  # 去掉 'data: ' 前缀
                                try:
                                    parsed_data = json.loads(event_data)
                                    yield parsed_data
                                except json.JSONDecodeError:
                                    self.logger.warning(f"无法解析事件数据: {event_data}")
        except Exception as e:
            error_msg = f"流式工作流执行过程中发生错误: {str(e)}"
            self.logger.error(error_msg)
            yield {"status": "error", "message": error_msg}
    
    def prepare_file_input(self, variable_name: str, file_id: str, file_type: str = "document") -> Dict[str, Dict[str, str]]:
        """
        准备包含文件的输入
        
        Args:
            variable_name: 变量名称
            file_id: 文件ID
            file_type: 文件类型，默认为document
            
        Returns:
            格式化的文件输入字典
        """
        return {
            variable_name: {
                "transfer_method": "local_file",
                "upload_file_id": file_id,
                "type": file_type
            }
        }
    
    def prepare_remote_file_input(self, variable_name: str, file_url: str, file_type: str = "document") -> Dict[str, Dict[str, str]]:
        """
        准备包含远程文件URL的输入
        
        Args:
            variable_name: 变量名称
            file_url: 文件URL
            file_type: 文件类型，默认为document
            
        Returns:
            格式化的远程文件输入字典
        """
        return {
            variable_name: {
                "transfer_method": "remote_url",
                "url": file_url,
                "type": file_type
            }
        }
    
    def run_workflow_with_file(self, file_path: str, variable_name: str, user: str, 
                              additional_inputs: Dict[str, Any] = None, 
                              streaming: bool = False) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """
        上传文件并运行工作流的便捷方法
        
        Args:
            file_path: 文件路径
            variable_name: 文件变量名称
            user: 用户标识
            additional_inputs: 额外的输入参数
            streaming: 是否使用流式模式
            
        Returns:
            工作流执行结果或生成器
        """
        # 上传文件
        file_id = self.upload_file(file_path, user)
        if not file_id:
            error_msg = "文件上传失败，无法执行工作流"
            self.logger.error(error_msg)
            if streaming:
                return (yield {"status": "error", "message": error_msg})
            else:
                return {"status": "error", "message": error_msg}
        
        # 准备输入
        inputs = self.prepare_file_input(variable_name, file_id)
        
        # 添加额外输入
        if additional_inputs:
            inputs.update(additional_inputs)
        
        # 执行工作流
        if streaming:
            return self.run_workflow_streaming(inputs, user)
        else:
            return self.run_workflow_blocking(inputs, user)


# 使用示例
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 初始化客户端
    client = WorkflowClient(api_key="your_api_key_here")
    
    # 示例1: 简单工作流调用（阻塞模式）
    result = client.run_workflow_blocking({}, "test_user")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 示例2: 文件上传并调用工作流（阻塞模式）
    file_result = client.run_workflow_with_file(
        file_path="example.txt",
        variable_name="document",
        user="test_user",
        streaming=False
    )
    print(json.dumps(file_result, indent=2, ensure_ascii=False))
    
    # 示例3: 流式模式调用
    for event in client.run_workflow_streaming({}, "test_user"):
        print(f"收到事件: {event.get('event', 'unknown')}")
        print(json.dumps(event, indent=2, ensure_ascii=False))
        print("-" * 50)
