import os
from flask import Flask

from app.utils.model_utils import load_model
from . import routes
from flask_cors import CORS


def create_app():
    app = Flask(__name__)

    app.config["MODEL"] = load_model("models/model.joblib")

    cors = CORS(
        app,
        resources={r"/*": {"origins": "http://localhost:3000"}},
        supports_credentials=True,
    )
    routes.init_app(app)

    UPLOAD_FOLDER = "storage/"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    return app
