"""
任务数据访问层模块，实现对Task数据的CRUD操作。
"""
import sqlite3
from typing import List, Optional, Dict, Any, Tuple
from models.task import Task


class TaskRepository:
    """任务数据访问类，实现对Task表的增删改查操作"""
    
    def __init__(self, conn: sqlite3.Connection, cursor: sqlite3.Cursor):
        """初始化任务数据访问层
        
        Args:
            conn: 数据库连接对象
            cursor: 数据库游标对象
        """
        self.conn = conn
        self.cursor = cursor
        self.table_name = "tasks"
        
    def create_table(self) -> bool:
        """创建任务表
        
        Returns:
            bool: 表创建是否成功
        """
        try:
            # 定义任务表结构
            # 定义各列的数据类型和约束
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
            
            # 构建列定义字符串
            columns_def = []
            for col_name, col_type in columns.items():
                columns_def.append(f"{col_name} {col_type}")

            create_table_sql = f'''CREATE TABLE IF NOT EXISTS {self.table_name} (
                {', '.join(columns_def)}
            )'''
            
            self.cursor.execute(create_table_sql)
            self.conn.commit()
            print(f"[Setup] 表 '{self.table_name}' 已检查/创建。")
            
            return True
            
        except sqlite3.Error as e:
            print(f"[Error] 创建表 '{self.table_name}' 时出错: {e}")
            return False
    
    def insert(self, task: Task) -> Optional[int]:
        """插入任务记录
        
        Args:
            task: 要插入的Task对象
            
        Returns:
            int: 新插入记录的ID，如果插入失败则返回None
        """
        try:
            # 将Task对象转换为字典
            task_dict = task.to_dict()
            
            # 如果存在task_id，则从字典中移除，因为它是自增的
            if 'task_id' in task_dict:
                del task_dict['task_id']
                
            # 构建INSERT语句
            columns = ', '.join(task_dict.keys())
            placeholders = ', '.join(['?' for _ in task_dict])
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
            print(f"[Error] 插入任务失败: {e}")
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
            values = [tuple(task_dict[col] for col in columns) for task_dict in task_dicts]
            
            # 执行批量插入
            self.cursor.executemany(insert_sql, values)
            self.conn.commit()
            
            # 获取受影响的行数
            inserted_count = self.cursor.rowcount
            print(f"[Info] 成功批量插入 {inserted_count} 条任务记录。")
            
            return inserted_count
            
        except sqlite3.Error as e:
            print(f"[Error] 批量插入任务失败: {e}")
            self.conn.rollback()
            return None
    
    def update(self, task: Task) -> bool:
        """更新任务记录
        
        Args:
            task: 要更新的Task对象，必须包含task_id
            
        Returns:
            bool: 更新是否成功
        """
        try:
            # 检查task_id是否存在
            if task.task_id is None:
                print("[Error] 无法更新任务：缺少task_id")
                return False
                
            # 将Task对象转换为字典
            task_dict = task.to_dict()
            
            # 从字典中移除task_id，它将在WHERE子句中使用
            task_id = task_dict.pop('task_id')
            
            # 构建SET子句
            set_clause = ', '.join([f"{col} = ?" for col in task_dict.keys()])
            
            # 添加last_updated字段
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
            print(f"[Error] 更新任务失败: {e}")
            self.conn.rollback()
            return False
    
    def delete(self, task_id: int) -> bool:
        """删除任务记录
        
        Args:
            task_id: 要删除的任务ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            # 构建DELETE语句
            delete_sql = f"DELETE FROM {self.table_name} WHERE task_id = ?"
            
            # 执行删除操作
            self.cursor.execute(delete_sql, (task_id,))
            self.conn.commit()
            
            # 检查是否有行被删除
            deleted_count = self.cursor.rowcount
            if deleted_count > 0:
                print(f"[Info] 成功删除任务 ID={task_id}")
                return True
            else:
                print(f"[Warning] 未找到要删除的任务 ID={task_id}")
                return False
                
        except sqlite3.Error as e:
            print(f"[Error] 删除任务失败: {e}")
            self.conn.rollback()
            return False
    
    def find_by_id(self, task_id: int) -> Optional[Task]:
        """根据ID查找任务
        
        Args:
            task_id: 要查找的任务ID
            
        Returns:
            Task: 找到的Task对象，如果未找到则返回None
        """
        try:
            # 构建SELECT语句
            select_sql = f"SELECT * FROM {self.table_name} WHERE task_id = ?"
            
            # 执行查询
            self.cursor.execute(select_sql, (task_id,))
            
            # 获取结果
            row = self.cursor.fetchone()
            
            # 如果未找到，返回None
            if row is None:
                return None
                
            # 将结果转换为Task对象
            return Task.from_row(row)
            
        except sqlite3.Error as e:
            print(f"[Error] 查找任务 ID={task_id} 失败: {e}")
            return None
    
    def find_all(self) -> List[Task]:
        """查找所有任务
        
        Returns:
            list: Task对象列表
        """
        try:
            # 构建SELECT语句
            select_sql = f"SELECT * FROM {self.table_name}"
            
            # 执行查询
            self.cursor.execute(select_sql)
            
            # 获取所有结果
            rows = self.cursor.fetchall()
            
            # 将结果转换为Task对象列表
            return [Task.from_row(row) for row in rows]
            
        except sqlite3.Error as e:
            print(f"[Error] 查找所有任务失败: {e}")
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
                return self.find_all()
                
            # 构建WHERE子句
            where_clauses = []
            values = []
            
            for col, val in criteria.items():
                where_clauses.append(f"{col} = ?")
                values.append(val)
                
            where_clause = ' AND '.join(where_clauses)
            
            # 构建SELECT语句
            select_sql = f"SELECT * FROM {self.table_name} WHERE {where_clause}"
            
            # 执行查询
            self.cursor.execute(select_sql, values)
            
            # 获取所有结果
            rows = self.cursor.fetchall()
            
            # 将结果转换为Task对象列表
            return [Task.from_row(row) for row in rows]
            
        except sqlite3.Error as e:
            print(f"[Error] 根据条件查找任务失败: {e}")
            return []
    
    def find_by_title_contains(self, title_part: str) -> List[Task]:
        """查找标题包含指定字符串的任务
        
        Args:
            title_part: 要搜索的标题部分
            
        Returns:
            list: 符合条件的Task对象列表
        """
        try:
            # 构建SELECT语句，使用LIKE进行模糊匹配
            select_sql = f"SELECT * FROM {self.table_name} WHERE title LIKE ?"
            
            # 执行查询，使用%作为通配符
            self.cursor.execute(select_sql, (f'%{title_part}%',))
            
            # 获取所有结果
            rows = self.cursor.fetchall()
            
            # 将结果转换为Task对象列表
            return [Task.from_row(row) for row in rows]
            
        except sqlite3.Error as e:
            print(f"[Error] 查找标题包含'{title_part}'的任务失败: {e}")
            return []