"""WSGI entry point for PythonAnywhere deployment."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from init_db import init

init()
application = create_app()
