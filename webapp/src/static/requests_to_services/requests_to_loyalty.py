import requests
from . import *


class RequestsToLoyaltyService:
    def __new__(cls, *args, **kwargs):
        if getattr(cls, '_instance', None) is None:
            cls._instance = super(RequestsToLoyaltyService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    @MyCircuitBreaker(name='loyalty_service')
    def get_info_about_loyalty(self, user_uuid) -> tuple[dict, int]:
        result = requests.get(
            f'{loyalty_service}{loy_service_port}{loyalty_service_path}/user_info/{user_uuid}'
        )

        if not result.ok:
            raise requests.ConnectionError({'message': 'Loyalty Service unavailable'})

        return result.json(), result.status_code

    @MyCircuitBreaker(name='loyalty_service')
    def update_count_reservations(self, user_uuid):
        result_loyalty = requests.patch(
            f'{loyalty_service}{loy_service_port}{loyalty_service_path}/increment_count_reservations/{user_uuid}'
        )

        if not result_loyalty.ok:
            raise requests.ConnectionError(result_loyalty.status_code)

        return result_loyalty.json(), result_loyalty.status_code

    @MyCircuitBreaker(name='loyalty_service')
    def decrement_count_reservations(self, user_uuid):
        result_loyalty = requests.patch(
            f'{loyalty_service}{loy_service_port}{loyalty_service_path}/decrement_count_reservations/{user_uuid}'
        )

        if not result_loyalty.ok:
            raise requests.ConnectionError(result_loyalty.status_code)

        return result_loyalty.json(), result_loyalty.status_code

