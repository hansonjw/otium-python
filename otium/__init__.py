import os
from flask import Flask
from . import db

import os
import re

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    uri = os.getenv("DATABASE_URL")
    if uri is not None and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    app.config.from_mapping(
        SECRET_KEY = "Super Secret",
        SQLALCHEMY_DATABASE_URI = uri or 'sqlite:///./../instance/otium.db',
        SQLALCHEMY_TRACK_MODIFICATIONS = False
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # import modules for blueprints

    from .routes import market
    app.register_blueprint(market.bp)

    from . import db
    db.init_app(app)

    return app