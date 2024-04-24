from db.models import MenuItem


def test_unrestricted_menu_item_deletion(test_db, customer_client):
    """
    Note:
        The previous vulnerability was just a low severity issue but
        allowed me to understand the application's technology better.

        After several minutes with the app, I already found much more
        interesting vulnerability!
        It looks like Chef forgot to add authorisation checks to "/menu/{id}"
        API endpoint and anyone can use DELETE method to delete items
        from the menu!

    Possible fix:
        Probably, it could be fixed in "delete_menu_item" function in
        "apis/menu/service.py" file by adding auth=Depends(...) with proper
        roles checks.
        There is an example implementation of authorisation checks in
        "update_menu_item" function.
    """

    # here, is the test confirming the vulnerability:
    menu_item = MenuItem(
        name="Chicken Burrito",
        price=10.99,
        category="",
        description="",
        image_base64="",
    )
    test_db.add(menu_item)
    test_db.commit()

    response = customer_client.delete(f"/menu/{menu_item.id}")
    assert response.status_code == 204
