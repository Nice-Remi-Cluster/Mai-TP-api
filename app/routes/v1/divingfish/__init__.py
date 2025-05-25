import os.path
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import httpx
from starlette import status

from app.schema.divingfish.request import GetUserBScoresRequest
from app.utils.os.path import mkdir_ignore_exists
from app.service.divingfish import alive_check
from app.service.divingfish.mai import update_all_music_info, query_player_scores_simple, download_music_cover
from loguru import logger

mkdir_ignore_exists("data/divingfish/")

router = APIRouter(
    prefix="/divingfish",
    tags=["divingfish"]
)

@router.get("/health", tags=["health"])
async def health():
    """
    获取水鱼服务状态

    Returns:
        Dict[str, Any]: 包含水鱼服务状态的字典
    """
    try:
        is_alive, msg = await alive_check()
        return {"is_alive": is_alive, "message": msg}
    except httpx.NetworkError or httpx.TimeoutException as e:
        logger.error(f"/health 无法连接水鱼服务器")
        return {"is_alive": False, "message": "无法连接水鱼服务器"}
    except Exception as e:
        logger.error(f"检查水鱼服务状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"检查水鱼服务状态失败: {str(e)}"
        )


@router.get("/music_update", response_model=Dict[str, Any], tags=["update_data"])
async def music_update():
    """
    更新所有音乐信息
    """
    try:
        result = await update_all_music_info()
        logger.info(f"从水鱼更新所有铺面信息成功: {result}")
        if result[0]:
            return {"status": "success", "message": "从水鱼更新所有铺面信息成功", "use_cache": result[0]}
        else:
            return {"status": "failed", "message": "从水鱼更新所有铺面信息失败", "use_cache": result[0]}
    except httpx.NetworkError | httpx.TimeoutException as e:
        logger.error(f"从水鱼更新所有铺面信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"从水鱼更新所有铺面信息失败，水鱼服务器可能宕机，详细请联系管理员查看日志"
        )
    except Exception as e:
        logger.error(f"从水鱼更新所有铺面信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"从水鱼更新所有铺面信息失败: {str(e)}"
        )


@router.post("/get_user_b_scores", response_model=Dict[str, Any], tags=["score"])
async def get_user_b_scores(req: GetUserBScoresRequest):
    """
    获取用户B50成绩
    """
    try:
        result = await query_player_scores_simple(req.username, req.is_qq, req.b50)
        return {"status": "success", "message": "获取用户B50成绩成功", "data": result[1]}
    except httpx.NetworkError or httpx.TimeoutException as e:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"获取用户B50成绩失败，水鱼服务器可能宕机，详细请联系管理员查看日志"
        )
    except Exception as e:
        logger.error(f"获取用户B50成绩失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户B50成绩失败: {str(e)}"
        )

@router.get("/get_music_cover", response_model=Dict[str, Any], tags=["game_data"])
async def get_music_cover(songs_id: int):
    """
    获取音乐封面
    """
    try:
        file_path = f"data/divingfish/cover/{songs_id}.png"

        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            pass
        else:
            d_status, d_detail = await download_music_cover(songs_id)
            if d_status:
                pass
            else:
                raise HTTPException(
                    status_code=status.HTTP_204_NO_CONTENT,
                    detail=f"从水鱼获取音乐封面失败，且本地无文件缓存，水鱼服务器可能宕机，详细请联系管理员查看日志"
                )
        return FileResponse(f"data/divingfish/cover/{songs_id}.png")
    except httpx.NetworkError or httpx.TimeoutException as e:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"从水鱼获取音乐封面失败，且本地无文件缓存，水鱼服务器可能宕机，详细请联系管理员查看日志"
        )
    except Exception as e:
        logger.error(f"从水鱼获取音乐封面失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"从水鱼获取音乐封面失败: {str(e)}"
        )




