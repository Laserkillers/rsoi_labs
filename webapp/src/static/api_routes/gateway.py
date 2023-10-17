import json
from _socket import gaierror
from datetime import datetime
from time import sleep
from functools import wraps
from os import getenv as env
from typing import Callable, Any

import circuitbreaker
import requests

from dateutil.relativedelta import relativedelta
from flask import make_response, request
# from flask_executor import Executor
from urllib3.exceptions import NameResolutionError, MaxRetryError

from src.static import routes
from src.config.program_config import ProgramConfiguration
from . import base_path
from ..requests_to_services import get_data_with_handle
from ..requests_to_services.requests_to_loyalty import RequestsToLoyaltyService
from ..requests_to_services.requests_to_payment import RequestsToPaymentService
from ..requests_to_services.requests_to_reserve import RequestsToReserveService


flask_blueprint = routes


reserve_service_handle = RequestsToReserveService()
loyalty_service_handle = RequestsToLoyaltyService()
payment_service_handle = RequestsToPaymentService()


@flask_blueprint.route(base_path + '/hotels', methods=['GET'])
def get_hotels_from_service():
    params = request.args
    page = int(params.get('page', 1))
    size = int(params.get('size', 1))

    data = get_data_with_handle(reserve_service_handle.get_all_hotels, page, size)
    if not data['success'] and data['status_code'] == 503:
        return make_response(
            data,
            data['status_code']
        )

    if data['status_code'] == 500:
        data = {}
    else:
        data = data['data']

    return make_response(
        data,
        200
    )


@flask_blueprint.route(base_path + '/me', methods=['GET'])
def get_info_about_user():
    user_uuid = request.headers.get('X-User-Name')
    if user_uuid is None or len(user_uuid) == 0:
        return make_response(
            {'message': 'Empty header X-User-Name'},
            400
        )

    result_reservations = get_data_with_handle(reserve_service_handle.get_user_info, user_uuid)
    if not result_reservations['success'] and result_reservations['status_code'] == 503:
        return make_response(
            result_reservations,
            result_reservations['status_code']
        )

    if result_reservations['status_code'] == 500:
        result_reservations = {}
    else:
        result_reservations = result_reservations['data']

    result_loyalty = get_data_with_handle(
        loyalty_service_handle.get_info_about_loyalty,
        user_uuid
    )

    if not result_loyalty['success'] and result_loyalty['status_code'] == 503:
        return make_response(
            result_loyalty,
            result_loyalty['status_code']
        )

    if result_loyalty['status_code'] == 500:
        result_loyalty = {}
    else:
        result_loyalty = result_loyalty['data']

    for reservation in result_reservations:
        result_payment = get_data_with_handle(
            payment_service_handle.get_info_about_payment,
            reservation["payment_uid"]
        )

        if not result_payment['success'] and result_payment['status_code'] == 503:
            return make_response(
                result_payment,
                result_payment['status_code']
            )

        if result_payment['status_code'] == 500:
            result_payment = {}
        else:
            result_payment = result_payment['data']

        reservation['payment'] = result_payment
        del reservation['payment_uid']

    total_result = {
        'reservations': result_reservations,
        'loyalty': result_loyalty
    }

    return make_response(
        total_result,
        200
    )


@flask_blueprint.route(base_path + '/reservations', methods=['GET'])
def get_info_about_reservations():
    user_uuid = request.headers.get('X-User-Name')
    if user_uuid is None or len(user_uuid) == 0:
        return make_response(
            {'message': 'Empty header X-User-Name'},
            400
        )

    result_reservations = get_data_with_handle(reserve_service_handle.get_user_info, user_uuid)
    if not result_reservations['success'] and result_reservations['status_code'] == 503:
        return make_response(
            result_reservations,
            result_reservations['status_code']
        )

    if result_reservations['status_code'] == 500:
        result_reservations = {}
    else:
        result_reservations = result_reservations['data']

    for reservation in result_reservations:
        result_payment = get_data_with_handle(
            payment_service_handle.get_info_about_payment,
            reservation["payment_uid"]
        )

        if not result_payment['success'] and result_payment['status_code'] == 503:
            return make_response(
                result_payment,
                result_payment['status_code']
            )

        if result_payment['status_code'] == 500:
            result_payment = {}
        else:
            result_payment = result_payment['data']

        reservation['payment'] = result_payment
        del reservation['payment_uid']

    return make_response(
        result_reservations,
        200
    )


@flask_blueprint.route(base_path + '/reservations', methods=['POST'])
def reserve_hotel():
    user_uuid = request.headers.get('X-User-Name')
    if user_uuid is None or len(user_uuid) == 0:
        return make_response(
            {'message': 'Empty header X-User-Name'},
            400
        )

    required_fields = {
        'hotelUid': str,
        'startDate': datetime.fromisoformat,
        'endDate': datetime.fromisoformat
    }

    if len(request.data) == 0 and len(request.form) == 0:
        return make_response({
            'message': 'Invalid data',
            'errors': {
                field: 'string' if f_type is str else 'integer' for field, f_type in required_fields.items()
            },
            'entered_data': request.data.decode()
        }, 400)

    if len(request.data) == 0:
        request_json = request.form.to_dict()
    else:
        request_json = json.loads(request.data)

    errors = {}
    for field, f_type in required_fields.items():

        if (value := request_json.get(field)) is None:
            errors[field] = 'string' if f_type is str else 'datetime'
            continue

        try:
            request_json[field] = f_type(value)
        except ValueError:
            errors[field] = 'string' if f_type is str else 'datetime'

    if len(errors.keys()) > 0:
        return make_response({
            'message': 'Invalid data',
            'errors': {
                field: 'string' if f_type is str else 'integer' for field, f_type in errors.items()
            }
        }, 400)

    # Конец проверки данных

    result_loyalty = get_data_with_handle(
        loyalty_service_handle.get_info_about_loyalty,
        user_uuid
    )

    if not result_loyalty['success']:
        return make_response(
            {'message': 'Loyalty Service unavailable'},
            503
        )
    else:
        result_loyalty = result_loyalty['data']

    hotel_price = get_data_with_handle(
        reserve_service_handle.get_single_price,
        request_json["hotelUid"]
    )

    if not hotel_price['success']:
        return make_response(
            hotel_price,
            hotel_price['status_code']
        )

    hotel_price = hotel_price['data']['price']

    loyalty_discount = result_loyalty['discount']
    days = relativedelta(request_json['endDate'], request_json['startDate']).days

    total_price = hotel_price * days * (1 - loyalty_discount / 100)

    # Сделать откат, если свалился расчёт
    result_pay = get_data_with_handle(
        payment_service_handle.set_new_pay,
        int(total_price)
    )

    if not result_pay['success']:
        return make_response(
            result_pay,
            result_pay['status_code']
        )

    result_pay = result_pay['data']

    reservation_info = request_json.copy()
    reservation_info['startDate'] = reservation_info['startDate'].isoformat()
    reservation_info['endDate'] = reservation_info['endDate'].isoformat()

    sub_request = {
        'reservation_info': reservation_info,
        'user_info': result_loyalty,
        'payment_info': result_pay
    }

    result_reservations = get_data_with_handle(
        reserve_service_handle.reserve_hotel,
        sub_request
    )

    if not result_reservations['success']:
        get_data_with_handle(
            payment_service_handle.set_pay_canceled,
            result_reservations["payment_uid"]
        )
        return make_response(
            hotel_price,
            hotel_price['status_code']
        )

    result_reservations = result_reservations['data']

    get_data_with_handle(
        loyalty_service_handle.update_count_reservations,
        user_uuid
    )

    total_result = result_reservations
    total_result['discount'] = loyalty_discount
    total_result['payment'] = result_pay

    total_result['hotelUid'] = total_result['hotel_id']['hotel_uid']
    total_result['reservationUid'] = total_result['reservation_uid']
    del total_result['reservation_uid']
    total_result['startDate'] = total_result['start_date']
    total_result['endDate'] = total_result['end_data']
    del total_result['start_date'], total_result['end_data']

    return make_response(
        total_result,
        200
    )


@flask_blueprint.route(base_path + '/reservations/<reservation_uid>', methods=['GET'])
def get_info_about_reservation(reservation_uid=None):
    user_uuid = request.headers.get('X-User-Name')

    if user_uuid is None or len(user_uuid) == 0:
        return make_response(
            {'message': 'Empty header X-User-Name'},
            400
        )

    result_reservations = get_data_with_handle(
        reserve_service_handle.get_info_reservation,
        reservation_uid,
        user_uuid)

    if not result_reservations['success'] and result_reservations['status_code'] == 503:
        return make_response(
            result_reservations,
            result_reservations['status_code']
        )

    if result_reservations['status_code'] == 500:
        result_reservations = {}
    else:
        result_reservations = result_reservations['data']

    total_result = result_reservations

    if total_result.get("payment_uid") is None:
        result_payment = {}
    else:
        result_payment = get_data_with_handle(
            payment_service_handle.get_info_about_payment,
            total_result["payment_uid"]
        )
        if not result_payment['success'] and result_payment['status_code'] == 503:
            return make_response(
                result_payment,
                result_payment['status_code']
            )

        if result_payment['status_code'] == 500:
            result_payment = {}
        else:
            print(result_payment)
            result_payment = result_payment['data']

    total_result["payment"] = result_payment

    return make_response(
        total_result,
        200
    )


@flask_blueprint.route(base_path + '/reservations/<reservation_uid>', methods=['DELETE'])
def delete_reservation(reservation_uid=None):
    user_uuid = request.headers.get('X-User-Name')

    if user_uuid is None or len(user_uuid) == 0:
        return make_response(
            {'message': 'Empty header X-User-Name'},
            400
        )

    result_reservations = get_data_with_handle(
        reserve_service_handle.get_info_reservation,
        reservation_uid,
        user_uuid
    )

    if not result_reservations['success']:
        return make_response(
            result_reservations,
            result_reservations['status_code']
        )
    else:
        result_reservations = result_reservations['data']

    if len(result_reservations.keys()) == 0:
        return make_response(
            {'message': 'Reservation not found'},
            404
        )

    # payment_uid = result_reservations['payment_uid']

    result_payment = get_data_with_handle(
        payment_service_handle.set_pay_canceled,
        result_reservations["payment_uid"]
    )

    result_reservation = get_data_with_handle(
        reserve_service_handle.set_reserve_canceled,
        reservation_uid,
        user_uuid
    )

    ProgramConfiguration().set_executor(decrement_count_reservations, user_uuid)

    # result_reservation = get_data_with_handle(
    #     loyalty_service_handle.decrement_count_reservations,
    #     user_uuid
    # )

    return make_response(
        '',
        204
    )
# @app.route("/start_background_task/<user_uuid>")
# def start_background_task(user_uuid: str):
#     executor.submit(decrement_count_reservations, user_uuid)


def decrement_count_reservations(user_uuid: str):
    attempts_count = 0
    while True:
        result_reservation = get_data_with_handle(
            loyalty_service_handle.decrement_count_reservations,
            user_uuid
        )
        if result_reservation['success']:
            print(f"Attempt_{attempts_count} is successes")
            break
        print(f"Attempt_{attempts_count} to decrement count reservations")
        attempts_count += 1
        sleep(int(env('DELAY_BTW_REQUEST')))
    return

@flask_blueprint.route(base_path + '/loyalty', methods=['GET'])
def get_info_about_loyalty(reservation_uid=None):
    user_uuid = request.headers.get('X-User-Name')

    if user_uuid is None or len(user_uuid) == 0:
        return make_response(
            {'message': 'Empty header X-User-Name'},
            400
        )

    result_loyalty = get_data_with_handle(
        loyalty_service_handle.get_info_about_loyalty,
        user_uuid
    )

    if not result_loyalty['success']:
        return make_response(
            {'message': 'Loyalty Service unavailable'},
            503
        )
    else:
        result_loyalty = result_loyalty['data']

    return make_response(
        result_loyalty,
        200
    )


