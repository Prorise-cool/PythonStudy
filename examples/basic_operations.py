"""
基本数据库操作示例模块，展示SQLite数据库的基本CRUD操作。
包括连接、创建表、增删改查等基本功能。
"""
import os
import sqlite3
from typing import List, Optional
from core.db_manager import DatabaseManager
from core.table_manager import TableManager
from models.task import Task
from repositories.task_repository import TaskRepository

class SQLiteExample:
    """SQLite基本操作示例类，实现单例模式"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """确保类只有一个实例"""
        if cls._instance is None:
            cls._instance = super(SQLiteExample, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_file: str = "sqlite_practice.db"):
        """初始化SQLite示例类"""
        # 避免重复初始化
        if self._initialized:
            return
            
        self.db_file = db_file
        self.db_manager = DatabaseManager(self.db_file)
        self.conn, self.cursor = self.db_manager.connect()
        self.task_repository = TaskRepository(self.conn, self.cursor)
        self.init_db()
        self._initialized = True
    def init_db(self) -> bool:
        """初始化数据库和表结构
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 若数据库文件存在，则删除原有数据库
            if os.path.exists(self.db_file):
                self.clean_db()
            # 创建任务表
            return self.task_repository.create_table()
        except Exception as e:
            print(f"[Error] 初始化数据库失败: {e}")
            return False
    
    def clean_db(self) -> bool:
        """清理数据库文件
        
        Returns:
            bool: 清理是否成功
        """
        return self.db_manager.clean_database()
    
    def insert_sample_tasks(self) -> int:
        """插入示例任务数据
        
        Returns:
            int: 成功插入的任务数量
        """
        print("\n--- 插入示例任务数据 ---")
        tasks = [
            Task(title="任务1", description="这是任务1的描述", priority=1),
            Task(title="任务2", description="这是任务2的描述", priority=2),
            Task(title="任务3", description="这是任务3的描述", priority=3),
            Task(title="任务4", description="这是任务4的描述", priority=4),
            Task(title="任务5", description="这是任务5的描述", priority=5),
        ]
        return self.task_repository.insert_many(tasks)
    
    def insert_single_task(self, task: Task) -> Optional[int]:
        """插入单个任务
        
        Args:
            task: 要插入的任务对象
            
        Returns:
            Optional[int]: 插入的任务ID，失败则返回None
        """
        return self.task_repository.insert_task(task)
    
    def find_all_tasks(self) -> List[Task]:
        """查询所有任务
        
        Returns:
            List[Task]: 任务列表
        """
        return self.task_repository.find_all_tasks()
    
    def find_task_by_id(self, task_id: int) -> Optional[Task]:
        """根据ID查询任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[Task]: 任务对象，未找到则返回None
        """
        return self.task_repository.find_task_by_id(task_id)
    
    def find_tasks_by_criteria(self, criteria: dict) -> List[Task]:
        """根据条件查询任务
        
        Args:
            criteria: 查询条件字典
            
        Returns:
            List[Task]: 符合条件的任务列表
        """
        return self.task_repository.find_by_criteria(criteria)
    
    def find_tasks_by_title(self, title_part: str) -> List[Task]:
        """根据标题模糊查询任务
        
        Args:
            title_part: 标题包含的文本
            
        Returns:
            List[Task]: 符合条件的任务列表
        """
        return self.task_repository.find_by_title_contains(title_part)
    
    def update_task(self, task: Task) -> bool:
        """更新任务
        
        Args:
            task: 要更新的任务对象
            
        Returns:
            bool: 更新是否成功
        """
        return self.task_repository.update_task(task)
    
    def delete_task(self, task_id: int) -> bool:
        """删除任务
        
        Args:
            task_id: 要删除的任务ID
            
        Returns:
            bool: 删除是否成功
        """
        return self.task_repository.delete_task(task_id)
    
    def close(self) -> None:
        """关闭数据库连接"""
        self.db_manager.close()
if __name__ == '__main__':
    # 实例化示例类
    print('\033[1;36m===== 初始化 SQLite 示例 =====\033[0m')
    sqlite_example = SQLiteExample()
    
    # 插入示例任务数据
    print('\033[1;32m===== 插入示例任务数据 =====\033[0m')
    sqlite_example.insert_sample_tasks()
    
    # 查询所有任务
    print('\033[1;34m===== 查询所有任务 =====\033[0m')
    tasks = sqlite_example.find_all_tasks()
    for task in tasks:
        print('\033[0;37m' + str(task.to_dict()) + '\033[0m')
    
    # 查询单个任务
    print('\033[1;34m===== 查询单个任务 (ID=1) =====\033[0m')
    task = sqlite_example.find_task_by_id(1)
    print('\033[0;33m' + str(task.to_dict()) + '\033[0m')
    
    # 查询任务列表
    print('\033[1;34m===== 查询高优先级任务 (priority=3) =====\033[0m')
    tasks = sqlite_example.find_tasks_by_criteria({'priority': 3})
    for task in tasks:
        print('\033[0;35m' + str(task.to_dict()) + '\033[0m')
    
    # 查询任务标题包含某些字符的任务
    print('\033[1;34m===== 查询标题包含"任务"的任务 =====\033[0m')
    tasks = sqlite_example.find_tasks_by_title('任务')
    for task in tasks:
        print('\033[0;36m' + str(task.to_dict()) + '\033[0m')
    
    # 更新任务
    print('\033[1;33m===== 更新任务 (ID=1) =====\033[0m')
    task = Task(task_id=1, title="任务1-更新", description="这是任务1的更新描述", priority=1, is_completed=True)
    sqlite_example.update_task(task)
    
    # 查询更新后的任务
    print('\033[1;34m===== 查询更新后的任务 (ID=1) =====\033[0m')
    task = sqlite_example.find_task_by_id(1)
    print('\033[0;32m' + str(task.to_dict()) + '\033[0m')
    
    # 删除任务
    print('\033[1;31m===== 删除任务 (ID=1) =====\033[0m')
    sqlite_example.delete_task(1)
    
    # 查询删除后的任务
    print('\033[1;34m===== 查询删除后的任务 (ID=1) =====\033[0m')
    task = sqlite_example.find_task_by_id(1)
    print('\033[0;31m' + str(task) + '\033[0m')
    
    # 关闭数据库连接
    print('\033[1;36m===== 关闭数据库连接 =====\033[0m')
    sqlite_example.close()