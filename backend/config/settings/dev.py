from .base import *

DEBUG = True
SECRET_KEY = env("SECRET_KEY", default="django-insecure-dev-key")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
