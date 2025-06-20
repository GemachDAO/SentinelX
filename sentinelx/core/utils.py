from __future__ import annotations
import json
import logging
import hashlib
import time
from datetime import datetime
from typing import Any, Dict, Optional, Union, List
from pathlib import Path
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)

# Audit log configuration
AUDIT_LOG_FILE = "sentinelx_audit.log"
audit_logger = logging.getLogger("sentinelx.audit")

def setup_audit_logging(log_file: str = AUDIT_LOG_FILE) -> None:
    """Set up audit logging to file."""
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    audit_logger.addHandler(handler)
    audit_logger.setLevel(logging.INFO)

def audit_log(message: str, **data: Any) -> None:
    """Log an audit event with structured data."""
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "message": message,
        "data": data
    }
    
    # Log to console (JSON format)
    print(json.dumps(entry))
    
    # Log to audit file if configured
    if audit_logger.handlers:
        audit_logger.info(json.dumps(entry))

def safe_dict_get(d: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get a value from a dictionary with dot notation support."""
    keys = key.split('.')
    value = d
    
    try:
        for k in keys:
            value = value[k]
        return value
    except (KeyError, TypeError, AttributeError):
        return default

def hash_data(data: Union[str, bytes, Dict[str, Any]]) -> str:
    """Generate SHA256 hash of data."""
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True)
    elif isinstance(data, str):
        data = data.encode('utf-8')
    
    return hashlib.sha256(data).hexdigest()

def sanitize_for_log(data: Any, sensitive_keys: Optional[List[str]] = None) -> Any:
    """Sanitize data for logging by masking sensitive information."""
    if sensitive_keys is None:
        sensitive_keys = [
            'password', 'token', 'key', 'secret', 'api_key', 
            'private_key', 'auth', 'credential', 'pass'
        ]
    
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            if any(sensitive in k.lower() for sensitive in sensitive_keys):
                sanitized[k] = "***REDACTED***"
            else:
                sanitized[k] = sanitize_for_log(v, sensitive_keys)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_for_log(item, sensitive_keys) for item in data]
    else:
        return data

def timing_decorator(func):
    """Decorator to measure and log function execution time."""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.debug(f"{func.__name__} completed in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} failed after {duration:.2f}s: {e}")
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.debug(f"{func.__name__} completed in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} failed after {duration:.2f}s: {e}")
            raise
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

def validate_file_path(path: Union[str, Path], must_exist: bool = True) -> Path:
    """Validate and return a Path object, with optional existence check."""
    path_obj = Path(path)
    
    if must_exist and not path_obj.exists():
        raise FileNotFoundError(f"File not found: {path_obj}")
    
    if must_exist and not path_obj.is_file():
        raise ValueError(f"Path is not a file: {path_obj}")
    
    return path_obj

def validate_directory_path(path: Union[str, Path], create: bool = False) -> Path:
    """Validate and return a directory Path object, optionally creating it."""
    path_obj = Path(path)
    
    if not path_obj.exists():
        if create:
            path_obj.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {path_obj}")
        else:
            raise FileNotFoundError(f"Directory not found: {path_obj}")
    
    if not path_obj.is_dir():
        raise ValueError(f"Path is not a directory: {path_obj}")
    
    return path_obj

def format_bytes(bytes_value: int) -> str:
    """Format bytes into human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"

def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.0f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

class ProgressTracker:
    """Simple progress tracking utility."""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
    
    def update(self, increment: int = 1) -> None:
        """Update progress by increment."""
        self.current += increment
        if self.current % max(1, self.total // 10) == 0:  # Log every 10%
            self._log_progress()
    
    def _log_progress(self) -> None:
        """Log current progress."""
        percentage = (self.current / self.total) * 100
        elapsed = time.time() - self.start_time
        
        if self.current > 0:
            eta = (elapsed / self.current) * (self.total - self.current)
            logger.info(f"{self.description}: {percentage:.1f}% ({self.current}/{self.total}) - ETA: {format_duration(eta)}")
        else:
            logger.info(f"{self.description}: {percentage:.1f}% ({self.current}/{self.total})")
    
    def finish(self) -> None:
        """Mark progress as finished."""
        self.current = self.total
        elapsed = time.time() - self.start_time
        logger.info(f"{self.description}: Completed in {format_duration(elapsed)}")

def retry_on_exception(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator to retry function on exception with exponential backoff."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"{func.__name__} attempt {attempt + 1} failed: {e}, retrying in {current_delay}s")
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"{func.__name__} failed after {max_retries + 1} attempts")
            
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"{func.__name__} attempt {attempt + 1} failed: {e}, retrying in {current_delay}s")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"{func.__name__} failed after {max_retries + 1} attempts")
            
            raise last_exception
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
