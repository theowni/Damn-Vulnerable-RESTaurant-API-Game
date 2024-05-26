import json

from db.models import MenuItem


def test_get_menu_returns_200_with_data(test_db, anon_client):
    menu_item1 = MenuItem(
        name="Item 1", price=10.99, category="", description="", image_base64=""
    )
    menu_item2 = MenuItem(
        name="Item 2", price=15.99, category="", description="", image_base64=""
    )
    test_db.add(menu_item1)
    test_db.add(menu_item2)
    test_db.commit()

    response = anon_client.get("/menu")
    assert response.status_code == 200

    menu_items = response.json()
    assert len(menu_items) == 2
    assert menu_items[0]["name"] == "Item 1"
    assert menu_items[0]["price"] == 10.99
    assert menu_items[1]["name"] == "Item 2"
    assert menu_items[1]["price"] == 15.99


def test_create_menu_item_by_employee_or_chef_returns_201(
    test_db, employee_client, chef_client
):
    menu_item_data = {
        "name": "Item 3",
        "price": 20.99,
        "category": "",
        "description": "",
        "image_url": "",
    }
    response = employee_client.put("/menu", content=json.dumps(menu_item_data))
    assert response.status_code == 201

    menu_item_data = {
        "name": "Item 3",
        "price": 20.99,
        "category": "",
        "description": "",
        "image_url": "",
    }
    response = chef_client.put("/menu", content=json.dumps(menu_item_data))
    assert response.status_code == 201


def test_delete_menu_item_by_employee_or_chef_returns_204(
    test_db, employee_client, chef_client
):
    menu_item = MenuItem(
        name="Item", price=10.99, category="", description="", image_base64=""
    )
    test_db.add(menu_item)
    test_db.commit()
    response = employee_client.delete(f"/menu/{menu_item.id}")
    assert response.status_code == 204

    menu_item = MenuItem(
        name="Item", price=10.99, category="", description="", image_base64=""
    )
    test_db.add(menu_item)
    test_db.commit()
    response = chef_client.delete(f"/menu/{menu_item.id}")
    assert response.status_code == 204


def test_delete_menu_item_by_employee_or_chef_returns_204(
    test_db, employee_client, chef_client
):
    menu_item = MenuItem(
        name="Item", price=10.99, category="", description="", image_base64=""
    )
    test_db.add(menu_item)
    test_db.commit()
    response = employee_client.delete(f"/menu/{menu_item.id}")
    assert response.status_code == 204

    menu_item = MenuItem(
        name="Item", price=10.99, category="", description="", image_base64=""
    )
    test_db.add(menu_item)
    test_db.commit()
    response = chef_client.delete(f"/menu/{menu_item.id}")
    assert response.status_code == 204


def test_delete_menu_item_by_unauthorized_user_returns_401(test_db, anon_client):
    menu_item = MenuItem(
        name="Item", price=10.99, category="", description="", image_base64=""
    )
    test_db.add(menu_item)
    test_db.commit()
    response = anon_client.delete(f"/menu/{menu_item.id}")
    # validating response status code
    assert response.status_code == 401
    # validating if menu item still exists in db
    assert test_db.query(MenuItem).count() == 1
