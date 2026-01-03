# Database Tools

Tools for working with SQLite databases. These tools provide a simple, safe interface for database operations with proper connection management and error handling.

## Core Design Principles

### Connection Management

The `DatabaseConnection` class manages database connections automatically. It can work with file-based databases or in-memory databases, and handles connection lifecycle (creation, closing, cleanup).

**Why implemented this way**:
- Context manager support (`with` statement) ensures connections are always closed
- Automatic parent directory creation for file databases
- Row factory set to `sqlite3.Row` for column access by name (more readable than tuples)
- In-memory databases for testing and temporary data

### Parameterized Queries

All queries support parameterization to prevent SQL injection. Use `?` placeholders and pass parameters as a tuple.

**Why this matters**: Direct string interpolation in SQL queries is dangerous. Parameterized queries are safe and more efficient.

## Understanding the Tools

### `DatabaseConnection` - Connection Management

**What it does**: Manages a SQLite database connection, handling creation, closing, and cleanup.

**Why we use it**: Provides a clean interface for database operations with automatic resource management.

**How to use**:
```python
from ixmachina.tools.database import DatabaseConnection

# File-based database
with DatabaseConnection("my_database.db") as db:
    # Use db.connection for operations
    pass

# In-memory database (temporary)
with DatabaseConnection() as db:
    # Data exists only while connection is open
    pass
```

**When to use**: Always use this for database operations. It ensures proper connection handling and cleanup.

---

### `execute_query` - Run SQL Queries

**What it does**: Executes SQL queries (SELECT, INSERT, UPDATE, DELETE, etc.) and returns results.

**Why we use it**: Provides a consistent interface for all database operations with proper error handling and result formatting.

**Why implemented this way**:
- Automatically detects query type (SELECT vs. modification)
- Returns rows as dictionaries (column access by name)
- Provides row count for modification queries
- Handles errors gracefully with structured error messages

**How to use**:
```python
from ixmachina.tools.database import DatabaseConnection, execute_query

with DatabaseConnection("my_database.db") as db:
    # SELECT query
    result = execute_query(
        "SELECT * FROM users WHERE age > ?",
        parameters=(18,),
        database=db
    )
    if result["success"]:
        for row in result["results"]:
            print(row["name"])  # Access by column name
    
    # INSERT query
    result = execute_query(
        "INSERT INTO users (name, age) VALUES (?, ?)",
        parameters=("John", 25),
        database=db
    )
    if result["success"]:
        print(f"Inserted {result['rowcount']} row(s)")
```

**When to use**: For any SQL operation. Use parameterized queries (with `?` placeholders) for safety.

---

### `create_table` - Create Database Tables

**What it does**: Creates a table with specified columns and constraints.

**Why we use it**: Provides a structured way to define tables with proper type handling and constraint validation.

**How to use**:
```python
from ixmachina.tools.database import DatabaseConnection, create_table

with DatabaseConnection("my_database.db") as db:
    result = create_table(
        table_name="users",
        columns={
            "id": "INTEGER PRIMARY KEY",
            "name": "TEXT NOT NULL",
            "age": "INTEGER",
            "email": "TEXT UNIQUE"
        },
        database=db
    )
    if result["success"]:
        print("Table created successfully")
```

**When to use**: When setting up a new database or adding new tables.

---

### `list_tables` - List All Tables

**What it does**: Returns a list of all table names in the database.

**Why we use it**: Quick way to see what tables exist in a database.

**How to use**:
```python
from ixmachina.tools.database import DatabaseConnection, list_tables

with DatabaseConnection("my_database.db") as db:
    result = list_tables(database=db)
    if result["success"]:
        print(f"Tables: {result['tables']}")
```

**When to use**: For database introspection or when you need to check if a table exists.

---

### `get_table_schema` - Get Table Structure

**What it does**: Returns the schema (column names, types, constraints) of a table.

**Why we use it**: Understand table structure before querying or modifying it.

**How to use**:
```python
from ixmachina.tools.database import DatabaseConnection, get_table_schema

with DatabaseConnection("my_database.db") as db:
    result = get_table_schema(table_name="users", database=db)
    if result["success"]:
        for column in result["schema"]:
            print(f"{column['name']}: {column['type']}")
```

**When to use**: When you need to understand a table's structure, especially when working with unknown databases.

---

## Common Patterns

### Working with Agents

When using with agents, the database connection is typically bound using the `@bind` decorator (see `bind.md` in utils documentation). The agent automatically passes the connection to query functions.

```python
# Database is bound to agent, queries automatically use it
agent.run("Create a table called 'users' with columns id, name, and email")
agent.run("Insert a user named 'John' with email 'john@example.com'")
agent.run("List all users")
```

### Error Handling

Always check the `success` key before using results:

```python
result = execute_query("SELECT * FROM users", database=db)
if not result["success"]:
    print(f"Error: {result['error']}")
    return
# Use result["results"] here
```

### Transaction Management

SQLite supports transactions. Use `db.commit()` to save changes or `db.rollback()` to undo:

```python
with DatabaseConnection("my_database.db") as db:
    try:
        execute_query("INSERT INTO users (name) VALUES (?)", ("John",), database=db)
        execute_query("INSERT INTO users (name) VALUES (?)", ("Jane",), database=db)
        db.commit()  # Save both inserts
    except Exception:
        db.rollback()  # Undo both if any fails
```

---

## Design Decisions

### Why SQLite Only?

SQLite is:
- File-based (easy to manage, no server needed)
- Self-contained (database is a single file)
- Perfect for most use cases (web apps, data analysis, testing)
- Widely supported and reliable

For production systems requiring multiple connections or advanced features, consider PostgreSQL or MySQL, but SQLite covers most needs.

### Why Row Factory?

Using `sqlite3.Row` instead of tuples:
- More readable: `row["name"]` vs `row[1]`
- Less error-prone: column names are clearer than positions
- Self-documenting: code shows what column is being accessed

### Why Parameterized Queries Only?

Security and performance:
- Prevents SQL injection attacks
- More efficient (SQLite can cache query plans)
- Handles special characters correctly (quotes, etc.)

Never use string formatting for SQL queries. Always use `?` placeholders.

