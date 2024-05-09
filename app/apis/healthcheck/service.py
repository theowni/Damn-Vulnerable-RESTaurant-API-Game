from fastapi import APIRouter, Response

router = APIRouter()


@router.get("/healthcheck")
def healthcheck(response: Response):
    # response.headers["X-Powered-By"] = "Python 3.8, FastAPI ^0.103.0"
    return {"ok": True}
