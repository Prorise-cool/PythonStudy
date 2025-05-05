"""
基本数据库操作示例模块，展示SQLite数据库的基本CRUD操作。
包括连接、创建表、增删改查等基本功能。
"""
import os
import sqlite3
from core.db_manager import DatabaseManager
from core.table_manager import TableManager
from models.task import Task
from repositories.task_repository import TaskRepository


def run_basic_operations():
    """运行基本数据库操作示例"""
    print("\n--- SQLite基本操作示例 ---")
    
    # 使用DatabaseManager创建数据库连接
    db_file = "example_sqlite.db"
    db_manager = DatabaseManager(db_file)
    
    # 清理旧数据库文件
    if os.path.exists(db_file):
        print(f"清理旧数据库文件: {db_file}")
        os.remove(db_file)
    
    # 连接数据库
    conn, cursor = db_manager.connect()
    if not conn or not cursor:
        print("无法连接到数据库，示例终止。")
        return
    
    # 创建任务仓库
    task_repo = TaskRepository(conn, cursor)
    
    # 创建任务表
    print("\n1. 创建任务表")
    if task_repo.create_table():
        print("  任务表创建成功")
    else:
        print("  任务表创建失败，示例终止。")
        db_manager.close()
        return
    
    # 插入单条任务记录
    print("\n2. 插入单条任务记录")
    task1 = Task(
        title="学习 SQLite 基础操作",
        description="完成SQLite基本CRUD操作的学习",
        priority=1,
        due_date="2025-05-15"
    )
    task1_id = task_repo.insert(task1)
    if task1_id:
        print(f"  任务插入成功，ID: {task1_id}")
    else:
        print("  任务插入失败")
    
    # 批量插入任务记录
    print("\n3. 批量插入任务记录")
    batch_tasks = [
        Task(title="编写SQLite示例代码", priority=2, due_date="2025-05-16"),
        Task(title="阅读SQLite文档", description="深入学习SQLite高级特性", priority=3)
    ]
    inserted_count = task_repo.insert_many(batch_tasks)
    if inserted_count:
        print(f"  成功批量插入 {inserted_count} 条任务记录")
    else:
        print("  批量插入任务失败")
    
    # 查询所有任务
    print("\n4. 查询所有任务")
    all_tasks = task_repo.find_all()
    print(f"  共查询到 {len(all_tasks)} 条任务:")
    for task in all_tasks:
        print(f"    ID: {task.task_id}, 标题: {task.title}, 优先级: {task.priority}, 截止日期: {task.due_date}")
    
    # 根据ID查询单个任务
    print("\n5. 根据ID查询单个任务")
    if task1_id:
        task = task_repo.find_by_id(task1_id)
        if task:
            print(f"  找到任务 ID={task1_id}:")
            print(f"    标题: {task.title}")
            print(f"    描述: {task.description}")
            print(f"    优先级: {task.priority}")
            print(f"    截止日期: {task.due_date}")
            print(f"    是否完成: {task.is_completed}")
        else:
            print(f"  未找到任务 ID={task1_id}")
    
    # 更新任务
    print("\n6. 更新任务")
    if task1_id:
        task = task_repo.find_by_id(task1_id)
        if task:
            task.description = "已完成SQLite基本CRUD操作的学习"
            task.is_completed = True
            if task_repo.update(task):
                print(f"  成功更新任务 ID={task1_id}")
            else:
                print(f"  更新任务 ID={task1_id} 失败")
        else:
            print(f"  未找到要更新的任务 ID={task1_id}")
    
    # 根据条件查询任务
    print("\n7. 根据条件查询任务")
    priority_2_tasks = task_repo.find_by_criteria({"priority": 2})
    print(f"  查询到 {len(priority_2_tasks)} 条优先级为2的任务:")
    for task in priority_2_tasks:
        print(f"    ID: {task.task_id}, 标题: {task.title}")
    
    # 模糊查询任务
    print("\n8. 模糊查询任务")
    sqlite_tasks = task_repo.find_by_title_contains("SQLite")
    print(f"  查询到 {len(sqlite_tasks)} 条标题包含'SQLite'的任务:")
    for task in sqlite_tasks:
        print(f"    ID: {task.task_id}, 标题: {task.title}")
    
    # 删除任务
    print("\n9. 删除任务")
    if len(all_tasks) > 0:
        task_to_delete = all_tasks[-1].task_id
        if task_repo.delete(task_to_delete):
            print(f"  成功删除任务 ID={task_to_delete}")
        else:
            print(f"  删除任务 ID={task_to_delete} 失败")
    
    # 再次查询所有任务确认结果
    print("\n10. 确认操作结果")
    final_tasks = task_repo.find_all()
    print(f"  操作后剩余 {len(final_tasks)} 条任务:")
    for task in final_tasks:
        completed = "已完成" if task.is_completed else "未完成"
        print(f"    ID: {task.task_id}, 标题: {task.title}, 状态: {completed}")
    
    # 关闭数据库连接
    db_manager.close()
    print("\n示例结束，数据库连接已关闭。")


if __name__ == "__main__":
    run_basic_operations()