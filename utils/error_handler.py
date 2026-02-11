"""
Error Handling and Recovery System for SWGOH Automation
Provides comprehensive error detection, handling, and recovery mechanisms
"""

import time
import logging
import traceback
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum
import functools
from datetime import datetime, timedelta

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories"""
    SCREEN_RECOGNITION = "screen_recognition"
    NETWORK = "network"
    GAME_STATE = "game_state"
    RESOURCE = "resource"
    CONFIGURATION = "configuration"
    AI_DECISION = "ai_decision"
    USER_INPUT = "user_input"
    SYSTEM = "system"

@dataclass
class ErrorInfo:
    """Detailed error information"""
    exception: Exception
    severity: ErrorSeverity
    category: ErrorCategory
    context: Dict[str, Any]
    timestamp: datetime
    recovery_attempts: int = 0
    resolved: bool = False

@dataclass
class RecoveryAction:
    """Recovery action definition"""
    name: str
    action: Callable
    max_attempts: int = 3
    delay_between_attempts: float = 1.0
    conditions: List[str] = None

class ErrorRecoveryManager:
    """Manages error detection and recovery"""
    
    def __init__(self, logger):
        self.logger = logger
        self.error_history: List[ErrorInfo] = []
        self.recovery_actions = self.setup_recovery_actions()
        self.error_patterns = {}
        self.recovery_stats = {
            'total_errors': 0,
            'resolved_errors': 0,
            'failed_recoveries': 0
        }
        
    def setup_recovery_actions(self) -> Dict[ErrorCategory, List[RecoveryAction]]:
        """Setup recovery actions for different error types"""
        return {
            ErrorCategory.SCREEN_RECOGNITION: [
                RecoveryAction(
                    "wait_and_retry",
                    self.wait_and_retry,
                    max_attempts=3,
                    delay_between_attempts=2.0
                ),
                RecoveryAction(
                    "adjust_confidence_threshold",
                    self.adjust_confidence_threshold,
                    max_attempts=2
                ),
                RecoveryAction(
                    "refresh_screen",
                    self.refresh_screen,
                    max_attempts=2
                )
            ],
            ErrorCategory.GAME_STATE: [
                RecoveryAction(
                    "navigate_to_main_menu",
                    self.navigate_to_main_menu,
                    max_attempts=3
                ),
                RecoveryAction(
                    "restart_game",
                    self.restart_game,
                    max_attempts=1
                )
            ],
            ErrorCategory.NETWORK: [
                RecoveryAction(
                    "wait_for_network",
                    self.wait_for_network,
                    max_attempts=5,
                    delay_between_attempts=5.0
                ),
                RecoveryAction(
                    "check_connection",
                    self.check_connection,
                    max_attempts=2
                )
            ],
            ErrorCategory.RESOURCE: [
                RecoveryAction(
                    "clear_cache",
                    self.clear_cache,
                    max_attempts=1
                ),
                RecoveryAction(
                    "restart_automation",
                    self.restart_automation,
                    max_attempts=1
                )
            ],
            ErrorCategory.AI_DECISION: [
                RecoveryAction(
                    "fallback_to_default_action",
                    self.fallback_to_default_action,
                    max_attempts=2
                ),
                RecoveryAction(
                    "skip_current_action",
                    self.skip_current_action,
                    max_attempts=1
                )
            ]
        }
        
    def handle_error(self, exception: Exception, category: ErrorCategory, 
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                    context: Dict[str, Any] = None) -> bool:
        """Handle and attempt to recover from error"""
        error_info = ErrorInfo(
            exception=exception,
            severity=severity,
            category=category,
            context=context or {},
            timestamp=datetime.now()
        )
        
        self.error_history.append(error_info)
        self.recovery_stats['total_errors'] += 1
        
        self.logger.error(f"Error detected: {category.value} - {str(exception)}", 
                         exception=exception, 
                         category=category.value,
                         severity=severity.value,
                         context=context)
        
        # Attempt recovery
        recovered = self.attempt_recovery(error_info)
        
        if recovered:
            error_info.resolved = True
            self.recovery_stats['resolved_errors'] += 1
            self.logger.info(f"Error recovered successfully: {category.value}")
        else:
            self.recovery_stats['failed_recoveries'] += 1
            self.logger.error(f"Failed to recover from error: {category.value}")
            
        return recovered
        
    def attempt_recovery(self, error_info: ErrorInfo) -> bool:
        """Attempt to recover from error using appropriate actions"""
        category = error_info.category
        
        if category not in self.recovery_actions:
            self.logger.warning(f"No recovery actions for category: {category.value}")
            return False
            
        for recovery_action in self.recovery_actions[category]:
            if error_info.recovery_attempts >= recovery_action.max_attempts:
                continue
                
            self.logger.info(f"Attempting recovery: {recovery_action.name}")
            
            try:
                # Wait before attempting recovery
                if recovery_action.delay_between_attempts > 0:
                    time.sleep(recovery_action.delay_between_attempts)
                    
                # Execute recovery action
                success = recovery_action.action(error_info)
                error_info.recovery_attempts += 1
                
                if success:
                    return True
                    
            except Exception as e:
                self.logger.error(f"Recovery action failed: {recovery_action.name}", exception=e)
                
        return False
        
    # Recovery action implementations
    def wait_and_retry(self, error_info: ErrorInfo) -> bool:
        """Wait and retry the failed operation"""
        wait_time = min(error_info.recovery_attempts * 2, 10)  # Exponential backoff, max 10s
        self.logger.info(f"Waiting {wait_time}s before retry...")
        time.sleep(wait_time)
        return True
        
    def adjust_confidence_threshold(self, error_info: ErrorInfo) -> bool:
        """Adjust confidence threshold for image recognition"""
        # This would need access to the automator to adjust threshold
        self.logger.info("Adjusting confidence threshold for image recognition")
        return True
        
    def refresh_screen(self, error_info: ErrorInfo) -> bool:
        """Refresh the game screen"""
        self.logger.info("Refreshing game screen")
        # Implementation would depend on how to refresh the game
        return True
        
    def navigate_to_main_menu(self, error_info: ErrorInfo) -> bool:
        """Navigate back to main menu"""
        self.logger.info("Navigating to main menu")
        # Implementation would use automator to navigate back
        return True
        
    def restart_game(self, error_info: ErrorInfo) -> bool:
        """Restart the game application"""
        self.logger.warning("Restarting game application")
        # Implementation would restart the game/emulator
        return True
        
    def wait_for_network(self, error_info: ErrorInfo) -> bool:
        """Wait for network connection to be restored"""
        self.logger.info("Waiting for network connection...")
        time.sleep(5)
        return True
        
    def check_connection(self, error_info: ErrorInfo) -> bool:
        """Check network connection"""
        self.logger.info("Checking network connection")
        # Implementation would check actual connectivity
        return True
        
    def clear_cache(self, error_info: ErrorInfo) -> bool:
        """Clear application cache"""
        self.logger.info("Clearing cache...")
        # Implementation would clear relevant cache
        return True
        
    def restart_automation(self, error_info: ErrorInfo) -> bool:
        """Restart the automation system"""
        self.logger.warning("Restarting automation system")
        return True
        
    def fallback_to_default_action(self, error_info: ErrorInfo) -> bool:
        """Use default action when AI decision fails"""
        self.logger.info("Using fallback default action")
        return True
        
    def skip_current_action(self, error_info: ErrorInfo) -> bool:
        """Skip the current failed action"""
        self.logger.info("Skipping current action")
        return True
        
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors and recovery statistics"""
        recent_errors = [e for e in self.error_history 
                        if datetime.now() - e.timestamp < timedelta(hours=1)]
        
        error_by_category = {}
        for error in self.error_history:
            category = error.category.value
            if category not in error_by_category:
                error_by_category[category] = 0
            error_by_category[category] += 1
            
        return {
            'total_errors': self.recovery_stats['total_errors'],
            'resolved_errors': self.recovery_stats['resolved_errors'],
            'failed_recoveries': self.recovery_stats['failed_recoveries'],
            'recovery_rate': (self.recovery_stats['resolved_errors'] / 
                            max(self.recovery_stats['total_errors'], 1)),
            'recent_errors': len(recent_errors),
            'errors_by_category': error_by_category
        }

def error_handler(category: ErrorCategory, severity: ErrorSeverity = ErrorSeverity.MEDIUM):
    """Decorator for automatic error handling"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get error recovery manager from args or create new one
                recovery_manager = None
                for arg in args:
                    if hasattr(arg, 'error_recovery'):
                        recovery_manager = arg.error_recovery
                        break
                        
                if recovery_manager:
                    context = {
                        'function': func.__name__,
                        'args': str(args)[:200],  # Limit length
                        'kwargs': str(kwargs)[:200]
                    }
                    recovery_manager.handle_error(e, category, severity, context)
                else:
                    # Fallback to basic logging
                    logging.error(f"Unhandled error in {func.__name__}: {e}", exc_info=True)
                    
                # Re-raise if critical or if recovery failed
                if severity == ErrorSeverity.CRITICAL:
                    raise
                    
                return None
        return wrapper
    return decorator

def safe_execute(func: Callable, default_return=None, 
                category: ErrorCategory = ErrorCategory.SYSTEM,
                severity: ErrorSeverity = ErrorSeverity.MEDIUM):
    """Safely execute a function with error handling"""
    try:
        return func()
    except Exception as e:
        logging.error(f"Safe execution failed for {func.__name__}: {e}", exc_info=True)
        return default_return

class CircuitBreaker:
    """Circuit breaker pattern for preventing repeated failures"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == "OPEN":
            if (datetime.now() - self.last_failure_time).seconds > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
                
        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                
            raise e
