# sqlite_practice/examples/advanced_queries_oop.py

"""
高级查询示例模块 (面向对象重构版)。
使用类封装演示流程，遵循面向对象原则，使用彩色输出。
展示SQLite数据库的高级查询功能，通过调用分层框架实现。
"""
import sys
import os
import sqlite3
from datetime import datetime, timedelta  # 导入 datetime/timedelta
from typing import Optional, Any, List  # 引入类型提示

# --- 导入框架组件 ---
from core.db_manager import DatabaseManager
from models.task import Task  # Task dataclass
from repositories.task_repository import TaskRepository
from services.task_service import TaskService


# --- 辅助类：用于彩色/样式化打印 ---
class Colors:
    """定义 ANSI 转义码常量用于彩色输出"""
    HEADER = '\033[95m'  # 紫色 (用于标题)
    BLUE = '\033[94m'  # 蓝色 (用于 SQL 或代码)
    CYAN = '\033[96m'  # 青色 (用于提示信息)
    GREEN = '\033[92m'  # 绿色 (用于成功信息)
    WARNING = '\033[93m'  # 黄色 (用于警告)
    FAIL = '\033[91m'  # 红色 (用于错误)
    BOLD = '\033[1m'  # 加粗
    UNDERLINE = '\033[4m'  # 下划线
    END = '\033[0m'  # 重置所有格式


# --- 打印辅助函数 ---
def print_header(text: str):
    """打印带样式的标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}--- {text} ---{Colors.END}")


def print_subheader(text: str):
    """打印带样式的子标题"""
    print(f"\n{Colors.CYAN}{Colors.UNDERLINE}  {text}{Colors.END}")


def print_info(text: str):
    """打印普通信息"""
    print(f"  {text}")


def print_success(text: str):
    """打印成功信息"""
    print(f"{Colors.GREEN}  ✔ {text}{Colors.END}")


def print_warning(text: str):
    """打印警告信息"""
    print(f"{Colors.WARNING}  ⚠️ [Warning] {text}{Colors.END}")


def print_error(text: str):
    """打印错误信息"""
    print(f"{Colors.FAIL}  ❌ [Error] {text}{Colors.END}")


def print_sql(sql: str):
    """打印格式化的 SQL 语句"""
    print(f"{Colors.BLUE}    SQL: {sql.strip()}{Colors.END}")


def print_result_item(item: Any, indent: int = 4):
    """打印格式化的查询结果项"""
    prefix = " " * indent
    if isinstance(item, Task):
        # 使用 Task 的 __repr__ (dataclass 自动生成)
        print(f"{prefix}{item}")
    elif hasattr(item, 'keys'):  # 支持 sqlite3.Row 或字典
        details = ", ".join([f"{Colors.BOLD}{key}{Colors.END}: {item[key]}" for key in item.keys()])
        print(f"{prefix}Row({details})")
    else:
        print(f"{prefix}{item}")


# --- 主演示类 ---
class AdvancedQueryDemoOO:
    """
    面向对象的 SQLite 高级查询演示类。
    封装了演示的设置、执行和清理逻辑。
    """
    # 类属性定义数据库文件路径
    DB_FILE = "advanced_queries_oop.db"

    def __init__(self):
        """初始化演示类实例"""
        print_header("初始化高级查询演示 (OOP)")
        # 创建 DatabaseManager 实例，但不立即连接
        self.db_manager = DatabaseManager(self.DB_FILE)
        # 初始化依赖对象为 None
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
        self.task_repo: Optional[TaskRepository] = None
        self.task_service: Optional[TaskService] = None
        # 执行数据库清理
        self._cleanup_db()

    def _cleanup_db(self):
        """(私有方法) 清理旧的数据库文件"""
        if os.path.exists(self.DB_FILE):
            try:
                os.remove(self.DB_FILE)
                print_info(f"旧数据库文件 '{self.DB_FILE}' 已清理。")
            except OSError as e:
                print_error(f"清理数据库文件 '{self.DB_FILE}' 失败: {e}")
                # 清理失败可能导致后续问题，可以选择退出或继续
                # sys.exit(1)

    def _setup_database_and_framework(self):
        """(私有方法) 建立数据库连接，初始化框架组件，并填充测试数据"""
        print_subheader("1. 设置数据库和框架组件")
        # self.db_manager 在 __init__ 中已创建
        # 使用 with 语句管理连接
        # 注意：这里我们将 conn 和 cursor 存储在 self 上，以便后续方法使用
        # 这在简单演示类中可行，但在多线程或长期运行应用中需谨慎管理状态
        self.conn, self.cursor = self.db_manager.connect()  # 直接调用 connect
        if not self.conn or not self.cursor:
            raise ConnectionError("未能获取数据库连接或游标")

        # 初始化 Repository (依赖 conn, cursor)
        # Repository 初始化时会尝试创建表
        self.task_repo = TaskRepository(self.conn, self.cursor)

        # 初始化 Service (依赖 task_repo)
        self.task_service = TaskService(self.task_repo)
        print_success("Repository 和 Service 初始化成功。")

        # 新建数据表
        self.task_repo.create_table()

        # 填充测试数据
        if not self._populate_test_data():
            raise RuntimeError("填充测试数据失败。")  # 如果填充失败，抛出异常

    def get_future_date(self, days: int, format_str: str = '%Y-%m-%d') -> str:
        """获取未来日期字符串

        Args:
            days: 向后推的天数
            format_str: 日期格式，默认为 'YYYY-MM-DD'

        Returns:
            str: 未来日期字符串
        """
        future_date = datetime.now() + timedelta(days=days)
        return future_date.strftime(format_str)

    def _populate_test_data(self) -> bool:
        """(私有方法) 向数据库填充测试数据"""
        if not self.task_repo: return False  # 防御性检查
        print_subheader("2. 填充测试数据")
        today = datetime.now().strftime('%Y-%m-%d')
        tomorrow = self.get_future_date(1)
        next_week = self.get_future_date(7)
        next_month = self.get_future_date(30)
        yesterday = self.get_future_date(-1)

        test_tasks = [
            Task(title="完成项目设计文档", description="项目需求和架构设计", priority=1, due_date=tomorrow),
            Task(title="修复关键Bug", description="修复用户报告的登录问题", priority=1, due_date=today),
            Task(title="制定项目计划", description="项目时间线和里程碑规划", priority=1, due_date=next_week),
            Task(title="紧急会议准备", priority=1, due_date=today, is_completed=False),
            Task(title="代码重构", description="重构认证模块的代码", priority=2, due_date=next_week),
            Task(title="单元测试编写", description="为核心功能编写单元测试", priority=2, due_date=next_week),
            Task(title="API文档更新", description="更新REST API文档", priority=2, due_date=next_month),
            Task(title="中期报告撰写", priority=2, due_date=self.get_future_date(10)),
            Task(title="性能优化", description="优化数据库查询性能", priority=3, due_date=next_month),
            Task(title="学习新技术", description="学习 GraphQL 技术", priority=3, due_date=None),
            Task(title="代码审查", description="审查团队成员的代码", priority=3, due_date=next_week),
            Task(title="环境搭建", description="搭建开发环境", priority=1, is_completed=True, due_date=yesterday),
            Task(title="需求分析", description="分析用户需求", priority=2, is_completed=True, due_date=today),
            Task(title="旧项目归档", priority=3, is_completed=True, due_date=None)
        ]

        inserted_count = self.task_repo.insert_many(test_tasks)
        if inserted_count is not None:
            print_success(
                f"已尝试插入 {len(test_tasks)} 条测试数据，成功 {inserted_count if inserted_count != -1 else len(test_tasks)} 条。")
            return True
        else:
            print_error("填充测试数据过程中发生错误。")
            return False

    def _demonstrate_raw_sql(self):
        """(私有方法) 演示直接执行原生 SQL 查询"""
        print_header("演示: 直接执行原生 SQL 查询")
        if not self.cursor:
            print_error("数据库游标无效。")
            return

        try:
            print_subheader("1. 按优先级统计任务数量 (GROUP BY, COUNT)")
            self.cursor.execute(
                f"SELECT priority, COUNT(*) as task_count FROM {self.task_repo.table_name} GROUP BY priority ORDER BY priority")
            for row in self.cursor.fetchall(): print_result_item(row)

            print_subheader("2. 连接查询示例 (LEFT JOIN 语法演示)")
            join_sql = f"SELECT t.task_id, t.title, u.username FROM {self.task_repo.table_name} t LEFT JOIN users u ON t.user_id = u.user_id WHERE t.priority = 1 LIMIT 5"
            print_sql(join_sql + " (仅演示语法, users 表不存在)")

            print_subheader("3. 使用 CASE 表达式统计任务状态")
            self.cursor.execute(
                f"SELECT SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END) as completed_count, SUM(CASE WHEN is_completed = 0 THEN 1 ELSE 0 END) as pending_count, COUNT(*) as total_count FROM {self.task_repo.table_name}")
            stats = self.cursor.fetchone()
            if stats: print_result_item(stats)

            print_subheader("4. 复杂条件查询: 一周内到期的高优先级(<=2)未完成任务")
            self.cursor.execute(
                f"SELECT task_id, title, priority, due_date FROM {self.task_repo.table_name} WHERE is_completed = 0 AND priority <= ? AND (due_date IS NOT NULL AND due_date <= date('now', '+7 days')) ORDER BY priority ASC, due_date ASC",
                (2,))
            urgent_tasks = self.cursor.fetchall()
            print_info(f"找到 {len(urgent_tasks)} 条:")
            for task in urgent_tasks: print_result_item(task)

            print_subheader("5. 分页查询: 获取第 2 页数据 (每页 3 条)")
            page_size, page_number = 3, 2
            offset = (page_number - 1) * page_size
            self.cursor.execute(
                f"SELECT task_id, title FROM {self.task_repo.table_name} ORDER BY task_id LIMIT ? OFFSET ?",
                (page_size, offset))
            page_tasks = self.cursor.fetchall()
            print_info(f"第 {page_number} 页 (每页 {page_size} 条):")
            for task in page_tasks: print_result_item(task)

            print_subheader("6. 子查询: 查找所有今天到期的任务 (使用 EXISTS)")
            self.cursor.execute(
                f"SELECT task_id, title, due_date FROM {self.task_repo.table_name} t1 WHERE EXISTS (SELECT 1 FROM {self.task_repo.table_name} t2 WHERE t2.task_id = t1.task_id AND t2.due_date = date('now')) ORDER BY priority")
            today_tasks = self.cursor.fetchall()
            print_info(f"今天 ({datetime.now().strftime('%Y-%m-%d')}) 到期的任务 ({len(today_tasks)} 条):")
            for task in today_tasks: print_result_item(task)

        except sqlite3.Error as e:
            print_error(f"执行原生 SQL 查询时出错: {e}")

    def _demonstrate_repository_queries(self):
        """(私有方法) 演示使用 TaskRepository 方法进行查询"""
        print_header("演示: 使用 Repository 方法进行查询")
        if not self.task_repo:
            print_error("TaskRepository 未初始化。")
            return

        try:
            print_subheader("1. 查找优先级为 1 的任务")
            priority_1_tasks = self.task_repo.find_by_criteria({"priority": 1})
            print_info(f"找到 {len(priority_1_tasks)} 条:")
            for task in priority_1_tasks: print_result_item(task)

            print_subheader("2. 查找已完成的任务")
            completed_tasks = self.task_repo.find_by_criteria({"is_completed": True})
            print_info(f"找到 {len(completed_tasks)} 条:")
            for task in completed_tasks: print_result_item(task)

            print_subheader("3. 搜索标题中包含 '代码' 的任务")
            code_tasks = self.task_repo.find_by_title_contains("代码")
            print_info(f"找到 {len(code_tasks)} 条:")
            for task in code_tasks: print_result_item(task)

            print_subheader("4. 组合条件查询 (优先级=2 且 未完成)")
            prio2_incomplete = self.task_repo.find_by_criteria({"priority": 2, "is_completed": False})
            print_info(f"找到 {len(prio2_incomplete)} 条:")
            for task in prio2_incomplete: print_result_item(task)

        except Exception as e:
            print_error(f"使用 Repository 查询时出错: {e}")

    def _demonstrate_service_queries(self):
        """(私有方法) 演示使用 TaskService 方法进行业务查询"""
        print_header("演示: 使用 Service 层进行业务查询")
        if not self.task_service:
            print_error("TaskService 未初始化。")
            return

        try:
            print_subheader("1. 获取未完成的任务")
            incomplete_tasks = self.task_service.get_incomplete_tasks()
            print_info(f"找到 {len(incomplete_tasks)} 条:")
            for task in incomplete_tasks[:3]: print_result_item(task)
            if len(incomplete_tasks) > 3: print_info(f"    ... 及其他 {len(incomplete_tasks) - 3} 条")

            print_subheader("2. 获取未来 7 天内到期的任务")
            due_soon_tasks = self.task_service.get_tasks_due_within_days(7)
            print_info(f"找到 {len(due_soon_tasks)} 条:")
            for task in due_soon_tasks: print_result_item(task)

            print_subheader("3. 获取已逾期的未完成任务")
            overdue_tasks = self.task_service.get_overdue_tasks()
            print_info(f"找到 {len(overdue_tasks)} 条:")
            for task in overdue_tasks: print_result_item(task)

        except Exception as e:
            print_error(f"使用 Service 查询时出错: {e}")

    def run(self):
        """
        执行完整的演示流程: 设置 -> 填充数据 -> 各种查询演示 -> 清理。
        使用 try...finally 确保数据库连接总是被关闭。
        """
        try:
            # --- 步骤 1: 设置数据库和框架 ---
            # 使用 with 语句确保连接在 setup 完成后也可用，
            # 同时在 run 方法结束时通过 finally 关闭。
            # 或者，让 setup 返回 conn/cursor/repo/service
            self._setup_database_and_framework()

            # --- 步骤 2: 执行各种查询演示 ---
            if self.cursor: self._demonstrate_raw_sql()
            if self.task_repo: self._demonstrate_repository_queries()
            if self.task_service: self._demonstrate_service_queries()

            print_success("\n所有查询演示执行完毕。")

        except ConnectionError as ce:
            print_error(f"数据库连接错误: {ce}")
        except RuntimeError as rte:  # 捕获 setup 中可能抛出的错误
            print_error(f"运行时错误 (可能在设置或填充数据时): {rte}")
        except sqlite3.Error as db_err:
            print_error(f"数据库操作错误: {db_err}")
            import traceback
            traceback.print_exc()
        except Exception as e:
            print_error(f"发生意外错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # --- 步骤 3: 清理 ---
            # 无论 run 方法中发生什么，都确保关闭连接
            if self.db_manager:
                self.db_manager.close()
            print_header("高级查询演示流程结束")


# --- 脚本入口 ---
if __name__ == "__main__":
    # 1. 创建演示类的实例
    demo = AdvancedQueryDemoOO()
    # 2. 运行演示
    demo.run()
