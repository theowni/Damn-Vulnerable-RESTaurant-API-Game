import base64

import requests
from apis.menu import schemas
from db.models import MenuItem
from fastapi import HTTPException
from urllib.parse import urlparse


def _image_url_to_base64(image_url: str):
    parsed_url = urlparse(image_url)
    domain = parsed_url.netloc
    if domain == 'localhost' or domain == '127.0.0.1':
       raise HTTPException(status_code=500, detail="Error!")
    valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
    if not parsed_url.path.lower().endswith(valid_extensions):
        raise HTTPException(status_code=500, detail="Error!")
    response = requests.get(image_url)
    content_type = response.headers.get("content-type", "")
    if not content_type.startswith("image"):
        raise HTTPException(status_code=500, detail="Error!")
    return base64.b64encode(response.content).decode()


def create_menu_item(
    db,
    menu_item: schemas.MenuItemCreate,
):
    menu_item_dict = menu_item.dict()
    image_url = menu_item_dict.pop("image_url", None)
    db_item = MenuItem(**menu_item_dict)

    if image_url:
        db_item.image_base64 = _image_url_to_base64(image_url)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item


def update_menu_item(
    db,
    item_id: int,
    menu_item: schemas.MenuItemCreate,
):
    db_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Menu Item not found")

    menu_item_dict = menu_item.dict()
    image_url = menu_item_dict.pop("image_url", None)

    for key, value in menu_item_dict.items():
        setattr(db_item, key, value)

    if image_url:
        db_item.image_base64 = _image_url_to_base64(image_url)

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_menu_item(db, item_id: int):
    db_item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="MenuItem not found")

    db.delete(db_item)
    db.commit()
