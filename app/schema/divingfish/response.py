
from typing import List, Dict
from pydantic import BaseModel, Field
from typing import List, Optional, Union

class DivingFishChart(BaseModel):
    notes: List[int] = Field(..., description="谱面音符数")
    charter: str = Field(..., description="谱师")

class DivingFishBasicInfo(BaseModel):
    title: str = Field(..., description="歌曲标题")
    artist: str = Field(..., description="歌曲歌手")
    genre: str = Field(..., description="歌曲类型")
    bpm: float = Field(..., description="歌曲bpm")
    release_date: str = Field(..., description="歌曲发布时间")
    from_: str = Field(..., alias="from", description="歌曲来源")
    is_new: bool = Field(..., description="歌曲是否为最新")

class DivingFishMusicInfo(BaseModel):
    id: str = Field(..., description="歌曲id")
    title: str = Field(..., description="歌曲标题")
    type: str = Field(..., description="歌曲类型")
    ds: List[float] = Field(..., description="歌曲难度")
    level: List[str] = Field(..., description="歌曲等级")
    cids: List[int] = Field(..., description="歌曲cid")
    charts: List[DivingFishChart] = Field(..., description="歌曲chart信息")
    basic_info: DivingFishBasicInfo = Field(..., description="歌曲基本信息")

class ChartDifficultyStats(BaseModel):
    """难度统计信息模型"""
    cnt: float = Field(..., description="记录数量")
    diff: str = Field(..., description="难度等级")
    fit_diff: float = Field(..., description="拟合后的难度")
    avg: float = Field(..., description="平均分")
    avg_dx: float = Field(..., description="平均DX分")
    std_dev: float = Field(..., description="标准差")
    dist: List[int] = Field(..., description="分数分布")
    fc_dist: List[Union[float, int]] = Field(..., description="全连击分布")

class ChartStats(BaseModel):
    """谱面统计信息模型，包含各个难度的统计数据"""
    stats: List[ChartDifficultyStats] = Field(..., description="谱面各难度的统计数据")

class DiffStat(BaseModel):
    """歌曲难度信息模型"""
    achievements: float = Field(..., description="难度平均达成率")
    dist: List[float] = Field(..., description="难度的评级分布 (依次对应 d, c, b, bb, bbb, a, aa, aaa, s, sp, ss, ssp, sss, sssp)")
    fc_dist: List[float] = Field(..., description="难度的 Full Combo 分布 (依次对应 非、fc、fcp、ap、app)")

class DiffStats(BaseModel):
    """歌曲难度统计信息模型"""
    stats: Dict[str, DiffStat] = Field(..., description="歌曲各谱面的难度统计数据")