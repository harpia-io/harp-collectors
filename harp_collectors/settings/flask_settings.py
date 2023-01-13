import os

# Flask settings
SERVER_NAME = os.getenv('SERVER_NAME', '0.0.0.0')
SERVER_PORT = os.getenv('SERVER_PORT', 8081)
FLASK_THREADED = os.getenv('FLASK_THREADED', True)
FLASK_DEBUG = os.getenv('FLASK_DEBUG', False)
URL_PREFIX = os.getenv('URL_PREFIX', '/api/v1')
SERVICE_NAMESPACE = os.getenv('SERVICE_NAMESPACE', 'dev')

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = os.getenv('RESTPLUS_SWAGGER_UI_DOC_EXPANSION', 'list')
RESTPLUS_VALIDATE = os.getenv('RESTPLUS_VALIDATE', True)
RESTPLUS_MASK_SWAGGER = os.getenv('RESTPLUS_MASK_SWAGGER', False)
RESTPLUS_ERROR_404_HELP = os.getenv('RESTPLUS_ERROR_404_HELP', False)


SERVICE_NAME = os.getenv('SERVICE_NAME', 'harpia-collectors')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOKI_SERVER = os.getenv('LOKI_SERVER', '127.0.0.1')
LOKI_PORT = os.getenv('LOKI_PORT', 3100)


class TracingConfig:
    TEMPO_URL = os.getenv('TEMPO_URL', '')