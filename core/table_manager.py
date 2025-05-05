"""
表管理模块，负责SQLite数据库表的创建和基础操作。
提供表结构定义、创建、修改等功能。
"""
import sqlite3
from typing import Dict, Any, List, Optional


class TableManager:
    """表管理类，负责SQLite数据库表的创建和操作"""
    
    def __init__(self, conn: sqlite3.Connection, cursor: sqlite3.Cursor):
        """初始化表管理器
        
        Args:
            conn: 数据库连接对象
            cursor: 数据库游标对象
        """
        self.conn = conn
        self.cursor = cursor
    
    def create_table(self, table_name: str, columns: Dict[str, str]) -> bool:
        """创建数据库表

        Args:
            table_name: 表名
            columns: 表列定义字典，格式为 {列名: 列类型}
            
        Returns:
            bool: 表创建是否成功
        """
        try:
            # 确保连接和游标有效
            if not self.conn or not self.cursor:
                print(f"[Error] 数据库连接或游标无效")
                return False
                
            # 构建列定义字符串
            columns_def = []
            for col_name, col_type in columns.items():
                columns_def.append(f"{col_name} {col_type}")

            create_table_sql = f'''CREATE TABLE IF NOT EXISTS {table_name} (
                {', '.join(columns_def)}
            )'''
            
            self.cursor.execute(create_table_sql)
            self.conn.commit()
            print(f"[Setup] 表 '{table_name}' 已检查/创建。")
            
            return True
            
        except sqlite3.Error as e:
            print(f"[Error] 创建表 '{table_name}' 时出错: {e}")
            return False
            
    def add_column(self, table_name: str, column_name: str, column_type: str) -> bool:
        """向已有表添加新列
        
        Args:
            table_name: 表名
            column_name: 列名
            column_type: 列类型和约束
            
        Returns:
            bool: 添加列是否成功
        """
        try:
            alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            self.cursor.execute(alter_sql)
            self.conn.commit()
            print(f"[Setup] 已向表 '{table_name}' 添加列 '{column_name} {column_type}'")
            return True
        except sqlite3.Error as e:
            print(f"[Error] 向表 '{table_name}' 添加列时出错: {e}")
            return False
            
    def table_exists(self, table_name: str) -> bool:
        """检查表是否存在
        
        Args:
            table_name: 表名
            
        Returns:
            bool: 表是否存在
        """
        try:
            self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            return self.cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"[Error] 检查表 '{table_name}' 是否存在时出错: {e}")
            return False
            
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """获取表结构信息
        
        Args:
            table_name: 表名
            
        Returns:
            list: 包含列信息的字典列表
        """
        try:
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = []
            for row in self.cursor.fetchall():
                column_info = {
                    'cid': row['cid'],
                    'name': row['name'],
                    'type': row['type'],
                    'notnull': row['notnull'],
                    'default_value': row['dflt_value'],
                    'pk': row['pk']
                }
                columns.append(column_info)
            return columns
        except sqlite3.Error as e:
            print(f"[Error] 获取表 '{table_name}' 信息时出错: {e}")
            return [] 