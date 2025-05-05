"""
高级查询示例模块，展示SQLite数据库的高级查询功能。
包括复杂条件查询、排序、分页、聚合函数等。
"""
import sqlite3
import os
from core.db_manager import DatabaseManager
from models.task import Task
from repositories.task_repository import TaskRepository
from services.task_service import TaskService
from utils.date_utils import get_current_date, get_future_date


def populate_test_data(task_repo):
    """填充测试数据
    
    Args:
        task_repo: 任务仓库对象
    """
    print("\n填充测试数据...")
    # 创建一批测试任务
    today = get_current_date()
    tomorrow = get_future_date(1)
    next_week = get_future_date(7)
    next_month = get_future_date(30)
    
    test_tasks = [
        # 高优先级任务
        Task(title="完成项目设计文档", description="项目需求和架构设计", priority=1, due_date=tomorrow),
        Task(title="修复关键Bug", description="修复用户报告的登录问题", priority=1, due_date=today),
        Task(title="制定项目计划", description="项目时间线和里程碑规划", priority=1, due_date=next_week),
        
        # 中优先级任务
        Task(title="代码重构", description="重构认证模块的代码", priority=2, due_date=next_week),
        Task(title="单元测试编写", description="为核心功能编写单元测试", priority=2, due_date=next_week),
        Task(title="API文档更新", description="更新REST API文档", priority=2, due_date=next_month),
        
        # 低优先级任务
        Task(title="性能优化", description="优化数据库查询性能", priority=3, due_date=next_month),
        Task(title="学习新技术", description="学习GraphQL技术", priority=3),
        Task(title="代码审查", description="审查团队成员的代码", priority=3, due_date=next_week),
        
        # 部分已完成任务
        Task(title="环境搭建", description="搭建开发环境", priority=1, is_completed=True, due_date=today),
        Task(title="需求分析", description="分析用户需求", priority=2, is_completed=True, due_date=today)
    ]
    
    task_repo.insert_many(test_tasks)
    print(f"已插入 {len(test_tasks)} 条测试数据")


def run_raw_sql_queries(cursor):
    """执行原始SQL查询示例
    
    Args:
        cursor: 数据库游标对象
    """
    print("\n--- 执行原始SQL查询 ---")
    
    # 1. 聚合查询：按优先级统计任务数量
    print("\n1. 按优先级统计任务数量")
    cursor.execute("""
        SELECT priority, COUNT(*) as task_count
        FROM tasks
        GROUP BY priority
        ORDER BY priority
    """)
    results = cursor.fetchall()
    for row in results:
        print(f"  优先级 {row['priority']}: {row['task_count']} 条任务")
        
    # 2. 连接查询示例 (假设有关联表)
    # 注意：此示例仅为展示连接查询语法，实际上我们没有创建user表
    print("\n2. 连接查询示例 (仅展示语法)")
    join_sql = """
        SELECT t.task_id, t.title, u.username
        FROM tasks t
        LEFT JOIN users u ON t.user_id = u.user_id
        WHERE t.priority = 1
        LIMIT 5
    """
    print(f"  SQL: {join_sql}")
    
    # 3. 使用CASE表达式和聚合函数
    print("\n3. 使用CASE表达式统计任务状态")
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END) as completed_count,
            SUM(CASE WHEN is_completed = 0 THEN 1 ELSE 0 END) as pending_count,
            COUNT(*) as total_count
        FROM tasks
    """)
    stats = cursor.fetchone()
    print(f"  总任务数: {stats['total_count']}")
    print(f"  已完成: {stats['completed_count']}")
    print(f"  待完成: {stats['pending_count']}")
    
    # 4. 复杂条件查询和排序
    print("\n4. 复杂条件查询和排序")
    cursor.execute("""
        SELECT task_id, title, priority, due_date
        FROM tasks
        WHERE is_completed = 0 
          AND priority <= 2
          AND (due_date IS NOT NULL AND due_date <= date('now', '+7 day'))
        ORDER BY priority ASC, due_date ASC
    """)
    urgent_tasks = cursor.fetchall()
    print(f"  一周内到期的高优先级未完成任务 ({len(urgent_tasks)} 条):")
    for task in urgent_tasks:
        print(f"    ID: {task['task_id']}, 优先级: {task['priority']}, 截止日期: {task['due_date']}, 标题: {task['title']}")
    
    # 5. 分页查询
    print("\n5. 分页查询")
    page_size = 3
    page_number = 1
    offset = (page_number - 1) * page_size
    
    cursor.execute("""
        SELECT task_id, title
        FROM tasks
        ORDER BY task_id
        LIMIT ? OFFSET ?
    """, (page_size, offset))
    page_tasks = cursor.fetchall()
    
    print(f"  第 {page_number} 页任务 (每页 {page_size} 条):")
    for task in page_tasks:
        print(f"    ID: {task['task_id']}, 标题: {task['title']}")
    
    # 6. 子查询和EXISTS
    print("\n6. 使用子查询查找今天到期的任务")
    cursor.execute("""
        SELECT task_id, title, due_date
        FROM tasks
        WHERE EXISTS (
            SELECT 1
            FROM tasks t2
            WHERE t2.task_id = tasks.task_id
              AND t2.due_date = date('now')
        )
        ORDER BY priority
    """)
    today_tasks = cursor.fetchall()
    print(f"  今天到期的任务 ({len(today_tasks)} 条):")
    for task in today_tasks:
        print(f"    ID: {task['task_id']}, 到期日: {task['due_date']}, 标题: {task['title']}")


def run_repository_queries(task_repo):
    """使用Repository执行查询示例
    
    Args:
        task_repo: 任务仓库对象
    """
    print("\n--- 使用Repository执行查询 ---")
    
    # 1. 查找优先级为1的任务
    print("\n1. 查找优先级为1的任务")
    priority_1_tasks = task_repo.find_by_criteria({"priority": 1})
    print(f"  优先级为1的任务 ({len(priority_1_tasks)} 条):")
    for task in priority_1_tasks:
        print(f"    ID: {task.task_id}, 标题: {task.title}, 截止日期: {task.due_date}")
    
    # 2. 查找已完成的任务
    print("\n2. 查找已完成的任务")
    completed_tasks = task_repo.find_by_criteria({"is_completed": 1})
    print(f"  已完成的任务 ({len(completed_tasks)} 条):")
    for task in completed_tasks:
        print(f"    ID: {task.task_id}, 标题: {task.title}")
    
    # 3. 根据标题搜索任务
    print("\n3. 搜索标题中包含'代码'的任务")
    code_tasks = task_repo.find_by_title_contains("代码")
    print(f"  标题包含'代码'的任务 ({len(code_tasks)} 条):")
    for task in code_tasks:
        print(f"    ID: {task.task_id}, 标题: {task.title}")


def run_service_queries(task_service):
    """使用Service执行业务逻辑查询示例
    
    Args:
        task_service: 任务服务对象
    """
    print("\n--- 使用Service执行业务逻辑查询 ---")
    
    # 1. 获取未完成的任务
    print("\n1. 获取未完成的任务")
    incomplete_tasks = task_service.get_incomplete_tasks()
    print(f"  未完成的任务 ({len(incomplete_tasks)} 条):")
    for task in incomplete_tasks[:3]:  # 只显示前3条
        print(f"    ID: {task.task_id}, 标题: {task.title}, 优先级: {task.priority}")
    if len(incomplete_tasks) > 3:
        print(f"    ... 及其他 {len(incomplete_tasks) - 3} 条")
    
    # 2. 获取7天内到期的任务
    print("\n2. 获取7天内到期的任务")
    due_soon_tasks = task_service.get_tasks_due_within_days(7)
    print(f"  7天内到期的任务 ({len(due_soon_tasks)} 条):")
    for task in due_soon_tasks:
        print(f"    ID: {task.task_id}, 标题: {task.title}, 截止日期: {task.due_date}")
    
    # 3. 获取已逾期的任务
    print("\n3. 获取已逾期的任务")
    overdue_tasks = task_service.get_overdue_tasks()
    print(f"  已逾期的任务 ({len(overdue_tasks)} 条):")
    for task in overdue_tasks:
        print(f"    ID: {task.task_id}, 标题: {task.title}, 截止日期: {task.due_date}")


def run_advanced_queries():
    """运行高级查询示例"""
    print("\n=== SQLite高级查询示例 ===")
    
    # 使用DatabaseManager创建数据库连接
    db_file = "advanced_queries.db"
    db_manager = DatabaseManager(db_file)
    
    # 清理旧数据库文件
    if os.path.exists(db_file):
        print(f"清理旧数据库文件: {db_file}")
        os.remove(db_file)
    
    # 使用with语句自动管理连接
    with db_manager as manager:
        conn = manager.conn
        cursor = manager.cursor
        
        if not conn or not cursor:
            print("无法连接到数据库，示例终止。")
            return
        
        # 创建任务仓库和服务
        task_repo = TaskRepository(conn, cursor)
        task_service = TaskService(task_repo)
        
        # 创建任务表
        if not task_repo.create_table():
            print("任务表创建失败，示例终止。")
            return
        
        # 填充测试数据
        populate_test_data(task_repo)
        
        # 执行原始SQL查询示例
        run_raw_sql_queries(cursor)
        
        # 使用Repository执行查询示例
        run_repository_queries(task_repo)
        
        # 使用Service执行业务逻辑查询示例
        run_service_queries(task_service)
    
    print("\n示例结束，数据库连接已关闭。")


if __name__ == "__main__":
    run_advanced_queries()