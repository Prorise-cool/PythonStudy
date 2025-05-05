"""
任务数据模型模块，定义Task相关的数据结构。
# sqlite_practice/models/task.py
"""
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime


@dataclass
class Task:
    """任务数据模型类，使用dataclass简化代码"""
    title: str  # 任务标题（必填）
    priority: int = 3  # 优先级（默认3）
    is_completed: bool = False  # 是否完成（默认False）

    task_id: Optional[int] = None  # 任务ID（可选，若不指定，则由数据库自动生成）
    due_date: Optional[str] = None  # 截止日期（可选
    attachment: Optional[str] = None  # 附件（可选）
    created_at: Optional[str] = None  # 创建时间（可选）
    description: Optional[str] = None  # 任务描述（可选）
    last_updated: Optional[str] = None  # 最后更新时间（可选）

    def __post_init__(self):
        """dataclass提供的初始化后自动执行的函数，用于设置默认值"""
        if self.created_at is None:
            #  如果没有提供当前创建时间，则使用当前时间
            self.created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self) -> dict:
        """将对象转换为字典，用于数据库操作

        Returns:
            dict: 包含任务数据的字典
        """

        # 使用dataclasses.asdict获取基础字典
        task_dict = asdict(self)

        # SQLite中布尔值以0/1存储，需要转换
        task_dict['is_completed'] = 1 if self.is_completed else 0

        # 如果task_id为None，从字典中移除它
        if self.task_id is None:
            task_dict.pop('task_id')

        return task_dict

    @classmethod
    def from_row(cls, row) -> 'Task':
        """从数据库行创建Task对象
        
        这个方法的作用是将数据库查询结果（SQLite行数据）转换为Task对象。
        看起来复杂是因为它需要处理多种可能的输入格式：
        1. sqlite3.Row对象（有keys方法的字典类对象）
        2. 元组或列表形式的结果
        
        虽然dataclass简化了类定义，但不能自动处理从外部数据源（如数据库）
        创建对象的过程，尤其是当数据需要类型转换时（如整数到布尔值）。
        
        这种复杂性是为了提高代码的健壮性，确保从不同来源的数据都能正确转换为Task对象。
        如果确定数据库始终返回同一格式的结果，可以简化此方法。

        Args:
            row: sqlite3.Row对象或类似字典/序列的对象

        Returns:
            Task: 创建的Task对象
        """
        # 创建一个包含所有可能属性的字典
        task_data = {}

        # 检查row中是否有每个属性并添加到task_data
        # 使用get方法避免KeyError
        if hasattr(row, 'keys'):
            # 如果row有keys方法（如sqlite3.Row），使用它
            for key in row.keys():
                task_data[key] = row[key]
        else:
            # 否则尝试按照索引获取
            try:
                task_data = {
                    'task_id': row[0] if len(row) > 0 else None,
                    'title': row[1] if len(row) > 1 else None,
                    'description': row[2] if len(row) > 2 else None,
                    'priority': row[3] if len(row) > 3 else 3,
                    'due_date': row[4] if len(row) > 4 else None,
                    'is_completed': bool(row[5]) if len(row) > 5 else False,
                    'attachment': row[6] if len(row) > 6 else None,
                    'created_at': row[7] if len(row) > 7 else None,
                    'last_updated': row[8] if len(row) > 8 else None
                }
            except (IndexError, TypeError):
                # 如果索引访问失败，返回具有默认值的Task
                return cls(title="Unknown")

        # 处理布尔值转换
        if 'is_completed' in task_data:
            task_data['is_completed'] = bool(task_data['is_completed'])

        # 创建并返回Task对象
        return cls(**task_data) 
