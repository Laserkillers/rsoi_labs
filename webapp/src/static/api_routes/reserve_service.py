import json
from datetime import datetime

from playhouse.shortcuts import model_to_dict
from os import getenv as env
from uuid import uuid4

from flask import make_response, request

from src.static.entities.person import Person

from . import reserve_service_path
from .. import routes
from ..entities.hotels import Hotels
from ..entities.reservation import Reservation

flask_blueprint = routes


@flask_blueprint.route(reserve_service_path + '/hotels', methods=['GET'])
def get_all_hotels():
    params = request.args
    page = int(params.get('page', 1))
    size = int(params.get('size', 1))

    hotels = Hotels.select().dicts()

    result = [
        value for value in hotels
    ]

    result = result[((page - 1) * size):(page * size)]

    response = {
        "page": page,
        "pageSize": size,
        "totalElements": len(result),
        "items": result
    }

    return make_response(
        response,
        200)


@flask_blueprint.route(reserve_service_path + '/user_info/<user_uuid>')
def get_info_by_user_id(user_uuid=None):
    if user_uuid is None:
        return make_response(
            {'message': 'Empty response'},
            400
        )
    reservations = Reservation.select().join(Hotels).where(Reservation.username == user_uuid).dicts()
    return [
        value for value in reservations
    ]


@flask_blueprint.route(reserve_service_path + '/hotel_price/<hotel_uuid>')
def get_hotel_price(hotel_uuid=None):
    if hotel_uuid is None:
        return make_response(
            {'message': 'Empty response'},
            400
        )
    hotel = Hotels.get(Hotels.hotel_uid == hotel_uuid)
    return {
        'price': hotel.price
    }


@flask_blueprint.route(reserve_service_path + '/reserve_hotel', methods=['POST'])
def reserve_hotel_service():
    if len(request.data) != 0:
        request_json = json.loads(request.data)
    else:
        request_json = request.form.to_dict()

    reservation_info = request_json['reservation_info']
    hotel_uuid = reservation_info['hotelUid']
    start_date = datetime.fromisoformat(reservation_info['startDate'])
    end_date = datetime.fromisoformat(reservation_info['endDate'])

    user_info = request_json['user_info']
    username = user_info['username']

    payment_info = request_json['payment_info']
    payment_uid = payment_info['payment_uid']

    hotel = Hotels.get(Hotels.hotel_uid == hotel_uuid)
    hotel = model_to_dict(hotel)

    reserve_row = Reservation()
    reserve_row.reservation_uid = uuid4()
    reserve_row.username = username
    reserve_row.status = 'PAID'
    reserve_row.payment_uid = payment_uid
    reserve_row.start_date = start_date
    reserve_row.end_data = end_date
    reserve_row.hotel_id = hotel['id']
    reserve_row.save()

    reserve_row.start_date = start_date.strftime("%Y-%m-%d")
    reserve_row.end_data = end_date.strftime("%Y-%m-%d")

    return make_response(model_to_dict(reserve_row), 201)

