"""
日志配置模块
统一配置 loguru 的日志格式
"""
import sys
import os
from loguru import logger

# 移除默认的处理器
logger.remove()

# 日志格式：时间 | 文件名:行数 | 函数名 | 日志级别 | 消息
log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{line}</cyan> | "
    "<cyan>{function}</cyan> | "
    "<level>{message}</level>"
)

# 获取日志级别（从环境变量或默认为 INFO）
log_level = os.getenv("LOG_LEVEL", "INFO")

# 添加控制台处理器
logger.add(
    sys.stderr,
    format=log_format,
    level=log_level,
    colorize=True
)

# 可选：添加文件处理器（用于生产环境）
log_file = os.getenv("LOG_FILE", None)
if log_file:
    logger.add(
        log_file,
        format=log_format,
        level=log_level,
        rotation="500 MB",  # 文件大小超过 500MB 时轮转
        retention="7 days"  # 保留 7 天的日志
    )

