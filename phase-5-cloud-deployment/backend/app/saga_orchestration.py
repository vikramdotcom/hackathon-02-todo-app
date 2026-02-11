"""
Saga Pattern for Distributed Transactions

Manage distributed transactions with compensating actions.
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class SagaStatus(str, Enum):
    """Saga execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


class SagaStep:
    """Single step in saga."""

    def __init__(
        self,
        name: str,
        action: Callable,
        compensation: Callable
    ):
        """Initialize saga step."""
        self.name = name
        self.action = action
        self.compensation = compensation
        self.executed = False
        self.compensated = False


class Saga:
    """Saga orchestrator."""

    def __init__(self, saga_id: str, name: str):
        """Initialize saga."""
        self.saga_id = saga_id
        self.name = name
        self.steps: List[SagaStep] = []
        self.status = SagaStatus.PENDING
        self.executed_steps: List[str] = []
        self.created_at = datetime.utcnow()
        self.completed_at: Optional[datetime] = None

    def add_step(self, name: str, action: Callable, compensation: Callable):
        """Add step to saga."""
        step = SagaStep(name, action, compensation)
        self.steps.append(step)

    async def execute(self) -> bool:
        """Execute saga."""
        self.status = SagaStatus.RUNNING
        logger.info(f"Starting saga: {self.name}")

        try:
            for step in self.steps:
                logger.info(f"Executing step: {step.name}")
                await step.action()
                step.executed = True
                self.executed_steps.append(step.name)

            self.status = SagaStatus.COMPLETED
            self.completed_at = datetime.utcnow()
            logger.info(f"Saga completed: {self.name}")
            return True

        except Exception as e:
            logger.error(f"Saga failed: {self.name} - {e}")
            self.status = SagaStatus.FAILED
            await self._compensate()
            return False

    async def _compensate(self):
        """Execute compensation actions."""
        self.status = SagaStatus.COMPENSATING
        logger.warning(f"Compensating saga: {self.name}")

        for step in reversed(self.steps):
            if step.executed and not step.compensated:
                try:
                    logger.info(f"Compensating step: {step.name}")
                    await step.compensation()
                    step.compensated = True
                except Exception as e:
                    logger.error(f"Compensation failed: {step.name} - {e}")

        self.status = SagaStatus.COMPENSATED
        logger.info(f"Saga compensated: {self.name}")


class SagaManager:
    """Manage multiple sagas."""

    def __init__(self):
        """Initialize saga manager."""
        self.sagas: Dict[str, Saga] = {}

    def create_saga(self, saga_id: str, name: str) -> Saga:
        """Create new saga."""
        saga = Saga(saga_id, name)
        self.sagas[saga_id] = saga
        return saga

    async def execute_saga(self, saga_id: str) -> bool:
        """Execute saga by ID."""
        if saga_id not in self.sagas:
            raise ValueError(f"Saga not found: {saga_id}")

        saga = self.sagas[saga_id]
        return await saga.execute()

    def get_saga(self, saga_id: str) -> Optional[Saga]:
        """Get saga by ID."""
        return self.sagas.get(saga_id)


# Global instance
saga_manager = SagaManager()
