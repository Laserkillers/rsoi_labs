import json
from . import *


class RequestsToReserveService:
    def __new__(cls, *args, **kwargs):
        if getattr(cls, '_instance', None) is None:
            cls._instance = super(RequestsToReserveService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    @MyCircuitBreaker(name='reserve_service')
    def get_all_hotels(self, page: int, size: int) -> tuple[dict, int]:
        result = requests.get(
            f'{reserve_service}{res_service_port}{reserve_service_path}/hotels',
            params={'page': page, 'size': size}
        )
        if not result.ok:
            raise requests.ConnectionError(result.status_code)

        return result.json(), result.status_code

    @MyCircuitBreaker(name='reserve_service')
    def get_user_info(self, user_uuid) -> tuple[dict, int]:
        result = requests.get(
            f'{reserve_service}{res_service_port}{reserve_service_path}/user_info/{user_uuid}'
        )

        if not result.ok:
            raise requests.ConnectionError(result.status_code)

        return result.json(), result.status_code

    @MyCircuitBreaker(name='reserve_service')
    def get_single_price(self, hotelUid: str) -> tuple[dict, int]:
        hotel_price = requests.get(
            f'{reserve_service}{res_service_port}{reserve_service_path}/hotel_price/{hotelUid}'
        )
        if not hotel_price.ok:
            raise requests.ConnectionError(hotel_price.status_code)

        return hotel_price.json(), hotel_price.status_code

    @MyCircuitBreaker(name='reserve_service')
    def reserve_hotel(self, sub_request: dict):

        result_reservations = requests.post(
            f'{reserve_service}{res_service_port}{reserve_service_path}/reserve_hotel',
            data=json.dumps(sub_request)
        )

        if not result_reservations.ok:
            raise requests.ConnectionError(result_reservations.status_code)

        return result_reservations.json(), result_reservations.status_code

    @MyCircuitBreaker(name='reserve_service')
    def get_info_reservation(self, reservation_uid, user_uuid):
        result_reservations = requests.get(
            f'{reserve_service}{res_service_port}{reserve_service_path}/reservation_info/{reservation_uid}',
            data={
                'user_name': user_uuid
            }
        )
        if not result_reservations.ok:
            raise requests.ConnectionError(result_reservations.status_code)

        return result_reservations.json(), result_reservations.status_code

    @MyCircuitBreaker(name='reserve_hotel')
    def set_reserve_canceled(self, reservation_uid, user_uuid):
        result_reservation = requests.delete(
            f'{reserve_service}{res_service_port}{reserve_service_path}/reservation_info/{reservation_uid}',
            data={
                'user_name': user_uuid
            }
        )
        if not result_reservation.ok:
            raise requests.ConnectionError(result_reservation.status_code)

        return '', result_reservation.status_code


