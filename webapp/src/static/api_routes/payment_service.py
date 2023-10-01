import json
from playhouse.shortcuts import model_to_dict
from os import getenv as env

from flask import make_response, request

from src.static.entities.person import Person

from . import routes, payment_service_path

flask_blueprint = routes


@flask_blueprint.route(payment_service_path + '/payments', methods=['GET'])
def get_all_payments():
    return make_response({}, 200)