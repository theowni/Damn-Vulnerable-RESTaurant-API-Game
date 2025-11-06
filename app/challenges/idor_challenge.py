from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder

from db.session import get_db
from db.models import Order
from apis.auth.utils import get_current_user

router = APIRouter(
    prefix="/idor",
    tags=["idor"]
)

@router.get("/orders/{order_id}")
async def get_order_secure(order_id: int, db=Depends(get_db), current_user = Depends(get_current_user)):
    """
    IDOR patch: devolver la orden solo si pertenece al usuario autenticado.
    """
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    # VALIDACIÓN: el usuario autenticado debe ser el propietario
    if getattr(db_order, "user_id", None) != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return jsonable_encoder(db_order)
