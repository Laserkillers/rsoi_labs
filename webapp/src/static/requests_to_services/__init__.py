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
        func: Callable[[], tuple[dict | list, int]], *args, **kwargs) -> dict:
    ret_info = {}
    try:
        data, status_code = func(*args, **kwargs)
        ret_info['data'] = data
        ret_info['status_code'] = status_code
        ret_info['success'] = True
    except circuitbreaker.CircuitBreakerError as e:
        return {
            "status_code": 503,
            'success': False,
            "message": f"{e}"
        }
    except requests.exceptions.ConnectionError as e:
        return {
            "status_code": 500,
            'success': False,
            "message": f"{e}"
        }
    return ret_info
