"""
Middleware Pipeline Infrastructure for CLI Todo Application
Defines the core pipeline infrastructure used by all middleware components
"""
from typing import Dict, Any, Callable, List, Optional
from dataclasses import dataclass
from enum import Enum


class MiddlewareResultStatus(Enum):
    """Enumeration of possible middleware result statuses"""
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"
    VALIDATION_FAILED = "VALIDATION_FAILED"


@dataclass
class MiddlewareResult:
    """Result of middleware processing"""
    status: MiddlewareResultStatus
    data: Dict[str, Any]
    error_message: Optional[str] = None
    suggestions: List[str] = None

    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []


class MiddlewarePipeline:
    """Orchestrates the execution of middleware components in proper order with error handling"""

    def __init__(self):
        self.middlewares: List[Callable] = []
        self.name = "MiddlewarePipeline"

    def add_middleware(self, middleware_callable: Callable) -> 'MiddlewarePipeline':
        """Add a middleware to the pipeline"""
        self.middlewares.append(middleware_callable)
        return self

    def add_middleware_with_name(self, middleware_instance, name: str = None) -> 'MiddlewarePipeline':
        """Add a middleware instance to the pipeline with proper wrapping"""
        wrapped_middleware = self._wrap_middleware(middleware_instance)
        self.middlewares.append(wrapped_middleware)
        return self

    def process(self, initial_data: Dict[str, Any]) -> MiddlewareResult:
        """Process data through all middleware in sequence with proper error handling"""
        # Create a mutable copy of the data to pass through the pipeline
        current_data = initial_data.copy()

        # Process through each middleware in sequence
        for i, middleware in enumerate(self.middlewares):
            try:
                # Create a closure to pass to the middleware for chaining
                def create_next_processor(next_idx):
                    def next_middleware(data):
                        if next_idx < len(self.middlewares):
                            return self.middlewares[next_idx](data)
                        else:
                            # End of pipeline - return success result
                            return MiddlewareResult(
                                status=MiddlewareResultStatus.SUCCESS,
                                data=data
                            )
                    return next_middleware

                # Process with the current middleware
                result = middleware(current_data)

                # If any middleware returns an error status, stop processing
                if result.status != MiddlewareResultStatus.SUCCESS:
                    return result

                # Update the data for the next middleware
                current_data = result.data

            except Exception as e:
                # Handle any exceptions during middleware processing
                return MiddlewareResult(
                    status=MiddlewareResultStatus.ERROR,
                    data=current_data,
                    error_message=f"Error in middleware {i} processing: {str(e)}",
                    suggestions=["Check the input format and try again"]
                )

        # Return final result after all middleware have processed
        return MiddlewareResult(
            status=MiddlewareResultStatus.SUCCESS,
            data=current_data
        )

    def process_with_detailed_errors(self, initial_data: Dict[str, Any]) -> MiddlewareResult:
        """Process with detailed error information and better error handling between stages"""
        # Create a mutable copy of the data to pass through the pipeline
        current_data = initial_data.copy()

        # Process through each middleware in sequence
        for i, middleware in enumerate(self.middlewares):
            try:
                # Create a closure to pass to the middleware for chaining
                def create_next_processor(next_idx):
                    def next_middleware(data):
                        if next_idx < len(self.middlewares):
                            try:
                                return self.middlewares[next_idx](data)
                            except Exception as e:
                                return MiddlewareResult(
                                    status=MiddlewareResultStatus.ERROR,
                                    data=data,
                                    error_message=f"Error in middleware {next_idx} (next in chain): {str(e)}",
                                    suggestions=["Check the input format and try again"]
                                )
                        else:
                            # End of pipeline - return success result
                            return MiddlewareResult(
                                status=MiddlewareResultStatus.SUCCESS,
                                data=data
                            )
                    return next_middleware

                # Process with the current middleware
                result = middleware(current_data)

                # If any middleware returns an error status, stop processing
                if result.status != MiddlewareResultStatus.SUCCESS:
                    return result

                # Update the data for the next middleware
                current_data = result.data

            except Exception as e:
                # Handle any exceptions during middleware processing
                middleware_name = f"middleware_{i}"
                if hasattr(middleware, '__name__'):
                    middleware_name = middleware.__name__
                elif hasattr(middleware, '__class__'):
                    middleware_name = middleware.__class__.__name__

                return MiddlewareResult(
                    status=MiddlewareResultStatus.ERROR,
                    data=current_data,
                    error_message=f"Error in {middleware_name} (position {i}): {str(e)}",
                    suggestions=["Check the input format and try again", f"Review middleware {middleware_name} configuration"]
                )

        # Return final result after all middleware have processed
        return MiddlewareResult(
            status=MiddlewareResultStatus.SUCCESS,
            data=current_data
        )

    def get_middleware_count(self) -> int:
        """Get the number of middleware in the pipeline"""
        return len(self.middlewares)

    def clear_middlewares(self):
        """Clear all middleware from the pipeline"""
        self.middlewares.clear()

    def _wrap_middleware(self, middleware_instance) -> Callable:
        """Wrap a middleware instance to be compatible with the pipeline"""
        def wrapped(data: Dict[str, Any]) -> MiddlewareResult:
            try:
                # Create the next middleware processor
                def create_next_processor(current_index):
                    def next_middleware(next_data):
                        # Find the index of the current middleware in the list
                        try:
                            current_pos = self.middlewares.index(wrapped)
                            next_pos = current_pos + 1
                            if next_pos < len(self.middlewares):
                                return self.middlewares[next_pos](next_data)
                            else:
                                # End of pipeline
                                return MiddlewareResult(
                                    status=MiddlewareResultStatus.SUCCESS,
                                    data=next_data
                                )
                        except ValueError:
                            # If the middleware isn't in the list, process as last
                            return MiddlewareResult(
                                status=MiddlewareResultStatus.SUCCESS,
                                data=next_data
                            )

                    return next_middleware

                result = middleware_instance.process(data, create_next_processor(0))

                # Ensure result is a MiddlewareResult
                if not isinstance(result, MiddlewareResult):
                    return MiddlewareResult(
                        status=MiddlewareResultStatus.SUCCESS,
                        data=result if isinstance(result, dict) else data
                    )
                return result

            except Exception as e:
                return MiddlewareResult(
                    status=MiddlewareResultStatus.ERROR,
                    data=data,
                    error_message=f"Error in {getattr(middleware_instance, 'name', 'unknown_middleware')}: {str(e)}",
                    suggestions=["Check the input format and try again"]
                )

        return wrapped


def middleware_wrapper(middleware_instance):
    """Wrapper to make middleware instances compatible with the pipeline"""
    def wrapped(data: Dict[str, Any]) -> MiddlewareResult:
        try:
            # Create a simple next function that just returns success
            def simple_next(data):
                return MiddlewareResult(
                    status=MiddlewareResultStatus.SUCCESS,
                    data=data
                )

            result = middleware_instance.process(data, simple_next)
            if not isinstance(result, MiddlewareResult):
                # If the middleware didn't return a MiddlewareResult, wrap it
                return MiddlewareResult(
                    status=MiddlewareResultStatus.SUCCESS,
                    data=result if isinstance(result, dict) else data
                )
            return result
        except Exception as e:
            return MiddlewareResult(
                status=MiddlewareResultStatus.ERROR,
                data=data,
                error_message=f"Error in {getattr(middleware_instance, 'name', 'unknown_middleware')}: {str(e)}",
                suggestions=["Check the input format and try again"]
            )

    return wrapped