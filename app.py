"""D&H Meats Website — Flask entry point (port 8000)"""
from app import create_app

application = create_app()

if __name__ == '__main__':
    application.run(host='127.0.0.1', port=8000, debug=True)
