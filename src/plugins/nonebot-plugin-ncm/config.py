import nonebot
from loguru import logger
from pydantic import BaseSettings


class Config(BaseSettings):
    # plugin custom config
    plugin_setting: str = "default"
    superusers: list = ["1140106918"]
    ncm_admin: list = ["1140106918", "1140106918"]  # 设置命令权限（非解析下载，仅解析功能开关设置）
    ncm_phone: str = "18766633323"  # 账号
    ncm_password: str = "Asong123"  # 密码
    ncm_song: bool = True  # 单曲解析开关
    ncm_list: bool = True  # 歌单解析开关
    ncm_priority: int = 2  # 解析优先级
    whitelist: list = ["542260102", "783021755"]  # 白名单(一键导入)
    class Config:
        extra = "ignore"


global_config = nonebot.get_driver().config
ncm_config = Config(**global_config.dict())  # 载入配置

