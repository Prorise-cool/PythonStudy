"""
日期工具模块，提供日期相关的辅助函数。
"""
from datetime import datetime, timedelta
from typing import Optional


def validate_date_format(date_str: str, format_str: str = '%Y-%m-%d') -> bool:
    """验证日期字符串是否符合指定格式
    
    Args:
        date_str: 要验证的日期字符串
        format_str: 日期格式，默认为 'YYYY-MM-DD'
        
    Returns:
        bool: 日期格式是否有效
    """
    try:
        datetime.strptime(date_str, format_str)
        return True
    except ValueError:
        return False


def get_current_date(format_str: str = '%Y-%m-%d') -> str:
    """获取当前日期字符串
    
    Args:
        format_str: 日期格式，默认为 'YYYY-MM-DD'
        
    Returns:
        str: 当前日期字符串
    """
    return datetime.now().strftime(format_str)


def get_future_date(days: int, format_str: str = '%Y-%m-%d') -> str:
    """获取未来日期字符串
    
    Args:
        days: 向后推的天数
        format_str: 日期格式，默认为 'YYYY-MM-DD'
        
    Returns:
        str: 未来日期字符串
    """
    future_date = datetime.now() + timedelta(days=days)
    return future_date.strftime(format_str)


def is_date_in_range(date_str: str, start_date: str, end_date: str, 
                     format_str: str = '%Y-%m-%d') -> bool:
    """判断日期是否在指定范围内
    
    Args:
        date_str: 要检查的日期字符串
        start_date: 开始日期字符串
        end_date: 结束日期字符串
        format_str: 日期格式，默认为 'YYYY-MM-DD'
        
    Returns:
        bool: 日期是否在范围内
    """
    try:
        date = datetime.strptime(date_str, format_str)
        start = datetime.strptime(start_date, format_str)
        end = datetime.strptime(end_date, format_str)
        return start <= date <= end
    except ValueError:
        return False


def calculate_days_remaining(due_date_str: str, format_str: str = '%Y-%m-%d') -> Optional[int]:
    """计算距离截止日期的剩余天数
    
    Args:
        due_date_str: 截止日期字符串
        format_str: 日期格式，默认为 'YYYY-MM-DD'
        
    Returns:
        int: 剩余天数，如果日期格式无效则返回None
    """
    try:
        due_date = datetime.strptime(due_date_str, format_str)
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        delta = due_date - today
        return delta.days
    except ValueError:
        return None
    

def format_date(date_str: str, input_format: str = '%Y-%m-%d', 
                output_format: str = '%d/%m/%Y') -> Optional[str]:
    """将日期从一种格式转换为另一种格式
    
    Args:
        date_str: 要转换的日期字符串
        input_format: 输入日期格式
        output_format: 输出日期格式
        
    Returns:
        str: 转换后的日期字符串，如果格式无效则返回None
    """
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except ValueError:
        return None