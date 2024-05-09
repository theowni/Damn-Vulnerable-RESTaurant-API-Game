from typing import List

from apis.auth.utils import RolesBasedAuthChecker, get_current_user
from apis.menu import schemas, utils
from db.models import MenuItem, User, UserRole
from db.session import get_db
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing_extensions import Annotated

router = APIRouter()


@router.get("/menu", response_model=List[schemas.MenuItem])
def get_menu(db: Session = Depends(get_db)):
    return db.query(MenuItem).all()


@router.put(
    "/menu", response_model=schemas.MenuItem, status_code=status.HTTP_201_CREATED
)
def create_menu_item(
    menu_item: schemas.MenuItemCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    auth=Depends(RolesBasedAuthChecker([UserRole.EMPLOYEE, UserRole.CHEF])),
):
    db_item = utils.create_menu_item(db, menu_item)
    return db_item


@router.put("/menu/{item_id}", response_model=schemas.MenuItem)
def update_menu_item(
    item_id: int,
    menu_item: schemas.MenuItemCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    auth=Depends(RolesBasedAuthChecker([UserRole.EMPLOYEE, UserRole.CHEF])),
):
    db_item = utils.update_menu_item(db, item_id, menu_item)
    return db_item


@router.delete("/menu/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(
    item_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    # auth=Depends(RolesBasedAuthChecker([UserRole.EMPLOYEE, UserRole.CHEF])),
):
    utils.delete_menu_item(db, item_id)
    return {"ok": True}
