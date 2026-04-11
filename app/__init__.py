from flask import Flask

def create_app():
    app = Flask(__name__)

    from app.db import init_db
    init_db()

    from app.routes import main
    app.register_blueprint(main)

    return app