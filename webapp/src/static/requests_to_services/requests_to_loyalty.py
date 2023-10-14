import requests
from . import *
# from .. import loyalty_service_path
# from . import *


class RequestsToLoyaltyService:
    def __new__(cls, *args, **kwargs):
        if getattr(cls, '_instance', None) is None:
            cls._instance = super(RequestsToLoyaltyService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    @MyCircuitBreaker(name='loyalty_service')
    def get_info_about_loyalty(self, user_uuid):
        result = requests.get(
            f'{loyalty_service}{loy_service_port}{loyalty_service_path}/user_info/{user_uuid}'
        )

        if not result.ok:
            raise requests.ConnectionError(result.status_code)

        return result.json()