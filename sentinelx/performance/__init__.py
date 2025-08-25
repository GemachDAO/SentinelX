"""
Performance monitoring and optimization tools for SentinelX.
Provides profiling, benchmarking, and performance analysis capabilities.
"""
from __future__ import annotations
import time
import asyncio
import cProfile
import pstats
import io
import gc
import threading
import functools
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from ..core.utils import logger

# Optional dependencies with graceful fallback
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

try:
    import memory_profiler
    MEMORY_PROFILER_AVAILABLE = True
except ImportError:
    MEMORY_PROFILER_AVAILABLE = False
    memory_profiler = None

try:
    import line_profiler
    LINE_PROFILER_AVAILABLE = True
except ImportError:
    LINE_PROFILER_AVAILABLE = False
    line_profiler = None

@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    execution_time: float
    cpu_usage: Dict[str, float]
    memory_usage: Dict[str, float]
    disk_io: Dict[str, int] = field(default_factory=dict)
    network_io: Dict[str, int] = field(default_factory=dict)
    function_stats: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    
class PerformanceProfiler:
    """Advanced performance profiler for SentinelX tasks."""
    
    def __init__(self):
        if PSUTIL_AVAILABLE:
            self.process = psutil.Process()
        else:
            self.process = None
        self.baseline_metrics = None
        self._profiling_data = {}
    
    @contextmanager
    def profile_context(self, name: str = "default"):
        """Context manager for profiling code blocks."""
        start_time = time.perf_counter()
        
        # CPU and memory tracking only if psutil is available
        if self.process:
            start_cpu = self.process.cpu_percent()
            start_memory = self.process.memory_info()
        else:
            start_cpu = 0
            start_memory = type('MockMemInfo', (), {'rss': 0})()
        
        # Enable garbage collection tracking
        gc_before = gc.get_stats()
        
        try:
            yield
        finally:
            end_time = time.perf_counter()
            
            if self.process:
                end_cpu = self.process.cpu_percent()
                end_memory = self.process.memory_info()
            else:
                end_cpu = 0
                end_memory = type('MockMemInfo', (), {'rss': 0})()
            
            gc_after = gc.get_stats()
            
            metrics = PerformanceMetrics(
                execution_time=end_time - start_time,
                cpu_usage={
                    "start": start_cpu,
                    "end": end_cpu,
                    "average": (start_cpu + end_cpu) / 2
                },
                memory_usage={
                    "start_rss": start_memory.rss,
                    "end_rss": end_memory.rss,
                    "peak_rss": end_memory.rss,
                    "delta_rss": end_memory.rss - start_memory.rss
                }
            )
            
            self._profiling_data[name] = metrics
            logger.info(f"Profile '{name}': {metrics.execution_time:.3f}s, "
                       f"Memory delta: {metrics.memory_usage['delta_rss']:,} bytes")

    def profile_function(self, func: Callable, *args, **kwargs) -> tuple[Any, PerformanceMetrics]:
        """Profile a single function call."""
        profiler = cProfile.Profile()
        
        start_time = time.perf_counter()
        if self.process:
            start_memory = self.process.memory_info()
        else:
            start_memory = type('MockMemInfo', (), {'rss': 0})()
        
        profiler.enable()
        try:
            result = func(*args, **kwargs)
        finally:
            profiler.disable()
        
        end_time = time.perf_counter()
        if self.process:
            end_memory = self.process.memory_info()
            cpu_percent = self.process.cpu_percent()
        else:
            end_memory = type('MockMemInfo', (), {'rss': 0})()
            cpu_percent = 0
        
        # Analyze profiler stats
        stats_stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stats_stream)
        stats.sort_stats('tottime')
        stats.print_stats(20)  # Top 20 functions
        
        metrics = PerformanceMetrics(
            execution_time=end_time - start_time,
            cpu_usage={"total": cpu_percent},
            memory_usage={
                "start": start_memory.rss,
                "end": end_memory.rss,
                "delta": end_memory.rss - start_memory.rss
            },
            function_stats={
                "profile_output": stats_stream.getvalue(),
                "total_calls": stats.total_calls,
                "primitive_calls": stats.prim_calls
            }
        )
        
        return result, metrics
    
    async def profile_async_function(self, coro: Callable, *args, **kwargs) -> tuple[Any, PerformanceMetrics]:
        """Profile an async function."""
        start_time = time.perf_counter()
        if self.process:
            start_memory = self.process.memory_info()
        else:
            start_memory = type('MockMemInfo', (), {'rss': 0})()
        
        result = await coro(*args, **kwargs)
        
        end_time = time.perf_counter()
        if self.process:
            end_memory = self.process.memory_info()
            cpu_percent = self.process.cpu_percent()
        else:
            end_memory = type('MockMemInfo', (), {'rss': 0})()
            cpu_percent = 0
        
        metrics = PerformanceMetrics(
            execution_time=end_time - start_time,
            cpu_usage={"total": cpu_percent},
            memory_usage={
                "start": start_memory.rss,
                "end": end_memory.rss,
                "delta": end_memory.rss - start_memory.rss
            }
        )
        
        return result, metrics
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics."""
        if not PSUTIL_AVAILABLE:
            return {
                "cpu": {"percent": 0, "count": 1, "freq": None},
                "memory": {"virtual": {}, "swap": {}},
                "disk": {},
                "network": {},
                "process": {},
                "note": "psutil not available - limited metrics"
            }
        
        return {
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            "memory": {
                "virtual": psutil.virtual_memory()._asdict(),
                "swap": psutil.swap_memory()._asdict()
            },
            "disk": {
                device.device: psutil.disk_usage(device.mountpoint)._asdict()
                for device in psutil.disk_partitions()
                if device.mountpoint
            },
            "network": {
                interface: stats._asdict()
                for interface, stats in psutil.net_io_counters(pernic=True).items()
            },
            "process": {
                "pid": self.process.pid if self.process else 0,
                "cpu_percent": self.process.cpu_percent() if self.process else 0,
                "memory_info": self.process.memory_info()._asdict() if self.process else {},
                "num_threads": self.process.num_threads() if self.process else 0,
                "open_files": len(self.process.open_files()) if self.process else 0,
                "connections": len(self.process.connections()) if self.process else 0
            }
        }
    
    def analyze_performance(self, metrics: PerformanceMetrics) -> List[str]:
        """Analyze metrics and provide optimization recommendations."""
        recommendations = []
        
        # Memory analysis
        if metrics.memory_usage.get("delta_rss", 0) > 100 * 1024 * 1024:  # 100MB
            recommendations.append("High memory usage detected. Consider using generators or processing data in chunks.")
        
        # CPU analysis  
        if metrics.cpu_usage.get("average", 0) > 80:
            recommendations.append("High CPU usage. Consider using async/await or multiprocessing for CPU-bound tasks.")
        
        # Execution time analysis
        if metrics.execution_time > 30:  # 30 seconds
            recommendations.append("Long execution time. Consider adding progress indicators and timeout handling.")
        
        # Function profiling analysis
        if "profile_output" in metrics.function_stats:
            output = metrics.function_stats["profile_output"]
            if "time.sleep" in output:
                recommendations.append("Sleep calls detected. Consider using async sleep for better concurrency.")
            if "requests.get" in output or "urllib" in output:
                recommendations.append("Synchronous HTTP calls detected. Consider using aiohttp for better performance.")
        
        return recommendations

class PerformanceOptimizer:
    """Automatic performance optimization utilities."""
    
    def __init__(self):
        self.profiler = PerformanceProfiler()
        self._optimization_cache = {}
    
    def memoize(self, maxsize: int = 128):
        """Decorator for caching function results."""
        def decorator(func):
            cache = {}
            cache_order = []
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Create cache key
                key = str(args) + str(sorted(kwargs.items()))
                
                if key in cache:
                    return cache[key]
                
                result = func(*args, **kwargs)
                
                # Manage cache size
                if len(cache) >= maxsize:
                    oldest_key = cache_order.pop(0)
                    del cache[oldest_key]
                
                cache[key] = result
                cache_order.append(key)
                return result
            
            wrapper.cache_info = lambda: {"hits": 0, "misses": 0, "maxsize": maxsize, "currsize": len(cache)}
            wrapper.cache_clear = lambda: (cache.clear(), cache_order.clear())
            return wrapper
        return decorator
    
    def async_timeout(self, timeout: float):
        """Decorator to add timeout to async functions."""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
                except asyncio.TimeoutError:
                    logger.warning(f"Function {func.__name__} timed out after {timeout}s")
                    raise
            return wrapper
        return decorator
    
    def parallel_execution(self, max_workers: int = None, use_processes: bool = False):
        """Decorator for parallel execution of function calls."""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(items: List[Any], *args, **kwargs):
                executor_class = ProcessPoolExecutor if use_processes else ThreadPoolExecutor
                
                with executor_class(max_workers=max_workers) as executor:
                    futures = [
                        executor.submit(func, item, *args, **kwargs)
                        for item in items
                    ]
                    results = [future.result() for future in futures]
                
                return results
            return wrapper
        return decorator
    
    def profile_and_optimize(self, func: Callable):
        """Decorator that profiles function and suggests optimizations."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result, metrics = self.profiler.profile_function(func, *args, **kwargs)
            recommendations = self.profiler.analyze_performance(metrics)
            
            if recommendations:
                logger.info(f"Performance recommendations for {func.__name__}:")
                for rec in recommendations:
                    logger.info(f"  - {rec}")
            
            return result
        return wrapper

class BenchmarkSuite:
    """Benchmark suite for SentinelX tasks and components."""
    
    def __init__(self):
        self.results = {}
        self.profiler = PerformanceProfiler()
    
    async def benchmark_task(self, task_name: str, task_func: Callable, iterations: int = 10) -> Dict[str, Any]:
        """Benchmark a task with multiple iterations."""
        logger.info(f"Benchmarking task '{task_name}' with {iterations} iterations...")
        
        execution_times = []
        memory_deltas = []
        
        for i in range(iterations):
            with self.profiler.profile_context(f"{task_name}_iter_{i}"):
                if asyncio.iscoroutinefunction(task_func):
                    await task_func()
                else:
                    task_func()
            
            metrics = self.profiler._profiling_data[f"{task_name}_iter_{i}"]
            execution_times.append(metrics.execution_time)
            memory_deltas.append(metrics.memory_usage.get("delta_rss", 0))
        
        # Calculate statistics
        avg_time = sum(execution_times) / len(execution_times)
        min_time = min(execution_times)
        max_time = max(execution_times)
        avg_memory = sum(memory_deltas) / len(memory_deltas)
        
        benchmark_result = {
            "task_name": task_name,
            "iterations": iterations,
            "execution_time": {
                "average": avg_time,
                "min": min_time,
                "max": max_time,
                "total": sum(execution_times)
            },
            "memory_usage": {
                "average_delta": avg_memory,
                "max_delta": max(memory_deltas),
                "min_delta": min(memory_deltas)
            },
            "throughput": iterations / sum(execution_times),
            "system_metrics": self.profiler.get_system_metrics()
        }
        
        self.results[task_name] = benchmark_result
        return benchmark_result
    
    def generate_report(self, output_path: Optional[Path] = None) -> str:
        """Generate benchmark report."""
        report = ["# SentinelX Performance Benchmark Report\n"]
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if not self.results:
            report.append("No benchmark results available.\n")
            return "\n".join(report)
        
        # Summary table
        report.append("## Summary\n")
        report.append("| Task | Avg Time (s) | Min Time (s) | Max Time (s) | Throughput (ops/s) |")
        report.append("|------|--------------|--------------|--------------|-------------------|")
        
        for task_name, result in self.results.items():
            exec_time = result["execution_time"]
            report.append(
                f"| {task_name} | {exec_time['average']:.3f} | "
                f"{exec_time['min']:.3f} | {exec_time['max']:.3f} | "
                f"{result['throughput']:.2f} |"
            )
        
        report.append("\n")
        
        # Detailed results
        report.append("## Detailed Results\n")
        for task_name, result in self.results.items():
            report.append(f"### {task_name}\n")
            report.append(f"- **Iterations**: {result['iterations']}")
            report.append(f"- **Average Execution Time**: {result['execution_time']['average']:.3f}s")
            report.append(f"- **Memory Usage (avg)**: {result['memory_usage']['average_delta']:,} bytes")
            report.append(f"- **Throughput**: {result['throughput']:.2f} operations/second")
            report.append("")
        
        report_text = "\n".join(report)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(report_text)
            logger.info(f"Benchmark report saved to {output_path}")
        
        return report_text

# Export main classes
__all__ = [
    "PerformanceProfiler", 
    "PerformanceOptimizer", 
    "BenchmarkSuite", 
    "PerformanceMetrics"
]
