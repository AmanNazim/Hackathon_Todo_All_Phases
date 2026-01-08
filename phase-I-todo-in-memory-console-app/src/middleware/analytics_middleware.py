"""
Analytics Middleware for CLI Todo Application
T054: Create AnalyticsMiddleware for tracking command usage
"""
import time
from datetime import datetime
from typing import Dict, Any, Callable
from src.middleware.pipeline import MiddlewareResult, MiddlewareResultStatus


class AnalyticsMiddleware:
    """
    Middleware to track command usage and collect analytics
    Implements T054: Create AnalyticsMiddleware for tracking command usage
    """

    def __init__(self):
        self.name = "AnalyticsMiddleware"
        self.command_stats = {}
        self.performance_stats = {}
        self.interaction_patterns = {}
        self.system_health_indicators = {}
        self.session_start_time = datetime.now()

    def process(self, data: Dict[str, Any], next_middleware: Callable) -> MiddlewareResult:
        """
        Process the input data by tracking analytics and metadata
        """
        # Get the intent for tracking
        intent = data.get('intent', 'unknown')

        # Track command execution
        self._track_command_stats(intent)

        # Record start time for performance tracking
        start_time = time.time()

        # Process with the next middleware in the chain
        result = next_middleware(data)

        # Calculate and record performance metrics
        duration = (time.time() - start_time) * 1000  # Convert to milliseconds
        self._track_performance_stats(intent, duration)

        # Update the data with analytics information
        if 'analytics' not in data:
            data['analytics'] = {}

        data['analytics']['command_type'] = intent
        data['analytics']['execution_time_ms'] = duration
        data['analytics']['timestamp'] = datetime.now().isoformat()

        # Update system health indicators
        self._update_system_health(result)

        return result

    def _track_command_stats(self, intent: str):
        """
        Track command execution statistics
        """
        if intent not in self.command_stats:
            self.command_stats[intent] = {
                'count': 0,
                'first_used': datetime.now().isoformat(),
                'last_used': datetime.now().isoformat()
            }

        self.command_stats[intent]['count'] += 1
        self.command_stats[intent]['last_used'] = datetime.now().isoformat()

    def _track_performance_stats(self, intent: str, duration: float):
        """
        Track performance metrics for command execution
        """
        if intent not in self.performance_stats:
            self.performance_stats[intent] = {
                'execution_times': [],
                'average_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'total_calls': 0
            }

        stats = self.performance_stats[intent]
        stats['execution_times'].append(duration)
        stats['total_calls'] += 1

        # Update min/max
        stats['min_time'] = min(stats['min_time'], duration)
        stats['max_time'] = max(stats['max_time'], duration)

        # Recalculate average
        stats['average_time'] = sum(stats['execution_times']) / len(stats['execution_times'])

    def _update_system_health(self, result: MiddlewareResult):
        """
        Update system health indicators based on processing result
        """
        # Track overall health metrics
        if 'overall' not in self.system_health_indicators:
            self.system_health_indicators['overall'] = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'error_rate': 0
            }

        overall = self.system_health_indicators['overall']
        overall['total_requests'] += 1

        if result.status == MiddlewareResultStatus.SUCCESS:
            overall['successful_requests'] += 1
        else:
            overall['failed_requests'] += 1

        # Update error rate
        if overall['total_requests'] > 0:
            overall['error_rate'] = (overall['failed_requests'] / overall['total_requests']) * 100

    def get_command_statistics(self) -> Dict[str, Any]:
        """
        Get command usage statistics
        """
        return self.command_stats.copy()

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for all commands
        """
        return self.performance_stats.copy()

    def get_interaction_patterns(self) -> Dict[str, Any]:
        """
        Get interaction pattern statistics
        """
        return self.interaction_patterns.copy()

    def get_system_health(self) -> Dict[str, Any]:
        """
        Get system health indicators
        """
        return self.system_health_indicators.copy()

    def get_session_analytics(self) -> Dict[str, Any]:
        """
        Get analytics for the current session
        """
        return {
            'session_duration': str(datetime.now() - self.session_start_time),
            'total_commands_executed': sum(stat['count'] for stat in self.command_stats.values()),
            'command_distribution': {cmd: stat['count'] for cmd, stat in self.command_stats.items()},
            'performance_overview': {
                cmd: {
                    'avg_time': stat['average_time'],
                    'min_time': stat['min_time'],
                    'max_time': stat['max_time'],
                    'calls': stat['total_calls']
                } for cmd, stat in self.performance_stats.items()
            },
            'system_health': self.get_system_health()
        }

    def reset_session_analytics(self):
        """
        Reset analytics for a new session
        """
        self.command_stats = {}
        self.performance_stats = {}
        self.interaction_patterns = {}
        self.system_health_indicators = {}
        self.session_start_time = datetime.now()