from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.routes.v1 import router as v1_router
from cfg import config as cfg
from tortoise.contrib.fastapi import RegisterTortoise, tortoise_exception_handlers
from tortoise import Tortoise


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # 使用RegisterTortoise和Aerich管理的迁移，而不是生成模式
#     async with RegisterTortoise(
#         app,
#         config=cfg.TORTOISE_ORM,
#         generate_schemas=False,  # 由于使用Aerich，这里设置为False
#         add_exception_handlers=True,
#     ):
#         yield
#
#     await Tortoise.close_connections()

app = FastAPI(
    title="Third party api for remi service about maimaidx",
)

app.include_router(v1_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
