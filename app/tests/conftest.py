import os
import sys
from typing import Any, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# this is to include app dir in sys.path so that we can import from db,main.py

from init_app import init_app

# disable tests caching
sys.dont_write_bytecode = True

from apis.auth.utils import get_current_user, get_password_hash
from apis.router import api_router
from db.base import Base

# from main import app
from db.models import User, UserRole
from db.session import get_db

SQLALCHEMY_DATABASE_URL = "sqlite://"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def app():
    app = init_app()
    return app


@pytest.fixture(scope="function")
def test_db():
    db = TestingSessionLocal()
    Base.metadata.create_all(bind=engine)
    yield db
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def anon_client(app, test_db: TestingSessionLocal) -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """
    app.dependency_overrides[get_db] = lambda: test_db

    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def customer_client(
    app, test_db: TestingSessionLocal
) -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """
    user = User(
        id=3,
        username="customer",
        password=get_password_hash("password"),
        first_name="Customer",
        last_name="",
        phone_number="1234",
        role=UserRole.CUSTOMER,
    )
    test_db.add(user)
    test_db.commit()

    app.dependency_overrides[get_db] = lambda: test_db
    app.dependency_overrides[get_current_user] = lambda: user

    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def employee_client(
    app, test_db: TestingSessionLocal
) -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """
    user = User(
        id=2,
        username="employee",
        password=get_password_hash("password"),
        first_name="Employee",
        last_name="",
        phone_number="12345",
        role=UserRole.EMPLOYEE,
    )
    test_db.add(user)
    test_db.commit()

    app.dependency_overrides[get_db] = lambda: test_db
    app.dependency_overrides[get_current_user] = lambda: user

    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def chef_client(app, test_db: TestingSessionLocal) -> Generator[TestClient, Any, None]:
    """
    Create a new FastAPI TestClient that uses the `db_session` fixture to override
    the `get_db` dependency that is injected into routes.
    """
    user = User(
        id=1,
        username="chef",
        password=get_password_hash("password"),
        first_name="Chef",
        last_name="",
        phone_number="123456",
        role=UserRole.CHEF,
    )
    test_db.add(user)
    test_db.commit()

    app.dependency_overrides[get_db] = lambda: test_db
    app.dependency_overrides[get_current_user] = lambda: user

    with TestClient(app) as client:
        yield client
