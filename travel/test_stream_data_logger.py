#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流式数据测试和日志记录器
用于测试 run_enhanced_streaming_api 函数的原始数据输出
"""

import sys
import os
import json
import time
import traceback
from datetime import datetime
from typing import Dict, Any, List, Generator
import logging

# 添加路径以导入相关模块
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 导入测试目标模块
try:
    from enhanced_stream_api_V1 import run_enhanced_streaming_api
    from supervisor_agent import create_multi_turn_chat_supervisor
    from simple_multi_turn_system.config import SUPERVISOR_CONFIG
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保所有依赖模块都存在")
    sys.exit(1)

class StreamDataLogger:
    """流式数据记录器"""
    
    def __init__(self, log_dir: str = "stream_test_logs"):
        """
        初始化日志记录器
        
        Args:
            log_dir: 日志文件目录
        """
        self.log_dir = log_dir
        self.test_start_time = datetime.now()
        self.chunk_count = 0
        self.total_data_size = 0
        self.data_types_seen = set()
        self.field_structures = {}
        
        # 创建日志目录
        os.makedirs(log_dir, exist_ok=True)
        
        # 初始化日志文件
        self.setup_loggers()
        
    def setup_loggers(self):
        """设置各种日志记录器"""
        timestamp = self.test_start_time.strftime("%Y%m%d_%H%M%S")
        
        # 原始数据日志
        self.raw_data_file = open(
            os.path.join(self.log_dir, f"raw_stream_data_{timestamp}.log"), 
            'w', encoding='utf-8'
        )
        
        # 结构分析日志
        self.structure_file = open(
            os.path.join(self.log_dir, f"data_structure_{timestamp}.log"), 
            'w', encoding='utf-8'
        )
        
        # 性能指标日志
        self.performance_file = open(
            os.path.join(self.log_dir, f"performance_metrics_{timestamp}.log"), 
            'w', encoding='utf-8'
        )
        
        # 错误日志
        logging.basicConfig(
            filename=os.path.join(self.log_dir, f"error_log_{timestamp}.log"),
            level=logging.ERROR,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # 写入日志头部信息
        self._write_log_headers()
    
    def _write_log_headers(self):
        """写入日志文件头部信息"""
        header_info = f"""
=== 流式数据测试日志 ===
测试开始时间: {self.test_start_time.isoformat()}
测试目标: run_enhanced_streaming_api 函数
配置参数: {SUPERVISOR_CONFIG}
========================================

"""
        
        self.raw_data_file.write(header_info)
        self.structure_file.write(header_info)
        self.performance_file.write(header_info)
        
        # 刷新缓冲区
        self.raw_data_file.flush()
        self.structure_file.flush()
        self.performance_file.flush()
    
    def log_chunk(self, chunk: Dict[str, Any], chunk_timestamp: datetime):
        """
        记录单个数据块
        
        Args:
            chunk: 数据块
            chunk_timestamp: 数据块时间戳
        """
        self.chunk_count += 1
        
        try:
            # 序列化数据块
            chunk_json = json.dumps(chunk, ensure_ascii=False, indent=2)
            chunk_size = len(chunk_json.encode('utf-8'))
            self.total_data_size += chunk_size
            
            # 记录原始数据
            self._log_raw_data(chunk, chunk_json, chunk_timestamp, chunk_size)
            
            # 分析数据结构
            self._analyze_structure(chunk, chunk_timestamp)
            
            # 记录性能指标
            self._log_performance(chunk_timestamp, chunk_size)
            
            # 实时输出进度
            print(f"[{chunk_timestamp.strftime('%H:%M:%S.%f')[:-3]}] "
                  f"Chunk #{self.chunk_count} | Size: {chunk_size} bytes | "
                  f"Type: {type(chunk).__name__}")
            
        except Exception as e:
            logging.error(f"记录数据块时出错: {str(e)}\n{traceback.format_exc()}")
            print(f"❌ 记录数据块 #{self.chunk_count} 时出错: {str(e)}")
    
    def _log_raw_data(self, chunk: Dict[str, Any], chunk_json: str, 
                      timestamp: datetime, size: int):
        """记录原始数据"""
        log_entry = f"""
--- CHUNK #{self.chunk_count} ---
时间戳: {timestamp.isoformat()}
数据大小: {size} bytes
原始数据:
{chunk_json}
---

"""
        self.raw_data_file.write(log_entry)
        self.raw_data_file.flush()
    
    def _analyze_structure(self, chunk: Dict[str, Any], timestamp: datetime):
        """分析数据结构"""
        try:
            structure_info = self._extract_structure_info(chunk)
            
            log_entry = f"""
--- 结构分析 #{self.chunk_count} ---
时间戳: {timestamp.isoformat()}
数据类型: {type(chunk).__name__}
字段结构: {json.dumps(structure_info, ensure_ascii=False, indent=2)}
---

"""
            self.structure_file.write(log_entry)
            self.structure_file.flush()
            
            # 更新全局结构统计
            self._update_structure_stats(structure_info)
            
        except Exception as e:
            logging.error(f"分析数据结构时出错: {str(e)}")
    
    def _extract_structure_info(self, obj: Any, max_depth: int = 5, current_depth: int = 0) -> Dict[str, Any]:
        """递归提取数据结构信息"""
        if current_depth >= max_depth:
            return {"type": type(obj).__name__, "truncated": True}
        
        if isinstance(obj, dict):
            return {
                "type": "dict",
                "keys": list(obj.keys()),
                "fields": {
                    key: self._extract_structure_info(value, max_depth, current_depth + 1)
                    for key, value in obj.items()
                }
            }
        elif isinstance(obj, list):
            return {
                "type": "list",
                "length": len(obj),
                "item_types": [type(item).__name__ for item in obj[:5]],  # 只分析前5个元素
                "sample_structure": self._extract_structure_info(obj[0], max_depth, current_depth + 1) if obj else None
            }
        else:
            return {
                "type": type(obj).__name__,
                "value_sample": str(obj)[:100] if len(str(obj)) > 100 else str(obj)
            }
    
    def _update_structure_stats(self, structure_info: Dict[str, Any]):
        """更新结构统计信息"""
        data_type = structure_info.get("type", "unknown")
        self.data_types_seen.add(data_type)
        
        if data_type == "dict":
            keys = structure_info.get("keys", [])
            for key in keys:
                if key not in self.field_structures:
                    self.field_structures[key] = {"count": 0, "types": set()}
                self.field_structures[key]["count"] += 1
                field_type = structure_info.get("fields", {}).get(key, {}).get("type", "unknown")
                self.field_structures[key]["types"].add(field_type)
    
    def _log_performance(self, timestamp: datetime, chunk_size: int):
        """记录性能指标"""
        elapsed_time = (timestamp - self.test_start_time).total_seconds()
        avg_chunk_size = self.total_data_size / self.chunk_count if self.chunk_count > 0 else 0
        
        log_entry = f"""
时间戳: {timestamp.isoformat()}
Chunk #{self.chunk_count}
当前块大小: {chunk_size} bytes
累计数据量: {self.total_data_size} bytes
平均块大小: {avg_chunk_size:.2f} bytes
累计耗时: {elapsed_time:.3f} seconds
处理速率: {self.chunk_count / elapsed_time:.2f} chunks/sec
数据速率: {self.total_data_size / elapsed_time:.2f} bytes/sec
---

"""
        self.performance_file.write(log_entry)
        self.performance_file.flush()
    
    def generate_summary(self):
        """生成测试总结"""
        test_end_time = datetime.now()
        total_duration = (test_end_time - self.test_start_time).total_seconds()
        
        summary = {
            "test_info": {
                "start_time": self.test_start_time.isoformat(),
                "end_time": test_end_time.isoformat(),
                "total_duration_seconds": total_duration
            },
            "data_statistics": {
                "total_chunks": self.chunk_count,
                "total_data_size_bytes": self.total_data_size,
                "average_chunk_size_bytes": self.total_data_size / self.chunk_count if self.chunk_count > 0 else 0,
                "processing_rate_chunks_per_sec": self.chunk_count / total_duration if total_duration > 0 else 0,
                "data_rate_bytes_per_sec": self.total_data_size / total_duration if total_duration > 0 else 0
            },
            "structure_analysis": {
                "data_types_seen": list(self.data_types_seen),
                "field_statistics": {
                    key: {
                        "occurrence_count": stats["count"],
                        "data_types": list(stats["types"])
                    }
                    for key, stats in self.field_structures.items()
                }
            },
            "config_used": SUPERVISOR_CONFIG
        }
        
        # 保存总结到JSON文件
        timestamp = self.test_start_time.strftime("%Y%m%d_%H%M%S")
        summary_file = os.path.join(self.log_dir, f"test_summary_{timestamp}.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        return summary
    
    def close(self):
        """关闭所有日志文件"""
        try:
            self.raw_data_file.close()
            self.structure_file.close()
            self.performance_file.close()
        except Exception as e:
            logging.error(f"关闭日志文件时出错: {str(e)}")


def test_stream_api_with_logging(user_input: str, test_name: str = "default"):
    """
    测试流式API并记录所有数据
    
    Args:
        user_input: 用户输入
        test_name: 测试名称
    """
    print(f"\n🚀 开始测试: {test_name}")
    print(f"📝 用户输入: {user_input}")
    print(f"⚙️ 配置参数: {SUPERVISOR_CONFIG}")
    print("=" * 60)
    
    # 创建日志记录器
    log_dir = f"stream_test_logs/{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    logger = StreamDataLogger(log_dir)
    
    try:
        # 初始化supervisor
        print("🔧 正在初始化supervisor...")
        supervisor = create_multi_turn_chat_supervisor()
        print("✅ Supervisor初始化成功")
        
        # 开始流式处理
        print("🌊 开始流式处理...")
        start_time = time.time()
        
        for chunk in run_enhanced_streaming_api(
            user_input=user_input,
            supervisor=supervisor,
            **SUPERVISOR_CONFIG
        ):
            chunk_timestamp = datetime.now()
            logger.log_chunk(chunk, chunk_timestamp)
        
        end_time = time.time()
        print(f"\n✅ 流式处理完成，总耗时: {end_time - start_time:.3f} 秒")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {str(e)}")
        logging.error(f"测试失败: {str(e)}\n{traceback.format_exc()}")
        
    finally:
        # 生成测试总结
        print("\n📊 正在生成测试总结...")
        summary = logger.generate_summary()
        logger.close()
        
        # 打印总结信息
        print("\n" + "=" * 60)
        print("📋 测试总结")
        print("=" * 60)
        print(f"📦 总数据块数: {summary['data_statistics']['total_chunks']}")
        print(f"📏 总数据量: {summary['data_statistics']['total_data_size_bytes']} bytes")
        print(f"⚡ 处理速率: {summary['data_statistics']['processing_rate_chunks_per_sec']:.2f} chunks/sec")
        print(f"🔍 发现的数据类型: {', '.join(summary['structure_analysis']['data_types_seen'])}")
        print(f"📁 日志保存位置: {log_dir}")
        
        return summary


def run_multiple_tests():
    """运行多个测试用例"""
    test_cases = [
        {
            "name": "simple_query",
            "input": "推荐北京的景点",
            "description": "简单景点推荐查询"
        },
        {
            "name": "complex_planning",
            "input": "我想要一个3天的北京旅游计划，包括故宫、天坛、颐和园",
            "description": "复杂旅游规划查询"
        },
        {
            "name": "detailed_request",
            "input": "我和女朋友计划下个月去杭州玩3天，预算3000元，喜欢历史文化和美食，请帮我制定详细的旅游计划",
            "description": "详细需求的旅游规划"
        }
    ]
    
    print("🎯 开始批量测试流式API")
    print(f"📋 共 {len(test_cases)} 个测试用例")
    
    all_summaries = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"🧪 测试用例 {i}/{len(test_cases)}: {test_case['description']}")
        print(f"{'='*80}")
        
        try:
            summary = test_stream_api_with_logging(
                user_input=test_case["input"],
                test_name=test_case["name"]
            )
            all_summaries.append({
                "test_case": test_case,
                "summary": summary
            })
            
            print(f"✅ 测试用例 {i} 完成")
            
        except Exception as e:
            print(f"❌ 测试用例 {i} 失败: {str(e)}")
            all_summaries.append({
                "test_case": test_case,
                "error": str(e)
            })
        
        # 测试间隔
        if i < len(test_cases):
            print("\n⏳ 等待5秒后开始下一个测试...")
            time.sleep(5)
    
    # 生成总体报告
    generate_overall_report(all_summaries)
    
    return all_summaries


def generate_overall_report(all_summaries: List[Dict[str, Any]]):
    """生成总体测试报告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"stream_test_logs/overall_report_{timestamp}.json"
    
    # 创建目录
    os.makedirs("stream_test_logs", exist_ok=True)
    
    # 计算统计信息
    successful_tests = [s for s in all_summaries if "summary" in s]
    failed_tests = [s for s in all_summaries if "error" in s]
    
    total_chunks = sum(s["summary"]["data_statistics"]["total_chunks"] for s in successful_tests)
    total_data_size = sum(s["summary"]["data_statistics"]["total_data_size_bytes"] for s in successful_tests)
    
    report = {
        "test_overview": {
            "timestamp": timestamp,
            "total_tests": len(all_summaries),
            "successful_tests": len(successful_tests),
            "failed_tests": len(failed_tests),
            "success_rate": len(successful_tests) / len(all_summaries) * 100 if all_summaries else 0
        },
        "aggregate_statistics": {
            "total_chunks_across_all_tests": total_chunks,
            "total_data_size_bytes_across_all_tests": total_data_size,
            "average_chunks_per_test": total_chunks / len(successful_tests) if successful_tests else 0,
            "average_data_size_per_test": total_data_size / len(successful_tests) if successful_tests else 0
        },
        "detailed_results": all_summaries
    }
    
    # 保存报告
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 打印总体报告
    print(f"\n{'='*80}")
    print("📊 总体测试报告")
    print(f"{'='*80}")
    print(f"🧪 总测试数: {report['test_overview']['total_tests']}")
    print(f"✅ 成功测试: {report['test_overview']['successful_tests']}")
    print(f"❌ 失败测试: {report['test_overview']['failed_tests']}")
    print(f"📈 成功率: {report['test_overview']['success_rate']:.1f}%")
    print(f"📦 总数据块: {report['aggregate_statistics']['total_chunks_across_all_tests']}")
    print(f"📏 总数据量: {report['aggregate_statistics']['total_data_size_bytes_across_all_tests']} bytes")
    print(f"📄 报告文件: {report_file}")


def quick_test():
    """快速测试单个用例"""
    return test_stream_api_with_logging(
        user_input="推荐杭州的景点",
        test_name="quick_test"
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="流式API数据测试工具")
    parser.add_argument("--mode", choices=["quick", "single", "batch"], default="quick",
                       help="测试模式: quick(快速测试), single(单个测试), batch(批量测试)")
    parser.add_argument("--input", type=str, help="用户输入(single模式使用)")
    parser.add_argument("--name", type=str, default="custom_test", help="测试名称(single模式使用)")
    
    args = parser.parse_args()
    
    if args.mode == "quick":
        print("🚀 运行快速测试...")
        quick_test()
    elif args.mode == "single":
        if not args.input:
            print("❌ single模式需要提供 --input 参数")
            sys.exit(1)
        print(f"🚀 运行单个测试: {args.name}")
        test_stream_api_with_logging(args.input, args.name)
    elif args.mode == "batch":
        print("🚀 运行批量测试...")
        run_multiple_tests()
    
    print("\n🎉 测试完成！")
