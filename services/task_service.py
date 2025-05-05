"""
任务服务模块，提供业务逻辑层功能。
负责处理任务相关的业务规则和操作。
# sqlite_practice/services/task_service.py
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from models.task import Task
from repositories.task_repository import TaskRepository


class TaskService:
    """任务服务类，处理任务相关的业务逻辑"""
    
    def __init__(self, task_repository: TaskRepository):
        """初始化任务服务
        
        Args:
            task_repository: 任务数据访问对象
        """
        self.task_repository = task_repository
    
    def create_task(self, title: str, description: str = None, priority: int = 3, 
                   due_date: str = None, is_completed: bool = False, 
                   attachment: bytes = None) -> Optional[int]:
        """创建新任务
        
        Args:
            title: 任务标题
            description: 任务描述
            priority: 优先级 (1-5)，默认为3
            due_date: 截止日期，格式为'YYYY-MM-DD'
            is_completed: 是否已完成
            attachment: 附件数据
            
        Returns:
            int: 新创建任务的ID，失败则返回None
        """
        # 验证优先级范围
        if priority < 1 or priority > 5:
            print(f"[Warning] 优先级 {priority} 超出范围 (1-5)，将使用默认值 3")
            priority = 3
            
        # 验证日期格式
        if due_date:
            try:
                # 尝试解析日期格式
                datetime.strptime(due_date, '%Y-%m-%d')
            except ValueError:
                print(f"[Warning] 日期格式 '{due_date}' 无效，应为 'YYYY-MM-DD'，将设为空")
                due_date = None
                
        # 验证标题不为空
        if not title:
            print("[Error] 任务标题不能为空")
            return None
            
        # 创建任务对象
        task = Task(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            is_completed=is_completed,
            attachment=attachment
        )
        
        # 保存任务
        return self.task_repository.insert_task(task)
    
    def create_tasks_batch(self, task_data_list: List[Dict[str, Any]]) -> Optional[int]:
        """批量创建任务
        
        Args:
            task_data_list: 包含任务数据的字典列表
            
        Returns:
            int: 成功创建的任务数量，失败则返回None
        """
        if not task_data_list:
            print("[Warning] 没有任务数据需要创建")
            return 0
            
        tasks = []
        for task_data in task_data_list:
            # 验证必要字段
            if 'title' not in task_data or not task_data['title']:
                print("[Warning] 跳过缺少标题的任务")
                continue
                
            # 创建任务对象
            task = Task(
                title=task_data['title'],
                description=task_data.get('description'),
                priority=task_data.get('priority', 3),
                due_date=task_data.get('due_date'),
                is_completed=task_data.get('is_completed', False),
                attachment=task_data.get('attachment')
            )
            tasks.append(task)
            
        if not tasks:
            print("[Warning] 没有有效的任务需要创建")
            return 0
            
        # 批量保存任务
        return self.task_repository.insert_many(tasks)
    
    def update_task(self, task_id: int, **kwargs) -> bool:
        """更新任务
        
        Args:
            task_id: 要更新的任务ID
            **kwargs: 要更新的字段和值
            
        Returns:
            bool: 更新是否成功
        """
        # 查找现有任务
        task = self.task_repository.find_task_by_id(task_id)
        if not task:
            print(f"[Error] 未找到要更新的任务 ID={task_id}")
            return False
            
        # 更新字段
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
            else:
                print(f"[Warning] 忽略未知字段 '{key}'")
                
        # 保存更新
        return self.task_repository.update_task(task)
    
    def complete_task(self, task_id: int) -> bool:
        """将任务标记为已完成
        
        Args:
            task_id: 要标记的任务ID
            
        Returns:
            bool: 操作是否成功
        """
        return self.update_task(task_id, is_completed=True)
    
    def delete_task(self, task_id: int) -> bool:
        """删除任务
        
        Args:
            task_id: 要删除的任务ID
            
        Returns:
            bool: 删除是否成功
        """
        return self.task_repository.delete_task(task_id)
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """获取指定ID的任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            Task: 任务对象，未找到则返回None
        """
        return self.task_repository.find_task_by_id(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        """获取所有任务
        
        Returns:
            list: 任务对象列表
        """
        return self.task_repository.find_all_tasks()
    
    def get_tasks_by_priority(self, priority: int) -> List[Task]:
        """获取指定优先级的任务
        
        Args:
            priority: 优先级
            
        Returns:
            list: 任务对象列表
        """
        return self.task_repository.find_by_criteria({'priority': priority})
    
    def get_incomplete_tasks(self) -> List[Task]:
        """获取未完成的任务
        
        Returns:
            list: 任务对象列表
        """
        return self.task_repository.find_by_criteria({'is_completed': 0})  # SQLite中布尔值存储为0/1
    
    def get_overdue_tasks(self) -> List[Task]:
        """获取已逾期的任务
        
        Returns:
            list: 任务对象列表
        """
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 获取所有任务
        all_tasks = self.task_repository.find_all_tasks()
        
        # 筛选出截止日期已过且未完成的任务
        overdue_tasks = []
        for task in all_tasks:
            if (task.due_date and task.due_date < today and not task.is_completed):
                overdue_tasks.append(task)
                
        return overdue_tasks
    
    def search_tasks_by_title(self, title_part: str) -> List[Task]:
        """搜索标题包含指定字符串的任务
        
        Args:
            title_part: 标题中要搜索的文本
            
        Returns:
            list: 符合条件的任务对象列表
        """
        return self.task_repository.find_by_title_contains(title_part)
    
    def get_tasks_due_within_days(self, days: int) -> List[Task]:
        """获取指定天数内到期的任务
        
        Args:
            days: 天数
            
        Returns:
            list: 任务对象列表
        """
        today = datetime.now()
        end_date = (today + timedelta(days=days)).strftime('%Y-%m-%d')
        today_str = today.strftime('%Y-%m-%d')
        
        # 获取所有任务
        all_tasks = self.task_repository.find_all_tasks()
        
        # 筛选出在指定日期范围内到期的任务
        due_tasks = []
        for task in all_tasks:
            if (task.due_date and today_str <= task.due_date <= end_date):
                due_tasks.append(task)
                
        return due_tasks