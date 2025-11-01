from datetime import datetime, timezone, timedelta
from typing import Optional, Union
import pytz


def now_utc() -> datetime:
    """获取当前UTC时间"""
    return datetime.now(timezone.utc)


def now_local(tz_name: str = "Asia/Shanghai") -> datetime:
    """获取当前本地时间"""
    tz = pytz.timezone(tz_name)
    return datetime.now(tz)


def utc_to_local(utc_dt: datetime, tz_name: str = "Asia/Shanghai") -> datetime:
    """UTC时间转换为本地时间"""
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)
    tz = pytz.timezone(tz_name)
    return utc_dt.astimezone(tz)


def local_to_utc(local_dt: datetime, tz_name: str = "Asia/Shanghai") -> datetime:
    """本地时间转换为UTC时间"""
    if local_dt.tzinfo is None:
        tz = pytz.timezone(tz_name)
        local_dt = tz.localize(local_dt)
    return local_dt.astimezone(timezone.utc)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """格式化日期时间"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """解析日期时间字符串"""
    return datetime.strptime(dt_str, format_str)


def add_time(dt: datetime, **kwargs) -> datetime:
    """添加时间间隔"""
    return dt + timedelta(**kwargs)


def subtract_time(dt: datetime, **kwargs) -> datetime:
    """减去时间间隔"""
    return dt - timedelta(**kwargs)


def time_diff(dt1: datetime, dt2: datetime) -> timedelta:
    """计算时间差"""
    if dt1.tzinfo is None:
        dt1 = dt1.replace(tzinfo=timezone.utc)
    if dt2.tzinfo is None:
        dt2 = dt2.replace(tzinfo=timezone.utc)
    return dt1 - dt2


def is_future(dt: datetime) -> bool:
    """判断是否为未来时间"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt > now_utc()


def is_past(dt: datetime) -> bool:
    """判断是否为过去时间"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt < now_utc()


def age_from_datetime(dt: datetime) -> str:
    """计算从指定时间到现在的年龄描述"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    now = now_utc()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years}年前"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months}个月前"
    elif diff.days > 0:
        return f"{diff.days}天前"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours}小时前"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes}分钟前"
    else:
        return "刚刚"


def get_start_of_day(dt: datetime) -> datetime:
    """获取一天的开始时间"""
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def get_end_of_day(dt: datetime) -> datetime:
    """获取一天的结束时间"""
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)


def get_start_of_month(dt: datetime) -> datetime:
    """获取一个月的开始时间"""
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def get_end_of_month(dt: datetime) -> datetime:
    """获取一个月的结束时间"""
    if dt.month == 12:
        next_month = dt.replace(year=dt.year + 1, month=1, day=1)
    else:
        next_month = dt.replace(month=dt.month + 1, day=1)
    
    return next_month - timedelta(microseconds=1)


def get_weekday(dt: datetime) -> int:
    """获取星期几（0=周一，6=周日）"""
    return dt.weekday()


def is_weekend(dt: datetime) -> bool:
    """判断是否为周末"""
    return get_weekday(dt) >= 5  # 5=周六，6=周日