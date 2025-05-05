"""
数据库管理模块，负责SQLite数据库的连接和基础操作。
提供连接管理、资源释放等功能。
"""
import sqlite3
import os
from typing import Tuple, Optional


class DatabaseManager:
    """数据库管理类，负责SQLite数据库的连接和操作"""
    
    # 默认数据库文件路径
    DEFAULT_DB_FILE = "sqlite_practice.db"
    
    def __init__(self, db_file: str = DEFAULT_DB_FILE):
        """初始化数据库管理器
        
        Args:
            db_file: 数据库文件路径
        """
        self.db_file = db_file
        self.conn = None
        self.cursor = None
        
    def clean_database(self) -> bool:
        """清理旧数据库文件
        
        Returns:
            bool: 清理是否成功
        """
        try:
            if os.path.exists(self.db_file):
                os.remove(self.db_file)
                print(f"[Setup] 旧数据库文件 '{self.db_file}' 已删除。")
            return True
        except Exception as e:
            print(f"[Error] 清理数据库文件 '{self.db_file}' 失败: {e}")
            return False
    
    def connect(self) -> Tuple[Optional[sqlite3.Connection], Optional[sqlite3.Cursor]]:
        """建立数据库连接并返回连接对象和游标对象
        
        Returns:
            tuple: (连接对象, 游标对象)，如果连接失败则返回 (None, None)
        """
        try:
            self.conn = sqlite3.connect(self.db_file)
            # 设置 Row Factory 使查询结果可以通过列名访问/提高可读性
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            print(f"[Setup] 成功连接到数据库 '{self.db_file}' 并创建游标。")
            return self.conn, self.cursor
        except sqlite3.Error as e:
            print(f"[Error] 无法连接到数据库 '{self.db_file}'，错误信息：{e}")
            return None, None
    
    def close(self) -> None:
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print(f"[Cleanup] 数据库连接已关闭。")
            
    def __enter__(self):
        """上下文管理器入口，允许使用 with 语句"""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口，自动关闭连接"""
        self.close()
        if exc_type:
            # 发生异常时输出信息，但不抑制异常
            print(f"[Error] 操作数据库时发生异常: {exc_val}")
            return False  # 允许异常继续传播 