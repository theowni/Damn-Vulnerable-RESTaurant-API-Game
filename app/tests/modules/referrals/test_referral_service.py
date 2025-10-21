from apis.auth.utils import get_password_hash
from db.models import DiscountCoupon, User, UserRole


def test_get_referral_code_returns_200(test_db, customer_client):
    """Test that getting a referral code returns 200 and a code."""
    response = customer_client.get("/referral-code")

    assert response.status_code == 200
    data = response.json()
    assert data.get("code") is not None
    assert len(data.get("code")) == 8


def test_get_referral_code_returns_same_code_on_second_call(test_db, customer_client):
    """Test that getting a referral code twice returns the same code."""
    response1 = customer_client.get("/referral-code")
    code1 = response1.json().get("code")

    response2 = customer_client.get("/referral-code")
    code2 = response2.json().get("code")

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert code1 == code2


def test_get_referral_code_unauthorised_returns_401(test_db, anon_client):
    """Test that unauthenticated request returns 401."""
    response = anon_client.get("/referral-code")

    assert response.status_code == 401


def test_apply_referral_code_returns_200(test_db, customer_client):
    """Test that applying a valid referral code returns 200."""
    # Create a second user with a referral code
    referrer = User(
        id=100,
        username="referrer",
        password=get_password_hash("password"),
        first_name="Referrer",
        last_name="",
        phone_number="9999",
        role=UserRole.CUSTOMER,
        referral_code="ABC12345",
    )
    test_db.add(referrer)
    test_db.commit()

    # Apply the referral code
    data = {"referral_code": "ABC12345"}
    response = customer_client.post("/apply-referral", json=data)

    assert response.status_code == 200
    result = response.json()
    assert result.get("discount") == 20
    assert "applied successfully" in result.get("message")


def test_apply_referral_code_invalid_returns_200_with_zero_discount(
    test_db, customer_client
):
    """Test that applying an invalid referral code returns 200 with zero discount."""
    data = {"referral_code": "INVALID00"}
    response = customer_client.post("/apply-referral", json=data)

    assert response.status_code == 200
    result = response.json()
    assert result.get("discount") == 0.0
    assert "Invalid referral code" in result.get("message")


def test_apply_referral_code_creates_discount_coupon(test_db, customer_client):
    """Test that applying a referral code creates a discount coupon record."""
    # Create a referrer user
    referrer = User(
        id=101,
        username="referrer2",
        password=get_password_hash("password"),
        first_name="Referrer",
        last_name="",
        phone_number="8888",
        role=UserRole.CUSTOMER,
        referral_code="XYZ98765",
    )
    test_db.add(referrer)
    test_db.commit()

    # Apply the referral code
    data = {"referral_code": "XYZ98765"}
    response = customer_client.post("/apply-referral", json=data)

    assert response.status_code == 200

    # Check that a discount coupon was created
    coupon = (
        test_db.query(DiscountCoupon)
        .filter(DiscountCoupon.referrer_user_id == referrer.id)
        .first()
    )
    assert coupon is not None
    assert coupon.discount_percentage == 20
    assert coupon.used is False


def test_get_discount_coupons_returns_200(test_db, customer_client):
    """Test that getting discount coupons returns 200."""
    response = customer_client.get("/discount-coupons")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_discount_coupons_returns_user_coupons(test_db, customer_client):
    """Test that getting discount coupons returns only user's coupons."""
    # Create a referrer user
    referrer = User(
        id=103,
        username="referrer4",
        password=get_password_hash("password"),
        first_name="Referrer",
        last_name="",
        phone_number="6666",
        role=UserRole.CUSTOMER,
        referral_code="GHI89012",
    )
    test_db.add(referrer)
    test_db.commit()

    # Apply the referral code
    data = {"referral_code": "GHI89012"}
    customer_client.post("/apply-referral", json=data)

    # Get the coupons
    response = customer_client.get("/discount-coupons")

    assert response.status_code == 200
    coupons = response.json()
    assert len(coupons) == 1
    assert coupons[0].get("discount_percentage") == 20
    assert coupons[0].get("used") is False


def test_get_discount_coupons_unauthorised_returns_401(test_db, anon_client):
    """Test that unauthenticated request to get coupons returns 401."""
    response = anon_client.get("/discount-coupons")

    assert response.status_code == 401


def test_apply_referral_code_unauthorised_returns_401(test_db, anon_client):
    """Test that unauthenticated request to apply referral returns 401."""
    data = {"referral_code": "ABC12345"}
    response = anon_client.post("/apply-referral", json=data)

    assert response.status_code == 401
