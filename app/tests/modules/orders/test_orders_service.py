from db.models import MenuItem, Order, OrderItem
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
    # Create a menu item to associate with the order
    menu_item = MenuItem(
        name="Special Pizza",
        price=15.99,
        category="Pizza",
        description="A delicious pizza with a special blend of toppings",
        image_base64="base64string",
    )
    test_db.add(menu_item)
    test_db.commit()

    # Create an order and add to the database
    order = Order(delivery_address="123 Main St", phone_number="555-1234", user_id=1)
    test_db.add(order)
    test_db.commit()

    # Create an order item and add it to the order
    order_item = OrderItem(order_id=order.id, menu_item_id=menu_item.id, quantity=2)
    test_db.add(order_item)
    test_db.commit()

    # Make a GET request to fetch orders
    response = customer_client.get("/orders")

    assert response.status_code == status.HTTP_200_OK
    orders_response = response.json()

    # Assertions for the response
    assert len(orders_response) == 1
    assert orders_response[0].get("id") == order.id
    assert orders_response[0].get("delivery_address") == "123 Main St"
    assert orders_response[0].get("phone_number") == "555-1234"
    assert (
        len(orders_response[0].get("items")) == 1
    )  # Checking there is exactly one item in the order
    assert orders_response[0].get("items")[0]["menu_item_id"] == menu_item.id
    assert orders_response[0].get("items")[0]["quantity"] == 2
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
    # Create a menu item to associate with the order
    menu_item = MenuItem(
        name="Deluxe Burger",
        price=9.99,
        category="Burgers",
        description="A large burger with all toppings",
        image_base64="base64string",
    )
    test_db.add(menu_item)
    test_db.commit()

    # Create an order and add to the database
    order = Order(delivery_address="123 Main St", phone_number="555-1234", user_id=1)
    test_db.add(order)
    test_db.commit()

    # Create an order item and add it to the order
    order_item = OrderItem(order_id=order.id, menu_item_id=menu_item.id, quantity=1)
    test_db.add(order_item)
    test_db.commit()

    # Make a GET request to fetch the specific order
    response = customer_client.get(f"/orders/{order.id}")

    assert response.status_code == status.HTTP_200_OK
    order_response = response.json()

    # Assertions for the response
    assert order_response.get("id") == order.id
    assert order_response.get("delivery_address") == "123 Main St"
    assert order_response.get("phone_number") == "555-1234"
    assert order_response.get("user_id") == 1
    assert order_response.get("status") == "Pending"
    assert (
        len(order_response.get("items")) == 1
    )  # Ensure there is one item in the order
    assert order_response.get("items")[0]["menu_item_id"] == menu_item.id
    assert order_response.get("items")[0]["quantity"] == 1


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


def test_create_order_with_multiple_items(customer_client, test_db):
    # Create multiple menu items
    item1 = MenuItem(
        name="Cheese Pizza",
        price=12.00,
        category="Pizza",
        description="Cheesy goodness",
        image_base64="",
    )
    item2 = MenuItem(
        name="Veggie Pizza",
        price=15.00,
        category="Pizza",
        description="Loaded with veggies",
        image_base64="",
    )
    test_db.add_all([item1, item2])
    test_db.commit()

    order_data = {
        "delivery_address": "123 Pizza Street",
        "phone_number": "555-6789",
        "items": [
            {"menu_item_id": item1.id, "quantity": 1},
            {"menu_item_id": item2.id, "quantity": 1},
        ],
    }

    response = customer_client.post("/orders", json=order_data)

    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert len(response_json.get("items")) == 2
    assert response_json.get("delivery_address") == "123 Pizza Street"
    assert response_json.get("phone_number") == "555-6789"


def test_list_multiple_orders(customer_client, test_db):
    # Create and add multiple orders with items
    menu_item = MenuItem(
        name="Burger", price=8.99, description="A tasty burger", image_base64=""
    )
    test_db.add(menu_item)
    test_db.commit()

    order1 = Order(delivery_address="456 Main St", phone_number="555-2345", user_id=1)
    order2 = Order(delivery_address="789 Side St", phone_number="555-5678", user_id=1)
    test_db.add_all([order1, order2])
    test_db.commit()

    order_item1 = OrderItem(order_id=order1.id, menu_item_id=menu_item.id, quantity=2)
    order_item2 = OrderItem(order_id=order2.id, menu_item_id=menu_item.id, quantity=3)
    test_db.add_all([order_item1, order_item2])
    test_db.commit()

    response = customer_client.get("/orders")

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert len(response_json) == 2
    assert response_json[0]["delivery_address"] in ["456 Main St", "789 Side St"]
    assert response_json[1]["delivery_address"] in ["456 Main St", "789 Side St"]


def test_get_individual_orders(customer_client, test_db):
    # Create and add multiple orders with items
    menu_item = MenuItem(
        name="Sandwich", price=5.99, description="Delicious sandwich", image_base64=""
    )
    test_db.add(menu_item)
    test_db.commit()

    order1 = Order(delivery_address="321 New Ave", phone_number="555-4321", user_id=1)
    order2 = Order(delivery_address="654 Old Ave", phone_number="555-8765", user_id=1)
    test_db.add_all([order1, order2])
    test_db.commit()

    order_item1 = OrderItem(order_id=order1.id, menu_item_id=menu_item.id, quantity=1)
    order_item2 = OrderItem(order_id=order2.id, menu_item_id=menu_item.id, quantity=1)
    test_db.add_all([order_item1, order_item2])
    test_db.commit()

    # Fetch each order individually
    for order in [order1, order2]:
        response = customer_client.get(f"/orders/{order.id}")
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json["id"] == order.id
        assert response_json["user_id"] == 1
        assert len(response_json["items"]) == 1
        assert response_json["items"][0]["menu_item_id"] == menu_item.id
        assert response_json["items"][0]["quantity"] == 1
