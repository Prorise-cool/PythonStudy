"""
任务数据模型模块，定义Task相关的数据结构。
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Task:
    """任务数据模型类，使用dataclass简化代码"""
    
    title: str  # 任务标题，必填
    description: Optional[str] = None  # 任务描述，可选
    priority: int = 3  # 优先级，默认为3
    due_date: Optional[str] = None  # 截止日期，可选
    is_completed: bool = False  # 是否完成，默认为False
    attachment: Optional[bytes] = None  # 附件，可选
    created_at: Optional[str] = None  # 创建时间，可选
    last_updated: Optional[str] = None  # 最后更新时间，可选
    task_id: Optional[int] = None  # 任务ID，由数据库生成
    
    def __post_init__(self):
        """对象初始化后运行的方法，用于设置默认值"""
        if self.created_at is None:
            # 如果没有提供创建时间，设置为当前时间
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> dict:
        """将对象转换为字典，用于数据库操作
        
        Returns:
            dict: 包含任务数据的字典
        """
        task_dict = {
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'due_date': self.due_date,
            'is_completed': 1 if self.is_completed else 0,  # SQLite中布尔值以0/1存储
            'attachment': self.attachment,
            'created_at': self.created_at,
            'last_updated': self.last_updated
        }
        
        # 只有在task_id存在时才添加到字典中
        if self.task_id is not None:
            task_dict['task_id'] = self.task_id
            
        return task_dict
    
    @classmethod
    def from_row(cls, row) -> 'Task':
        """从数据库行创建Task对象
        
        Args:
            row: sqlite3.Row对象或类似字典的对象
            
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