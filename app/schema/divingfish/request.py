from pydantic import BaseModel, Field


class GetUserBScoresRequest(BaseModel):
    username: str = Field(..., description="水鱼用户名或qq号")
    is_qq: bool = Field(..., description="是否为QQ")
    b50: bool = Field(..., description="是否为b50，否则查询b40")
