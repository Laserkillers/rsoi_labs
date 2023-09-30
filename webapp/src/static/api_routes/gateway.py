import json
from playhouse.shortcuts import model_to_dict
from os import getenv as env

from flask import make_response, request
import requests

from src.static.entities.person import Person

from src.static import routes
from . import base_path, reserve_service_path

flask_blueprint = routes

# mapping = base_path + '/hotels'

res_service_port = env('RESERVE_PORT')
pay_service_port = env('PAYMENT_PORT')
loy_service_port = env('LOYALTY_PORT')


@flask_blueprint.route(base_path + '/hotels', methods=['GET'])
def get_hotels_from_service():
    params = request.args
    page = int(params.get('page', 1))
    size = int(params.get('size', 1))

    if len(request.data) == 0:
        request_json = request.form.to_dict()
    else:
        request_json = json.loads(request.data)

    result = requests.get(
        f'http://reserve_service:{res_service_port}{reserve_service_path}/hotels',
        params={'page': page, 'size': size}
    )

    if result.status_code != 200:
        return make_response(
            'Smth is incorrect',
            result.status_code
        )

    return make_response(
        result.json(),
        200
    )
