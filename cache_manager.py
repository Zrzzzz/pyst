"""
缓存管理模块 - 模拟 Redis 缓存功能
使用数据库表存储缓存数据，加快查询速度
"""
import json
from datetime import datetime, timedelta
import logger_config  # 必须在导入 logger 之前
from loguru import logger
from database import get_session, close_session, QueryCache
from sqlalchemy.dialects.sqlite import insert


class CacheManager:
    """缓存管理器 - 模拟 Redis"""
    
    def __init__(self):
        self.session = get_session()
    
    def __del__(self):
        close_session(self.session)
    
    def get(self, cache_key, cache_date=None):
        """
        获取缓存数据
        
        Args:
            cache_key: 缓存键
            cache_date: 缓存日期（可选，默认为今天）
        
        Returns:
            缓存数据（字典）或 None
        """
        try:
            if cache_date is None:
                cache_date = datetime.now().strftime('%Y%m%d')
            
            # 查询缓存
            cache = self.session.query(QueryCache).filter(
                QueryCache.cache_key == cache_key,
                QueryCache.cache_date == cache_date,
                QueryCache.expire_at > datetime.now()
            ).first()
            
            if cache:
                logger.debug(f"缓存命中: {cache_key}")
                return json.loads(cache.cache_value)
            
            logger.debug(f"缓存未命中: {cache_key}")
            return None
        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
            return None
    
    def set(self, cache_key, cache_value, ttl_hours=24, cache_date=None):
        """
        设置缓存数据 - 使用 UPSERT 方式，如果存在则更新，不存在则插入

        Args:
            cache_key: 缓存键
            cache_value: 缓存值（字典或列表）
            ttl_hours: 缓存过期时间（小时）
            cache_date: 缓存日期（可选，默认为今天）
        """
        try:
            if cache_date is None:
                cache_date = datetime.now().strftime('%Y%m%d')

            expire_at = datetime.now() + timedelta(hours=ttl_hours)
            now = datetime.now()

            # 使用 SQLite 的 INSERT OR REPLACE 语法（通过 SQLAlchemy 的 on_conflict_do_update）
            stmt = insert(QueryCache).values(
                cache_key=cache_key,
                cache_value=json.dumps(cache_value, ensure_ascii=False),
                cache_date=cache_date,
                expire_at=expire_at,
                created_at=now,
                updated_at=now
            )

            # 如果 cache_key 冲突，则更新这些字段
            stmt = stmt.on_conflict_do_update(
                index_elements=['cache_key'],
                set_={
                    'cache_value': json.dumps(cache_value, ensure_ascii=False),
                    'cache_date': cache_date,
                    'expire_at': expire_at,
                    'updated_at': now
                }
            )

            self.session.execute(stmt)
            self.session.commit()
            logger.debug(f"缓存已设置: {cache_key}")
        except Exception as e:
            self.session.rollback()
            logger.error(f"设置缓存失败: {e}")
    
    def delete(self, cache_key, cache_date=None):
        """删除缓存"""
        try:
            if cache_date is None:
                cache_date = datetime.now().strftime('%Y%m%d')
            
            self.session.query(QueryCache).filter(
                QueryCache.cache_key == cache_key,
                QueryCache.cache_date == cache_date
            ).delete()
            self.session.commit()
            
            logger.debug(f"缓存已删除: {cache_key}")
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
            self.session.rollback()
    
    def clear_expired(self):
        """清理过期缓存"""
        try:
            count = self.session.query(QueryCache).filter(
                QueryCache.expire_at <= datetime.now()
            ).delete()
            self.session.commit()
            
            logger.info(f"清理过期缓存: {count} 条")
        except Exception as e:
            logger.error(f"清理过期缓存失败: {e}")
            self.session.rollback()
    
    def clear_all(self, cache_date=None):
        """清理所有缓存"""
        try:
            if cache_date is None:
                cache_date = datetime.now().strftime('%Y%m%d')
            
            count = self.session.query(QueryCache).filter(
                QueryCache.cache_date == cache_date
            ).delete()
            self.session.commit()
            
            logger.info(f"清理所有缓存: {count} 条")
        except Exception as e:
            logger.error(f"清理所有缓存失败: {e}")
            self.session.rollback()

