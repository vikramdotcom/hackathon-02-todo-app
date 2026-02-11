"""
Batch Operations Utilities

Provides utilities for batch processing of todos and other resources.
"""

import logging
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class BatchOperation:
    """Batch operation result."""

    def __init__(self, operation: str):
        """Initialize batch operation."""
        self.operation = operation
        self.total = 0
        self.successful = 0
        self.failed = 0
        self.errors: List[Dict[str, Any]] = []
        self.results: List[Any] = []
        self.started_at = datetime.utcnow()
        self.completed_at: Optional[datetime] = None

    def add_success(self, result: Any):
        """Add successful result."""
        self.successful += 1
        self.results.append(result)

    def add_failure(self, item_id: Any, error: str):
        """Add failure."""
        self.failed += 1
        self.errors.append({"item_id": item_id, "error": error})

    def complete(self):
        """Mark operation as complete."""
        self.completed_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        duration = None
        if self.completed_at:
            duration = (self.completed_at - self.started_at).total_seconds()

        return {
            "operation": self.operation,
            "total": self.total,
            "successful": self.successful,
            "failed": self.failed,
            "success_rate": self.successful / self.total if self.total > 0 else 0,
            "duration_seconds": duration,
            "errors": self.errors,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class BatchProcessor:
    """Process items in batches."""

    @staticmethod
    async def process_batch(
        items: List[Any],
        processor: Callable,
        batch_size: int = 100,
        max_concurrent: int = 10
    ) -> BatchOperation:
        """
        Process items in batches.

        Args:
            items: Items to process
            processor: Async function to process each item
            batch_size: Items per batch
            max_concurrent: Maximum concurrent operations

        Returns:
            BatchOperation result
        """
        operation = BatchOperation("batch_process")
        operation.total = len(items)

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_item(item):
            async with semaphore:
                try:
                    result = await processor(item)
                    operation.add_success(result)
                except Exception as e:
                    item_id = item.get("id") if isinstance(item, dict) else str(item)
                    operation.add_failure(item_id, str(e))
                    logger.error(f"Error processing item {item_id}: {e}")

        # Process in batches
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            tasks = [process_item(item) for item in batch]
            await asyncio.gather(*tasks, return_exceptions=True)

        operation.complete()
        return operation


class BulkOperations:
    """Bulk operations for todos."""

    @staticmethod
    async def bulk_create(todos: List[Dict[str, Any]]) -> BatchOperation:
        """Bulk create todos."""
        operation = BatchOperation("bulk_create")
        operation.total = len(todos)

        for todo in todos:
            try:
                # Simulate todo creation
                result = {"id": len(operation.results) + 1, **todo}
                operation.add_success(result)
            except Exception as e:
                operation.add_failure(todo.get("title", "unknown"), str(e))

        operation.complete()
        return operation

    @staticmethod
    async def bulk_update(updates: List[Dict[str, Any]]) -> BatchOperation:
        """Bulk update todos."""
        operation = BatchOperation("bulk_update")
        operation.total = len(updates)

        for update in updates:
            try:
                todo_id = update.get("id")
                if not todo_id:
                    raise ValueError("Missing todo ID")

                # Simulate todo update
                result = {"id": todo_id, "updated": True}
                operation.add_success(result)
            except Exception as e:
                operation.add_failure(update.get("id", "unknown"), str(e))

        operation.complete()
        return operation

    @staticmethod
    async def bulk_delete(todo_ids: List[int]) -> BatchOperation:
        """Bulk delete todos."""
        operation = BatchOperation("bulk_delete")
        operation.total = len(todo_ids)

        for todo_id in todo_ids:
            try:
                # Simulate todo deletion
                result = {"id": todo_id, "deleted": True}
                operation.add_success(result)
            except Exception as e:
                operation.add_failure(todo_id, str(e))

        operation.complete()
        return operation

    @staticmethod
    async def bulk_complete(todo_ids: List[int]) -> BatchOperation:
        """Bulk complete todos."""
        operation = BatchOperation("bulk_complete")
        operation.total = len(todo_ids)

        for todo_id in todo_ids:
            try:
                # Simulate todo completion
                result = {"id": todo_id, "completed": True}
                operation.add_success(result)
            except Exception as e:
                operation.add_failure(todo_id, str(e))

        operation.complete()
        return operation

    @staticmethod
    async def bulk_assign_tags(todo_ids: List[int], tags: List[str]) -> BatchOperation:
        """Bulk assign tags to todos."""
        operation = BatchOperation("bulk_assign_tags")
        operation.total = len(todo_ids)

        for todo_id in todo_ids:
            try:
                # Simulate tag assignment
                result = {"id": todo_id, "tags": tags}
                operation.add_success(result)
            except Exception as e:
                operation.add_failure(todo_id, str(e))

        operation.complete()
        return operation

    @staticmethod
    async def bulk_set_priority(todo_ids: List[int], priority: str) -> BatchOperation:
        """Bulk set priority for todos."""
        operation = BatchOperation("bulk_set_priority")
        operation.total = len(todo_ids)

        for todo_id in todo_ids:
            try:
                # Simulate priority update
                result = {"id": todo_id, "priority": priority}
                operation.add_success(result)
            except Exception as e:
                operation.add_failure(todo_id, str(e))

        operation.complete()
        return operation


class TransactionManager:
    """Manage transactional batch operations."""

    def __init__(self):
        """Initialize transaction manager."""
        self.operations: List[Callable] = []
        self.rollback_operations: List[Callable] = []

    def add_operation(self, operation: Callable, rollback: Optional[Callable] = None):
        """Add operation to transaction."""
        self.operations.append(operation)
        if rollback:
            self.rollback_operations.append(rollback)

    async def execute(self) -> BatchOperation:
        """Execute all operations in transaction."""
        operation = BatchOperation("transaction")
        operation.total = len(self.operations)

        executed = []

        try:
            for op in self.operations:
                result = await op()
                executed.append(result)
                operation.add_success(result)

            operation.complete()
            return operation

        except Exception as e:
            logger.error(f"Transaction failed: {e}")

            # Rollback executed operations
            for i, rollback in enumerate(reversed(self.rollback_operations[:len(executed)])):
                try:
                    await rollback()
                except Exception as rollback_error:
                    logger.error(f"Rollback failed: {rollback_error}")

            operation.add_failure("transaction", str(e))
            operation.complete()
            raise


class ChunkedProcessor:
    """Process large datasets in chunks."""

    @staticmethod
    async def process_in_chunks(
        items: List[Any],
        processor: Callable,
        chunk_size: int = 1000,
        progress_callback: Optional[Callable] = None
    ) -> BatchOperation:
        """
        Process items in chunks with progress tracking.

        Args:
            items: Items to process
            processor: Processing function
            chunk_size: Items per chunk
            progress_callback: Optional progress callback

        Returns:
            BatchOperation result
        """
        operation = BatchOperation("chunked_process")
        operation.total = len(items)

        total_chunks = (len(items) + chunk_size - 1) // chunk_size

        for chunk_index in range(total_chunks):
            start = chunk_index * chunk_size
            end = min(start + chunk_size, len(items))
            chunk = items[start:end]

            try:
                result = await processor(chunk)
                operation.add_success(result)

                # Progress callback
                if progress_callback:
                    progress = (chunk_index + 1) / total_chunks
                    await progress_callback(progress, chunk_index + 1, total_chunks)

            except Exception as e:
                operation.add_failure(f"chunk_{chunk_index}", str(e))
                logger.error(f"Error processing chunk {chunk_index}: {e}")

        operation.complete()
        return operation


class ParallelProcessor:
    """Process items in parallel."""

    @staticmethod
    async def process_parallel(
        items: List[Any],
        processor: Callable,
        max_workers: int = 10
    ) -> BatchOperation:
        """
        Process items in parallel.

        Args:
            items: Items to process
            processor: Processing function
            max_workers: Maximum parallel workers

        Returns:
            BatchOperation result
        """
        operation = BatchOperation("parallel_process")
        operation.total = len(items)

        semaphore = asyncio.Semaphore(max_workers)

        async def process_with_semaphore(item):
            async with semaphore:
                try:
                    result = await processor(item)
                    operation.add_success(result)
                except Exception as e:
                    item_id = item.get("id") if isinstance(item, dict) else str(item)
                    operation.add_failure(item_id, str(e))

        tasks = [process_with_semaphore(item) for item in items]
        await asyncio.gather(*tasks, return_exceptions=True)

        operation.complete()
        return operation


# Example usage
async def example_batch_operations():
    """Example batch operations."""

    # Bulk create
    todos = [
        {"title": "Todo 1", "priority": "high"},
        {"title": "Todo 2", "priority": "medium"},
        {"title": "Todo 3", "priority": "low"}
    ]

    result = await BulkOperations.bulk_create(todos)
    print(f"Created {result.successful}/{result.total} todos")

    # Bulk update
    updates = [
        {"id": 1, "completed": True},
        {"id": 2, "priority": "urgent"}
    ]

    result = await BulkOperations.bulk_update(updates)
    print(f"Updated {result.successful}/{result.total} todos")

    # Bulk complete
    result = await BulkOperations.bulk_complete([1, 2, 3])
    print(f"Completed {result.successful}/{result.total} todos")
