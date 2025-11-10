from apis.auth.utils import get_password_hash
from db.models import DiscountCoupon, MenuItem, Order, OrderItem, User, UserRole
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
    order = Order(delivery_address="123 Main St", phone_number="555-1234", user_id=3)
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


def test_get_order_should_return_200_on_success(customer_client, test_db):
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


def test_get_order_should_return_401_for_unauthenticated(anon_client, test_db):
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

    order1 = Order(delivery_address="456 Main St", phone_number="555-2345", user_id=3)
    order2 = Order(delivery_address="789 Side St", phone_number="555-5678", user_id=3)
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

    order1 = Order(delivery_address="321 New Ave", phone_number="555-4321", user_id=3)
    order2 = Order(delivery_address="654 Old Ave", phone_number="555-8765", user_id=3)
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
        assert response_json["user_id"] == 3
        assert len(response_json["items"]) == 1
        assert response_json["items"][0]["menu_item_id"] == menu_item.id
        assert response_json["items"][0]["quantity"] == 1


def test_create_order_calculates_final_price_without_coupon(customer_client, test_db):
    """Test that final_price is calculated correctly without a coupon."""
    menu_item = MenuItem(
        name="Pizza",
        price=25.00,
        category="Pizza",
        description="Delicious pizza",
        image_base64="",
    )
    test_db.add(menu_item)
    test_db.commit()

    order_data = {
        "delivery_address": "123 Main St",
        "phone_number": "555-1234",
        "items": [{"menu_item_id": menu_item.id, "quantity": 2}],
    }

    response = customer_client.post("/orders", json=order_data)

    assert response.status_code == status.HTTP_201_CREATED
    order_response = response.json()

    # Expected: 25.00 * 2 = 50.00
    assert order_response.get("final_price") == 50.00


def test_create_order_with_valid_coupon_applies_discount(customer_client, test_db):
    """Test that a valid coupon applies discount to order."""
    # Create menu item
    menu_item = MenuItem(
        name="Burger",
        price=10.00,
        category="Burgers",
        description="Tasty burger",
        image_base64="",
    )
    test_db.add(menu_item)
    test_db.commit()

    # Create coupon (20% discount) for the customer
    customer_user = test_db.query(User).filter(User.id == 3).first()
    coupon = DiscountCoupon(
        user_id=customer_user.id,
        referrer_user_id=None,
        discount_percentage=20,
        used=False,
    )
    test_db.add(coupon)
    test_db.commit()

    order_data = {
        "delivery_address": "123 Main St",
        "phone_number": "555-1234",
        "items": [{"menu_item_id": menu_item.id, "quantity": 1}],
        "coupon_id": coupon.id,
    }

    response = customer_client.post("/orders", json=order_data)

    assert response.status_code == status.HTTP_201_CREATED
    order_response = response.json()

    # Expected: 10.00 * 1 = 10.00, with 20% discount = 10.00 - 2.00 = 8.00
    assert order_response.get("final_price") == 8.00


def test_create_order_with_coupon_marks_coupon_as_used(customer_client, test_db):
    """Test that applying a coupon marks it as used."""
    menu_item = MenuItem(
        name="Pizza",
        price=20.00,
        category="Pizza",
        description="Pizza",
        image_base64="",
    )
    test_db.add(menu_item)
    test_db.commit()

    customer_user = test_db.query(User).filter(User.id == 3).first()
    coupon = DiscountCoupon(
        user_id=customer_user.id,
        referrer_user_id=None,
        discount_percentage=10,
        used=False,
    )
    test_db.add(coupon)
    test_db.commit()

    order_data = {
        "delivery_address": "123 Main St",
        "phone_number": "555-1234",
        "items": [{"menu_item_id": menu_item.id, "quantity": 1}],
        "coupon_id": coupon.id,
    }

    customer_client.post("/orders", json=order_data)

    # Refresh coupon from database
    test_db.refresh(coupon)

    assert coupon.used is True
    assert coupon.used_at is not None


def test_create_order_with_already_used_coupon_returns_400(customer_client, test_db):
    """Test that using an already-used coupon returns 400."""
    menu_item = MenuItem(
        name="Item", price=15.00, category="Items", description="Item", image_base64=""
    )
    test_db.add(menu_item)
    test_db.commit()

    customer_user = test_db.query(User).filter(User.id == 3).first()
    coupon = DiscountCoupon(
        user_id=customer_user.id,
        referrer_user_id=None,
        discount_percentage=15,
        used=True,  # Already used
    )
    test_db.add(coupon)
    test_db.commit()

    order_data = {
        "delivery_address": "123 Main St",
        "phone_number": "555-1234",
        "items": [{"menu_item_id": menu_item.id, "quantity": 1}],
        "coupon_id": coupon.id,
    }

    response = customer_client.post("/orders", json=order_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already been used" in response.json().get("detail")


def test_create_order_with_coupon_not_belonging_to_user_returns_404(
    customer_client, test_db
):
    """Test that using someone else's coupon returns 404."""
    menu_item = MenuItem(
        name="Item", price=12.00, category="Items", description="Item", image_base64=""
    )
    test_db.add(menu_item)
    test_db.commit()

    # Create coupon for a different user (not customer)
    other_user = User(
        id=200,
        username="other_user",
        password=get_password_hash("password"),
        first_name="Other",
        last_name="User",
        phone_number="9999",
        role=UserRole.CUSTOMER,
    )
    test_db.add(other_user)
    test_db.commit()

    coupon = DiscountCoupon(
        user_id=other_user.id, referrer_user_id=None, discount_percentage=20, used=False
    )
    test_db.add(coupon)
    test_db.commit()

    order_data = {
        "delivery_address": "123 Main St",
        "phone_number": "555-1234",
        "items": [{"menu_item_id": menu_item.id, "quantity": 1}],
        "coupon_id": coupon.id,
    }

    response = customer_client.post("/orders", json=order_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Coupon not found" in response.json().get("detail")


def test_create_order_with_invalid_coupon_id_returns_404(customer_client, test_db):
    """Test that using a non-existent coupon returns 404."""
    menu_item = MenuItem(
        name="Item", price=10.00, category="Items", description="Item", image_base64=""
    )
    test_db.add(menu_item)
    test_db.commit()

    order_data = {
        "delivery_address": "123 Main St",
        "phone_number": "555-1234",
        "items": [{"menu_item_id": menu_item.id, "quantity": 1}],
        "coupon_id": 99999,  # Non-existent coupon
    }

    response = customer_client.post("/orders", json=order_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Coupon not found" in response.json().get("detail")


def test_create_order_with_multiple_items_calculates_total_price_correctly(
    customer_client, test_db
):
    """Test that final_price is calculated correctly with multiple items and no coupon."""
    item1 = MenuItem(
        name="Pizza",
        price=15.00,
        category="Pizza",
        description="Pizza",
        image_base64="",
    )
    item2 = MenuItem(
        name="Drink",
        price=5.00,
        category="Drinks",
        description="Drink",
        image_base64="",
    )
    test_db.add_all([item1, item2])
    test_db.commit()

    order_data = {
        "delivery_address": "123 Main St",
        "phone_number": "555-1234",
        "items": [
            {"menu_item_id": item1.id, "quantity": 2},
            {"menu_item_id": item2.id, "quantity": 3},
        ],
    }

    response = customer_client.post("/orders", json=order_data)

    assert response.status_code == status.HTTP_201_CREATED
    order_response = response.json()

    # Expected: (15.00 * 2) + (5.00 * 3) = 30.00 + 15.00 = 45.00
    assert order_response.get("final_price") == 45.00


def test_create_order_with_multiple_items_and_coupon_applies_discount_to_total(
    customer_client, test_db
):
    """Test that discount is applied to the total of all items."""
    item1 = MenuItem(
        name="Pizza",
        price=20.00,
        category="Pizza",
        description="Pizza",
        image_base64="",
    )
    item2 = MenuItem(
        name="Salad",
        price=10.00,
        category="Salads",
        description="Salad",
        image_base64="",
    )
    test_db.add_all([item1, item2])
    test_db.commit()

    customer_user = test_db.query(User).filter(User.id == 3).first()
    coupon = DiscountCoupon(
        user_id=customer_user.id,
        referrer_user_id=None,
        discount_percentage=25,  # 25% discount
        used=False,
    )
    test_db.add(coupon)
    test_db.commit()

    order_data = {
        "delivery_address": "123 Main St",
        "phone_number": "555-1234",
        "items": [
            {"menu_item_id": item1.id, "quantity": 1},
            {"menu_item_id": item2.id, "quantity": 1},
        ],
        "coupon_id": coupon.id,
    }

    response = customer_client.post("/orders", json=order_data)

    assert response.status_code == status.HTTP_201_CREATED
    order_response = response.json()

    # Expected: (20.00 + 10.00) = 30.00, with 25% discount = 30.00 - 7.50 = 22.50
    assert order_response.get("final_price") == 22.50


def test_get_order_status_returns_200_for_customer(customer_client, test_db):
    """Test that get_order_status endpoint successfully returns order status."""
    # Create a menu item and order
    menu_item = MenuItem(
        name="Pasta",
        price=12.99,
        category="Main",
        description="Delicious pasta",
        image_base64="",
    )
    test_db.add(menu_item)
    test_db.commit()

    order = Order(
        delivery_address="456 Test St",
        phone_number="555-9999",
        user_id=3,
        status="Pending",
    )
    test_db.add(order)
    test_db.commit()

    order_item = OrderItem(order_id=order.id, menu_item_id=menu_item.id, quantity=1)
    test_db.add(order_item)
    test_db.commit()

    # Call the order status endpoint
    response = customer_client.get(f"/orders/status/{order.id}")

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json.get("order_id") == order.id
    assert response_json.get("status") == "ON_THE_WAY"  # From the simulated service


def test_get_order_status_returns_401_for_unauthenticated(anon_client, test_db):
    """Test that unauthenticated users cannot access order status endpoint."""
    order = Order(
        delivery_address="789 Test Ave",
        phone_number="555-8888",
        user_id=1,
        status="Pending",
    )
    test_db.add(order)
    test_db.commit()

    response = anon_client.get(f"/orders/status/{order.id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json().get("detail") == "Not authenticated"


def test_get_order_status_customer_cannot_access_other_customers_order(
    customer_client, test_db
):
    """Test that customer X cannot access customer Y's order status."""
    # Create another customer (customer Y)
    other_customer = User(
        id=999,
        username="other_customer",
        password=get_password_hash("password"),
        first_name="Other",
        last_name="Customer",
        phone_number="555-0000",
        role=UserRole.CUSTOMER,
    )
    test_db.add(other_customer)
    test_db.commit()

    # Create a menu item
    menu_item = MenuItem(
        name="Burger",
        price=9.99,
        category="Main",
        description="Tasty burger",
        image_base64="",
    )
    test_db.add(menu_item)
    test_db.commit()

    # Create an order for customer Y (user_id=999)
    other_customer_order = Order(
        delivery_address="999 Other St",
        phone_number="555-0000",
        user_id=999,
        status="Pending",
    )
    test_db.add(other_customer_order)
    test_db.commit()

    order_item = OrderItem(
        order_id=other_customer_order.id, menu_item_id=menu_item.id, quantity=1
    )
    test_db.add(order_item)
    test_db.commit()

    # Customer X (id=3) tries to access customer Y's order (id=999)
    response = customer_client.get(f"/orders/status/{other_customer_order.id}")

    # Should return 404 since the order doesn't belong to customer X
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get("detail") == "Order not found"
