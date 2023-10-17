import requests
from . import *


class RequestsToPaymentService:
    def __new__(cls, *args, **kwargs):
        if getattr(cls, '_instance', None) is None:
            cls._instance = super(RequestsToPaymentService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    @MyCircuitBreaker(name='payment_service')
    def get_info_about_payment(self, payment_uid: str):
        result_payment = requests.get(
            f'{payment_service}{pay_service_port}{payment_service_path}/payment/{payment_uid}'
        )

        if not result_payment.ok:
            raise requests.ConnectionError(result_payment.status_code)

        return result_payment.json(), result_payment.status_code

    @MyCircuitBreaker(name='payment_service')
    def set_new_pay(self, total_price: int):
        result_pay = requests.post(
            f'{payment_service}{pay_service_port}{payment_service_path}/set_pay',
            data={
                'price': total_price
            }
        )
        if not result_pay.ok:
            raise requests.ConnectionError(result_pay.status_code)

        return result_pay.json(), result_pay.status_code

    @MyCircuitBreaker(name='payment_service')
    def set_pay_canceled(self, payment_uid: str):
        result_payment = requests.delete(
            f'{payment_service}{pay_service_port}{payment_service_path}/payment/{payment_uid}'
        )
        if not result_payment.ok:
            raise requests.ConnectionError(result_payment.status_code)

        return '', result_payment.status_code



