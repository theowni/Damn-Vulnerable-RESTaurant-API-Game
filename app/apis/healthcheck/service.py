from fastapi import APIRouter, Response

router = APIRouter()


@router.get("/healthcheck")
def healthcheck(response: Response):
    return {"ok": True}
