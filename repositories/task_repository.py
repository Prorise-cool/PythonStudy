"""
任务数据访问层模块，实现对Task数据的CRUD操作。
"""
import sqlite3
from typing import List, Optional, Dict, Any, Tuple
from models.task import Task
from core.table_manager import TableManager


class TaskRepository:
    """任务数据访问类，实现对Task表的增删改查操作"""

    def __init__(self, conn: sqlite3.Connection, cursor: sqlite3.Cursor):
        self.conn = conn
        self.cursor = cursor
        self.table_name = 'tasks'  # 表名
        self.table_manager = TableManager(self.conn, self.cursor)

    def create_table(self) -> bool:
        """创建任务表"""
        columns = {
            "task_id": "INTEGER PRIMARY KEY AUTOINCREMENT",  # 任务ID
            "title": "TEXT NOT NULL",  # 任务标题
            "description": "TEXT",  # 任务描述
            "priority": "INTEGER DEFAULT 3",  # 优先级，默认3
            "due_date": "DATE",  # 截止日期
            "is_completed": "BOOLEAN DEFAULT 0",  # 是否完成，默认False
            "attachment": "BLOB",  # 附件，用于存储文件
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",  # 创建时间
            "last_updated": "TIMESTAMP"  # 最后更新时间
        }
        # 调用TableManager的create_table方法创建任务表
        created_flag = self.table_manager.create_table(self.table_name, columns)
        return created_flag

    def add_column(self, column_name: str, column_type: str) -> bool:
        """向任务表添加新列
        Args:
            column_name: 新列名
            column_type: 新列类型
            
        """
        added_flag = self.table_manager.add_column(self.table_name, column_name, column_type)
        return added_flag

    def get_table_info(self) -> List[Dict[str, Any]]:
        """获取任务表结构信息
        Returns:
            list: 包含列信息的字典列表
        """
        table_info = self.table_manager.get_table_info(self.table_name)
        return table_info

    def insert_task(self, task: Task) -> Optional[int]:
        """插入新任务
        Args:
            task: Task对象
        Returns:
            int: 新任务的ID，如果插入失败返回None
        """
        try:
            # 将Task对象转换为字典
            task_dict = task.to_dict()

            # 如果存在task_id，则从字典中移除，因为它是自增的
            if 'task_id' in task_dict:
                del task_dict['task_id']

            # 构建INSERT语句
            columns = ', '.join(task_dict.keys())
            """
            placeholders的执行逻辑：类似于下方的代码
            task_dict = {'task1': 'value1', 'task2': 'value2', 'task3': 'value3'}
            question_marks = ', '.join(['?' for _ in task_dict])
            print(question_marks)  # 输出: ?, ?, ?
            '"""
            placeholders = placeholders = ', '.join(['?' for _ in task_dict])
            values = tuple(task_dict.values())
            insert_sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
            # 执行插入操作
            self.cursor.execute(insert_sql, values)
            self.conn.commit()
            # 获取新插入记录的ID
            inserted_id = self.cursor.lastrowid
            print(f"[Info] 成功插入任务: '{task.title}', ID: {inserted_id}")
            return inserted_id
        except sqlite3.Error as e:
            print(f"[Error] 任务插入失败: {e}")
            self.conn.rollback()
            return None

    def insert_many(self, tasks: List[Task]) -> Optional[int]:
        """批量插入任务记录

        Args:
            tasks: 要插入的Task对象列表

        Returns:
            int: 成功插入的记录数，如果插入失败则返回None
        """
        try:
            # 确保有任务要插入
            if not tasks:
                print("[Warning] 没有任务要插入")
                return 0
            # 将所有Task对象转换为字典
            task_dicts = [task.to_dict() for task in tasks]
            # 移除所有task_id，因为它们是自增的
            for task_dict in task_dicts:
                if 'task_id' in task_dict:
                    del task_dict['task_id']
            # 确保所有任务的字段相同
            columns = list(task_dicts[0].keys())
            placeholders = ', '.join(['?' for _ in columns])

            # 构建INSERT语句
            insert_sql = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES ({placeholders})"

            # 准备批量插入的值
            # 这段代码使用列表推导式创建一个包含所有任务数据的列表:
            # 1. 外层循环遍历每个任务字典(task_dicts中的每个task_dict)
            # 2. 内层循环按照columns中定义的列顺序提取每个任务字典中的值
            # 3. 使用tuple()将每个任务的值转换为元组，确保与executemany()方法兼容
            # 4. 最终生成的values是一个元组列表，每个元组包含一个任务的所有字段值
            # 例如: [(任务1的值1, 任务1的值2...), (任务2的值1, 任务2的值2...), ...]
            values = [tuple(task_dict[col] for col in columns) for task_dict in task_dicts]
            print(f"[Info] 准备批量插入{len(values)}条任务")

            # 执行批量插入
            self.cursor.executemany(insert_sql, values)
            self.conn.commit()

            # 获取新插入记录的数量
            inserted_count = self.cursor.rowcount
            print(f"[Info] 成功插入{inserted_count}条任务")
            return inserted_count
        except sqlite3.Error as e:
            print(f"[Error] 任务插入失败: {e}")
            self.conn.rollback()
            return None

    def update_task(self, task: Task) -> bool:
        """更新任务记录
        Args:
            task: 要更新的Task对象，必须包含task_id
        Returns:
            bool: 是否更新成功
        """
        try:
            # 检查task_id是否存在
            if task.task_id is None:
                print("[Error] 无法更新任务：缺少task_id")
                return False
            # 将Task对象转换为字典
            task_dict = task.to_dict()

            # 从字典中移除task_id，他讲在WHERE子句中使用
            task_id = task_dict.pop('task_id')

            # 构建SET字句
            """
            这将生成类似于下面的SQL语句：
            UPDATE tasks SET title = 'task1', description = 'task1 description', priority = 1, due_date = '2022-01-01', is_completed = 1, attachment = b'123456', last_updated = '2022-01-01 00:00:00' WHERE task_id = 1
            """
            set_clause = ', '.join([f"{col} = ?" for col in task_dict.keys()])

            # 检查task_dict中是否已包含last_updated字段
            if 'last_updated' not in task_dict:
                # 如果没有包含last_updated字段，则使用SQLite的CURRENT_TIMESTAMP函数
                # 这样可以确保last_updated字段使用数据库服务器的当前时间
                set_clause += ", last_updated = CURRENT_TIMESTAMP"

            # 构建UPDATE语句
            update_sql = f"UPDATE {self.table_name} SET {set_clause} WHERE task_id = ?"
            # 准备参数值
            values = list(task_dict.values())
            values.append(task_id)
            
            # 执行更新操作
            self.cursor.execute(update_sql, values)
            self.conn.commit()

            # 检查是否有行被更新
            updated_count = self.cursor.rowcount
            if updated_count > 0:
                print(f"[Info] 成功更新任务 ID={task_id}")
                return True
            else:
                print(f"[Warning] 未找到要更新的任务 ID={task_id}")
                return False
        except sqlite3.Error as e:
            print(f"[Error] 任务更新失败: {e}")
            self.conn.rollback()
            return False

    def delete_task(self, task_id: int) -> bool:
        """删除任务记录
        Args:
            task_id: 要删除的任务ID
        Returns:
            bool: 是否删除成功
        """
        try:
            #   构建DELETE语句
            delete_sql = f"DELETE FROM {self.table_name} WHERE task_id = ?"

            # 执行删除操作
            self.cursor.execute(delete_sql, (task_id,))

            # 检查是否有行被删除
            deleted_count = self.cursor.rowcount
            if deleted_count > 0:
                print(f"[Info] 成功删除任务 ID={task_id}")
                return True
            else:
                print(f"[Warning] 未找到要删除的任务 ID={task_id}")
                return False
        except sqlite3.Error as e:
            print(f"[Error] 任务删除失败: {e}")
            self.conn.rollback()
            return False

    def find_task_by_id(self, task_id: int) -> Optional[Task]:
        """根据任务ID查找任务记录"""
        try:
            # 构建SELECT语句
            select_sql = f"SELECT * FROM {self.table_name} WHERE task_id = ?"

            # 执行查询操作
            self.cursor.execute(select_sql, (task_id,))

            #  获取查询结果
            row = self.cursor.fetchone()

            # 如果未找到，返回None
            if row is None:
                return None

            # 将结果转换为Task对象
            return Task.from_row(row)
        except sqlite3.Error as e:
            print(f"[Error] 任务查找失败: {e}")
            return None

    def find_all_tasks(self) -> List[Task]:
        """查找所有任务记录"""
        try:
            # 构建SELECT语句
            select_sql = f"SELECT * FROM {self.table_name}"

            # 执行查询操作
            self.cursor.execute(select_sql)

            # 获取所有结果
            rows = self.cursor.fetchall()

            # 将结果转换为Task对象列表
            return [Task.from_row(row) for row in rows]
        except sqlite3.Error as e:
            print(f"[Error] 任务查找失败: {e}")
            return []

    def find_by_criteria(self, criteria: Dict[str, Any]) -> List[Task]:
        """根据条件查找任务

        Args:
            criteria: 查询条件字典，格式为 {列名: 值}

        Returns:
            list: 符合条件的Task对象列表
        """
        try:
            # 确保有条件要查询
            if not criteria:
                return self.find_all_tasks()
            # 构建WHERE子句
            values = []  # 用于占位符
            where_clauses = []  # 用于条件
            for col, val in criteria.items():
                where_clauses.append(f"{col} = ?")
                values.append(val)
            where_clause = ' AND '.join(where_clauses)  # 例如：查询条件: priority = ? 若有多个条件，则用AND连接

            # 构建SELECT语句
            select_sql = f"SELECT * FROM {self.table_name} WHERE {where_clause}"

            # 执行查询操作
            self.cursor.execute(select_sql, values)

            # 获取所有结果
            rows = self.cursor.fetchall()

            # 奖结果转换为Task对象列表
            return [Task.from_row(row) for row in rows]


        except sqlite3.Error as e:
            print(f"[Error] 任务查找失败: {e}")
            return []

    def find_by_title_contains(self, title_part: str) -> List[Task]:
        """根据标题部分查找任务"""
        try:
            # 构建SELECT语句 使用LIKE模糊查询
            select_sql = f"SELECT * FROM {self.table_name} WHERE title LIKE ?"
            # 执行查询，使用%作为通配符
            self.cursor.execute(select_sql, (f'%{title_part}%',))
            # 获取所有结果
            rows = self.cursor.fetchall()

            # 将结果转换为Task对象列表
            return [Task.from_row(row) for row in rows]
        except sqlite3.Error as e:
            print(f"[Error] 任务查找失败: {e}")
            return []

