from config import settings
from db.base import Base
from db.session import engine
from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from init import load_initial_data
from init_app import init_app


def setup_static_files_and_docs(app: FastAPI):
    """Setup static files and custom documentation endpoints with favicon"""
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/docs", include_in_schema=False)
    def overridden_swagger():
        return get_swagger_ui_html(
            openapi_url=f"{app.root_path}/openapi.json",
            title=settings.TITLE,
            swagger_favicon_url=f"{app.root_path}/static/img/favicon-32x32.png",
        )

    @app.get("/redoc", include_in_schema=False)
    def overridden_redoc():
        return get_redoc_html(
            openapi_url=f"{app.root_path}/openapi.json",
            title=settings.TITLE,
            redoc_favicon_url=f"{app.root_path}/static/img/favicon-32x32.png",
        )


def start_application():
    app = init_app()
    if settings.DB_BACKEND == "memory":
        Base.metadata.create_all(bind=engine)

    setup_static_files_and_docs(app)
    load_initial_data()
    return app


app = start_application()
