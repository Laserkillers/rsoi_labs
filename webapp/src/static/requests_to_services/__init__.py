from typing import Callable

# from . import *
from .. import *


import circuitbreaker
import requests


class MyCircuitBreaker(circuitbreaker.CircuitBreaker):
    FAILURE_THRESHOLD = int(max_request_retry)
    RECOVERY_TIMEOUT = int(delay_btw_requests)
    EXPECTED_EXCEPTION = Exception


def get_data_with_handle(
        func: Callable, *args, **kwargs) -> dict:
    try:
        data = func(*args, **kwargs)
        status_code = data.status_code
        data = data.json()
        data['status_code'] = status_code
        data['success'] = True
    except circuitbreaker.CircuitBreakerError as e:
        return {
            "status_code": 503,
            'success': False,
            "message": f"Circuit breaker active: {e}"
        }
    except requests.exceptions.ConnectionError as e:
        return {
            "status_code": 500,
            'success': False,
            "message": f"Failed to get data: {e}"
        }
    return data
