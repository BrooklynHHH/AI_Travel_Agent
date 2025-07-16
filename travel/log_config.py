"""
日志配置模块
提供按时间命名的日志文件和详细的日志记录功能
"""

import logging
import os
from datetime import datetime
from pathlib import Path
import sys

class TimestampedLogger:
    """带时间戳的日志管理器"""
    
    def __init__(self, base_dir="logs"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)
        
        # 创建latest目录用于软链接
        self.latest_dir = self.base_dir / "latest"
        self.latest_dir.mkdir(exist_ok=True)
        
        # 生成时间戳
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # 初始化各种logger
        self.loggers = {}
        self._setup_loggers()
    
    def _setup_loggers(self):
        """设置各种类型的logger"""
        
        # 日志格式
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 创建不同类型的logger
        logger_configs = {
            'planning': 'planning.log',
            'optimization': 'optimization.log', 
            'api': 'api.log'
        }
        
        for logger_name, log_filename in logger_configs.items():
            # 创建带时间戳的日志文件名
            timestamped_filename = f"{self.timestamp}_{log_filename}"
            log_file_path = self.base_dir / timestamped_filename
            latest_link_path = self.latest_dir / log_filename
            
            # 创建logger
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.DEBUG)
            
            # 清除已有的handlers
            logger.handlers.clear()
            
            # 文件handler
            file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            
            # 控制台handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            
            # 添加handlers
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            
            # 防止重复日志
            logger.propagate = False
            
            self.loggers[logger_name] = logger
            
            # 创建软链接到latest目录
            try:
                if latest_link_path.exists():
                    latest_link_path.unlink()
                latest_link_path.symlink_to(f"../{timestamped_filename}")
            except OSError:
                # Windows系统可能不支持软链接，跳过
                pass
    
    def get_logger(self, logger_name):
        """获取指定类型的logger"""
        return self.loggers.get(logger_name, logging.getLogger(logger_name))
    
    def log_session_start(self, logger_name, session_id, operation_type, **kwargs):
        """记录会话开始"""
        logger = self.get_logger(logger_name)
        logger.info(f"[SESSION:{session_id}] [OPERATION:{operation_type}] 开始 - 参数: {kwargs}")
    
    def log_step(self, logger_name, session_id, step_count, message, **kwargs):
        """记录处理步骤"""
        logger = self.get_logger(logger_name)
        extra_info = f" - {kwargs}" if kwargs else ""
        logger.info(f"[SESSION:{session_id}] [STEP:{step_count}] {message}{extra_info}")
    
    def log_step_debug(self, logger_name, session_id, step_count, message, data=None):
        """记录详细调试信息"""
        logger = self.get_logger(logger_name)
        if data:
            logger.debug(f"[SESSION:{session_id}] [STEP:{step_count}] {message} - 数据: {str(data)[:500]}...")
        else:
            logger.debug(f"[SESSION:{session_id}] [STEP:{step_count}] {message}")
    
    def log_performance(self, logger_name, session_id, operation, duration_ms):
        """记录性能指标"""
        logger = self.get_logger(logger_name)
        logger.info(f"[SESSION:{session_id}] [PERFORMANCE] {operation} 耗时: {duration_ms:.3f}ms")
    
    def log_error(self, logger_name, session_id, error_msg, exception=None):
        """记录错误信息"""
        logger = self.get_logger(logger_name)
        if exception:
            logger.error(f"[SESSION:{session_id}] [ERROR] {error_msg}", exc_info=exception)
        else:
            logger.error(f"[SESSION:{session_id}] [ERROR] {error_msg}")
    
    def log_session_complete(self, logger_name, session_id, operation_type, total_steps, **kwargs):
        """记录会话完成"""
        logger = self.get_logger(logger_name)
        logger.info(f"[SESSION:{session_id}] [OPERATION:{operation_type}] 完成 - 总步骤: {total_steps}, 结果: {kwargs}")

# 全局日志管理器实例
_global_logger_manager = None

def get_logger_manager():
    """获取全局日志管理器实例"""
    global _global_logger_manager
    if _global_logger_manager is None:
        # 确保在travel目录下创建logs文件夹
        current_dir = Path(__file__).parent
        logs_dir = current_dir / "logs"
        _global_logger_manager = TimestampedLogger(logs_dir)
    return _global_logger_manager

def get_planning_logger():
    """获取旅游规划logger"""
    return get_logger_manager().get_logger('planning')

def get_optimization_logger():
    """获取方案优化logger"""
    return get_logger_manager().get_logger('optimization')

def get_api_logger():
    """获取API通用logger"""
    return get_logger_manager().get_logger('api')

# 便捷函数
def log_planning_step(session_id, step_count, message, **kwargs):
    """记录规划步骤"""
    get_logger_manager().log_step('planning', session_id, step_count, message, **kwargs)

def log_optimization_step(session_id, step_count, message, **kwargs):
    """记录优化步骤"""
    get_logger_manager().log_step('optimization', session_id, step_count, message, **kwargs)

def log_planning_error(session_id, error_msg, exception=None):
    """记录规划错误"""
    get_logger_manager().log_error('planning', session_id, error_msg, exception)

def log_optimization_error(session_id, error_msg, exception=None):
    """记录优化错误"""
    get_logger_manager().log_error('optimization', session_id, error_msg, exception)
