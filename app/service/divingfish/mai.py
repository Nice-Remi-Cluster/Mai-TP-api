from loguru import logger

from app.utils.os.path import mkdir_ignore_exists

try:
    import ujson as json
except ImportError:
    import json

import httpx
from cfg.config import DivingFishBaseUrl, DivingFishCoverUrl
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from app.enums.divingfish.gametype import GameDataType
import os
import aiofile

mkdir_ignore_exists("data/divingfish/cover")

DIVING_FISH_MAI_ENDPOINT = f"{DivingFishBaseUrl}/{GameDataType.MAIMAI.value}"

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1),
    retry=retry_if_exception_type(httpx.NetworkError) | retry_if_exception_type(httpx.TimeoutException)
)
async def update_all_music_info(force: bool = False) -> tuple[bool, bool]:
    """
    从Diving Fish MaiMai API获取并更新本地音乐信息数据。

    自动重试三次。
    该函数使用ETag机制检查音乐数据是否有更新，避免不必要的下载。
    如果本地缓存是最新的（HTTP 304），则继续使用缓存数据；否则获取最新数据并更新本地文件，并记录日志。
    可以通过force参数强制更新。

    :param force: bool, optional
        若为True，则即使本地缓存有效也强制更新。默认False。
    :return: tuple[bool, bool]
        - 第一个元素为True表示操作成功，False表示失败。
        - 第二个元素为True表示使用了缓存数据（HTTP 304），False表示拉取了新数据。
    :raises httpx.NetworkError: 网络请求异常。
    :raises httpx.TimeoutException: 请求超时。
    """
    try:
        headers = {}

        # 关于etag
        # https://github.com/Diving-Fish/maimaidx-prober/blob/main/database/zh-api-document.md#314-%E8%8E%B7%E5%8F%96-maimai-%E7%9A%84%E6%AD%8C%E6%9B%B2%E6%95%B0%E6%8D%AE
        if not force and os.path.exists("data/divingfish/music_data_ext.json"):
            async with aiofile.async_open("data/divingfish/music_data_ext.json", "r", encoding="utf-8") as f:
                headers["If-None-Match"] = json.loads(await f.read())["etag"]

        client = httpx.AsyncClient()

        resp = await client.get(
            f"{DIVING_FISH_MAI_ENDPOINT}/music_data",
            headers=headers
        )

        if resp.status_code == 200:
            async with aiofile.async_open("data/divingfish/music_data.json", "w", encoding="utf-8") as fp:
                await fp.write(json.dumps(resp.json()))
            async with aiofile.async_open("data/divingfish/music_data_ext.json", "w", encoding="utf-8") as fp:
                await fp.write(json.dumps({
                    "request_at": resp.headers["date"],
                    "etag": resp.headers["etag"],
                }))
            return True, False
        elif resp.status_code == 304:
            return True, True
        else:
            raise httpx.NetworkError(f"status_code: {resp.status_code}; content: {resp.text}")
    except httpx.NetworkError or httpx.TimeoutException as e:
        raise e
    except Exception as e:
        logger.exception(e)
        return False, False

async def query_music_info(music_id: int) -> dict:
    async with aiofile.async_open("data/divingfish/music_data.json", "r", encoding="utf-8") as f:
        music_data = json.loads(await f.read())
        for music in music_data:
            if music["id"] == music_id:
                return music
        return {}


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1),
    retry=retry_if_exception_type(httpx.NetworkError) | retry_if_exception_type(httpx.TimeoutException)
)
async def query_player_scores_simple(username: str, is_qq: bool, b50: bool = True) -> tuple[bool, dict]:
    try:
        client = httpx.AsyncClient()
        data = {
            "username" if not is_qq else "qq": username,
            "b50": "1" if b50 else "0"
        }
        resp = await client.post(f"{DIVING_FISH_MAI_ENDPOINT}/query/player", json=data)
        match resp.status_code:
            case 200:
                return True, resp.json()
            case 400:
                return False, resp.json()
            case 403:
                return False, resp.json()
            case _:
                return False, {
                    "status_code": resp.status_code,
                    "content": resp.text
                }
    except httpx.NetworkError or httpx.TimeoutException as e:
        raise e
    except Exception as e:
        logger.exception(e)
        return False, {"error": str(e)}


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1),
    retry=retry_if_exception_type(httpx.NetworkError) | retry_if_exception_type(httpx.TimeoutException)
)
async def download_music_cover(songs_id: int) -> tuple[bool, dict]:
    try:
        client = httpx.AsyncClient()
        resp = await client.get(DivingFishCoverUrl.replace("{{cover_id}}", str(songs_id).zfill(5)))
        if resp.status_code == 200:
            async with aiofile.async_open(f"data/divingfish/cover/{songs_id}.png", "wb") as f:
                await f.write(resp.content)
            return True, {}
        return False, {}
    except httpx.NetworkError or httpx.TimeoutException as e:
        raise e
    except Exception as e:
        logger.exception(e)
        return False, {"error": str(e)}


