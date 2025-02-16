from init_app import init_app
from init import load_initial_data


def start_application():
    app = init_app()
    load_initial_data()
    return app

app = start_application()
