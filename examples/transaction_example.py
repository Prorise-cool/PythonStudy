"""
事务处理示例模块，展示SQLite数据库的事务处理功能。
包括事务提交、回滚、保存点等操作。
"""
import os
import sqlite3
from core.db_manager import DatabaseManager
from models.task import Task
from repositories.task_repository import TaskRepository


def run_basic_transaction():
    """基本事务示例"""
    print("\n--- 基本事务示例 ---")
    
    # 创建一个临时数据库
    db_file = "transaction_example.db"
    if os.path.exists(db_file):
        os.remove(db_file)
    
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 创建测试表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            account_id INTEGER PRIMARY KEY,
            account_name TEXT NOT NULL,
            balance REAL NOT NULL
        )
    ''')
    
    # 插入初始数据
    cursor.executemany(
        "INSERT INTO accounts (account_name, balance) VALUES (?, ?)",
        [("账户A", 1000.0), ("账户B", 500.0)]
    )
    conn.commit()
    
    # 显示初始余额
    cursor.execute("SELECT * FROM accounts")
    accounts = cursor.fetchall()
    print("\n初始账户余额:")
    for acc in accounts:
        print(f"  {acc['account_name']}: {acc['balance']:.2f}")
    
    # 开始转账事务
    print("\n执行转账: 账户A -> 账户B 转账300元")
    try:
        # 在SQLite中，默认情况下每个DML语句都自动在事务中执行
        # 但如果我们想要多个语句作为一个原子操作，需要显式控制事务
        
        # 扣除账户A的余额
        cursor.execute(
            "UPDATE accounts SET balance = balance - ? WHERE account_name = ?",
            (300.0, "账户A")
        )
        
        # 在这里可以引入故意的错误来测试回滚
        # if True:
        #     raise Exception("模拟转账过程中的错误")
        
        # 增加账户B的余额
        cursor.execute(
            "UPDATE accounts SET balance = balance + ? WHERE account_name = ?",
            (300.0, "账户B")
        )
        
        # 提交事务
        conn.commit()
        print("  转账成功!")
        
    except Exception as e:
        # 如果发生错误，回滚事务
        conn.rollback()
        print(f"  转账失败! 错误: {e}")
        print("  事务已回滚，账户余额保持不变。")
    
    # 显示最终余额
    cursor.execute("SELECT * FROM accounts")
    accounts = cursor.fetchall()
    print("\n最终账户余额:")
    for acc in accounts:
        print(f"  {acc['account_name']}: {acc['balance']:.2f}")
    
    # 关闭连接
    cursor.close()
    conn.close()


def run_savepoint_transaction():
    """使用保存点的事务示例"""
    print("\n--- 使用保存点的事务示例 ---")
    
    # 创建一个临时数据库
    db_file = "savepoint_example.db"
    if os.path.exists(db_file):
        os.remove(db_file)
    
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 创建测试表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    
    try:
        # 开始事务
        print("\n开始事务...")
        
        # 添加第一批任务
        cursor.executemany(
            "INSERT INTO tasks (title, status) VALUES (?, ?)",
            [
                ("任务1", "待处理"),
                ("任务2", "待处理"),
                ("任务3", "待处理")
            ]
        )
        print("  已添加第一批任务")
        
        # 创建保存点
        print("  创建保存点 'sp1'")
        cursor.execute("SAVEPOINT sp1")
        
        # 添加第二批任务
        cursor.executemany(
            "INSERT INTO tasks (title, status) VALUES (?, ?)",
            [
                ("任务4", "待处理"),
                ("任务5", "待处理")
            ]
        )
        print("  已添加第二批任务")
        
        # 模拟错误情况
        if True:  # 设置为True来测试回滚到保存点
            print("  发现错误：第二批任务有问题！")
            print("  回滚到保存点 'sp1'")
            cursor.execute("ROLLBACK TO SAVEPOINT sp1")
        else:
            print("  第二批任务没有问题，保留所有更改")
            
        # 释放保存点
        cursor.execute("RELEASE SAVEPOINT sp1")
        
        # 添加第三批任务
        cursor.executemany(
            "INSERT INTO tasks (title, status) VALUES (?, ?)",
            [
                ("任务6", "待处理"),
                ("任务7", "待处理")
            ]
        )
        print("  已添加第三批任务")
        
        # 提交整个事务
        conn.commit()
        print("  整个事务已提交")
        
    except Exception as e:
        # 如果发生错误，回滚整个事务
        conn.rollback()
        print(f"  发生错误: {e}")
        print("  整个事务已回滚")
    
    # 显示最终的任务列表
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    print("\n最终任务列表:")
    for task in tasks:
        print(f"  ID: {task['task_id']}, 标题: {task['title']}, 状态: {task['status']}")
    
    # 关闭连接
    cursor.close()
    conn.close()


def run_with_transaction():
    """使用with语句的事务示例，优雅处理异常"""
    print("\n--- 使用with语句的事务示例 ---")
    
    # 创建一个临时数据库
    db_file = "with_transaction_example.db"
    if os.path.exists(db_file):
        os.remove(db_file)
    
    # 使用DatabaseManager提供的上下文管理功能
    with DatabaseManager(db_file) as db_manager:
        conn = db_manager.conn
        cursor = db_manager.cursor
        
        # 创建任务表
        task_repo = TaskRepository(conn, cursor)
        if not task_repo.create_table():
            print("任务表创建失败，示例终止。")
            return
        
        print("\n尝试在一个事务中批量处理任务...")
        try:
            # 开始事务 (SQLite默认在执行DML时自动开始事务)
            
            # 添加一些任务
            tasks = [
                Task(title="事务任务1", priority=1),
                Task(title="事务任务2", priority=2),
                Task(title="事务任务3", priority=3)
            ]
            task_repo.insert_many(tasks)
            
            # 模拟在事务中间修改一个任务状态
            # 查询所有任务
            all_tasks = task_repo.find_all()
            if all_tasks:
                # 修改第一个任务
                task_to_update = all_tasks[0]
                task_to_update.is_completed = True
                task_to_update.description = "在事务中更新的任务"
                task_repo.update(task_to_update)
                print(f"  已将任务 '{task_to_update.title}' 标记为完成")
            
            # 可以在这里引入错误来演示回滚
            # if True:
            #     raise Exception("模拟事务处理过程中的错误")
            
            # 删除最后一个任务
            if len(all_tasks) > 2:
                last_task = all_tasks[-1]
                task_repo.delete(last_task.task_id)
                print(f"  已删除任务 '{last_task.title}'")
            
            # 到这里事务会被自动提交 (在with块退出时)
            print("  事务成功完成!")
            
        except Exception as e:
            # 发生异常时会自动回滚 (在上下文管理器的__exit__中)
            print(f"  事务执行失败: {e}")
            print("  事务已回滚！")
    
    # with块外部，连接已关闭
    print("\n事务示例完成。")


def run_transaction_examples():
    """运行所有事务示例"""
    print("\n=== SQLite事务处理示例 ===")
    
    # 基本事务示例
    run_basic_transaction()
    
    # 使用保存点的事务示例
    run_savepoint_transaction()
    
    # 使用with语句的事务示例
    run_with_transaction()
    
    print("\n所有事务示例已完成。")


if __name__ == "__main__":
    run_transaction_examples()