"""
服务层操作示例模块，展示使用TaskService进行任务管理。
包括任务的创建、查询、更新、删除以及业务规则实现。
"""
import os
import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from core.db_manager import DatabaseManager
from models.task import Task
from repositories.task_repository import TaskRepository
from services.task_service import TaskService

class ServiceExample:
    """TaskService操作示例类，实现单例模式"""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """确保类只有一个实例"""
        if cls._instance is None:
            cls._instance = super(ServiceExample, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_file: str = "service_example.db"):
        """初始化服务示例类"""
        # 避免重复初始化
        if self._initialized:
            return
            
        self.db_file = db_file
        self.db_manager = DatabaseManager(self.db_file)
        self.conn, self.cursor = self.db_manager.connect()
        
        # 初始化仓库和服务层
        self.task_repository = TaskRepository(self.conn, self.cursor)
        self.task_service = TaskService(self.task_repository)
        
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
    
    def create_sample_tasks(self) -> int:
        """创建示例任务数据，展示单个创建和批量创建
        
        Returns:
            int: 成功创建的任务数量
        """
        print("\n--- 创建示例任务数据 ---")
        
        # 单个创建任务
        print("1. 通过服务层创建单个任务")
        task1_id = self.task_service.create_task(
            title="使用Service创建的任务1",
            description="这是通过TaskService创建的任务1",
            priority=2,
            due_date="2023-12-31"
        )
        print(f"创建任务成功，task_id: {task1_id}")

        # 演示验证失败的情况
        print("\n2. 演示任务验证失败情况")
        invalid_task_id = self.task_service.create_task(
            title="",  # 空标题应该被拒绝
            description="这个任务应该创建失败",
            priority=10  # 无效的优先级范围
        )
        print(f"创建无效任务的结果: {invalid_task_id}")

        # 批量创建任务
        print("\n3. 批量创建多个任务")
        tasks_data = [
            {
                'title': '批量任务1',
                'description': '这是批量创建的任务1',
                'priority': 1,
                'due_date': '2023-12-25'
            },
            {
                'title': '批量任务2',
                'description': '这是批量创建的任务2',
                'due_date': '2023-12-26'
            },
            {
                'title': '批量任务3',
                'description': '这是批量创建的任务3',
                'priority': 4
            },
            {
                'title': '',  # 这个会被跳过
                'description': '标题为空的任务应被跳过'
            }
        ]

        created_count = self.task_service.create_tasks_batch(tasks_data)
        print(f"批量创建成功的任务数量: {created_count}")

        return created_count + (1 if task1_id else 0)

    def demonstrate_search_operations(self) -> None:
        """演示各种任务查询操作"""
        print("\n--- 演示任务查询操作 ---")

        # 查询所有任务
        print("1. 查询所有任务")
        all_tasks = self.task_service.get_all_tasks()
        self._print_tasks(all_tasks)

        # 按ID查询单个任务
        if all_tasks:
            first_task_id = all_tasks[0].task_id
            print(f"\n2. 按ID查询任务 (task_id={first_task_id})")
            task = self.task_service.get_task(first_task_id)
            if task:
                print(f"找到任务: {task.title} (优先级: {task.priority})")
            else:
                print(f"未找到ID为{first_task_id}的任务")

        # 按优先级查询任务
        print("\n3. 查询优先级为1的任务")
        priority_tasks = self.task_service.get_tasks_by_priority(1)
        self._print_tasks(priority_tasks)

        # 查询标题包含特定文本的任务
        print("\n4. 查询标题包含'批量'的任务")
        title_tasks = self.task_service.search_tasks_by_title("批量")
        self._print_tasks(title_tasks)

        # 查询未完成的任务
        print("\n5. 查询未完成的任务")
        incomplete_tasks = self.task_service.get_incomplete_tasks()
        self._print_tasks(incomplete_tasks)

        # 查询未来7天内到期的任务
        print("\n6. 查询未来7天内到期的任务")
        due_soon_tasks = self.task_service.get_tasks_due_within_days(7)
        self._print_tasks(due_soon_tasks)

        # 查询已逾期的任务
        print("\n7. 查询已逾期的任务")
        overdue_tasks = self.task_service.get_overdue_tasks()
        self._print_tasks(overdue_tasks)

    def demonstrate_update_operations(self) -> None:
        """演示任务更新操作"""
        print("\n--- 演示任务更新操作 ---")

        # 获取所有任务
        all_tasks = self.task_service.get_all_tasks()
        if not all_tasks:
            print("没有任务可以更新")
            return

        # 更新第一个任务
        task_to_update = all_tasks[0]
        print(f"1. 更新任务 (task_id={task_to_update.task_id}, 原标题: {task_to_update.title})")

        success = self.task_service.update_task(
            task_to_update.task_id,
            title=f"{task_to_update.title} - 已更新",
            description=f"{task_to_update.description} - 添加了新的描述",
            priority=min(task_to_update.priority + 1, 5)  # 增加优先级但不超过5
        )

        if success:
            updated_task = self.task_service.get_task(task_to_update.task_id)
            print(f"更新成功。新标题: {updated_task.title}, 新优先级: {updated_task.priority}")
        else:
            print(f"更新任务失败")

        # 将任务标记为已完成
        if len(all_tasks) >= 2:
            task_to_complete = all_tasks[1]
            print(f"\n2. 将任务标记为已完成 (task_id={task_to_complete.task_id}, 标题: {task_to_complete.title})")

            success = self.task_service.complete_task(task_to_complete.task_id)
            if success:
                completed_task = self.task_service.get_task(task_to_complete.task_id)
                status = "已完成" if completed_task.is_completed else "未完成"
                print(f"任务状态更新为: {status}")
            else:
                print("更新任务状态失败")

    def demonstrate_delete_operations(self) -> None:
        """演示任务删除操作"""
        print("\n--- 演示任务删除操作 ---")

        # 获取所有任务
        all_tasks = self.task_service.get_all_tasks()
        if not all_tasks:
            print("没有任务可以删除")
            return

        # 删除最后一个任务
        task_to_delete = all_tasks[-1]
        print(f"删除任务 (task_id={task_to_delete.task_id}, 标题: {task_to_delete.title})")

        success = self.task_service.delete_task(task_to_delete.task_id)
        if success:
            print(f"删除成功")

            # 验证任务已被删除
            remaining_tasks = self.task_service.get_all_tasks()
            print(f"删除前的任务数量: {len(all_tasks)}, 删除后的任务数量: {len(remaining_tasks)}")
        else:
            print("删除任务失败")

    def _print_tasks(self, tasks: List[Task]) -> None:
        """打印任务列表

        Args:
            tasks: 任务对象列表
        """
        if not tasks:
            print("未找到任务")
            return

        print(f"找到 {len(tasks)} 个任务:")
        for i, task in enumerate(tasks, 1):
            status = "已完成" if task.is_completed else "未完成"
            due_date = f", 截止日期: {task.due_date}" if task.due_date else ""
            print(f"{i}. [{task.task_id}] {task.title} (优先级: {task.priority}, 状态: {status}{due_date})")
    
    def run_demo(self) -> None:
        """运行完整的服务层示例演示"""
        print("====== 开始TaskService服务层示例演示 ======")
        
        # 创建示例任务
        self.create_sample_tasks()
        
        # 演示查询操作
        self.demonstrate_search_operations()
        
        # 演示更新操作
        self.demonstrate_update_operations()
        
        # 再次查询所有任务（展示更新效果）
        print("\n--- 更新后的所有任务 ---")
        updated_tasks = self.task_service.get_all_tasks()
        self._print_tasks(updated_tasks)
        
        # 演示删除操作
        self.demonstrate_delete_operations()
        
        print("\n====== 服务层示例演示结束 ======")
    
    def close(self) -> None:
        """关闭数据库连接"""
        self.db_manager.close()


if __name__ == "__main__":
    # 创建示例并运行演示
    example = ServiceExample()
    try:
        example.run_demo()
    finally:
        example.close() 