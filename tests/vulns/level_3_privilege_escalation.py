import json

from db.models import User, UserRole


def test_privilege_escalation(test_db, customer_client):
    """
    Note:
        Now, the funny part starts!

        I was able to escalate privileges from customer to employee!
        I achieved this via "/users/update_role" API endpoint
        just by changing a role.

        With this role, I can now access the employee restricted endpoints...
        What can I do with these permissions next? :thinking_face:

        btw. my employer didn't respond to my initial findings.
        This API is so vulnerable...

    Possible fix:
        It could be fixed by making sure that only employees
        or Chef can grant Employee role.

        Probably, the fix could be implemented in "apis/users/service.py" file
        in "update_user_role" function - in a similar way as first vuln.
    """

    # here, is the test confirming the vulnerability:
    user = User(
        username="regular_customer",
        password="password",
        first_name="customer",
        last_name="",
        phone_number="1234567890",
        role=UserRole.CUSTOMER,
    )
    test_db.add(user)
    test_db.commit()

    user_update_data = {
        "username": "regular_customer",
        "role": "Employee",
    }

    response = customer_client.put(
        f"/users/update_role", content=json.dumps(user_update_data)
    )
    assert response.status_code == 200
    assert user.role == "Employee"  # I was able to escalate from customer to employee!
