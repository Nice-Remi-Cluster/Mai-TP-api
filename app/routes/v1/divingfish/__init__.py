import os.path
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import httpx
from starlette import status

from app.schema.divingfish.request import GetUserBScoresRequest
from app.schema.divingfish.response import DivingFishMusicInfo, ChartStats, DiffStats
from app.utils.os.path import mkdir_ignore_exists
from app.service.divingfish import alive_check
from app.service.divingfish.mai import update_all_music_info, query_player_scores_simple, download_music_cover, \
    update_all_chart_stats, query_music_info, query_chart_stats, query_diff_stats
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
    except httpx.NetworkError or httpx.TimeoutException as e:
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


@router.get("/chart_stats_update", response_model=Dict[str, Any], tags=["update_data"])
async def chart_stats_update():
    """
    更新所有铺面拟合难度等信息
    """
    try:
        result = await update_all_chart_stats()
        logger.info(f"从水鱼更新所有铺面额外信息成功: {result}")
        if result:
            return {"status": "success", "message": "从水鱼更新所有铺面额外信息成功"}
        else:
            return {"status": "failed", "message": "从水鱼更新所有铺面额外信息失败"}
    except httpx.NetworkError or httpx.TimeoutException as e:
        logger.error(f"从水鱼更新所有铺面额外信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"从水鱼更新所有铺面额外信息失败，水鱼服务器可能宕机，详细请联系管理员查看日志"
        )
    except Exception as e:
        logger.exception(f"从水鱼更新所有铺面额外信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"从水鱼更新所有铺面额外信息失败: {str(e)}"
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


@router.get("/get_music_cover", response_class=FileResponse, tags=["game_data"])
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


@router.get("/get_music_info", response_model=DivingFishMusicInfo, tags=["game_data"])
async def get_music_info(music_id: int):
    """
    获取音乐信息

    id 	    string 	歌曲的唯一标识符，其与现行的歌曲 ID 号一致 \n
    title 	string 	歌曲的标题 \n
    type 	string 	歌曲的类型，为 "DX" 或 "SD" \n
    ds   	array of float 	    歌曲的难度定数列表，由 Basic 至 Re:Master \n
    level  	array of string 	歌曲的难度等级列表，与 ds 的区别在于仅精确到整数或 "+" 等级 \n
    cids 	array of int 	    歌曲特定难度谱面的唯一标识符 \n
    charts              array of object 	歌曲的谱面信息列表，每个对象包含以下字段： \n
    charts[].notes  	array of int 	    谱面的音符数量列表，依次为 Tap、Hold、Slide、（Touch，仅 DX 类型）、Break \n
    charts[].charter    string 	            谱师信息 \n
    basic_info              	object 	歌曲的基本信息，包含以下字段： \n
    basic_info.title        	string 	歌曲的标题 \n
    basic_info.artist       	string 	曲师信息 \n
    basic_info.genre        	string 	歌曲的流派 \n
    basic_info.bpm          	int 	歌曲的 BPM 信息 \n
    basic_info.release_date 	string 	歌曲的发行日期（目前均为空） \n
    basic_info.from 	        string 	歌曲的稼动版本（以国服为准） \n
    basic_info.is_new 	        boolean 歌曲是否为当前版本的新歌 \n

    """
    try:
        if not os.path.exists(f"data/divingfish/music_data.json"):
            await update_all_music_info()
        result = await query_music_info(music_id)
        if result != {}:
            return result
        return {"status": "failed", "message": "无歌曲信息文件且从水鱼获取音乐信息失败"}
    except httpx.NetworkError or httpx.TimeoutException as e:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=f"无歌曲信息文件且从水鱼获取音乐信息失败，水鱼服务器可能宕机，详细请联系管理员查看日志"
        )
    except Exception as e:
        logger.error(f"无歌曲信息文件且从水鱼获取音乐信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"无歌曲信息文件且从水鱼获取音乐信息失败: {str(e)}"
        )


@router.get("/get_chart_stats", response_model=ChartStats, tags=["game_data"])
async def get_chart_stats(music_id: int):
    """
    获取铺面难度统计信息

    返回的 ChartStats 模型包含以下信息：
    stats: 包含各个难度等级统计数据的列表，每个难度统计数据包含：
      - cnt: 记录数量
      - diff: 难度等级
      - fit_diff: 拟合后的难度
      - avg: 平均分
      - avg_dx: 平均DX分
      - std_dev: 标准差
      - dist: 分数分布
      - fc_dist: 全连击分布
    """
    try:
        if not os.path.exists("data/divingfish/chart_stats.json"):
            await update_all_chart_stats()
        result = await query_chart_stats(music_id)
        if result != {}:
            return {"stats": result}
        return {"stats": []}
    except (httpx.NetworkError, httpx.TimeoutException):
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="无铺面统计信息文件且从水鱼获取铺面统计信息失败，水鱼服务器可能宕机，详细请联系管理员查看日志"
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"无铺面统计信息文件且从水鱼获取铺面统计信息失败: {str(e)}"
        )

@router.get("/get_diff_stats", response_model=DiffStats, tags=["game_data"])
async def get_diff_stats():
    """
    获取铺面难度统计信息

    返回的 DiffStats 模型包含以下信息：
    stats:           所有难度统计数据的字典，键为难度等级 \n
      achievements 	难度平均达成率 \n
      dist 	        难度的评级分布（依次对应 d, c, b, bb, bbb, a, aa, aaa, s, sp, ss, ssp, sss, sssp）\n
      fc_dist 	    难度的 Full Combo 分布（依次对应 非、fc、fcp、ap、app）\n
    """
    try:
        if not os.path.exists("data/divingfish/chart_stats.json"):
            await update_all_chart_stats()
        result = await query_diff_stats()
        if result != {}:
            return {"stats": result}
        return {"stats": {}}
    except (httpx.NetworkError, httpx.TimeoutException):
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail="无铺面统计信息文件且从水鱼获取铺面统计信息失败，水鱼服务器可能宕机，详细请联系管理员查看日志"
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"无铺面统计信息文件且从水鱼获取铺面统计信息失败: {str(e)}"
        )


