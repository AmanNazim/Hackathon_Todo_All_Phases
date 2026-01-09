"""
Metadata Injection System for CLI Todo Application
Implements T130-T134: Metadata Injection functionality
"""
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum
import statistics


class MetricType(Enum):
    """Types of metrics that can be collected"""
    COMMAND_EXECUTION_TIME = "command_execution_time"
    USER_INTERACTION_PATTERN = "user_interaction_pattern"
    PERFORMANCE_METRIC = "performance_metric"
    HEALTH_INDICATOR = "health_indicator"


@dataclass
class CommandMetrics:
    """Container for command execution metrics"""
    command_type: str
    execution_time_ms: float
    timestamp: datetime
    success: bool
    user_input_length: int = 0
    processing_overhead_ms: float = 0.0


@dataclass
class UserInteractionPatterns:
    """Container for user interaction pattern tracking"""
    user_id: str
    command_sequence: List[str] = field(default_factory=list)
    time_between_commands: List[float] = field(default_factory=list)
    preferred_command_style: str = "natural_language"  # "menu" or "natural_language"
    command_frequency_per_minute: float = 0.0
    most_used_commands: List[Tuple[str, int]] = field(default_factory=list)


@dataclass
class PerformanceMetrics:
    """Container for system performance metrics"""
    memory_usage_mb: float
    cpu_usage_percent: float
    response_time_ms: float
    throughput_commands_per_second: float
    timestamp: datetime


@dataclass
class HealthIndicators:
    """Container for system health indicators"""
    is_healthy: bool
    memory_pressure: str  # "low", "moderate", "high", "critical"
    response_time_status: str  # "fast", "normal", "slow", "delayed"
    error_rate: float
    uptime_seconds: float
    timestamp: datetime


class MetadataCollector:
    """Collects various types of metadata from the system"""

    def __init__(self, max_entries: int = 1000):
        self._max_entries = max_entries
        self._command_metrics: deque = deque(maxlen=max_entries)
        self._user_patterns: Dict[str, UserInteractionPatterns] = {}
        self._performance_metrics: deque = deque(maxlen=max_entries)
        self._health_indicators: deque = deque(maxlen=max_entries)

        # Statistics tracking
        self._command_stats: Dict[str, List[float]] = defaultdict(list)  # execution times by command type
        self._total_commands_executed = 0
        self._successful_commands = 0
        self._failed_commands = 0

        # Lock for thread safety
        self._lock = threading.RLock()

    def collect_command_execution_metadata(self, command_type: str, execution_time_ms: float,
                                         success: bool, user_input_length: int = 0) -> None:
        """Collect metadata for command execution"""
        with self._lock:
            # Create command metrics object
            command_metric = CommandMetrics(
                command_type=command_type,
                execution_time_ms=execution_time_ms,
                timestamp=datetime.now(),
                success=success,
                user_input_length=user_input_length,
                processing_overhead_ms=0.0  # This will be calculated separately
            )

            # Add to collection
            self._command_metrics.append(command_metric)

            # Update statistics
            self._command_stats[command_type].append(execution_time_ms)
            self._total_commands_executed += 1
            if success:
                self._successful_commands += 1
            else:
                self._failed_commands += 1

    def collect_user_interaction_pattern(self, user_id: str, command: str,
                                       time_since_last: Optional[float] = None) -> None:
        """Track user interaction patterns"""
        with self._lock:
            if user_id not in self._user_patterns:
                self._user_patterns[user_id] = UserInteractionPatterns(user_id=user_id)

            pattern = self._user_patterns[user_id]
            pattern.command_sequence.append(command)

            if time_since_last is not None:
                pattern.time_between_commands.append(time_since_last)

                # Calculate command frequency
                if len(pattern.time_between_commands) > 0:
                    avg_interval = statistics.mean(pattern.time_between_commands)
                    if avg_interval > 0:
                        pattern.command_frequency_per_minute = 60.0 / avg_interval

    def collect_performance_metrics(self, memory_usage_mb: float, cpu_usage_percent: float,
                                  response_time_ms: float, throughput_cps: float) -> None:
        """Collect system performance metrics"""
        with self._lock:
            perf_metric = PerformanceMetrics(
                memory_usage_mb=memory_usage_mb,
                cpu_usage_percent=cpu_usage_percent,
                response_time_ms=response_time_ms,
                throughput_commands_per_second=throughput_cps,
                timestamp=datetime.now()
            )

            self._performance_metrics.append(perf_metric)

    def collect_health_indicators(self, memory_pressure: str, response_time_status: str,
                                error_rate: float, uptime_seconds: float) -> None:
        """Collect system health indicators"""
        with self._lock:
            health_indicator = HealthIndicators(
                is_healthy=memory_pressure in ["low", "moderate"] and error_rate < 0.05,
                memory_pressure=memory_pressure,
                response_time_status=response_time_status,
                error_rate=error_rate,
                uptime_seconds=uptime_seconds,
                timestamp=datetime.now()
            )

            self._health_indicators.append(health_indicator)

    def get_command_execution_stats(self, command_type: Optional[str] = None) -> Dict[str, Any]:
        """Get command execution statistics"""
        with self._lock:
            if command_type:
                if command_type in self._command_stats and self._command_stats[command_type]:
                    times = self._command_stats[command_type]
                    return {
                        'avg_execution_time_ms': statistics.mean(times),
                        'min_execution_time_ms': min(times),
                        'max_execution_time_ms': max(times),
                        'std_deviation_ms': statistics.stdev(times) if len(times) > 1 else 0,
                        'count': len(times)
                    }
                else:
                    return {'avg_execution_time_ms': 0, 'count': 0}
            else:
                # Return stats for all command types
                all_stats = {}
                for cmd_type, times in self._command_stats.items():
                    if times:
                        all_stats[cmd_type] = {
                            'avg_execution_time_ms': statistics.mean(times),
                            'min_execution_time_ms': min(times),
                            'max_execution_time_ms': max(times),
                            'std_deviation_ms': statistics.stdev(times) if len(times) > 1 else 0,
                            'count': len(times)
                        }
                return all_stats

    def get_command_execution_timeline(self, limit: int = 50) -> List[CommandMetrics]:
        """Get recent command execution timeline"""
        with self._lock:
            return list(self._command_metrics)[-limit:]

    def get_user_interaction_pattern(self, user_id: str) -> Optional[UserInteractionPatterns]:
        """Get interaction pattern for a specific user"""
        with self._lock:
            return self._user_patterns.get(user_id)

    def get_all_user_patterns(self) -> Dict[str, UserInteractionPatterns]:
        """Get all user interaction patterns"""
        with self._lock:
            return self._user_patterns.copy()

    def get_performance_metrics(self, limit: int = 50) -> List[PerformanceMetrics]:
        """Get recent performance metrics"""
        with self._lock:
            return list(self._performance_metrics)[-limit:]

    def get_health_indicators(self, limit: int = 50) -> List[HealthIndicators]:
        """Get recent health indicators"""
        with self._lock:
            return list(self._health_indicators)[-limit:]

    def get_system_summary(self) -> Dict[str, Any]:
        """Get a summary of system metrics"""
        with self._lock:
            total_time = sum(sum(times) for times in self._command_stats.values())
            total_commands = sum(len(times) for times in self._command_stats.values())

            avg_response_time = total_time / total_commands if total_commands > 0 else 0

            return {
                'total_commands_executed': self._total_commands_executed,
                'successful_commands': self._successful_commands,
                'failed_commands': self._failed_commands,
                'success_rate': self._successful_commands / self._total_commands_executed if self._total_commands_executed > 0 else 0,
                'average_response_time_ms': avg_response_time,
                'unique_command_types': len(self._command_stats),
                'recent_command_count': len(self._command_metrics)
            }

    def clear_metadata(self) -> None:
        """Clear all collected metadata"""
        with self._lock:
            self._command_metrics.clear()
            self._user_patterns.clear()
            self._performance_metrics.clear()
            self._health_indicators.clear()
            self._command_stats.clear()
            self._total_commands_executed = 0
            self._successful_commands = 0
            self._failed_commands = 0


class MetadataInjectionSystem:
    """Main system for injecting metadata into the application flow"""

    def __init__(self, max_entries: int = 1000):
        self.collector = MetadataCollector(max_entries)
        self._enabled = True
        self._lock = threading.RLock()

    def enable_collection(self) -> None:
        """Enable metadata collection"""
        with self._lock:
            self._enabled = True

    def disable_collection(self) -> None:
        """Disable metadata collection"""
        with self._lock:
            self._enabled = False

    def is_enabled(self) -> bool:
        """Check if metadata collection is enabled"""
        with self._lock:
            return self._enabled

    def inject_command_execution_metadata(self, command_type: str, execution_time_ms: float,
                                        success: bool, user_input_length: int = 0) -> None:
        """Inject command execution metadata if collection is enabled"""
        if self._enabled:
            start_time = time.time()
            self.collector.collect_command_execution_metadata(
                command_type, execution_time_ms, success, user_input_length
            )
            end_time = time.time()
            # Calculate processing overhead
            overhead_ms = (end_time - start_time) * 1000
            if overhead_ms > 10:
                # Log warning if overhead exceeds threshold
                print(f"WARNING: Metadata collection overhead {overhead_ms:.2f}ms exceeds 10ms threshold")

    def inject_user_interaction_metadata(self, user_id: str, command: str,
                                       time_since_last: Optional[float] = None) -> None:
        """Inject user interaction metadata if collection is enabled"""
        if self._enabled:
            self.collector.collect_user_interaction_pattern(user_id, command, time_since_last)

    def inject_performance_metadata(self, memory_usage_mb: float, cpu_usage_percent: float,
                                  response_time_ms: float, throughput_cps: float) -> None:
        """Inject performance metadata if collection is enabled"""
        if self._enabled:
            self.collector.collect_performance_metrics(
                memory_usage_mb, cpu_usage_percent, response_time_ms, throughput_cps
            )

    def inject_health_metadata(self, memory_pressure: str, response_time_status: str,
                             error_rate: float, uptime_seconds: float) -> None:
        """Inject health metadata if collection is enabled"""
        if self._enabled:
            self.collector.collect_health_indicators(
                memory_pressure, response_time_status, error_rate, uptime_seconds
            )

    def get_injected_metadata(self, metadata_type: str) -> Any:
        """Get injected metadata of a specific type"""
        if metadata_type == "command_stats":
            return self.collector.get_command_execution_stats()
        elif metadata_type == "user_patterns":
            return self.collector.get_all_user_patterns()
        elif metadata_type == "performance":
            return self.collector.get_performance_metrics()
        elif metadata_type == "health":
            return self.collector.get_health_indicators()
        elif metadata_type == "summary":
            return self.collector.get_system_summary()
        else:
            return None

    def get_command_execution_timeline(self, limit: int = 50) -> List[CommandMetrics]:
        """Get command execution timeline"""
        return self.collector.get_command_execution_timeline(limit)

    def get_user_interaction_pattern(self, user_id: str) -> Optional[UserInteractionPatterns]:
        """Get interaction pattern for a specific user"""
        return self.collector.get_user_interaction_pattern(user_id)

    def get_system_summary(self) -> Dict[str, Any]:
        """Get system summary"""
        return self.collector.get_system_summary()

    def clear_all_metadata(self) -> None:
        """Clear all collected metadata"""
        self.collector.clear_metadata()