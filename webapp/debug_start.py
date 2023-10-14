from src.config.flask_config import ServerConfiguration

if __name__ == "__main__":
    app = ServerConfiguration('debug')
    app.run()