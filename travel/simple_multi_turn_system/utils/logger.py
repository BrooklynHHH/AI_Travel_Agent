#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志工具模块
"""

import logging
import os
import json
from datetime import datetime
from config import LOG_LEVEL, LOG_FORMAT, LOG_FILE, PROJECT_ROOT, ENABLE_API_OUTPUT_LOG, API_OUTPUT_LOG_DIR

def setup_logger(name: str = "simple_multi_turn", level: str = None) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别
        
    Returns:
        配置好的日志记录器
    """
    # 使用配置文件中的级别，如果没有指定的话
    log_level = level or LOG_LEVEL
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建格式化器
    formatter = logging.Formatter(LOG_FORMAT)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    log_file_path = os.path.join(PROJECT_ROOT, LOG_FILE)
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def log_user_input(logger: logging.Logger, user_input: str, session_id: str = None):
    """记录用户输入"""
    session_info = f"[{session_id}] " if session_id else ""
    logger.info(f"💬 {session_info}用户输入: {user_input}")

def log_system_response(logger: logging.Logger, response: str, session_id: str = None):
    """记录系统响应"""
    session_info = f"[{session_id}] " if session_id else ""
    logger.info(f"🤖 {session_info}系统响应: {response[:100]}...")

def log_stream_chunk(logger: logging.Logger, chunk_type: str, content_length: int, session_id: str = None):
    """记录流式数据块"""
    session_info = f"[{session_id}] " if session_id else ""
    logger.debug(f"📡 {session_info}流式数据: {chunk_type}, 长度: {content_length}")

def log_error(logger: logging.Logger, error: Exception, context: str = "", session_id: str = None):
    """记录错误信息"""
    session_info = f"[{session_id}] " if session_id else ""
    logger.error(f"❌ {session_info}{context}: {str(error)}", exc_info=True)

def log_session_event(logger: logging.Logger, event: str, session_id: str, details: str = ""):
    """记录会话事件"""
    logger.info(f"🔄 [{session_id}] {event}: {details}")

def log_api_output(chunk_data: str, session_id: str = None):
    """
    记录API输出数据块到本地文件
    
    Args:
        chunk_data: 输出的数据块内容
        session_id: 会话ID
    """
    if not ENABLE_API_OUTPUT_LOG:
        return
    
    try:
        # 创建日志目录
        log_dir = os.path.join(PROJECT_ROOT, API_OUTPUT_LOG_DIR)
        os.makedirs(log_dir, exist_ok=True)
        
        # 生成日志文件名（按日期）
        today = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(log_dir, f"api_output_{today}.log")
        
        # 计算数据块大小
        chunk_size = len(chunk_data.encode('utf-8'))
        
        # 格式化日志条目
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        session_info = session_id or "unknown"
        
        # 构建日志条目
        log_entry = {
            "timestamp": timestamp,
            "session_id": session_info,
            "chunk_size": chunk_size,
            "data": chunk_data.strip()
        }
        
        # 写入日志文件
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            
    except Exception as e:
        # 如果API输出日志失败，记录到主日志中，但不影响主流程
        main_logger = logging.getLogger("simple_multi_turn_api")
        main_logger.error(f"API输出日志记录失败: {str(e)}")
