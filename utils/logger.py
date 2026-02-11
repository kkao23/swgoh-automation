"""
Enhanced Logging System for SWGOH Automation
Provides comprehensive logging with error tracking and performance monitoring
"""

import logging
import logging.handlers
import os
import sys
import time
import traceback
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: datetime
    level: str
    message: str
    module: str
    function: str
    line: int
    extra_data: Dict[str, Any] = None

class SWGOHLogger:
    """Enhanced logger for SWGOH automation"""
    
    def __init__(self, name: str = "swgoh_bot", log_dir: str = "logs"):
        self.name = name
        self.log_dir = log_dir
        self.logger = self.setup_logger()
        self.error_count = 0
        self.warning_count = 0
        self.session_start = datetime.now()
        self.performance_data = {}
        
    def setup_logger(self) -> logging.Logger:
        """Setup comprehensive logging configuration"""
        # Create log directory
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create logger
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File handlers
        # Main log file with rotation
        main_handler = logging.handlers.RotatingFileHandler(
            os.path.join(self.log_dir, f"{self.name}.log"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        main_handler.setLevel(logging.INFO)
        main_handler.setFormatter(detailed_formatter)
        logger.addHandler(main_handler)
        
        # Error log file
        error_handler = logging.handlers.RotatingFileHandler(
            os.path.join(self.log_dir, f"{self.name}_errors.log"),
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        logger.addHandler(error_handler)
        
        # Performance log file
        perf_handler = logging.handlers.RotatingFileHandler(
            os.path.join(self.log_dir, f"{self.name}_performance.log"),
            maxBytes=5*1024*1024,  # 5MB
            backupCount=2,
            encoding='utf-8'
        )
        perf_handler.setLevel(logging.DEBUG)
        perf_handler.setFormatter(detailed_formatter)
        logger.addHandler(perf_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
        
        return logger
        
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log(logging.DEBUG, message, **kwargs)
        
    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log(logging.INFO, message, **kwargs)
        
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.warning_count += 1
        self._log(logging.WARNING, message, **kwargs)
        
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs):
        """Log error message with exception details"""
        self.error_count += 1
        
        if exception:
            kwargs['exception_type'] = type(exception).__name__
            kwargs['exception_message'] = str(exception)
            kwargs['traceback'] = traceback.format_exc()
            message += f" - Exception: {type(exception).__name__}: {str(exception)}"
            
        self._log(logging.ERROR, message, **kwargs)
        
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._log(logging.CRITICAL, message, **kwargs)
        
    def _log(self, level: int, message: str, **kwargs):
        """Internal logging method"""
        # Get caller information
        frame = sys._getframe(2)  # Go up 2 frames to get actual caller
        module = frame.f_globals.get('__name__', 'unknown')
        function = frame.f_code.co_name
        line = frame.f_lineno
        
        # Create log entry
        log_entry = LogEntry(
            timestamp=datetime.now(),
            level=logging.getLevelName(level),
            message=message,
            module=module,
            function=function,
            line=line,
            extra_data=kwargs
        )
        
        # Log with extra data
        extra = {'extra_data': kwargs} if kwargs else {}
        self.logger.log(level, message, extra=extra)
        
        # Store performance data if provided
        if 'duration' in kwargs:
            self.record_performance(module, function, kwargs['duration'])
            
    def record_performance(self, module: str, function: str, duration: float):
        """Record performance metrics"""
        key = f"{module}.{function}"
        if key not in self.performance_data:
            self.performance_data[key] = []
            
        self.performance_data[key].append({
            'timestamp': datetime.now(),
            'duration': duration
        })
        
        # Keep only last 100 entries per function
        if len(self.performance_data[key]) > 100:
            self.performance_data[key] = self.performance_data[key][-100:]
            
    def log_action_start(self, action: str, **kwargs):
        """Log the start of an action"""
        self.info(f"Starting action: {action}", action=action, start_time=time.time(), **kwargs)
        
    def log_action_end(self, action: str, success: bool, **kwargs):
        """Log the end of an action"""
        duration = kwargs.pop('duration', None)
        if duration is None and 'start_time' in kwargs:
            duration = time.time() - kwargs['start_time']
            
        status = "SUCCESS" if success else "FAILED"
        self.info(f"Action {action} {status}", action=action, success=success, duration=duration, **kwargs)
        
    def log_screenshot(self, purpose: str, file_path: str = None):
        """Log screenshot capture"""
        if file_path:
            self.debug(f"Screenshot captured: {purpose}", purpose=purpose, file_path=file_path)
        else:
            self.debug(f"Screenshot captured: {purpose}", purpose=purpose)
            
    def log_ai_decision(self, decision: str, confidence: float, context: Dict = None):
        """Log AI decision making"""
        self.info(f"AI Decision: {decision}", 
                decision=decision, 
                confidence=confidence, 
                context=context or {})
                
    def log_energy_state(self, energy_type: str, current: int, maximum: int):
        """Log energy state"""
        percentage = (current / maximum * 100) if maximum > 0 else 0
        self.debug(f"Energy state - {energy_type}: {current}/{maximum} ({percentage:.1f}%)",
                   energy_type=energy_type, current=current, maximum=maximum, percentage=percentage)
                   
    def log_battle_result(self, mode: str, stage: str, victory: bool, stars: int, duration: float):
        """Log battle result"""
        self.info(f"Battle {mode} {stage} - {'Victory' if victory else 'Defeat'} ({stars} stars, {duration:.1f}s)",
                mode=mode, stage=stage, victory=victory, stars=stars, duration=duration)
                
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        duration = datetime.now() - self.session_start
        
        # Calculate performance stats
        performance_summary = {}
        for key, entries in self.performance_data.items():
            if entries:
                durations = [e['duration'] for e in entries]
                performance_summary[key] = {
                    'count': len(entries),
                    'avg_duration': sum(durations) / len(durations),
                    'min_duration': min(durations),
                    'max_duration': max(durations)
                }
                
        return {
            'session_duration': str(duration),
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'performance_summary': performance_summary
        }
        
    def save_session_report(self):
        """Save detailed session report"""
        stats = self.get_session_stats()
        
        report = {
            'session_info': {
                'start_time': self.session_start.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration_seconds': (datetime.now() - self.session_start).total_seconds()
            },
            'statistics': stats,
            'errors': self.error_count,
            'warnings': self.warning_count
        }
        
        report_file = os.path.join(self.log_dir, f"session_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            self.info(f"Session report saved: {report_file}")
        except Exception as e:
            self.error(f"Failed to save session report: {e}")
            
    def cleanup_old_logs(self, days_to_keep: int = 7):
        """Clean up old log files"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        try:
            for filename in os.listdir(self.log_dir):
                file_path = os.path.join(self.log_dir, filename)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < cutoff_date:
                        os.remove(file_path)
                        self.info(f"Cleaned up old log file: {filename}")
        except Exception as e:
            self.error(f"Failed to cleanup old logs: {e}")

class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self, logger: SWGOHLogger, operation: str):
        self.logger = logger
        self.operation = operation
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        self.logger.log_action_start(self.operation)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        success = exc_type is None
        
        if exc_type:
            self.logger.error(f"Operation {self.operation} failed: {exc_val}", 
                            exception=exc_val, duration=duration)
        else:
            self.logger.log_action_end(self.operation, True, duration=duration)

# Global logger instance
swgoh_logger = SWGOHLogger()
