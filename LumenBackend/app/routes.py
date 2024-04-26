import os
from .endpoints import prediction_endpoints, file_endpoints


def init_app(app):
    app.register_blueprint(
        prediction_endpoints.predict_blueprint,
        url_prefix="/predict",
    )
    app.register_blueprint(
        file_endpoints.file_blueprint,
        url_prefix="/file",
    )
