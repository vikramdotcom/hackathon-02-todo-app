"""
Query Builder and ORM Utilities

Advanced query building utilities for database operations.
"""

import logging
from typing import List, Dict, Any, Optional, Type
from datetime import datetime

logger = logging.getLogger(__name__)


class QueryBuilder:
    """Build SQL queries programmatically."""

    def __init__(self, table: str):
        """Initialize query builder."""
        self.table = table
        self.select_fields: List[str] = ["*"]
        self.where_conditions: List[str] = []
        self.where_params: List[Any] = []
        self.order_by_fields: List[str] = []
        self.limit_value: Optional[int] = None
        self.offset_value: int = 0
        self.join_clauses: List[str] = []

    def select(self, *fields: str) -> 'QueryBuilder':
        """Select specific fields."""
        self.select_fields = list(fields)
        return self

    def where(self, condition: str, *params: Any) -> 'QueryBuilder':
        """Add WHERE condition."""
        self.where_conditions.append(condition)
        self.where_params.extend(params)
        return self

    def where_equals(self, field: str, value: Any) -> 'QueryBuilder':
        """Add WHERE field = value."""
        self.where_conditions.append(f"{field} = ?")
        self.where_params.append(value)
        return self

    def where_in(self, field: str, values: List[Any]) -> 'QueryBuilder':
        """Add WHERE field IN (...)."""
        placeholders = ", ".join(["?"] * len(values))
        self.where_conditions.append(f"{field} IN ({placeholders})")
        self.where_params.extend(values)
        return self

    def where_like(self, field: str, pattern: str) -> 'QueryBuilder':
        """Add WHERE field LIKE pattern."""
        self.where_conditions.append(f"{field} LIKE ?")
        self.where_params.append(pattern)
        return self

    def where_between(self, field: str, start: Any, end: Any) -> 'QueryBuilder':
        """Add WHERE field BETWEEN start AND end."""
        self.where_conditions.append(f"{field} BETWEEN ? AND ?")
        self.where_params.extend([start, end])
        return self

    def order_by(self, field: str, direction: str = "ASC") -> 'QueryBuilder':
        """Add ORDER BY clause."""
        self.order_by_fields.append(f"{field} {direction}")
        return self

    def limit(self, limit: int) -> 'QueryBuilder':
        """Add LIMIT clause."""
        self.limit_value = limit
        return self

    def offset(self, offset: int) -> 'QueryBuilder':
        """Add OFFSET clause."""
        self.offset_value = offset
        return self

    def join(self, table: str, condition: str, join_type: str = "INNER") -> 'QueryBuilder':
        """Add JOIN clause."""
        self.join_clauses.append(f"{join_type} JOIN {table} ON {condition}")
        return self

    def build(self) -> tuple[str, List[Any]]:
        """Build SQL query."""
        # SELECT
        query = f"SELECT {', '.join(self.select_fields)} FROM {self.table}"

        # JOIN
        if self.join_clauses:
            query += " " + " ".join(self.join_clauses)

        # WHERE
        if self.where_conditions:
            query += " WHERE " + " AND ".join(self.where_conditions)

        # ORDER BY
        if self.order_by_fields:
            query += " ORDER BY " + ", ".join(self.order_by_fields)

        # LIMIT
        if self.limit_value:
            query += f" LIMIT {self.limit_value}"

        # OFFSET
        if self.offset_value:
            query += f" OFFSET {self.offset_value}"

        return query, self.where_params


class Repository:
    """Base repository pattern."""

    def __init__(self, table: str, db_session):
        """Initialize repository."""
        self.table = table
        self.db = db_session

    def query(self) -> QueryBuilder:
        """Create query builder."""
        return QueryBuilder(self.table)

    async def find_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        """Find record by ID."""
        query, params = self.query().where_equals("id", id).limit(1).build()
        result = await self.db.execute(query, params)
        return result.first() if result else None

    async def find_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Find all records."""
        query, params = self.query().limit(limit).offset(offset).build()
        result = await self.db.execute(query, params)
        return result.all()

    async def find_where(self, conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find records matching conditions."""
        builder = self.query()

        for field, value in conditions.items():
            builder.where_equals(field, value)

        query, params = builder.build()
        result = await self.db.execute(query, params)
        return result.all()

    async def count(self, conditions: Optional[Dict[str, Any]] = None) -> int:
        """Count records."""
        builder = QueryBuilder(self.table).select("COUNT(*) as count")

        if conditions:
            for field, value in conditions.items():
                builder.where_equals(field, value)

        query, params = builder.build()
        result = await self.db.execute(query, params)
        row = result.first()
        return row["count"] if row else 0

    async def exists(self, conditions: Dict[str, Any]) -> bool:
        """Check if record exists."""
        count = await self.count(conditions)
        return count > 0

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new record."""
        fields = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        query = f"INSERT INTO {self.table} ({fields}) VALUES ({placeholders})"

        result = await self.db.execute(query, list(data.values()))
        data["id"] = result.lastrowid
        return data

    async def update(self, id: int, data: Dict[str, Any]) -> bool:
        """Update record."""
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {self.table} SET {set_clause} WHERE id = ?"

        params = list(data.values()) + [id]
        result = await self.db.execute(query, params)
        return result.rowcount > 0

    async def delete(self, id: int) -> bool:
        """Delete record."""
        query = f"DELETE FROM {self.table} WHERE id = ?"
        result = await self.db.execute(query, [id])
        return result.rowcount > 0

    async def bulk_insert(self, records: List[Dict[str, Any]]) -> int:
        """Bulk insert records."""
        if not records:
            return 0

        fields = ", ".join(records[0].keys())
        placeholders = ", ".join(["?"] * len(records[0]))
        query = f"INSERT INTO {self.table} ({fields}) VALUES ({placeholders})"

        count = 0
        for record in records:
            await self.db.execute(query, list(record.values()))
            count += 1

        return count


class TodoRepository(Repository):
    """Todo-specific repository."""

    def __init__(self, db_session):
        """Initialize todo repository."""
        super().__init__("todos", db_session)

    async def find_by_user(self, user_id: int, completed: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Find todos by user."""
        builder = self.query().where_equals("user_id", user_id)

        if completed is not None:
            builder.where_equals("completed", completed)

        query, params = builder.order_by("created_at", "DESC").build()
        result = await self.db.execute(query, params)
        return result.all()

    async def find_overdue(self, user_id: int) -> List[Dict[str, Any]]:
        """Find overdue todos."""
        now = datetime.utcnow().isoformat()
        query, params = (
            self.query()
            .where_equals("user_id", user_id)
            .where_equals("completed", False)
            .where("due_date < ?", now)
            .order_by("due_date", "ASC")
            .build()
        )

        result = await self.db.execute(query, params)
        return result.all()

    async def find_by_priority(self, user_id: int, priority: str) -> List[Dict[str, Any]]:
        """Find todos by priority."""
        query, params = (
            self.query()
            .where_equals("user_id", user_id)
            .where_equals("priority", priority)
            .where_equals("completed", False)
            .order_by("due_date", "ASC")
            .build()
        )

        result = await self.db.execute(query, params)
        return result.all()

    async def search(self, user_id: int, search_term: str) -> List[Dict[str, Any]]:
        """Search todos."""
        pattern = f"%{search_term}%"
        builder = self.query().where_equals("user_id", user_id)
        builder.where("(title LIKE ? OR description LIKE ?)", pattern, pattern)

        query, params = builder.build()
        result = await self.db.execute(query, params)
        return result.all()


# Example usage
async def example_queries(db):
    """Example query usage."""
    # Simple query
    builder = QueryBuilder("todos")
    query, params = (
        builder
        .select("id", "title", "completed")
        .where_equals("user_id", 1)
        .where_equals("completed", False)
        .order_by("created_at", "DESC")
        .limit(10)
        .build()
    )

    # Complex query with joins
    builder = QueryBuilder("todos")
    query, params = (
        builder
        .select("todos.*", "users.name")
        .join("users", "todos.user_id = users.id")
        .where("todos.due_date < ?", datetime.utcnow())
        .order_by("todos.priority", "DESC")
        .build()
    )

    # Using repository
    repo = TodoRepository(db)
    todos = await repo.find_by_user(user_id=1, completed=False)
    overdue = await repo.find_overdue(user_id=1)
