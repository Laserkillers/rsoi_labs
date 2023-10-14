from os import getenv as env
from flask import Blueprint

routes = Blueprint('requests', __name__)

res_service_port = env('RESERVE_PORT')
if res_service_port is None:
    res_service_port = ''

pay_service_port = env('PAYMENT_PORT')
if pay_service_port is None:
    pay_service_port = ''

loy_service_port = env('LOYALTY_PORT')
if loy_service_port is None:
    loy_service_port = ''

reserve_service = env('RESERVATION_SERVICE')
if reserve_service is None:
    reserve_service = 'http://reserve_service'

loyalty_service = env('LOYALTY_SERVICE')
if loyalty_service is None:
    loyalty_service = 'http://loyalty_service'

payment_service = env('PAYMENT_SERVICE')
if payment_service is None:
    payment_service = 'http://payment_service'

max_request_retry = env('MAX_REQUEST_RETRY')
if max_request_retry is None:
    max_request_retry = 5

delay_btw_requests = env('DELAY_BTW_REQUEST')
if delay_btw_requests is None:
    delay_btw_requests = 10

reserve_service_path = '/api/reserve'
payment_service_path = '/api/payment'
loyalty_service_path = '/api/loyalty'

from .api_routes import reserve_service_path, payment_service_path, loyalty_service_path

from src.static.api_routes import *
