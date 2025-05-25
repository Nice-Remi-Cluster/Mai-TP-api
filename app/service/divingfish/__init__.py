try:
    import ujson as json
except ImportError:
    import json

import httpx
from cfg.config import DivingFishBaseUrl
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1),
    retry=retry_if_exception_type(httpx.NetworkError) | retry_if_exception_type(httpx.TimeoutException)
)
async def alive_check() -> tuple[bool, dict]:
    """
    验证水鱼是否存活
    """
    try:
        client = httpx.AsyncClient()
        resp = await client.get(f"{DivingFishBaseUrl}/alive")
        if resp.status_code == 200 and resp.json() == {"message":"ok"}:
            return True, resp.json()
        return False, resp.json()
    except httpx.NetworkError or httpx.TimeoutException as e:
        raise e
    except Exception as e:
        return False, {"message": e}