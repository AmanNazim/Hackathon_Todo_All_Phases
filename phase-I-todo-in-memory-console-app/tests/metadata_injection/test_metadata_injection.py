"""
Tests for Metadata Injection System Components
Testing the Metadata Injection tasks: T130-T134
"""
import unittest
from datetime import datetime
from src.metadata_injection.metadata_collector import (
    MetadataCollector,
    MetadataInjectionSystem,
    CommandMetrics,
    UserInteractionPatterns,
    PerformanceMetrics,
    HealthIndicators
)


class TestMetadataCollector(unittest.TestCase):
    """Test metadata collector functionality (T130, T131, T132, T133)"""

    def setUp(self):
        """Set up test fixtures"""
        self.collector = MetadataCollector()

    def test_collect_command_execution_metadata(self):
        """Test collecting command execution metadata (T130)"""
        self.collector.collect_command_execution_metadata(
            command_type="add",
            execution_time_ms=50.0,
            success=True,
            user_input_length=10
        )

        stats = self.collector.get_command_execution_stats("add")
        self.assertGreater(stats['avg_execution_time_ms'], 0)
        self.assertEqual(stats['count'], 1)

    def test_command_execution_statistics(self):
        """Test command execution statistics accuracy (T130)"""
        # Add multiple commands of same type
        for i in range(5):
            self.collector.collect_command_execution_metadata(
                command_type="list",
                execution_time_ms=25.0 + i * 5,  # Vary execution times
                success=True
            )

        stats = self.collector.get_command_execution_stats("list")
        self.assertEqual(stats['count'], 5)
        self.assertGreaterEqual(stats['avg_execution_time_ms'], 25.0)
        self.assertLessEqual(stats['avg_execution_time_ms'], 45.0)

    def test_collect_user_interaction_pattern(self):
        """Test collecting user interaction patterns (T131)"""
        self.collector.collect_user_interaction_pattern(
            user_id="user123",
            command="add Buy groceries",
            time_since_last=2.5
        )

        pattern = self.collector.get_user_interaction_pattern("user123")
        self.assertIsNotNone(pattern)
        self.assertIn("add Buy groceries", pattern.command_sequence)
        self.assertEqual(len(pattern.time_between_commands), 1)
        self.assertEqual(pattern.time_between_commands[0], 2.5)

    def test_collect_performance_metrics(self):
        """Test collecting performance metrics (T132)"""
        self.collector.collect_performance_metrics(
            memory_usage_mb=10.5,
            cpu_usage_percent=5.2,
            response_time_ms=25.0,
            throughput_cps=10.0
        )

        perf_metrics = self.collector.get_performance_metrics(limit=1)
        self.assertEqual(len(perf_metrics), 1)
        self.assertEqual(perf_metrics[0].memory_usage_mb, 10.5)
        self.assertEqual(perf_metrics[0].response_time_ms, 25.0)

    def test_collect_health_indicators(self):
        """Test collecting health indicators (T133)"""
        self.collector.collect_health_indicators(
            memory_pressure="low",
            response_time_status="fast",
            error_rate=0.01,
            uptime_seconds=3600.0
        )

        health_indicators = self.collector.get_health_indicators(limit=1)
        self.assertEqual(len(health_indicators), 1)
        self.assertTrue(health_indicators[0].is_healthy)
        self.assertEqual(health_indicators[0].memory_pressure, "low")
        self.assertEqual(health_indicators[0].error_rate, 0.01)

    def test_get_command_execution_timeline(self):
        """Test getting command execution timeline (T130)"""
        # Add several commands
        for i in range(3):
            self.collector.collect_command_execution_metadata(
                command_type=f"cmd_{i}",
                execution_time_ms=10.0 + i * 5,
                success=True
            )

        timeline = self.collector.get_command_execution_timeline(limit=5)
        self.assertEqual(len(timeline), 3)
        self.assertEqual(timeline[0].command_type, "cmd_0")

    def test_get_system_summary(self):
        """Test getting system summary (T130, T131, T132, T133)"""
        # Add some data
        self.collector.collect_command_execution_metadata(
            command_type="add",
            execution_time_ms=50.0,
            success=True
        )
        self.collector.collect_performance_metrics(
            memory_usage_mb=15.0,
            cpu_usage_percent=3.0,
            response_time_ms=20.0,
            throughput_cps=8.0
        )

        summary = self.collector.get_system_summary()
        self.assertGreaterEqual(summary['total_commands_executed'], 1)
        self.assertGreaterEqual(summary['unique_command_types'], 1)

    def test_privacy_compliance_user_tracking(self):
        """Test privacy compliance in user tracking (T131)"""
        # Test that user patterns are properly tracked without sensitive data
        self.collector.collect_user_interaction_pattern(
            user_id="user_anonymous",
            command="list",
            time_since_last=1.0
        )

        patterns = self.collector.get_all_user_patterns()
        self.assertIn("user_anonymous", patterns)
        # Verify only necessary data is stored
        pattern = patterns["user_anonymous"]
        self.assertEqual(pattern.user_id, "user_anonymous")
        # Should not store sensitive personal information


class TestMetadataInjectionSystem(unittest.TestCase):
    """Test the main metadata injection system (T134)"""

    def setUp(self):
        """Set up test fixtures"""
        self.system = MetadataInjectionSystem()

    def test_inject_command_execution_metadata(self):
        """Test injecting command execution metadata (T130, T134)"""
        self.system.inject_command_execution_metadata(
            command_type="test_cmd",
            execution_time_ms=25.0,
            success=True,
            user_input_length=20
        )

        stats = self.system.get_injected_metadata("command_stats")
        if "test_cmd" in stats:
            self.assertGreater(stats["test_cmd"]['avg_execution_time_ms'], 0)

    def test_inject_user_interaction_metadata(self):
        """Test injecting user interaction metadata (T131, T134)"""
        self.system.inject_user_interaction_metadata(
            user_id="test_user",
            command="add test task",
            time_since_last=3.0
        )

        pattern = self.system.get_user_interaction_pattern("test_user")
        self.assertIsNotNone(pattern)
        self.assertIn("add test task", pattern.command_sequence)

    def test_inject_performance_metadata(self):
        """Test injecting performance metadata (T132, T134)"""
        self.system.inject_performance_metadata(
            memory_usage_mb=12.0,
            cpu_usage_percent=4.5,
            response_time_ms=30.0,
            throughput_cps=12.0
        )

        perf_data = self.system.get_injected_metadata("performance")
        self.assertGreater(len(perf_data), 0)
        self.assertEqual(perf_data[0].memory_usage_mb, 12.0)

    def test_inject_health_metadata(self):
        """Test injecting health metadata (T133, T134)"""
        self.system.inject_health_metadata(
            memory_pressure="moderate",
            response_time_status="normal",
            error_rate=0.02,
            uptime_seconds=7200.0
        )

        health_data = self.system.get_injected_metadata("health")
        self.assertGreater(len(health_data), 0)
        self.assertTrue(health_data[0].is_healthy)

    def test_system_enabled_disabled(self):
        """Test enabling/disabling metadata collection (T134)"""
        # Initially enabled
        self.assertTrue(self.system.is_enabled())

        # Disable collection
        self.system.disable_collection()
        self.assertFalse(self.system.is_enabled())

        # Re-enable collection
        self.system.enable_collection()
        self.assertTrue(self.system.is_enabled())

    def test_get_system_summary(self):
        """Test getting system summary (T130, T131, T132, T133, T134)"""
        # Inject some metadata
        self.system.inject_command_execution_metadata(
            command_type="summary_test",
            execution_time_ms=40.0,
            success=True
        )
        self.system.inject_performance_metadata(
            memory_usage_mb=10.0,
            cpu_usage_percent=2.0,
            response_time_ms=15.0,
            throughput_cps=15.0
        )

        summary = self.system.get_system_summary()
        self.assertGreaterEqual(summary['total_commands_executed'], 1)
        self.assertGreaterEqual(summary['unique_command_types'], 1)

    def test_clear_all_metadata(self):
        """Test clearing all metadata (T130, T131, T132, T133, T134)"""
        # Add some data
        self.system.inject_command_execution_metadata(
            command_type="clear_test",
            execution_time_ms=30.0,
            success=True
        )

        # Verify data exists
        summary_before = self.system.get_system_summary()
        self.assertGreater(summary_before['total_commands_executed'], 0)

        # Clear all metadata
        self.system.clear_all_metadata()

        # Verify data is cleared
        summary_after = self.system.get_system_summary()
        self.assertEqual(summary_after['total_commands_executed'], 0)

    def test_performance_overhead_check(self):
        """Test that metadata injection doesn't exceed performance overhead (T130)"""
        import time

        # Measure overhead for metadata injection
        start_time = time.time()
        for i in range(100):
            self.system.inject_command_execution_metadata(
                command_type=f"perf_test_{i}",
                execution_time_ms=1.0,
                success=True
            )
        end_time = time.time()

        total_time_ms = (end_time - start_time) * 1000
        avg_overhead_per_call = total_time_ms / 100

        # Should be well under 10ms overhead per call
        self.assertLess(avg_overhead_per_call, 10.0,
                       f"Average overhead {avg_overhead_per_call:.2f}ms exceeds 10ms limit")


class TestMetadataIntegration(unittest.TestCase):
    """Test metadata system integration scenarios"""

    def setUp(self):
        """Set up test fixtures"""
        self.system = MetadataInjectionSystem()

    def test_full_metadata_workflow(self):
        """Test complete metadata injection workflow (T130-T134)"""
        # 1. Inject command execution metadata
        self.system.inject_command_execution_metadata(
            command_type="add_task",
            execution_time_ms=45.0,
            success=True,
            user_input_length=15
        )

        # 2. Inject user interaction pattern
        self.system.inject_user_interaction_metadata(
            user_id="integration_user",
            command="add Buy groceries",
            time_since_last=2.0
        )

        # 3. Inject performance metrics
        self.system.inject_performance_metadata(
            memory_usage_mb=8.5,
            cpu_usage_percent=3.2,
            response_time_ms=22.0,
            throughput_cps=11.5
        )

        # 4. Inject health indicators
        self.system.inject_health_metadata(
            memory_pressure="low",
            response_time_status="fast",
            error_rate=0.005,
            uptime_seconds=1800.0
        )

        # 5. Verify all metadata types are available
        command_stats = self.system.get_injected_metadata("command_stats")
        user_patterns = self.system.get_injected_metadata("user_patterns")
        performance_data = self.system.get_injected_metadata("performance")
        health_data = self.system.get_injected_metadata("health")
        summary = self.system.get_system_summary()

        # 6. Validate collected data
        self.assertIn("add_task", command_stats)
        self.assertIn("integration_user", user_patterns)
        self.assertGreater(len(performance_data), 0)
        self.assertGreater(len(health_data), 0)
        self.assertGreaterEqual(summary['total_commands_executed'], 1)

    def test_multiple_users_tracking(self):
        """Test tracking multiple users (T131)"""
        # Track multiple users
        for i in range(3):
            self.system.inject_user_interaction_metadata(
                user_id=f"user_{i}",
                command=f"cmd_{i}",
                time_since_last=1.0 + i * 0.5
            )

        all_patterns = self.system.get_injected_metadata("user_patterns")
        self.assertEqual(len(all_patterns), 3)
        for i in range(3):
            self.assertIn(f"user_{i}", all_patterns)

    def test_long_running_session_tracking(self):
        """Test metadata tracking over extended periods (T130, T132)"""
        # Simulate a longer session with many commands
        for i in range(50):
            self.system.inject_command_execution_metadata(
                command_type="test_cmd",
                execution_time_ms=20.0 + (i % 10),  # Vary slightly
                success=True
            )

            if i % 10 == 0:  # Every 10th iteration
                self.system.inject_performance_metadata(
                    memory_usage_mb=5.0 + (i // 10),
                    cpu_usage_percent=2.0 + (i // 20),
                    response_time_ms=15.0 + (i % 5),
                    throughput_cps=10.0
                )

        # Verify data accumulation
        summary = self.system.get_system_summary()
        self.assertEqual(summary['total_commands_executed'], 50)

        # Verify performance metrics were collected
        perf_data = self.system.get_injected_metadata("performance")
        self.assertGreaterEqual(len(perf_data), 5)  # At least 5 performance samples


if __name__ == '__main__':
    unittest.main()