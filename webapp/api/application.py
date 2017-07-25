from webapp import nicer_logging
from webapp import settings
from webapp.api import v1
from webapp.api.json_encoder import DateTimeEncoder
from webapp.ids import generate_id
from webapp.implementation.backend import Backend
from webapp.implementation.celery_app import app as celery_app
import flask

LOG = nicer_logging.getLogger(__name__)


__all__ = ['create_app']


def create_app():
    app = _create_app_from_blueprints()
    app.config['RESTFUL_JSON'] = {
            'indent': 4,
            'sort_keys': True,
            'cls': DateTimeEncoder,
    }

    return app


def _create_app_from_blueprints():
    app = flask.Flask('webapp')
    app.register_blueprint(v1.blueprint, url_prefix='/v1')

    @app.before_request
    def before_request():
        correlation_id = generate_id()[:7]  # unique "enough" and short
        flask.g.correlation_id = correlation_id
        try:
            flask.g.backend = Backend(celery_app)
        except:
            LOG.exception("Exception occured while creating backend")
            return flask.jsonify({
                "error": "Internal Server Error: could not create backend"
                }), 500

    @app.teardown_request
    def teardown_request(exception):
        if hasattr(flask.g, 'backend'):
            flask.g.backend.cleanup()

    return app
