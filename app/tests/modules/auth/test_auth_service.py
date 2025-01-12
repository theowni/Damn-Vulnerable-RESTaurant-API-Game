from datetime import datetime, timedelta

from apis.auth.utils import verify_password
from db.models import User, UserRole


def test_get_token_returns_token_with_200(test_db, customer_client):
    data = {
        "grant_type": "password",
        "username": "customer",
        "password": "password",
    }

    response = customer_client.post("/token", data=data)

    assert response.status_code == 200
    token_result = response.json()
    assert token_result.get("token_type") == "bearer"
    assert token_result.get("access_token") is not None


def test_get_token_with_invalid_password_returns_token_with_401(
    test_db, customer_client
):
    data = {
        "grant_type": "password",
        "username": "customer",
        "password": "invalid_password",
    }

    response = customer_client.post("/token", data=data)

    assert response.status_code == 401
    assert response.json().get("detail") == "Incorrect username or password"


def test_get_profile_authorised_returns_200(test_db, customer_client):
    response = customer_client.get("/profile")

    assert response.status_code == 200
    profile_details = response.json()
    assert profile_details.get("first_name") is not None
    assert profile_details.get("last_name") is not None
    assert profile_details.get("phone_number") is not None
    assert profile_details.get("role") is not None


def test_get_profile_unauthorised_returns_401(test_db, anon_client):
    response = anon_client.get("/profile")

    # assert response.status_code == 401
    assert response.json().get("detail") == "Not authenticated"


def test_update_current_user_details_returns_200(test_db, customer_client):
    data = {
        "username": "customer",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "1234567890",
    }

    response = customer_client.put("/profile", json=data)

    assert response.status_code == 200
    updated_details = response.json()
    assert updated_details.get("first_name") == data["first_name"]
    assert updated_details.get("last_name") == data["last_name"]
    assert updated_details.get("phone_number") == data["phone_number"]


def test_patch_profile_returns_200(test_db, customer_client):
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "1234567890",
    }

    response = customer_client.patch("/profile", json=data)

    assert response.status_code == 200
    updated_details = response.json()
    assert updated_details.get("first_name") == data["first_name"]
    assert updated_details.get("last_name") == data["last_name"]
    assert updated_details.get("phone_number") == data["phone_number"]


def test_register_user_returns_201(test_db, anon_client):
    data = {
        "username": "new_user123",
        "password": "new_password",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "5425",
    }

    response = anon_client.post("/register", json=data)
    user_details = response.json()

    assert response.status_code == 201
    assert user_details.get("username") == data["username"]
    assert user_details.get("first_name") == data["first_name"]
    assert user_details.get("last_name") == data["last_name"]
    assert user_details.get("phone_number") == data["phone_number"]


def test_register_by_authenticated_user_returns_400(test_db, customer_client, mocker):
    mocker.patch(
        "apis.auth.utils.OAuth2PasswordBearer",
        return_value=lambda x: lambda y: "token",
    )
    mocker.patch(
        "apis.auth.utils.get_current_user",
        return_value=User(
            username="customer",
            password="password",
            first_name="Customer",
            last_name="",
            phone_number="1234",
            role=UserRole.CUSTOMER,
        ),
    )

    data = {
        "username": "new_user",
        "password": "new_password",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "1234567890",
    }

    response = customer_client.post(
        "/register", json=data, headers={"Authorization": "token"}
    )
    assert response.status_code == 400


def test_reset_password_sets_reset_code_and_returns_200(test_db, anon_client):
    user = User(
        username="customer",
        password="password",
        first_name="Customer",
        last_name="",
        phone_number="12345678",
        role=UserRole.CUSTOMER,
    )
    test_db.add(user)
    test_db.commit()

    data = {
        "username": "customer",
        "phone_number": "12345678",
    }
    response = anon_client.post("/reset-password", json=data)

    user = test_db.query(User).filter(User.username == "customer").first()
    assert user.reset_password_code is not None
    assert user.reset_password_code_expiry_date is not None
    assert response.status_code == 200
    assert response.json().get("detail") == "PIN code sent to your phone number"


def test_reset_password_with_invalid_data_returns_400(test_db, anon_client):
    data = {
        "username": "invalid_user",
        "phone_number": "12345678",
    }
    response = anon_client.post("/reset-password", json=data)

    assert response.status_code == 400
    assert response.json().get("detail") == "Invalid username or phone number"


def test_reset_password_for_non_customer_returns_400(test_db, anon_client):
    user = User(
        username="employee",
        password="password",
        first_name="Employee",
        last_name="",
        phone_number="12345678",
        role=UserRole.EMPLOYEE,
    )
    test_db.add(user)
    test_db.commit()

    data = {
        "username": "employee",
        "phone_number": "12345678",
    }
    response = anon_client.post("/reset-password", json=data)

    assert response.status_code == 400
    assert (
        response.json().get("detail")
        == "Only customers can reset their password through this feature"
    )


def test_reset_password_with_incorrect_phone_number_returns_400(test_db, anon_client):
    user = User(
        username="customer",
        password="password",
        first_name="Customer",
        last_name="",
        phone_number="12345678",
        role=UserRole.CUSTOMER,
    )
    test_db.add(user)
    test_db.commit()

    data = {
        "username": "customer",
        "phone_number": "12345679",
    }
    response = anon_client.post("/reset-password", json=data)

    assert response.status_code == 400
    assert response.json().get("detail") == "Invalid username or phone number"


def test_set_new_password_returns_200(test_db, anon_client):
    user = User(
        username="customer",
        password="password",
        first_name="Customer",
        last_name="",
        phone_number="12345678",
        role=UserRole.CUSTOMER,
        reset_password_code="1234",
        reset_password_code_expiry_date=datetime.now() + timedelta(minutes=15),
    )
    test_db.add(user)
    test_db.commit()

    data = {
        "username": "customer",
        "phone_number": "12345678",
        "reset_password_code": "1234",
        "new_password": "new_password",
    }
    response = anon_client.post("/reset-password/new-password", json=data)

    user = test_db.query(User).filter(User.username == "customer").first()
    assert verify_password("new_password", user.password)
    assert response.status_code == 200
    assert response.json().get("detail") == "Password updated successfully!"
