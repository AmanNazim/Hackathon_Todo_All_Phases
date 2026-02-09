"""
Query performance monitoring middleware for analytics.

Tracks query execution times and logs slow queries for optimization.
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Slow query threshold in seconds
SLOW_QUERY_THRESHOLD = 1.0


class QueryPerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware to monitor query performance and log slow queries.
    """

    def __init__(self, app: ASGIApp, threshold: float = SLOW_QUERY_THRESHOLD):
        super().__init__(app)
        self.threshold = threshold

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and measure execution time.

        Args:
            request: Incoming request
            call_next: Next middleware/handler

        Returns:
            Response from handler
        """
        # Only monitor analytics endpoints
        if not request.url.path.startswith("/api/v1/users/") or "/analytics/" not in request.url.path:
            return await call_next(request)

        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log slow queries
        if duration > self.threshold:
            logger.warning(
                f"Slow analytics query detected: "
                f"path={request.url.path} "
                f"method={request.method} "
                f"duration={duration:.2f}s "
                f"status={response.status_code}"
            )

        # Add performance header
        response.headers["X-Query-Time"] = f"{duration:.3f}"

        # Log all analytics queries for monitoring
        logger.info(
            f"Analytics query: "
            f"path={request.url.path} "
            f"method={request.method} "
            f"duration={duration:.3f}s "
            f"status={response.status_code}"
        )

        return response


async def log_slow_query(
    query_name: str,
    duration: float,
    threshold: float = SLOW_QUERY_THRESHOLD,
    **context
):
    """
    Log a slow query with context.

    Args:
        query_name: Name of the query
        duration: Query duration in seconds
        threshold: Threshold for slow queries
        **context: Additional context to log
    """
    if duration > threshold:
        context_str = ", ".join(f"{k}={v}" for k, v in context.items())
        logger.warning(
            f"Slow query: {query_name} "
            f"duration={duration:.2f}s "
            f"{context_str}"
        )


def track_query_performance(query_name: str):
    """
    Decorator to track query performance.

    Args:
        query_name: Name of the query to track

    Returns:
        Decorator function
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                # Log if slow
                await log_slow_query(
                    query_name,
                    duration,
                    user_id=kwargs.get('user_id', 'unknown')
                )

                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Query failed: {query_name} "
                    f"duration={duration:.2f}s "
                    f"error={str(e)}"
                )
                raise

        return wrapper
    return decorator


class QueryPerformanceTracker:
    """
    Context manager for tracking query performance.
    """

    def __init__(self, query_name: str, **context):
        self.query_name = query_name
        self.context = context
        self.start_time = None
        self.duration = None

    async def __aenter__(self):
        self.start_time = time.time()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.duration = time.time() - self.start_time

        if exc_type is None:
            # Success
            await log_slow_query(
                self.query_name,
                self.duration,
                **self.context
            )
        else:
            # Error
            logger.error(
                f"Query failed: {self.query_name} "
                f"duration={self.duration:.2f}s "
                f"error={exc_val}"
            )

        return False  # Don't suppress exceptions


# Performance statistics tracking
class PerformanceStats:
    """
    Track performance statistics for analytics queries.
    """

    def __init__(self):
        self.query_counts = {}
        self.query_durations = {}
        self.slow_query_counts = {}

    def record_query(self, query_name: str, duration: float):
        """
        Record a query execution.

        Args:
            query_name: Name of the query
            duration: Query duration in seconds
        """
        # Increment count
        self.query_counts[query_name] = self.query_counts.get(query_name, 0) + 1

        # Track duration
        if query_name not in self.query_durations:
            self.query_durations[query_name] = []
        self.query_durations[query_name].append(duration)

        # Track slow queries
        if duration > SLOW_QUERY_THRESHOLD:
            self.slow_query_counts[query_name] = self.slow_query_counts.get(query_name, 0) + 1

    def get_stats(self, query_name: str = None):
        """
        Get performance statistics.

        Args:
            query_name: Optional query name to filter by

        Returns:
            Dictionary with performance statistics
        """
        if query_name:
            durations = self.query_durations.get(query_name, [])
            if not durations:
                return None

            return {
                "query_name": query_name,
                "count": self.query_counts.get(query_name, 0),
                "slow_count": self.slow_query_counts.get(query_name, 0),
                "avg_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations)
            }

        # Return all stats
        all_stats = {}
        for qname in self.query_counts.keys():
            all_stats[qname] = self.get_stats(qname)

        return all_stats

    def reset(self):
        """Reset all statistics."""
        self.query_counts.clear()
        self.query_durations.clear()
        self.slow_query_counts.clear()


# Global performance tracker
performance_stats = PerformanceStats()
