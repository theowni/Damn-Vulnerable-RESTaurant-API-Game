from apis.admin.schemas import DiskUsage
from apis.admin.utils import get_disk_usage
from apis.auth.utils import get_current_user
from db.models import User, UserRole
from db.session import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing_extensions import Annotated

router = APIRouter()


@router.get(
    "/admin/stats/disk", response_model=DiskUsage, status_code=status.HTTP_200_OK
)
def get_disk_usage_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    parameters: str = "",
    db: Session = Depends(get_db),
):
    if current_user.role != UserRole.CHEF.value:
        raise HTTPException(
            status_code=403, detail="Only Chef is authorized to get current disk stats!"
        )

    usage = get_disk_usage(parameters)
    return DiskUsage(output=usage)
