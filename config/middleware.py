import logging
import time


logger = logging.getLogger('bookstore.requests')


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started_at = time.monotonic()
        response = self.get_response(request)
        duration_ms = (time.monotonic() - started_at) * 1000

        logger.info(
            '%s %s -> %s %.2fms',
            request.method,
            request.get_full_path(),
            response.status_code,
            duration_ms,
        )
        return response
