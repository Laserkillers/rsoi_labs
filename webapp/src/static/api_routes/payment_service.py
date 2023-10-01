import json
from playhouse.shortcuts import model_to_dict
from os import getenv as env

from flask import make_response, request
from uuid import uuid4

from src.static.entities.person import Person

from .. import routes
from . import payment_service_path
from ..entities.payment import Payment

flask_blueprint = routes


@flask_blueprint.route(payment_service_path + '/payments', methods=['GET'])
def get_all_payments():
    return make_response({}, 200)


@flask_blueprint.route(payment_service_path + '/set_pay', methods=['POST'])
def make_pay():

    if len(request.data) == 0:
        request_json = request.form.to_dict()
    else:
        request_json = json.loads(request.data)

    new_pay = Payment()
    new_pay.payment_uid = uuid4()
    new_pay.price = int(request_json['price'])
    new_pay.status = 'PAID'
    new_pay.save()

    return make_response(model_to_dict(new_pay), 201)

