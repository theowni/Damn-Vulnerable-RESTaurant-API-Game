import base64
import requests
from apis.menu import schemas
from db.models import MenuItem
from fastapi import HTTPException


def _image_url_to_base64(image_url: str):
    try:
        # Validate URL to prevent SSRF
        if not image_url.startswith(("http://", "https://")):
            raise ValueError("Invalid URL")

        # Limit the domains that can be accessed
        allowed_domains = ["localhost:8080"]  # Add your domain(s) here
        if not any(domain in image_url for domain in allowed_domains):
            raise ValueError("Access to this domain is not allowed")

        response = requests.get(image_url)
        response.raise_for_status()  # Raise exception if request fails

        # Check content type to ensure it's an image
        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("image"):
            raise ValueError("Invalid content type")

        # Check if image is in JPEG format
        if not content_type.lower().endswith("jpeg"):
            raise ValueError("Image is not in JPEG format")

        return base64.b64encode(response.content).decode()
    except Exception as e:
        # Log or handle the error appropriately
        raise HTTPException(status_code=400, detail=str(e))


def create_menu_item(db, menu_item: schemas.MenuItemCreate):
    menu_item_dict = menu_item.dict()
    image_url = menu_item_dict.pop("image_url", None)
    db_item = MenuItem(**menu_item_dict)

    if image_url:
        db_item.image_base64 = _image_url_to_base64(image_url)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item
