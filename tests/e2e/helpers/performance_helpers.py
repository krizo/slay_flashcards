import pytest


@pytest.fixture
def performance_monitor():
    """Monitor performance during E2E tests."""
    import time
    import psutil
    import os

    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.start_memory = None

        def start_monitoring(self):
            """Start performance monitoring."""
            self.start_time = time.time()
            process = psutil.Process(os.getpid())
            self.start_memory = process.memory_info().rss

        def stop_monitoring(self):
            """Stop monitoring and return metrics."""
            if self.start_time is None:
                return {}

            duration = time.time() - self.start_time
            process = psutil.Process(os.getpid())
            current_memory = process.memory_info().rss
            memory_delta = current_memory - self.start_memory

            return {
                "duration_seconds": duration,
                "memory_delta_mb": memory_delta / 1024 / 1024,
                "final_memory_mb": current_memory / 1024 / 1024
            }

    return PerformanceMonitor()

