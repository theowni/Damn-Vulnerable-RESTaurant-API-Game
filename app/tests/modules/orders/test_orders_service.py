from db.models import MenuItem, Order
from fastapi import status


def test_create_order_succesfully_returns_201(customer_client, test_db):
    menu_item = MenuItem(
        name="Item", price=10.99, category="", description="", image_base64=""
    )
    test_db.add(menu_item)
    test_db.commit()

    order_data = {
        "delivery_address": "123 Main St",
        "phone_number": "555-1234",
        "items": [{"menu_item_id": menu_item.id, "quantity": 2}],
    }

    response = customer_client.post(
        "/orders",
        json=order_data,
    )

    assert response.status_code == status.HTTP_201_CREATED
    orders_response = response.json()

    assert orders_response.get("id") is not None
    assert orders_response.get("delivery_address") == "123 Main St"
    assert orders_response.get("phone_number") == "555-1234"
    assert orders_response.get("items") == order_data["items"]
    assert orders_response.get("user_id") is not None
    assert orders_response.get("status") == "Pending"


def test_create_order_with_invalid_menu_item_id_returns_404(customer_client, test_db):
    order_data = {
        "delivery_address": "123 Main St",
        "phone_number": "555-1234",
        "items": [{"menu_item_id": 999, "quantity": 2}],
    }

    response = customer_client.post(
        "/orders",
        json=order_data,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get("detail") == "Menu item with ID 999 not found"


def test_create_order_with_invalid_quantity_returns_422(customer_client, test_db):
    menu_item = MenuItem(
        name="Item", price=10.99, category="", description="", image_base64=""
    )
    test_db.add(menu_item)
    test_db.commit()

    order_data = {
        "delivery_address": "123 Main St",
        "phone_number": "555-1234",
        "items": [{"menu_item_id": menu_item.id, "quantity": -1}],
    }

    response = customer_client.post(
        "/orders",
        json=order_data,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json().get("detail") == "Quantity must be greater than 0"


def test_create_order_unauthorised_returns_401(anon_client):
    response = anon_client.post("/orders")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json().get("detail") == "Not authenticated"


def test_get_orders_returns_one_item_with_200(customer_client, test_db):
    order = Order(delivery_address="123 Main St", phone_number="555-1234", user_id=1)
    test_db.add(order)
    test_db.commit()

    response = customer_client.get("/orders")

    assert response.status_code == status.HTTP_200_OK
    orders_response = response.json()

    assert len(orders_response) == 1
    assert orders_response[0].get("id") == order.id
    assert orders_response[0].get("delivery_address") == "123 Main St"
    assert orders_response[0].get("phone_number") == "555-1234"
    assert orders_response[0].get("items") == []
    assert orders_response[0].get("user_id") is not None
    assert orders_response[0].get("status") == "Pending"


def test_get_orders_empty_returns_empty_list_with_200(customer_client):
    response = customer_client.get("/orders")

    assert response.status_code == status.HTTP_200_OK
    orders_response = response.json()

    assert len(orders_response) == 0


def test_get_orders_unauthorised_returns_401(anon_client):
    response = anon_client.get("/orders")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json().get("detail") == "Not authenticated"


def test_get_order_succesfully_returns_200(customer_client, test_db):
    order = Order(delivery_address="123 Main St", phone_number="555-1234", user_id=1)
    test_db.add(order)
    test_db.commit()

    response = customer_client.get(f"/orders/{order.id}")

    assert response.status_code == status.HTTP_200_OK
    order_response = response.json()

    assert order_response.get("id") == order.id
    assert order_response.get("delivery_address") == "123 Main St"
    assert order_response.get("phone_number") == "555-1234"
    assert order_response.get("items") == []
    assert order_response.get("user_id") is not None
    assert order_response.get("status") == "Pending"


def test_get_order_unauthorised_returns_401(anon_client, test_db):
    order = Order(delivery_address="123 Main St", phone_number="555-1234", user_id=1)
    test_db.add(order)
    test_db.commit()

    response = anon_client.get(f"/orders/{order.id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json().get("detail") == "Not authenticated"


def test_get_order_not_exist_returns_404(customer_client):
    response = customer_client.get("/orders/999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get("detail") == "Order not found"
