from init import load_initial_data
from init_app import init_app


def start_application():
    app = init_app()
    load_initial_data()
    return app


app = start_application()
