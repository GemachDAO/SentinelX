"""
Test suite for SentinelX performance monitoring and optimization functionality.
"""
import pytest
import time
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Test the conditional import behavior
try:
    from sentinelx.performance import (
        PerformanceProfiler, PerformanceOptimizer, BenchmarkSuite, 
        PerformanceMetrics
    )
    HAS_PERFORMANCE = True
except ImportError:
    HAS_PERFORMANCE = False

pytestmark = pytest.mark.skipif(not HAS_PERFORMANCE, reason="Performance module not available")

@pytest.fixture
def sample_metrics():
    """Fixture providing sample performance metrics."""
    return PerformanceMetrics(
        execution_time=1.5,
        cpu_usage={"start": 10.0, "end": 15.0, "average": 12.5},
        memory_usage={"start_rss": 1000000, "end_rss": 1200000, "delta_rss": 200000},
        disk_io={"read": 1024, "write": 512},
        network_io={"sent": 256, "received": 128}
    )

class TestPerformanceMetrics:
    """Test PerformanceMetrics data structure."""
    
    def test_metrics_initialization(self):
        """Test PerformanceMetrics initialization."""
        metrics = PerformanceMetrics(
            execution_time=2.0,
            cpu_usage={"average": 25.0},
            memory_usage={"delta_rss": 100000}
        )
        
        assert metrics.execution_time == 2.0
        assert metrics.cpu_usage["average"] == 25.0
        assert metrics.memory_usage["delta_rss"] == 100000
        assert isinstance(metrics.disk_io, dict)
        assert isinstance(metrics.network_io, dict)
        assert isinstance(metrics.function_stats, dict)
        assert isinstance(metrics.recommendations, list)
    
    def test_metrics_defaults(self, sample_metrics):
        """Test default values in metrics."""
        assert len(sample_metrics.recommendations) == 0
        assert isinstance(sample_metrics.function_stats, dict)

class TestPerformanceProfiler:
    """Test PerformanceProfiler functionality."""
    
    @patch('psutil.Process')
    def test_profiler_initialization(self, mock_process):
        """Test PerformanceProfiler initialization."""
        profiler = PerformanceProfiler()
        assert profiler.process is not None
        assert profiler.baseline_metrics is None
        assert isinstance(profiler._profiling_data, dict)
    
    @patch('psutil.Process')
    def test_profile_context(self, mock_process):
        """Test performance profiling context manager."""
        # Mock process methods
        mock_process_instance = Mock()
        mock_process_instance.cpu_percent.side_effect = [10.0, 15.0]
        mock_memory_info = Mock()
        mock_memory_info.rss = 1000000
        mock_process_instance.memory_info.side_effect = [mock_memory_info, mock_memory_info]
        mock_process.return_value = mock_process_instance
        
        profiler = PerformanceProfiler()
        
        with profiler.profile_context("test_operation"):
            time.sleep(0.1)  # Simulate some work
        
        assert "test_operation" in profiler._profiling_data
        metrics = profiler._profiling_data["test_operation"]
        assert metrics.execution_time > 0
        assert "start" in metrics.cpu_usage
        assert "end" in metrics.cpu_usage
    
    @patch('psutil.Process')
    def test_profile_function(self, mock_process):
        """Test function profiling."""
        # Mock process
        mock_process_instance = Mock()
        mock_process_instance.cpu_percent.return_value = 20.0
        mock_memory_info = Mock()
        mock_memory_info.rss = 1000000
        mock_process_instance.memory_info.return_value = mock_memory_info
        mock_process.return_value = mock_process_instance
        
        def test_function(x, y):
            return x + y
        
        profiler = PerformanceProfiler()
        result, metrics = profiler.profile_function(test_function, 5, 3)
        
        assert result == 8
        assert metrics.execution_time >= 0
        assert "total" in metrics.cpu_usage
        assert "start" in metrics.memory_usage
        assert "end" in metrics.memory_usage
        assert "profile_output" in metrics.function_stats
    
    @pytest.mark.asyncio
    @patch('psutil.Process')
    async def test_profile_async_function(self, mock_process):
        """Test async function profiling."""
        # Mock process
        mock_process_instance = Mock()
        mock_process_instance.cpu_percent.return_value = 25.0
        mock_memory_info = Mock()
        mock_memory_info.rss = 1000000
        mock_process_instance.memory_info.return_value = mock_memory_info
        mock_process.return_value = mock_process_instance
        
        async def async_test_function(delay):
            await asyncio.sleep(delay)
            return "completed"
        
        profiler = PerformanceProfiler()
        result, metrics = await profiler.profile_async_function(async_test_function, 0.01)
        
        assert result == "completed"
        assert metrics.execution_time >= 0.01
        assert "total" in metrics.cpu_usage
    
    @patch('psutil.cpu_percent')
    @patch('psutil.cpu_count')
    @patch('psutil.virtual_memory')
    @patch('psutil.swap_memory')
    @patch('psutil.disk_partitions')
    @patch('psutil.net_io_counters')
    @patch('psutil.Process')
    def test_get_system_metrics(self, mock_process, mock_net, mock_disk, 
                               mock_swap, mock_virtual, mock_cpu_count, mock_cpu_percent):
        """Test system metrics collection."""
        # Mock system metrics
        mock_cpu_percent.return_value = 30.0
        mock_cpu_count.return_value = 4
        
        mock_virtual_mem = Mock()
        mock_virtual_mem._asdict.return_value = {"total": 8000000000, "available": 4000000000}
        mock_virtual.return_value = mock_virtual_mem
        
        mock_swap_mem = Mock()
        mock_swap_mem._asdict.return_value = {"total": 2000000000, "used": 500000000}
        mock_swap.return_value = mock_swap_mem
        
        mock_disk.return_value = []
        mock_net.return_value = {}
        
        # Mock process
        mock_process_instance = Mock()
        mock_process_instance.pid = 1234
        mock_process_instance.cpu_percent.return_value = 15.0
        mock_memory_info = Mock()
        mock_memory_info._asdict.return_value = {"rss": 100000000, "vms": 200000000}
        mock_process_instance.memory_info.return_value = mock_memory_info
        mock_process_instance.num_threads.return_value = 5
        mock_process_instance.open_files.return_value = []
        mock_process_instance.connections.return_value = []
        mock_process.return_value = mock_process_instance
        
        profiler = PerformanceProfiler()
        metrics = profiler.get_system_metrics()
        
        assert "cpu" in metrics
        assert "memory" in metrics
        assert "process" in metrics
        assert metrics["cpu"]["percent"] == 30.0
        assert metrics["cpu"]["count"] == 4
    
    def test_analyze_performance_high_memory(self, sample_metrics):
        """Test performance analysis for high memory usage."""
        # Set high memory delta (200MB)
        sample_metrics.memory_usage["delta_rss"] = 200 * 1024 * 1024
        
        profiler = PerformanceProfiler()
        recommendations = profiler.analyze_performance(sample_metrics)
        
        assert len(recommendations) > 0
        assert any("memory usage" in rec.lower() for rec in recommendations)
    
    def test_analyze_performance_high_cpu(self, sample_metrics):
        """Test performance analysis for high CPU usage."""
        sample_metrics.cpu_usage["average"] = 85.0
        
        profiler = PerformanceProfiler()
        recommendations = profiler.analyze_performance(sample_metrics)
        
        assert len(recommendations) > 0
        assert any("cpu usage" in rec.lower() for rec in recommendations)
    
    def test_analyze_performance_long_execution(self, sample_metrics):
        """Test performance analysis for long execution time."""
        sample_metrics.execution_time = 45.0  # 45 seconds
        
        profiler = PerformanceProfiler()
        recommendations = profiler.analyze_performance(sample_metrics)
        
        assert len(recommendations) > 0
        assert any("execution time" in rec.lower() for rec in recommendations)
    
    def test_analyze_performance_sync_calls(self, sample_metrics):
        """Test performance analysis for synchronous calls."""
        sample_metrics.function_stats["profile_output"] = "requests.get called multiple times"
        
        profiler = PerformanceProfiler()
        recommendations = profiler.analyze_performance(sample_metrics)
        
        assert len(recommendations) > 0
        assert any("http calls" in rec.lower() for rec in recommendations)

class TestPerformanceOptimizer:
    """Test PerformanceOptimizer functionality."""
    
    def test_optimizer_initialization(self):
        """Test PerformanceOptimizer initialization."""
        optimizer = PerformanceOptimizer()
        assert optimizer.profiler is not None
        assert isinstance(optimizer._optimization_cache, dict)
    
    def test_memoize_decorator(self):
        """Test memoization decorator."""
        optimizer = PerformanceOptimizer()
        
        call_count = 0
        
        @optimizer.memoize(maxsize=2)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * x
        
        # First call
        result1 = expensive_function(5)
        assert result1 == 25
        assert call_count == 1
        
        # Second call with same args (should use cache)
        result2 = expensive_function(5)
        assert result2 == 25
        assert call_count == 1  # Not incremented
        
        # Third call with different args
        result3 = expensive_function(3)
        assert result3 == 9
        assert call_count == 2
        
        # Test cache info
        cache_info = expensive_function.cache_info()
        assert "maxsize" in cache_info
        assert cache_info["maxsize"] == 2
    
    def test_memoize_cache_limit(self):
        """Test memoization cache size limit."""
        optimizer = PerformanceOptimizer()
        
        @optimizer.memoize(maxsize=2)
        def test_function(x):
            return x * 2
        
        # Fill cache beyond limit
        test_function(1)
        test_function(2)
        test_function(3)  # Should evict first entry
        
        cache_info = test_function.cache_info()
        assert cache_info["currsize"] <= 2
    
    @pytest.mark.asyncio
    async def test_async_timeout_decorator(self):
        """Test async timeout decorator."""
        optimizer = PerformanceOptimizer()
        
        @optimizer.async_timeout(0.1)
        async def fast_function():
            await asyncio.sleep(0.05)
            return "completed"
        
        @optimizer.async_timeout(0.1)
        async def slow_function():
            await asyncio.sleep(0.2)
            return "should_timeout"
        
        # Fast function should complete
        result = await fast_function()
        assert result == "completed"
        
        # Slow function should timeout
        with pytest.raises(asyncio.TimeoutError):
            await slow_function()
    
    def test_parallel_execution_decorator(self):
        """Test parallel execution decorator."""
        optimizer = PerformanceOptimizer()
        
        @optimizer.parallel_execution(max_workers=2)
        def process_item(item):
            return item * 2
        
        items = [1, 2, 3, 4, 5]
        results = process_item(items)
        
        assert len(results) == 5
        assert results == [2, 4, 6, 8, 10]
    
    @patch('sentinelx.performance.PerformanceProfiler')
    def test_profile_and_optimize_decorator(self, mock_profiler_class):
        """Test profile and optimize decorator."""
        # Mock profiler
        mock_profiler = Mock()
        mock_metrics = Mock()
        mock_metrics.execution_time = 0.5
        mock_profiler.profile_function.return_value = ("result", mock_metrics)
        mock_profiler.analyze_performance.return_value = ["Use async/await"]
        mock_profiler_class.return_value = mock_profiler
        
        optimizer = PerformanceOptimizer()
        
        @optimizer.profile_and_optimize
        def test_function():
            return "test_result"
        
        with patch('sentinelx.performance.logger') as mock_logger:
            result = test_function()
            
            assert result == "result"
            mock_profiler.profile_function.assert_called_once()
            mock_profiler.analyze_performance.assert_called_once()

class TestBenchmarkSuite:
    """Test BenchmarkSuite functionality."""
    
    def test_benchmark_suite_initialization(self):
        """Test BenchmarkSuite initialization."""
        suite = BenchmarkSuite()
        assert isinstance(suite.results, dict)
        assert suite.profiler is not None
    
    @pytest.mark.asyncio
    @patch('sentinelx.performance.PerformanceProfiler')
    async def test_benchmark_task(self, mock_profiler_class):
        """Test task benchmarking."""
        # Mock profiler
        mock_profiler = Mock()
        mock_profiler._profiling_data = {}
        
        # Create mock metrics for iterations
        for i in range(3):
            mock_metrics = Mock()
            mock_metrics.execution_time = 0.1 + (i * 0.01)  # Varying times
            mock_metrics.memory_usage = {"delta_rss": 1000 * (i + 1)}
            mock_profiler._profiling_data[f"test_task_iter_{i}"] = mock_metrics
        
        mock_profiler.get_system_metrics.return_value = {"cpu": {"percent": 20.0}}
        mock_profiler_class.return_value = mock_profiler
        
        async def mock_task():
            await asyncio.sleep(0.01)
        
        suite = BenchmarkSuite()
        
        # Mock the context manager
        with patch.object(suite.profiler, 'profile_context') as mock_context:
            mock_context.return_value.__enter__ = Mock()
            mock_context.return_value.__exit__ = Mock()
            
            result = await suite.benchmark_task("test_task", mock_task, iterations=3)
        
        assert result["task_name"] == "test_task"
        assert result["iterations"] == 3
        assert "execution_time" in result
        assert "memory_usage" in result
        assert "throughput" in result
        assert "system_metrics" in result
    
    def test_generate_report_empty(self):
        """Test report generation with no results."""
        suite = BenchmarkSuite()
        report = suite.generate_report()
        
        assert "No benchmark results available" in report
    
    def test_generate_report_with_results(self):
        """Test report generation with results."""
        suite = BenchmarkSuite()
        
        # Add mock results
        suite.results["test_task"] = {
            "task_name": "test_task",
            "iterations": 5,
            "execution_time": {
                "average": 1.2,
                "min": 1.0,
                "max": 1.5,
                "total": 6.0
            },
            "memory_usage": {
                "average_delta": 50000,
                "max_delta": 60000,
                "min_delta": 40000
            },
            "throughput": 4.17
        }
        
        report = suite.generate_report()
        
        assert "# SentinelX Performance Benchmark Report" in report
        assert "test_task" in report
        assert "1.200" in report  # Average time
        assert "4.17" in report   # Throughput
    
    def test_generate_report_to_file(self):
        """Test report generation to file."""
        suite = BenchmarkSuite()
        suite.results["test_task"] = {
            "task_name": "test_task",
            "iterations": 1,
            "execution_time": {"average": 1.0, "min": 1.0, "max": 1.0, "total": 1.0},
            "memory_usage": {"average_delta": 1000, "max_delta": 1000, "min_delta": 1000},
            "throughput": 1.0
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as tmp_file:
            tmp_path = Path(tmp_file.name)
        
        try:
            report = suite.generate_report(tmp_path)
            
            # Check file was created and contains expected content
            assert tmp_path.exists()
            content = tmp_path.read_text()
            assert "test_task" in content
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

class TestPerformanceIntegration:
    """Integration tests for performance monitoring."""
    
    @pytest.mark.integration
    def test_real_function_profiling(self):
        """Test profiling a real function."""
        profiler = PerformanceProfiler()
        
        def cpu_intensive_task():
            # Simple CPU-intensive task
            total = 0
            for i in range(10000):
                total += i * i
            return total
        
        result, metrics = profiler.profile_function(cpu_intensive_task)
        
        assert result > 0  # Should return a sum
        assert metrics.execution_time > 0
        assert "profile_output" in metrics.function_stats
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_async_profiling(self):
        """Test profiling a real async function."""
        profiler = PerformanceProfiler()
        
        async def async_task():
            await asyncio.sleep(0.01)
            return "async_result"
        
        result, metrics = await profiler.profile_async_function(async_task)
        
        assert result == "async_result"
        assert metrics.execution_time >= 0.01
    
    def test_context_manager_real_usage(self):
        """Test context manager with real code."""
        profiler = PerformanceProfiler()
        
        with profiler.profile_context("real_operation"):
            # Simulate some work
            data = [i**2 for i in range(1000)]
            result = sum(data)
        
        assert "real_operation" in profiler._profiling_data
        metrics = profiler._profiling_data["real_operation"]
        assert metrics.execution_time > 0
