#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化多轮对话系统配置文件
"""

import os

# 路径配置
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
AGENT_MI_PATH = os.path.join(PROJECT_ROOT, '../agent-mi/travel')

# API配置
API_HOST = '0.0.0.0'
API_PORT = 5000
DEBUG_MODE = True

# 会话配置
MAX_HISTORY_LENGTH = 10
SESSION_TIMEOUT = 3600  # 1小时

# 智能体配置
SUPERVISOR_CONFIG = {
    'verbose_level': 1,
    'show_tokens': True,
    'show_progress': True,
    'show_timing': True
}

# 内容格式化配置
CONTENT_TYPES = {
    'text': '📝',
    'recommendation': '🎯',
    'error': '❌',
    'system': '🤖',
    'planning': '📋',
    'transport': '🚗',
    'hotel': '🏨'
}

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = 'simple_multi_turn.log'
