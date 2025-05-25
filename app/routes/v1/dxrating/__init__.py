from typing import Dict, Any

from fastapi import APIRouter, HTTPException
import httpx
from starlette import status

from app.utils.os.path import mkdir_ignore_exists
from app.service.divingfish import alive_check
from app.service.divingfish.mai import update_all_music_info
from loguru import logger

mkdir_ignore_exists("data/dxrating/")

router = APIRouter(
    prefix="/dxrating",
    tags=["dxrating"]
)


