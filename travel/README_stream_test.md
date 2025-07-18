# 流式数据测试工具使用说明

## 概述

`test_stream_data_logger.py` 是一个专门用于测试和分析 `run_enhanced_streaming_api` 函数原始数据输出的工具。它能够详细记录流式数据的结构、性能指标和统计信息，为后期API封装提供数据基础。

## 功能特性

### 🔍 数据捕获
- **原始数据记录**：完整保存每个数据块的JSON格式
- **实时监控**：显示数据块处理进度和基本信息
- **错误处理**：捕获并记录处理过程中的异常

### 📊 数据分析
- **结构分析**：递归分析数据字段和类型结构
- **统计信息**：记录字段出现频率和数据类型分布
- **性能指标**：测量处理速度、数据量等性能参数

### 📝 日志记录
- **分类日志**：原始数据、结构分析、性能指标分别记录
- **时间戳**：精确记录每个数据块的时间信息
- **总结报告**：生成JSON格式的测试总结

## 使用方法

### 1. 快速测试
```bash
cd agent-mi/travel
python test_stream_data_logger.py --mode quick
```

### 2. 单个测试
```bash
python test_stream_data_logger.py --mode single --input "推荐北京景点" --name "beijing_test"
```

### 3. 批量测试
```bash
python test_stream_data_logger.py --mode batch
```

### 4. 在代码中使用
```python
from test_stream_data_logger import test_stream_api_with_logging

# 运行单个测试
summary = test_stream_api_with_logging(
    user_input="我想去杭州旅游3天",
    test_name="hangzhou_test"
)

print(f"总数据块数: {summary['data_statistics']['total_chunks']}")
```

## 输出文件说明

测试完成后，会在 `stream_test_logs/` 目录下生成以下文件：

### 📁 单个测试目录结构
```
stream_test_logs/
└── test_name_20250716_170000/
    ├── raw_stream_data_20250716_170000.log      # 原始数据日志
    ├── data_structure_20250716_170000.log       # 数据结构分析
    ├── performance_metrics_20250716_170000.log  # 性能指标
    ├── error_log_20250716_170000.log           # 错误日志
    └── test_summary_20250716_170000.json       # 测试总结
```

### 📄 文件内容说明

#### 1. 原始数据日志 (raw_stream_data_*.log)
```
--- CHUNK #1 ---
时间戳: 2025-07-16T17:00:01.123456
数据大小: 1024 bytes
原始数据:
{
  "stream_mode": "updates",
  "chunk": {...},
  "processed": true
}
---
```

#### 2. 数据结构分析 (data_structure_*.log)
```
--- 结构分析 #1 ---
时间戳: 2025-07-16T17:00:01.123456
数据类型: dict
字段结构: {
  "type": "dict",
  "keys": ["stream_mode", "chunk", "processed"],
  "fields": {...}
}
---
```

#### 3. 性能指标 (performance_metrics_*.log)
```
时间戳: 2025-07-16T17:00:01.123456
Chunk #1
当前块大小: 1024 bytes
累计数据量: 1024 bytes
平均块大小: 1024.00 bytes
累计耗时: 0.123 seconds
处理速率: 8.13 chunks/sec
数据速率: 8325.20 bytes/sec
---
```

#### 4. 测试总结 (test_summary_*.json)
```json
{
  "test_info": {
    "start_time": "2025-07-16T17:00:00.000000",
    "end_time": "2025-07-16T17:00:30.000000",
    "total_duration_seconds": 30.0
  },
  "data_statistics": {
    "total_chunks": 25,
    "total_data_size_bytes": 25600,
    "average_chunk_size_bytes": 1024.0,
    "processing_rate_chunks_per_sec": 0.83,
    "data_rate_bytes_per_sec": 853.33
  },
  "structure_analysis": {
    "data_types_seen": ["dict"],
    "field_statistics": {
      "stream_mode": {
        "occurrence_count": 25,
        "data_types": ["str"]
      }
    }
  },
  "config_used": {
    "verbose_level": 1,
    "show_tokens": true,
    "show_progress": true,
    "show_timing": true
  }
}
```

## 配置参数

测试使用的配置参数来自 `simple_multi_turn_system/config.py` 中的 `SUPERVISOR_CONFIG`：

```python
SUPERVISOR_CONFIG = {
    'verbose_level': 1,
    'show_tokens': True,
    'show_progress': True,
    'show_timing': True
}
```

## 预设测试用例

批量测试模式包含以下预设用例：

1. **简单查询** (`simple_query`)
   - 输入：`"推荐北京的景点"`
   - 目的：测试基础景点推荐功能

2. **复杂规划** (`complex_planning`)
   - 输入：`"我想要一个3天的北京旅游计划，包括故宫、天坛、颐和园"`
   - 目的：测试复杂行程规划功能

3. **详细需求** (`detailed_request`)
   - 输入：`"我和女朋友计划下个月去杭州玩3天，预算3000元，喜欢历史文化和美食，请帮我制定详细的旅游计划"`
   - 目的：测试详细需求处理能力

## 注意事项

1. **环境依赖**：确保所有相关模块都已正确安装和配置
2. **网络连接**：测试过程中需要访问外部API，确保网络连接正常
3. **存储空间**：日志文件可能较大，确保有足够的磁盘空间
4. **测试时间**：复杂测试可能需要较长时间，请耐心等待

## 故障排除

### 常见问题

1. **导入模块失败**
   ```
   ImportError: No module named 'enhanced_stream_api_V1'
   ```
   - 解决：检查文件路径和模块依赖

2. **Supervisor初始化失败**
   ```
   Error: 无法创建supervisor
   ```
   - 解决：检查API密钥和网络连接

3. **日志文件权限错误**
   ```
   PermissionError: [Errno 13] Permission denied
   ```
   - 解决：检查目录写入权限

### 调试模式

如需更详细的调试信息，可以修改日志级别：

```python
logging.basicConfig(level=logging.DEBUG)
```

## 数据分析建议

基于测试结果，您可以分析以下关键指标：

1. **数据块频率**：了解流式输出的时间特征
2. **数据结构稳定性**：检查字段结构的一致性
3. **性能瓶颈**：识别处理速度的限制因素
4. **数据量分布**：了解不同类型查询的数据量差异

这些分析结果将为您的流式API封装提供重要的设计参考。
