import os


ENVIRONMENT = os.environ.get("ENVIRONMENT", "dev")
DEBUG = ENVIRONMENT == "dev"
HOST = '0.0.0.0' if ENVIRONMENT == "prod" else 'localhost'

