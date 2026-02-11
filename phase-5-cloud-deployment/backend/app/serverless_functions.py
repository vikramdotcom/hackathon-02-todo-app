"""
Serverless Function Integration

Support for serverless function deployment and execution.
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class FunctionRuntime(str, Enum):
    """Function runtime environments."""
    PYTHON_39 = "python3.9"
    PYTHON_310 = "python3.10"
    PYTHON_311 = "python3.11"
    NODEJS_16 = "nodejs16"
    NODEJS_18 = "nodejs18"
    GO_119 = "go1.19"


class FunctionTrigger(str, Enum):
    """Function trigger types."""
    HTTP = "http"
    SCHEDULE = "schedule"
    QUEUE = "queue"
    STORAGE = "storage"
    DATABASE = "database"


class ServerlessFunction:
    """Serverless function definition."""

    def __init__(
        self,
        name: str,
        runtime: FunctionRuntime,
        handler: Callable,
        memory_mb: int = 128,
        timeout_seconds: int = 60
    ):
        """Initialize serverless function."""
        self.name = name
        self.runtime = runtime
        self.handler = handler
        self.memory_mb = memory_mb
        self.timeout_seconds = timeout_seconds
        self.environment: Dict[str, str] = {}
        self.triggers: List[Dict[str, Any]] = []
        self.created_at = datetime.utcnow()
        self.invocation_count = 0
        self.total_duration_ms = 0

    def add_trigger(self, trigger_type: FunctionTrigger, config: Dict[str, Any]):
        """Add trigger to function."""
        self.triggers.append({
            "type": trigger_type.value,
            "config": config
        })

    async def invoke(self, event: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Invoke function."""
        start_time = datetime.utcnow()

        try:
            self.invocation_count += 1

            logger.info(
                f"Invoking function: {self.name}",
                extra={"function": self.name, "invocation": self.invocation_count}
            )

            # Execute handler
            if asyncio.iscoroutinefunction(self.handler):
                result = await self.handler(event, context)
            else:
                result = self.handler(event, context)

            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.total_duration_ms += duration_ms

            logger.info(
                f"Function completed: {self.name}",
                extra={"function": self.name, "duration_ms": duration_ms}
            )

            return result

        except Exception as e:
            logger.error(
                f"Function error: {self.name}",
                extra={"function": self.name, "error": str(e)},
                exc_info=True
            )
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get function statistics."""
        avg_duration = (
            self.total_duration_ms / self.invocation_count
            if self.invocation_count > 0 else 0
        )

        return {
            "name": self.name,
            "runtime": self.runtime.value,
            "invocations": self.invocation_count,
            "avg_duration_ms": avg_duration,
            "memory_mb": self.memory_mb,
            "timeout_seconds": self.timeout_seconds
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "runtime": self.runtime.value,
            "memory_mb": self.memory_mb,
            "timeout_seconds": self.timeout_seconds,
            "triggers": self.triggers,
            "created_at": self.created_at.isoformat(),
            "stats": self.get_stats()
        }


class FunctionDeployer:
    """Deploy serverless functions."""

    def __init__(self):
        """Initialize function deployer."""
        self.functions: Dict[str, ServerlessFunction] = {}

    def deploy_function(self, function: ServerlessFunction):
        """Deploy function."""
        self.functions[function.name] = function

        logger.info(
            f"Deployed function: {function.name}",
            extra={
                "function": function.name,
                "runtime": function.runtime.value,
                "memory": function.memory_mb
            }
        )

    def undeploy_function(self, name: str):
        """Undeploy function."""
        if name in self.functions:
            del self.functions[name]
            logger.info(f"Undeployed function: {name}")

    def get_function(self, name: str) -> Optional[ServerlessFunction]:
        """Get function by name."""
        return self.functions.get(name)

    def list_functions(self) -> List[Dict[str, Any]]:
        """List all functions."""
        return [f.to_dict() for f in self.functions.values()]


class FunctionInvoker:
    """Invoke serverless functions."""

    def __init__(self, deployer: FunctionDeployer):
        """Initialize function invoker."""
        self.deployer = deployer

    async def invoke(
        self,
        function_name: str,
        event: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Invoke function."""
        function = self.deployer.get_function(function_name)

        if not function:
            raise ValueError(f"Function not found: {function_name}")

        ctx = context or {
            "request_id": self._generate_request_id(),
            "timestamp": datetime.utcnow().isoformat()
        }

        return await function.invoke(event, ctx)

    def _generate_request_id(self) -> str:
        """Generate request ID."""
        import uuid
        return str(uuid.uuid4())


class FunctionScheduler:
    """Schedule function executions."""

    def __init__(self, invoker: FunctionInvoker):
        """Initialize function scheduler."""
        self.invoker = invoker
        self.schedules: Dict[str, Dict[str, Any]] = {}

    def schedule_function(
        self,
        function_name: str,
        cron_expression: str,
        event: Optional[Dict[str, Any]] = None
    ):
        """Schedule function execution."""
        self.schedules[function_name] = {
            "cron": cron_expression,
            "event": event or {},
            "last_run": None,
            "next_run": None
        }

        logger.info(
            f"Scheduled function: {function_name}",
            extra={"function": function_name, "cron": cron_expression}
        )

    async def run_scheduled_functions(self):
        """Run scheduled functions."""
        # In production, use proper cron scheduler
        for function_name, schedule in self.schedules.items():
            try:
                await self.invoker.invoke(function_name, schedule["event"])
                schedule["last_run"] = datetime.utcnow()
            except Exception as e:
                logger.error(f"Scheduled function error: {e}")


class FunctionLogger:
    """Log function executions."""

    def __init__(self):
        """Initialize function logger."""
        self.logs: List[Dict[str, Any]] = []

    def log_invocation(
        self,
        function_name: str,
        request_id: str,
        duration_ms: float,
        success: bool,
        error: Optional[str] = None
    ):
        """Log function invocation."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "function": function_name,
            "request_id": request_id,
            "duration_ms": duration_ms,
            "success": success,
            "error": error
        }

        self.logs.append(log_entry)

    def get_logs(
        self,
        function_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get function logs."""
        logs = self.logs

        if function_name:
            logs = [log for log in logs if log["function"] == function_name]

        return logs[-limit:]


class FunctionMetrics:
    """Track function metrics."""

    def __init__(self):
        """Initialize function metrics."""
        self.metrics: Dict[str, Dict[str, Any]] = {}

    def record_invocation(
        self,
        function_name: str,
        duration_ms: float,
        memory_used_mb: float,
        success: bool
    ):
        """Record function invocation metrics."""
        if function_name not in self.metrics:
            self.metrics[function_name] = {
                "invocations": 0,
                "errors": 0,
                "total_duration_ms": 0,
                "total_memory_mb": 0
            }

        metrics = self.metrics[function_name]
        metrics["invocations"] += 1

        if not success:
            metrics["errors"] += 1

        metrics["total_duration_ms"] += duration_ms
        metrics["total_memory_mb"] += memory_used_mb

    def get_metrics(self, function_name: str) -> Dict[str, Any]:
        """Get metrics for function."""
        if function_name not in self.metrics:
            return {}

        metrics = self.metrics[function_name]
        invocations = metrics["invocations"]

        return {
            "invocations": invocations,
            "errors": metrics["errors"],
            "error_rate": metrics["errors"] / invocations if invocations > 0 else 0,
            "avg_duration_ms": metrics["total_duration_ms"] / invocations if invocations > 0 else 0,
            "avg_memory_mb": metrics["total_memory_mb"] / invocations if invocations > 0 else 0
        }


class FunctionVersioning:
    """Manage function versions."""

    def __init__(self):
        """Initialize function versioning."""
        self.versions: Dict[str, List[Dict[str, Any]]] = {}

    def create_version(
        self,
        function_name: str,
        code_hash: str,
        config: Dict[str, Any]
    ) -> str:
        """Create function version."""
        if function_name not in self.versions:
            self.versions[function_name] = []

        version_number = len(self.versions[function_name]) + 1
        version_id = f"v{version_number}"

        version = {
            "version_id": version_id,
            "code_hash": code_hash,
            "config": config,
            "created_at": datetime.utcnow().isoformat()
        }

        self.versions[function_name].append(version)

        logger.info(
            f"Created function version: {function_name} {version_id}",
            extra={"function": function_name, "version": version_id}
        )

        return version_id

    def get_version(
        self,
        function_name: str,
        version_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get function version."""
        if function_name not in self.versions:
            return None

        for version in self.versions[function_name]:
            if version["version_id"] == version_id:
                return version

        return None

    def list_versions(self, function_name: str) -> List[Dict[str, Any]]:
        """List function versions."""
        return self.versions.get(function_name, [])


class FunctionAlias:
    """Manage function aliases."""

    def __init__(self):
        """Initialize function aliases."""
        self.aliases: Dict[str, Dict[str, str]] = {}

    def create_alias(
        self,
        function_name: str,
        alias_name: str,
        version_id: str
    ):
        """Create function alias."""
        if function_name not in self.aliases:
            self.aliases[function_name] = {}

        self.aliases[function_name][alias_name] = version_id

        logger.info(
            f"Created alias: {function_name}:{alias_name} -> {version_id}",
            extra={
                "function": function_name,
                "alias": alias_name,
                "version": version_id
            }
        )

    def get_version_for_alias(
        self,
        function_name: str,
        alias_name: str
    ) -> Optional[str]:
        """Get version for alias."""
        if function_name not in self.aliases:
            return None

        return self.aliases[function_name].get(alias_name)


class ColdStartOptimizer:
    """Optimize function cold starts."""

    def __init__(self):
        """Initialize cold start optimizer."""
        self.warm_functions: Dict[str, datetime] = {}
        self.warmup_interval_seconds = 300  # 5 minutes

    def keep_warm(self, function_name: str):
        """Keep function warm."""
        self.warm_functions[function_name] = datetime.utcnow()

    def is_warm(self, function_name: str) -> bool:
        """Check if function is warm."""
        if function_name not in self.warm_functions:
            return False

        last_warmup = self.warm_functions[function_name]
        elapsed = (datetime.utcnow() - last_warmup).total_seconds()

        return elapsed < self.warmup_interval_seconds

    async def warmup_functions(self, function_names: List[str], invoker: FunctionInvoker):
        """Warmup functions."""
        for function_name in function_names:
            try:
                await invoker.invoke(function_name, {"warmup": True})
                self.keep_warm(function_name)
            except Exception as e:
                logger.error(f"Warmup failed for {function_name}: {e}")


# Global instances
function_deployer = FunctionDeployer()
function_invoker = FunctionInvoker(function_deployer)
function_scheduler = FunctionScheduler(function_invoker)
function_logger = FunctionLogger()
function_metrics = FunctionMetrics()
function_versioning = FunctionVersioning()
function_alias = FunctionAlias()
cold_start_optimizer = ColdStartOptimizer()


# Helper functions
def deploy_function(
    name: str,
    runtime: FunctionRuntime,
    handler: Callable,
    memory_mb: int = 128
) -> ServerlessFunction:
    """Deploy serverless function."""
    function = ServerlessFunction(name, runtime, handler, memory_mb)
    function_deployer.deploy_function(function)
    return function


async def invoke_function(
    function_name: str,
    event: Dict[str, Any]
) -> Any:
    """Invoke function."""
    return await function_invoker.invoke(function_name, event)


def schedule_function(
    function_name: str,
    cron_expression: str,
    event: Optional[Dict[str, Any]] = None
):
    """Schedule function."""
    function_scheduler.schedule_function(function_name, cron_expression, event)


# Example functions
async def hello_world_handler(event: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Example hello world function."""
    return {
        "statusCode": 200,
        "body": "Hello, World!"
    }


async def process_todo_handler(event: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Example todo processing function."""
    todo_id = event.get("todo_id")
    logger.info(f"Processing todo: {todo_id}")

    return {
        "statusCode": 200,
        "body": f"Processed todo {todo_id}"
    }
