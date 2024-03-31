import secrets
import string

from apis.auth.utils import create_user_if_not_exists
from apis.menu.schemas import MenuItemCreate
from apis.menu.utils import create_menu_item
from config import settings
from db.models import User, UserRole
from db.session import get_db
from sqlalchemy.orm import Session


def generate_random_secret():
    characters = string.ascii_letters + string.digits + string.punctuation
    password = "".join(secrets.choice(characters) for i in range(32))

    return password


def load_users(db: Session):
    create_user_if_not_exists(
        db,
        username=settings.CHEF_USERNAME,
        password=generate_random_secret(),
        first_name="Gustavo",
        last_name="",
        phone_number="(505) 146-0195",
        role=UserRole.CHEF,
    )
    create_user_if_not_exists(
        db,
        username="Mike",
        password="kaylee123",
        first_name="Mike",
        last_name="",
        phone_number="",
        role=UserRole.EMPLOYEE,
    )
    create_user_if_not_exists(
        db,
        username="Saul",
        password="Th4tsMyP4ssw0rd!",
        first_name="Saul",
        last_name="",
        phone_number="(505) 842-5662",
        role=UserRole.EMPLOYEE,
    )
    create_user_if_not_exists(
        db,
        username="hhm",
        password="12345678",
        first_name="Howard",
        last_name="Hamlin",
        phone_number="(505) 56434-7345",
        role=UserRole.CUSTOMER,
    )


def load_menu(db: Session):
    # Breakfasts
    create_menu_item(
        db,
        MenuItemCreate(
            name="Pollos Classic Breakfast",
            price=2.99,
            category="Pollos Breakfasts",
        ),
    )
    create_menu_item(
        db,
        MenuItemCreate(
            name="Pollos Chicken Biscuit",
            price=3.99,
            category="Pollos Breakfasts",
            description="Fried chicken filet on a buttered biscuit",
        ),
    )
    create_menu_item(
        db,
        MenuItemCreate(
            name="Pollos Breakfast Sandwich",
            price=4.59,
            category="Pollos Breakfasts",
            description="Two eggs, boneless grilled chicken, green chile and salsa served on our classic bun",
        ),
    )
    create_menu_item(
        db,
        MenuItemCreate(
            name="Pollos Breakfast Tacos",
            price=4.99,
            category="Pollos Breakfasts",
        ),
    )

    # Burritos
    create_menu_item(
        db,
        MenuItemCreate(
            name="Basic Hand Held",
            price=2.49,
            category="Pollos Burritos",
            description="Egg & potato",
        ),
    )
    create_menu_item(
        db,
        MenuItemCreate(
            name="Basic Smothered Chile & Cheese on Top",
            price=3.39,
            category="Pollos Burritos",
            description="Egg & potato",
        ),
    )
    create_menu_item(
        db,
        MenuItemCreate(
            name="New Mexico",
            price=3.99,
            category="Pollos Burritos",
            description="Egg, potato, green chile & cheese",
        ),
    )
    create_menu_item(
        db,
        MenuItemCreate(
            name="Albuquerque",
            price=4.59,
            category="Pollos Burritos",
            description="Sausage, egg, potato, red chile & cheese",
        ),
    )

    # Chicken Specialties
    create_menu_item(
        db,
        MenuItemCreate(
            name="Pollo Adovada",
            price=5.49,
            category="Chicken Specialties",
            description="Potato, red chile & cheese",
        ),
    )

    create_menu_item(
        db,
        MenuItemCreate(
            name="Pollo Picante",
            price=5.49,
            category="Chicken Specialties",
            description="Bean, potato, green chile & cheese",
        ),
    )

    create_menu_item(
        db,
        MenuItemCreate(
            name="Pollo Mexicana",
            price=5.49,
            category="Chicken Specialties",
            description="Potato, green chile & cheese",
        ),
    )

    create_menu_item(
        db,
        MenuItemCreate(
            name="Giuso De Pollo",
            price=3.99,
            category="Chicken Specialties",
            description="Bean, potato, red chile & cheese",
        ),
    )

    # Desserts
    create_menu_item(
        db,
        MenuItemCreate(
            name="Ice Cream",
            price=2.45,
            category="Desserts",
            description="Cone",
        ),
    )

    create_menu_item(
        db,
        MenuItemCreate(
            name="Chocoloate Shake",
            price=1.65,
            category="Desserts",
        ),
    )


def load_initial_data():
    db = next(get_db())

    chef_user = db.query(User).filter(User.username == settings.CHEF_USERNAME).first()
    if chef_user:
        # chef user is propagated to the database
        # it means that initial data is already loaded
        return

    load_users(db)
    load_menu(db)
