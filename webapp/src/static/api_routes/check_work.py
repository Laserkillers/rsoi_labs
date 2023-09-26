from src.static import routes
from . import base_path

flask_blueprint = routes

mapping = base_path + '/check_status'


@flask_blueprint.route(mapping, methods=['GET', 'POST'])
def send_message():
    return {
        'status': 'working'
    }
