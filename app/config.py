import os
import random
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)
from enum import Enum


class ENV(Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


ENVIRONMENT = ENV(os.getenv("ENV", ENV.PRODUCTION.value))


# 6 digits random secrets are secure enough,
# I don't believe someone could brute-force them
def generate_random_secret():
    return "".join(random.choices("1234567890", k=6))


class Settings:
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", generate_random_secret())
    CHEF_USERNAME = os.getenv("CHEF_USERNAME", "chef")

    # someone needs to remember to set this variable to True in env variables
    JWT_VERIFY_SIGNATURE = os.getenv("JWT_VERIFY_SIGNATURE")

    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "admin")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", 5432)
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "restaurant")

    TITLE: str = "Damn Vulnerable RESTaurant"
    DESCRIPTION: str = (
        "An intentionally vulnerable API service designed for learning and training purposes for ethical hackers, security engineers"
        ", and developers."
    )
    VERSION: str = "1.0.0"

    # Allow switching between Postgres (default) and in-memory SQLite.
    # This keeps Postgres as the default behavior while enabling
    # self-contained in-memory runs when DB_BACKEND=memory is set.
    DB_BACKEND: str = os.getenv("DB_BACKEND", "postgres")

    @property
    def DATABASE_URL(self) -> str:
        if self.DB_BACKEND == "memory":
            return "sqlite://"
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def SERVER_URL(self) -> str:
        return "http://localhost:8091/"

    @property
    def SERVERS(self) -> list[dict]:
        return [{"url": self.SERVER_URL, "description": self.SERVER_DESCRIPTION}]

    @property
    def ROOT_PATH(self) -> str:
        return ""

    @property
    def SERVER_DESCRIPTION(self) -> str:
        return "Local API server"


settings = Settings()
