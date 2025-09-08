from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
import os
from app.core.config import FILE_PATH, SUB_PATH, SUB_TOKEN

router = APIRouter()

@router.get(SUB_PATH)
def get_subscription(token: str = ""):
    if SUB_TOKEN and token != SUB_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
    fp = os.path.join(FILE_PATH, 'sub.txt')
    if os.path.exists(fp):
        return PlainTextResponse(open(fp, "r", encoding="utf-8").read())
    raise HTTPException(status_code=404, detail="Subscription not found")