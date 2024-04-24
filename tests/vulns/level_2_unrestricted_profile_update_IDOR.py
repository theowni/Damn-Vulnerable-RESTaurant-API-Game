import json

from db.models import User, UserRole


def test_unrestricted_profile_update_idor(test_db, customer_client):
    """
    Note:
        Holly molly, I found another vulnerability!

        Chef would be mad at me for this one...
        It's possible to modify any profile's details by providing username
        in HTTP request sent to "/profile" endpoint with PUT method.
        I could change anyone's phone number and other details so easily!

    Possible fix:
        Probably, it could be fixed by making sure that "current_user"
        is authorised to perform updates only in own profile.

        The fix could be implemented in "update_current_user_details"
        function in "apis/auth/service.py" file.
    """

    # here, is the test confirming the vulnerability:
    user = User(
        username="victim",
        password="password",
        first_name="victim",
        last_name="",
        phone_number="1234567890",
        role=UserRole.CUSTOMER,
    )
    test_db.add(user)
    test_db.commit()

    user_update_data = {
        "username": "victim",
        "first_name": "smile",
        "last_name": "chef",
        "phone_number": "123",
    }

    response = customer_client.put(f"/profile", content=json.dumps(user_update_data))
    assert response.status_code == 200
    assert (
        user.first_name == "smile"
    )  # I was able to change the first name of the user :)
    assert user.last_name == "chef"  # ...and the last name of the user
    assert user.phone_number == "123"  # ...and the phone number too
