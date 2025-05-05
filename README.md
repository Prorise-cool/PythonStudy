# SQLite 数据库操作实践

这个项目提供了一个完整的 SQLite 数据库操作框架，采用面向对象的最佳实践设计，帮助你系统地学习和应用 Python 中的 SQLite 数据库操作。

## 项目结构

```
sqlite_practice/
├── core/                     # 核心功能模块
│   ├── __init__.py
│   ├── db_manager.py         # 数据库连接管理
│   └── table_manager.py      # 表结构管理
├── models/                   # 数据模型
│   ├── __init__.py
│   └── task.py               # 任务数据模型
├── repositories/             # 数据访问层
│   ├── __init__.py
│   └── task_repository.py    # 任务数据访问
├── services/                 # 业务逻辑层
│   ├── __init__.py
│   └── task_service.py       # 任务业务逻辑
├── utils/                    # 工具类
│   ├── __init__.py
│   └── date_utils.py         # 日期处理工具
├── examples/                 # 示例代码
│   ├── __init__.py
│   ├── basic_operations.py   # 基本操作示例
│   ├── advanced_queries.py   # 高级查询示例
│   └── transaction_example.py # 事务处理示例
└── README.md                 # 项目说明文档
```

## 安装和前提条件

这个项目使用 Python 内置的 `sqlite3` 模块，不需要安装额外的依赖。

### 前提条件

- Python 3.6+ (推荐 Python 3.9+)
- 理解基本的 SQL 语法和关系型数据库概念

## 使用指南

### 1. 基本数据库连接

使用 `DatabaseManager` 类来管理数据库连接：

```python
from sqlite_practice.core.db_manager import DatabaseManager

# 创建数据库管理器实例
db_manager = DatabaseManager("my_database.db")

# 连接数据库
conn, cursor = db_manager.connect()

# 使用完毕后关闭连接
db_manager.close()

# 或者使用上下文管理器（推荐）
with DatabaseManager("my_database.db") as db_manager:
    conn = db_manager.conn
    cursor = db_manager.cursor
    
    # 在这里进行数据库操作
    # ...
# 连接会自动关闭
```

### 2. 创建和管理表

使用 `TableManager` 类来管理表结构：

```python
from sqlite_practice.core.table_manager import TableManager

# 使用已有的连接和游标创建表管理器
table_manager = TableManager(conn, cursor)

# 定义表结构
columns = {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "name": "TEXT NOT NULL",
    "age": "INTEGER",
    "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
}

# 创建表
table_manager.create_table("users", columns)

# 添加新列
table_manager.add_column("users", "email", "TEXT UNIQUE")

# 检查表是否存在
if table_manager.table_exists("users"):
    print("用户表已存在")
```

### 3. 使用数据模型和仓库

项目使用数据模型和仓库模式实现数据访问层：

```python
from sqlite_practice.models.task import Task
from sqlite_practice.repositories.task_repository import TaskRepository

# 创建任务仓库
task_repo = TaskRepository(conn, cursor)

# 创建表
task_repo.create_table()

# 创建任务对象
new_task = Task(
    title="完成SQLite学习",
    description="学习并掌握SQLite基本操作",
    priority=1,
    due_date="2025-05-20"
)

# 保存任务到数据库
task_id = task_repo.insert(new_task)
print(f"新任务ID: {task_id}")

# 查询所有任务
all_tasks = task_repo.find_all()
for task in all_tasks:
    print(f"ID: {task.task_id}, 标题: {task.title}")

# 按条件查询
high_priority_tasks = task_repo.find_by_criteria({"priority": 1})
```

### 4. 使用业务逻辑服务

使用服务层封装业务逻辑：

```python
from sqlite_practice.services.task_service import TaskService

# 创建任务服务
task_service = TaskService(task_repo)

# 创建新任务
task_id = task_service.create_task(
    title="学习事务处理",
    description="掌握SQLite事务机制",
    priority=2,
    due_date="2025-05-25"
)

# 获取未完成的任务
incomplete_tasks = task_service.get_incomplete_tasks()

# 将任务标记为已完成
task_service.complete_task(task_id)

# 获取一周内到期的任务
upcoming_tasks = task_service.get_tasks_due_within_days(7)
```

## 示例代码

提供了三个完整的示例脚本，演示系统各部分功能：

1. **基本操作** - `examples/basic_operations.py`：展示基本的CRUD操作
2. **高级查询** - `examples/advanced_queries.py`：展示复杂条件查询、排序、分页等
3. **事务处理** - `examples/transaction_example.py`：展示事务提交、回滚、保存点等操作

运行示例：

```bash
# 在项目根目录执行
python -m sqlite_practice.examples.basic_operations
python -m sqlite_practice.examples.advanced_queries
python -m sqlite_practice.examples.transaction_example
```

## 最佳实践

1. **始终使用参数化查询**：避免SQL注入，提高安全性
   ```python
   # 正确：使用参数化查询
   cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
   
   # 错误：字符串拼接（有SQL注入风险）
   cursor.execute(f"SELECT * FROM tasks WHERE task_id = {task_id}")
   ```

2. **使用 `with` 语句管理连接**：确保资源正确关闭
   ```python
   with DatabaseManager("my_database.db") as db:
       # 数据库操作
       pass
   # 自动关闭连接
   ```

3. **事务管理**：确保数据一致性
   ```python
   try:
       # 一系列相关操作
       conn.commit()  # 提交事务
   except Exception as e:
       conn.rollback()  # 出错时回滚
   ```

4. **使用合适的索引**：优化查询性能
   ```python
   cursor.execute("CREATE INDEX idx_task_priority ON tasks(priority)")
   ```

5. **分层架构**：遵循关注点分离原则
   - 数据模型层 (Model)：表示数据结构
   - 数据访问层 (Repository)：处理数据库交互
   - 业务逻辑层 (Service)：实现业务规则
   - 表示层 (UI/API)：展示和接收用户输入

## 许可证

MIT License