from flask import jsonify
from flask_executor import Executor

from src.config.flask_config import ServerConfiguration
from src.config.program_config import ProgramConfiguration
from src.static import routes, loyalty_service_handle
from os import getenv as env
from time import sleep

orig_app = ServerConfiguration('gunicorn').app
orig_app.register_blueprint(routes)

app = orig_app
executor = Executor(app)

app_config = ProgramConfiguration(executor)


@app.route("/")
def start_page():
    return jsonify(hello="world", first_message="test")
