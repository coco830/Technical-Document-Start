"""
数据库优化服务
提供索引管理、查询优化、性能分析等功能
"""
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import text, inspect, Index, Column, Integer, String, DateTime, func
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from sqlalchemy.sql import select, and_, or_

from app.core.database import engine, db_manager
from app.core.cache import cache_service
from app.core.config import settings

# 设置日志
logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """数据库优化器"""
    
    def __init__(self, engine: Engine = engine):
        self.engine = engine
    
    def analyze_table_performance(self, table_name: str) -> Dict[str, Any]:
        """分析表性能"""
        with self.engine.connect() as conn:
            # 获取表统计信息
            if "mysql" in str(self.engine.url).lower():
                stats = self._analyze_mysql_table(conn, table_name)
            elif "postgresql" in str(self.engine.url).lower():
                stats = self._analyze_postgresql_table(conn, table_name)
            else:
                stats = self._analyze_sqlite_table(conn, table_name)
            
            # 获取索引信息
            indexes = self._get_table_indexes(conn, table_name)
            
            # 获取查询统计
            query_stats = self._get_table_query_stats(conn, table_name)
            
            return {
                "table_name": table_name,
                "stats": stats,
                "indexes": indexes,
                "query_stats": query_stats,
                "recommendations": self._generate_table_recommendations(stats, indexes, query_stats)
            }
    
    def _analyze_mysql_table(self, conn, table_name: str) -> Dict[str, Any]:
        """分析MySQL表性能"""
        try:
            # 获取表状态
            result = conn.execute(text(f"SHOW TABLE STATUS LIKE '{table_name}'"))
            row = result.fetchone()
            
            if not row:
                return {}
            
            # 获取表大小
            size_result = conn.execute(text(f"""
                SELECT 
                    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)'
                FROM information_schema.TABLES 
                WHERE table_schema = DATABASE() AND table_name = '{table_name}'
            """))
            size_row = size_result.fetchone()
            
            # 获取行数
            count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count_row = count_result.fetchone()
            
            return {
                "engine": row[1] if len(row) > 1 else "InnoDB",
                "rows": count_row[0] if count_row else 0,
                "size_mb": size_row[0] if size_row else 0,
                "data_length": row[6] if len(row) > 6 else 0,
                "index_length": row[8] if len(row) > 8 else 0,
                "collation": row[14] if len(row) > 14 else "",
                "comment": row[17] if len(row) > 17 else ""
            }
        except Exception as e:
            logger.error(f"分析MySQL表失败: {str(e)}")
            return {}
    
    def _analyze_postgresql_table(self, conn, table_name: str) -> Dict[str, Any]:
        """分析PostgreSQL表性能"""
        try:
            # 获取表统计信息
            result = conn.execute(text(f"""
                SELECT 
                    schemaname,
                    tablename,
                    attname,
                    n_distinct,
                    correlation
                FROM pg_stats_correlation
                WHERE schemaname = 'public' AND tablename = '{table_name}'
            """))
            
            # 获取表大小
            size_result = conn.execute(text(f"""
                SELECT 
                    pg_size_pretty(pg_total_relation_size('public.{table_name}')) AS size,
                    pg_total_relation_size('public.{table_name}') AS size_bytes
            """))
            size_row = size_result.fetchone()
            
            # 获取行数
            count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count_row = count_result.fetchone()
            
            return {
                "rows": count_row[0] if count_row else 0,
                "size": size_row[0] if size_row else "0 bytes",
                "size_bytes": size_row[1] if size_row else 0,
                "correlations": [dict(row) for row in result] if result else []
            }
        except Exception as e:
            logger.error(f"分析PostgreSQL表失败: {str(e)}")
            return {}
    
    def _analyze_sqlite_table(self, conn, table_name: str) -> Dict[str, Any]:
        """分析SQLite表性能"""
        try:
            # 获取表信息
            result = conn.execute(text(f"PRAGMA table_info({table_name})"))
            columns = result.fetchall()
            
            # 获取表大小
            size_result = conn.execute(text(f"""
                SELECT 
                    COUNT(*) * AVG(LENGTH(name)) AS estimated_size
                FROM sqlite_master 
                WHERE type='table' AND name='{table_name}'
            """))
            size_row = size_result.fetchone()
            
            # 获取行数
            count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count_row = count_result.fetchone()
            
            return {
                "rows": count_row[0] if count_row else 0,
                "columns": columns,
                "estimated_size": size_row[0] if size_row else 0
            }
        except Exception as e:
            logger.error(f"分析SQLite表失败: {str(e)}")
            return {}
    
    def _get_table_indexes(self, conn, table_name: str) -> List[Dict[str, Any]]:
        """获取表索引信息"""
        try:
            if "mysql" in str(self.engine.url).lower():
                result = conn.execute(text(f"SHOW INDEX FROM {table_name}"))
                return [dict(row) for row in result] if result else []
            elif "postgresql" in str(self.engine.url).lower():
                result = conn.execute(text(f"""
                    SELECT 
                        indexname AS name,
                        indexdef AS definition
                    FROM pg_indexes 
                    WHERE tablename = '{table_name}'
                """))
                return [dict(row) for row in result] if result else []
            else:  # SQLite
                result = conn.execute(text(f"PRAGMA index_list({table_name})"))
                indexes = [row[0] for row in result] if result else []
                
                index_details = []
                for index_name in indexes:
                    detail_result = conn.execute(text(f"PRAGMA index_info({index_name})"))
                    details = [dict(row) for row in detail_result] if detail_result else []
                    index_details.append({
                        "name": index_name,
                        "details": details
                    })
                
                return index_details
        except Exception as e:
            logger.error(f"获取表索引失败: {str(e)}")
            return []
    
    def _get_table_query_stats(self, conn, table_name: str) -> Dict[str, Any]:
        """获取表查询统计"""
        try:
            if "mysql" in str(self.engine.url).lower():
                # MySQL查询统计
                result = conn.execute(text(f"""
                    SELECT 
                        DIGEST_TEXT AS query,
                        COUNT_STAR AS rows_examined,
                        SUM_TIMER_WAIT/1000000000 AS total_time_sec,
                        COUNT_STAR/SUM_TIMER_WAIT*1000000000 AS avg_rows_per_sec
                    FROM performance_schema.events_statements_summary_by_digest 
                    WHERE DIGEST_TEXT LIKE '%{table_name}%'
                    GROUP BY DIGEST_TEXT
                    ORDER BY SUM_TIMER_WAIT DESC
                    LIMIT 10
                """))
                return {"top_queries": [dict(row) for row in result] if result else []}
            elif "postgresql" in str(self.engine.url).lower():
                # PostgreSQL查询统计
                result = conn.execute(text(f"""
                    SELECT 
                        query,
                        calls,
                        total_time,
                        mean_time,
                        rows
                    FROM pg_stat_statements 
                    WHERE query LIKE '%{table_name}%'
                    ORDER BY total_time DESC
                    LIMIT 10
                """))
                return {"top_queries": [dict(row) for row in result] if result else []}
            else:
                # SQLite不支持查询统计
                return {"top_queries": []}
        except Exception as e:
            logger.error(f"获取表查询统计失败: {str(e)}")
            return {"top_queries": []}
    
    def _generate_table_recommendations(self, stats: Dict[str, Any], 
                                   indexes: List[Dict[str, Any]], 
                                   query_stats: Dict[str, Any]) -> List[str]:
        """生成表优化建议"""
        recommendations = []
        
        # 检查表大小
        if stats.get("size_mb", 0) > 1000:  # 超过1GB
            recommendations.append("表大小较大，考虑分区或归档历史数据")
        
        # 检查行数
        if stats.get("rows", 0) > 1000000:  # 超过100万行
            recommendations.append("表行数较多，确保有适当的索引")
        
        # 检查索引
        if len(indexes) < 2:
            recommendations.append("表索引较少，考虑为常用查询字段添加索引")
        
        # 检查查询性能
        top_queries = query_stats.get("top_queries", [])
        if top_queries:
            slow_queries = [q for q in top_queries if q.get("total_time_sec", 0) > 1.0]
            if slow_queries:
                recommendations.append("检测到慢查询，考虑优化查询或添加索引")
        
        return recommendations
    
    def create_missing_indexes(self, table_name: str, 
                           suggested_indexes: List[Dict[str, Any]]) -> bool:
        """创建缺失的索引"""
        try:
            with self.engine.connect() as conn:
                for index_info in suggested_indexes:
                    index_name = f"idx_{table_name}_{index_info['column']}"
                    
                    # 检查索引是否已存在
                    if "mysql" in str(self.engine.url).lower():
                        result = conn.execute(text(f"SHOW INDEX FROM {table_name} WHERE Key_name = '{index_name}'"))
                        if result.fetchone():
                            logger.info(f"索引 {index_name} 已存在，跳过创建")
                            continue
                        
                        # 创建索引
                        conn.execute(text(f"""
                            CREATE INDEX {index_name} ON {table_name} ({index_info['column']})
                        """))
                        logger.info(f"已创建索引 {index_name}")
                    
                    elif "postgresql" in str(self.engine.url).lower():
                        result = conn.execute(text(f"""
                            SELECT indexname FROM pg_indexes 
                            WHERE tablename = '{table_name}' AND indexname = '{index_name}'
                        """))
                        if result.fetchone():
                            logger.info(f"索引 {index_name} 已存在，跳过创建")
                            continue
                        
                        # 创建索引
                        conn.execute(text(f"""
                            CREATE INDEX {index_name} ON {table_name} ({index_info['column']})
                        """))
                        logger.info(f"已创建索引 {index_name}")
                    
                    else:  # SQLite
                        result = conn.execute(text(f"PRAGMA index_list({table_name})"))
                        existing_indexes = [row[0] for row in result] if result else []
                        
                        if index_name in existing_indexes:
                            logger.info(f"索引 {index_name} 已存在，跳过创建")
                            continue
                        
                        # 创建索引
                        conn.execute(text(f"""
                            CREATE INDEX {index_name} ON {table_name} ({index_info['column']})
                        """))
                        logger.info(f"已创建索引 {index_name}")
                
                return True
        except Exception as e:
            logger.error(f"创建索引失败: {str(e)}")
            return False
    
    def optimize_table(self, table_name: str) -> bool:
        """优化表"""
        try:
            with self.engine.connect() as conn:
                if "mysql" in str(self.engine.url).lower():
                    # MySQL优化表
                    conn.execute(text(f"OPTIMIZE TABLE {table_name}"))
                    logger.info(f"已优化MySQL表 {table_name}")
                    return True
                
                elif "postgresql" in str(self.engine.url).lower():
                    # PostgreSQL优化表（VACUUM ANALYZE）
                    conn.execute(text(f"VACUUM ANALYZE {table_name}"))
                    logger.info(f"已优化PostgreSQL表 {table_name}")
                    return True
                
                else:  # SQLite
                    # SQLite优化表（VACUUM）
                    conn.execute(text(f"VACUUM {table_name}"))
                    conn.execute(text(f"ANALYZE {table_name}"))
                    logger.info(f"已优化SQLite表 {table_name}")
                    return True
        except Exception as e:
            logger.error(f"优化表失败: {str(e)}")
            return False
    
    def analyze_slow_queries(self, limit: int = 20) -> List[Dict[str, Any]]:
        """分析慢查询"""
        try:
            with self.engine.connect() as conn:
                if "mysql" in str(self.engine.url).lower():
                    # MySQL慢查询
                    result = conn.execute(text(f"""
                        SELECT 
                            start_time,
                            query_time,
                            lock_time,
                            rows_sent,
                            rows_examined,
                            sql_text
                        FROM mysql.slow_log
                        ORDER BY query_time DESC
                        LIMIT {limit}
                    """))
                    return [dict(row) for row in result] if result else []
                
                elif "postgresql" in str(self.engine.url).lower():
                    # PostgreSQL慢查询（需要启用pg_stat_statements）
                    result = conn.execute(text(f"""
                        SELECT 
                            query,
                            calls,
                            total_time,
                            mean_time,
                            rows
                        FROM pg_stat_statements 
                        WHERE mean_time > 1.0
                        ORDER BY total_time DESC
                        LIMIT {limit}
                    """))
                    return [dict(row) for row in result] if result else []
                
                else:
                    # SQLite不支持慢查询日志
                    return []
        except Exception as e:
            logger.error(f"分析慢查询失败: {str(e)}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            with self.engine.connect() as conn:
                if "mysql" in str(self.engine.url).lower():
                    # MySQL数据库统计
                    result = conn.execute(text("""
                        SELECT 
                            SCHEMA_NAME as schema,
                            TABLE_NAME as table,
                            TABLE_ROWS as rows,
                            ROUND(((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024), 2) AS size_mb
                        FROM information_schema.TABLES
                        WHERE TABLE_SCHEMA = DATABASE()
                        ORDER BY size_mb DESC
                    """))
                    tables = [dict(row) for row in result] if result else []
                    
                    # 获取数据库总大小
                    size_result = conn.execute(text("""
                        SELECT 
                            ROUND(SUM(DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS total_size_mb
                        FROM information_schema.TABLES
                        WHERE TABLE_SCHEMA = DATABASE()
                    """))
                    size_row = size_result.fetchone()
                    
                    return {
                        "engine": "MySQL",
                        "total_size_mb": size_row[0] if size_row else 0,
                        "tables": tables
                    }
                
                elif "postgresql" in str(self.engine.url).lower():
                    # PostgreSQL数据库统计
                    result = conn.execute(text("""
                        SELECT 
                            schemaname as schema,
                            tablename as table,
                            n_tup_ins as rows,
                            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
                        FROM pg_stat_user_tables
                        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                    """))
                    tables = [dict(row) for row in result] if result else []
                    
                    # 获取数据库总大小
                    size_result = conn.execute(text("""
                        SELECT 
                            pg_size_pretty(SUM(pg_database_size('public'))) AS total_size
                        FROM pg_database_size('public')
                    """))
                    size_row = size_result.fetchone()
                    
                    return {
                        "engine": "PostgreSQL",
                        "total_size": size_row[0] if size_row else "0 bytes",
                        "tables": tables
                    }
                
                else:  # SQLite
                    result = conn.execute(text("""
                        SELECT 
                            name as table,
                            sql as definition
                        FROM sqlite_master
                        WHERE type='table'
                        ORDER BY name
                    """))
                    tables = [dict(row) for row in result] if result else []
                    
                    # 获取表大小
                    for table in tables:
                        count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table['table']}"))
                        count_row = count_result.fetchone()
                        table["rows"] = count_row[0] if count_row else 0
                    
                    return {
                        "engine": "SQLite",
                        "tables": tables
                    }
        except Exception as e:
            logger.error(f"获取数据库统计失败: {str(e)}")
            return {}
    
    def suggest_indexes_for_table(self, table_name: str) -> List[Dict[str, Any]]:
        """为表建议索引"""
        try:
            with self.engine.connect() as conn:
                # 获取表结构
                inspector = inspect(self.engine)
                columns = inspector.get_columns(table_name)
                
                # 获取主键
                primary_keys = [key["name"] for key in inspector.get_pk_constraint(table_name).constrained_columns] if inspector.get_pk_constraint(table_name) else []
                
                # 获取外键
                foreign_keys = [key["constrained_columns"][0] for key in inspector.get_foreign_keys(table_name)] if inspector.get_foreign_keys(table_name) else []
                
                # 获取唯一约束
                unique_constraints = []
                for constraint in inspector.get_unique_constraints(table_name):
                    unique_constraints.extend(constraint["constrained_columns"])
                
                # 建议索引的列
                suggested_indexes = []
                
                for column in columns:
                    col_name = column["name"]
                    
                    # 跳过主键、外键和唯一约束列
                    if col_name in primary_keys or col_name in foreign_keys or col_name in unique_constraints:
                        continue
                    
                    # 为字符串类型和日期类型列建议索引
                    if column["type"].lower() in ["varchar", "char", "text", "date", "datetime", "timestamp"]:
                        suggested_indexes.append({
                            "column": col_name,
                            "type": column["type"],
                            "reason": "字符串和日期类型列通常用于查询条件"
                        })
                
                return suggested_indexes
        except Exception as e:
            logger.error(f"建议索引失败: {str(e)}")
            return []


class QueryOptimizer:
    """查询优化器"""
    
    def __init__(self, engine: Engine = engine):
        self.engine = engine
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """分析查询性能"""
        try:
            with self.engine.connect() as conn:
                if "mysql" in str(self.engine.url).lower():
                    # MySQL查询分析
                    result = conn.execute(text(f"EXPLAIN FORMAT=JSON {query}"))
                    explain_plan = [dict(row) for row in result] if result else []
                    
                    # 检查是否使用了索引
                    uses_index = any("key" in str(plan).lower() for plan in explain_plan)
                    
                    return {
                        "query": query,
                        "explain_plan": explain_plan,
                        "uses_index": uses_index,
                        "recommendations": self._generate_query_recommendations(explain_plan)
                    }
                
                elif "postgresql" in str(self.engine.url).lower():
                    # PostgreSQL查询分析
                    result = conn.execute(text(f"EXPLAIN (FORMAT JSON) {query}"))
                    explain_plan = [dict(row) for row in result] if result else []
                    
                    # 检查是否使用了索引
                    uses_index = any("Index Scan" in str(plan).get("Node Type", "") for plan in explain_plan)
                    
                    return {
                        "query": query,
                        "explain_plan": explain_plan,
                        "uses_index": uses_index,
                        "recommendations": self._generate_query_recommendations(explain_plan)
                    }
                
                else:  # SQLite
                    result = conn.execute(text(f"EXPLAIN QUERY PLAN {query}"))
                    explain_plan = [dict(row) for row in result] if result else []
                    
                    # 检查是否使用了索引
                    uses_index = any("USING INDEX" in str(plan).get("detail", "") for plan in explain_plan)
                    
                    return {
                        "query": query,
                        "explain_plan": explain_plan,
                        "uses_index": uses_index,
                        "recommendations": self._generate_query_recommendations(explain_plan)
                    }
        except Exception as e:
            logger.error(f"分析查询失败: {str(e)}")
            return {
                "query": query,
                "error": str(e)
            }
    
    def _generate_query_recommendations(self, explain_plan: List[Dict[str, Any]]) -> List[str]:
        """生成查询优化建议"""
        recommendations = []
        
        # 检查全表扫描
        if any("Seq Scan" in str(plan).get("Node Type", "") or 
                "ALL" in str(plan).get("type", "") for plan in explain_plan):
            recommendations.append("检测到全表扫描，考虑添加适当的索引")
        
        # 检查文件排序
        if any("FileSort" in str(plan).get("Node Type", "") or 
                "Using filesort" in str(plan).get("Extra", "") for plan in explain_plan):
            recommendations.append("检测到文件排序，考虑优化查询或添加索引")
        
        # 检查临时表
        if any("Temporary" in str(plan).get("Node Type", "") or 
                "Using temporary" in str(plan).get("Extra", "") for plan in explain_plan):
            recommendations.append("检测到临时表使用，考虑优化查询结构")
        
        return recommendations


# 创建全局实例
db_optimizer = DatabaseOptimizer()
query_optimizer = QueryOptimizer()