from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from app.core.config import FILE_PATH

router = APIRouter()

@router.get("/config")
def get_config():
    fp = os.path.join(FILE_PATH, 'config.json')
    if os.path.exists(fp):
        return FileResponse(fp, media_type="application/json")
    raise HTTPException(status_code=404, detail="Config not found")

@router.get("/log")
def get_log():
    fp = os.path.join(FILE_PATH, 'cloudflared.log')
    if os.path.exists(fp):
        return FileResponse(fp, media_type="text/plain")
    raise HTTPException(status_code=404, detail="Log not found")