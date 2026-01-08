"""
Tests for Middleware Pipeline Components
Testing the Command Grammar & Parsing tasks: T040-T048
"""
import unittest
from unittest.mock import Mock, patch
from src.middleware.pipeline import MiddlewarePipeline, MiddlewareResult, MiddlewareResultStatus
from src.middleware.input_normalizer import InputNormalizer
from src.middleware.intent_classifier import IntentClassifier
from src.middleware.security_guard import SecurityGuard
from src.middleware.validation_middleware import ValidationMiddleware
from src.middleware.analytics_middleware import AnalyticsMiddleware
from src.middleware.renderer_middleware import RendererMiddleware


class TestMiddlewarePipeline(unittest.TestCase):
    """Test the middleware pipeline orchestrator (T056)"""

    def setUp(self):
        """Set up test fixtures"""
        self.pipeline = MiddlewarePipeline()

    def test_pipeline_initialization(self):
        """Test that the pipeline initializes correctly (T056)"""
        self.assertEqual(self.pipeline.get_middleware_count(), 0)
        self.assertEqual(self.pipeline.name, "MiddlewarePipeline")

    def test_add_single_middleware(self):
        """Test adding a single middleware to the pipeline (T056)"""
        initial_count = self.pipeline.get_middleware_count()

        self.pipeline.add_middleware(lambda data: MiddlewareResult(
            status=MiddlewareResultStatus.SUCCESS,
            data=data
        ))

        self.assertEqual(self.pipeline.get_middleware_count(), initial_count + 1)

    def test_process_through_pipeline(self):
        """Test processing data through the pipeline (T056)"""
        # Create a simple middleware that adds a key to the data
        def add_test_key(data):
            new_data = data.copy()
            new_data['test_key'] = 'test_value'
            return MiddlewareResult(
                status=MiddlewareResultStatus.SUCCESS,
                data=new_data
            )

        self.pipeline.add_middleware(add_test_key)

        initial_data = {'original': 'data'}
        result = self.pipeline.process(initial_data)

        self.assertTrue(result.status == MiddlewareResultStatus.SUCCESS)
        self.assertIn('test_key', result.data)
        self.assertEqual(result.data['test_key'], 'test_value')
        self.assertEqual(result.data['original'], 'data')

    def test_process_multiple_middlewares(self):
        """Test processing through multiple middleware in sequence (T056)"""
        # First middleware adds a key
        def add_first_key(data):
            new_data = data.copy()
            new_data['first'] = 'first_value'
            return MiddlewareResult(
                status=MiddlewareResultStatus.SUCCESS,
                data=new_data
            )

        # Second middleware adds another key
        def add_second_key(data):
            new_data = data.copy()
            new_data['second'] = 'second_value'
            return MiddlewareResult(
                status=MiddlewareResultStatus.SUCCESS,
                data=new_data
            )

        self.pipeline.add_middleware(add_first_key)
        self.pipeline.add_middleware(add_second_key)

        initial_data = {'original': 'data'}
        result = self.pipeline.process(initial_data)

        self.assertTrue(result.status == MiddlewareResultStatus.SUCCESS)
        self.assertIn('first', result.data)
        self.assertIn('second', result.data)
        self.assertEqual(result.data['first'], 'first_value')
        self.assertEqual(result.data['second'], 'second_value')

    def test_error_handling_in_pipeline(self):
        """Test error handling when a middleware throws an exception (T057)"""
        def successful_middleware(data):
            new_data = data.copy()
            new_data['processed_by'] = 'first'
            return MiddlewareResult(
                status=MiddlewareResultStatus.SUCCESS,
                data=new_data
            )

        def error_middleware(data):
            raise Exception("Something went wrong in middleware")

        def never_called_middleware(data):
            new_data = data.copy()
            new_data['processed_by'] = 'third'
            return MiddlewareResult(
                status=MiddlewareResultStatus.SUCCESS,
                data=new_data
            )

        self.pipeline.add_middleware(successful_middleware)
        self.pipeline.add_middleware(error_middleware)
        self.pipeline.add_middleware(never_called_middleware)

        initial_data = {'original': 'data'}
        result = self.pipeline.process(initial_data)

        self.assertTrue(result.status == MiddlewareResultStatus.ERROR)
        self.assertIn('error_message', result.__dict__)
        self.assertIsNotNone(result.error_message)

    def test_error_propagation_stop_processing(self):
        """Test that error propagation stops further processing (T057)"""
        def add_marker_middleware(data):
            new_data = data.copy()
            new_data['marker'] = 'added'
            return MiddlewareResult(
                status=MiddlewareResultStatus.SUCCESS,
                data=new_data
            )

        def error_middleware(data):
            raise Exception("Simulated error")

        def check_marker_not_present(data):
            # This should never be called due to error propagation
            new_data = data.copy()
            new_data['marker2'] = 'should_not_be_added'
            return MiddlewareResult(
                status=MiddlewareResultStatus.SUCCESS,
                data=new_data
            )

        self.pipeline.add_middleware(add_marker_middleware)
        self.pipeline.add_middleware(error_middleware)
        self.pipeline.add_middleware(check_marker_not_present)

        initial_data = {'original': 'data'}
        result = self.pipeline.process(initial_data)

        # Processing should stop at the error, so marker2 should not be added
        self.assertTrue(result.status == MiddlewareResultStatus.ERROR)
        self.assertNotIn('marker2', result.data)


class TestInputNormalizerMiddleware(unittest.TestCase):
    """Test the InputNormalizer middleware (T040, T046)"""

    def setUp(self):
        """Set up test fixtures"""
        self.normalizer = InputNormalizer()

    def test_normalize_simple_command(self):
        """Test normalizing a simple command (T040)"""
        data = {'raw_input': '  add   Buy groceries  '}
        result = self.normalizer.process(data, lambda x: MiddlewareResult(MiddlewareResultStatus.SUCCESS, x))

        self.assertTrue(result.status == MiddlewareResultStatus.SUCCESS)
        self.assertIn('normalized_input', result.data)
        self.assertEqual(result.data['normalized_input'], 'add buy groceries')

    def test_normalize_with_extra_whitespace(self):
        """Test normalizing input with extra whitespace (T046)"""
        data = {'raw_input': '   list    completed   '}
        result = self.normalizer.process(data, lambda x: MiddlewareResult(MiddlewareResultStatus.SUCCESS, x))

        self.assertTrue(result.status == MiddlewareResultStatus.SUCCESS)
        self.assertEqual(result.data['normalized_input'], 'list completed')

    def test_normalize_case_insensitive(self):
        """Test normalizing case insensitive input (T046)"""
        data = {'raw_input': 'ADD BUY GROCERIES'}
        result = self.normalizer.process(data, lambda x: MiddlewareResult(MiddlewareResultStatus.SUCCESS, x))

        self.assertTrue(result.status == MiddlewareResultStatus.SUCCESS)
        self.assertEqual(result.data['normalized_input'], 'add buy groceries')


class TestIntentClassifierMiddleware(unittest.TestCase):
    """Test the IntentClassifier middleware (T041, T046)"""

    def setUp(self):
        """Set up test fixtures"""
        self.classifier = IntentClassifier()

    def test_classify_add_intent(self):
        """Test classifying add command intent (T040)"""
        data = {'normalized_input': 'add Buy groceries'}
        result = self.classifier.process(data, lambda x: MiddlewareResult(MiddlewareResultStatus.SUCCESS, x))

        self.assertTrue(result.status == MiddlewareResultStatus.SUCCESS)
        self.assertEqual(result.data['intent'], 'add')

    def test_classify_list_intent(self):
        """Test classifying list command intent (T041)"""
        data = {'normalized_input': 'list completed'}
        result = self.classifier.process(data, lambda x: MiddlewareResult(MiddlewareResultStatus.SUCCESS, x))

        self.assertTrue(result.status == MiddlewareResultStatus.SUCCESS)
        self.assertEqual(result.data['intent'], 'list')

    def test_classify_update_intent(self):
        """Test classifying update command intent (T042)"""
        data = {'normalized_input': 'update 123 New title'}
        result = self.classifier.process(data, lambda x: MiddlewareResult(MiddlewareResultStatus.SUCCESS, x))

        self.assertTrue(result.status == MiddlewareResultStatus.SUCCESS)
        self.assertEqual(result.data['intent'], 'update')

    def test_classify_delete_intent(self):
        """Test classifying delete command intent (T043)"""
        data = {'normalized_input': 'delete 123'}
        result = self.classifier.process(data, lambda x: MiddlewareResult(MiddlewareResultStatus.SUCCESS, x))

        self.assertTrue(result.status == MiddlewareResultStatus.SUCCESS)
        self.assertEqual(result.data['intent'], 'delete')

    def test_classify_complete_intent(self):
        """Test classifying complete command intent (T044)"""
        data = {'normalized_input': 'complete 123'}
        result = self.classifier.process(data, lambda x: MiddlewareResult(MiddlewareResultStatus.SUCCESS, x))

        self.assertTrue(result.status == MiddlewareResultStatus.SUCCESS)
        self.assertEqual(result.data['intent'], 'complete')

    def test_classify_help_intent(self):
        """Test classifying help command intent (T045)"""
        data = {'normalized_input': 'help add'}
        result = self.classifier.process(data, lambda x: MiddlewareResult(MiddlewareResultStatus.SUCCESS, x))

        self.assertTrue(result.status == MiddlewareResultStatus.SUCCESS)
        self.assertEqual(result.data['intent'], 'help')


class TestSecurityGuardMiddleware(unittest.TestCase):
    """Test the SecurityGuard middleware (T052)"""

    def setUp(self):
        """Set up test fixtures"""
        self.security_guard = SecurityGuard()

    def test_safe_command_passes_validation(self):
        """Test that safe commands pass security validation (T052)"""
        data = {'normalized_input': 'add Buy groceries'}
        result = self.security_guard.process(data, lambda x: MiddlewareResult(MiddlewareResultStatus.SUCCESS, x))

        self.assertTrue(result.status == MiddlewareResultStatus.SUCCESS)

    def test_command_with_semicolon_fails_validation(self):
        """Test that commands with semicolons fail security validation (T052)"""
        data = {'normalized_input': 'add Buy groceries; rm -rf /'}
        result = self.security_guard.process(data, lambda x: MiddlewareResult(MiddlewareResultStatus.SUCCESS, x))

        self.assertTrue(result.status == MiddlewareResultStatus.SECURITY_VIOLATION)

    def test_command_with_pipe_fails_validation(self):
        """Test that commands with pipes fail security validation (T052)"""
        data = {'normalized_input': 'add Buy groceries | echo malicious'}
        result = self.security_guard.process(data, lambda x: MiddlewareResult(MiddlewareResultStatus.SUCCESS, x))

        self.assertTrue(result.status == MiddlewareResultStatus.SECURITY_VIOLATION)


class TestValidationMiddleware(unittest.TestCase):
    """Test the ValidationMiddleware (T053)"""

    def setUp(self):
        """Set up test fixtures"""
        self.validator = ValidationMiddleware()

    def test_valid_add_command_passes_validation(self):
        """Test that valid add commands pass validation (T040, T053)"""
        data = {
            'intent': 'add',
            'parsed_params': {'title': 'Buy groceries', 'description': 'Weekly shopping'}
        }
        result = self.validator.process(data, lambda x: MiddlewareResult(MiddlewareResultStatus.SUCCESS, x))

        self.assertTrue(result.status == MiddlewareResultStatus.SUCCESS)

    def test_add_command_without_title_fails_validation(self):
        """Test that add commands without title fail validation (T040, T053)"""
        data = {
            'intent': 'add',
            'parsed_params': {'title': '', 'description': 'Weekly shopping'}
        }
        result = self.validator.process(data, lambda x: MiddlewareResult(MiddlewareResultStatus.SUCCESS, x))

        self.assertTrue(result.status == MiddlewareResultStatus.VALIDATION_FAILED)

    def test_valid_update_command_passes_validation(self):
        """Test that valid update commands pass validation (T042, T053)"""
        data = {
            'intent': 'update',
            'parsed_params': {'task_id': '123', 'title': 'New title'}
        }
        result = self.validator.process(data, lambda x: MiddlewareResult(MiddlewareResultStatus.SUCCESS, x))

        self.assertTrue(result.status == MiddlewareResultStatus.SUCCESS)

    def test_update_command_without_task_id_fails_validation(self):
        """Test that update commands without task ID fail validation (T042, T053)"""
        data = {
            'intent': 'update',
            'parsed_params': {'task_id': '', 'title': 'New title'}
        }
        result = self.validator.process(data, lambda x: MiddlewareResult(MiddlewareResultStatus.SUCCESS, x))

        self.assertTrue(result.status == MiddlewareResultStatus.VALIDATION_FAILED)

    def test_update_command_without_title_fails_validation(self):
        """Test that update commands without title fail validation (T042, T053)"""
        data = {
            'intent': 'update',
            'parsed_params': {'task_id': '123', 'title': ''}
        }
        result = self.validator.process(data, lambda x: MiddlewareResult(MiddlewareResultStatus.SUCCESS, x))

        self.assertTrue(result.status == MiddlewareResultStatus.VALIDATION_FAILED)


class TestAnalyticsMiddleware(unittest.TestCase):
    """Test the AnalyticsMiddleware (T054)"""

    def setUp(self):
        """Set up test fixtures"""
        self.analytics = AnalyticsMiddleware()

    def test_command_tracking_works(self):
        """Test that command execution is tracked (T054)"""
        data = {'intent': 'add', 'results': {'success': True}}
        result = self.analytics.process(data, lambda x: MiddlewareResult(MiddlewareResultStatus.SUCCESS, x))

        self.assertTrue(result.status == MiddlewareResultStatus.SUCCESS)
        self.assertIn('analytics', result.data)
        self.assertIn('command_type', result.data['analytics'])

    def test_performance_metrics_collected(self):
        """Test that performance metrics are collected (T054)"""
        data = {'intent': 'list', 'results': {'tasks': []}}
        result = self.analytics.process(data, lambda x: MiddlewareResult(MiddlewareResultStatus.SUCCESS, x))

        self.assertTrue(result.status == MiddlewareResultStatus.SUCCESS)
        self.assertIn('analytics', result.data)
        self.assertIn('execution_time_ms', result.data['analytics'])


class TestRendererMiddleware(unittest.TestCase):
    """Test the RendererMiddleware (T055)"""

    def setUp(self):
        """Set up test fixtures"""
        self.renderer = RendererMiddleware()

    def test_output_formatting_works(self):
        """Test that output is formatted according to theme (T055)"""
        data = {
            'intent': 'add',
            'results': {'success': True, 'task_id': '123', 'title': 'Test task'}
        }
        result = self.renderer.process(data, lambda x: MiddlewareResult(MiddlewareResultStatus.SUCCESS, x))

        self.assertTrue(result.status == MiddlewareResultStatus.SUCCESS)
        self.assertIn('formatted_output', result.data)
        self.assertIsInstance(result.data['formatted_output'], str)

    def test_error_formatting_works(self):
        """Test that error output is formatted properly (T055)"""
        data = {
            'intent': 'add',
            'results': {'success': False, 'error': 'Task title is required'}
        }
        result = self.renderer.process(data, lambda x: MiddlewareResult(MiddlewareResultStatus.SUCCESS, x))

        self.assertTrue(result.status == MiddlewareResultStatus.SUCCESS)
        self.assertIn('formatted_output', result.data)
        self.assertIsInstance(result.data['formatted_output'], str)
        self.assertIn('Task title is required', result.data['formatted_output'])


if __name__ == '__main__':
    unittest.main()