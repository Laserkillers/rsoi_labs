import json
from playhouse.shortcuts import model_to_dict
from os import getenv as env

from flask import make_response, request

from src.static.entities.loyalty import Loyalty
from src.static.entities.person import Person

from . import routes, loyalty_service_path

flask_blueprint = routes


@flask_blueprint.route(loyalty_service_path + '/loyalty', methods=['GET'])
def get_all_loyalty():
    return make_response({}, 200)


@flask_blueprint.route(loyalty_service_path + '/user_info/<user_uuid>')
def get_user_loyalty_info(user_uuid=None):
    if user_uuid is None:
        return make_response(
            {'message': 'Empty response'},
            400
        )

    res_loyalty = Loyalty.get(Loyalty.username == user_uuid)

    return make_response(
        model_to_dict(res_loyalty),
        200
    )