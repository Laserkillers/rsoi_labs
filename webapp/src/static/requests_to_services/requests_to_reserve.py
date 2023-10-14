from . import *


class RequestsToReserveService:
    def __new__(cls, *args, **kwargs):
        if getattr(cls, '_instance', None) is None:
            cls._instance = super(RequestsToReserveService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    @MyCircuitBreaker(name='reserve_service')
    def get_all_hotels(self, page: int, size: int) -> dict:
        result = requests.get(
            f'{reserve_service}{res_service_port}{reserve_service_path}/hotels',
            params={'page': page, 'size': size}
        )
        if not result.ok:
            raise requests.ConnectionError(result.status_code)

        return result.json()

    @MyCircuitBreaker(name='reserve_service')
    def get_user_info(self, user_uuid):
        result = requests.get(
            f'{reserve_service}{res_service_port}{reserve_service_path}/user_info/{user_uuid}'
        )

        if not result.ok:
            raise requests.ConnectionError(result.status_code)

        return result.json()
