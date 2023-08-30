from typing import Union

from apis.router import api_router
from db.base import Base
from db.models import *
from db.session import engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from init import load_initial_data


def start_application():
    app = FastAPI(
        title="Damn Vulnerable RESTaurant",
        description="An intentionally vulnerable API service designed for learning and training purposes for ethical hackers, security engineers, and developers.",
        version="1.0.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)
    load_initial_data()
    return app


app = start_application()
