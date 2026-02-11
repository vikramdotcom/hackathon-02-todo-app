"""
Multi-Tenancy Support

Handle multi-tenant architecture with tenant isolation.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class TenantStatus(str, Enum):
    """Tenant status."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    EXPIRED = "expired"


class Tenant:
    """Tenant entity."""

    def __init__(
        self,
        tenant_id: str,
        name: str,
        plan: str = "free",
        status: TenantStatus = TenantStatus.ACTIVE
    ):
        """Initialize tenant."""
        self.tenant_id = tenant_id
        self.name = name
        self.plan = plan
        self.status = status
        self.created_at = datetime.utcnow()
        self.settings: Dict[str, Any] = {}
        self.limits: Dict[str, int] = self._get_default_limits()

    def _get_default_limits(self) -> Dict[str, int]:
        """Get default limits based on plan."""
        limits_by_plan = {
            "free": {
                "max_users": 5,
                "max_todos": 100,
                "max_storage_mb": 100,
                "api_rate_limit": 100
            },
            "basic": {
                "max_users": 20,
                "max_todos": 1000,
                "max_storage_mb": 1000,
                "api_rate_limit": 1000
            },
            "premium": {
                "max_users": 100,
                "max_todos": 10000,
                "max_storage_mb": 10000,
                "api_rate_limit": 10000
            },
            "enterprise": {
                "max_users": -1,  # Unlimited
                "max_todos": -1,
                "max_storage_mb": -1,
                "api_rate_limit": -1
            }
        }

        return limits_by_plan.get(self.plan, limits_by_plan["free"])

    def is_within_limits(self, resource: str, current_usage: int) -> bool:
        """Check if within resource limits."""
        limit = self.limits.get(resource, 0)

        if limit == -1:  # Unlimited
            return True

        return current_usage < limit

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tenant_id": self.tenant_id,
            "name": self.name,
            "plan": self.plan,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "limits": self.limits
        }


class TenantManager:
    """Manage tenants."""

    def __init__(self):
        """Initialize tenant manager."""
        self.tenants: Dict[str, Tenant] = {}

    def create_tenant(
        self,
        tenant_id: str,
        name: str,
        plan: str = "free"
    ) -> Tenant:
        """Create new tenant."""
        if tenant_id in self.tenants:
            raise ValueError(f"Tenant already exists: {tenant_id}")

        tenant = Tenant(tenant_id, name, plan)
        self.tenants[tenant_id] = tenant

        logger.info(
            f"Created tenant: {tenant_id}",
            extra={"tenant_id": tenant_id, "name": name, "plan": plan}
        )

        return tenant

    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        return self.tenants.get(tenant_id)

    def update_tenant_plan(self, tenant_id: str, plan: str):
        """Update tenant plan."""
        tenant = self.get_tenant(tenant_id)

        if not tenant:
            raise ValueError(f"Tenant not found: {tenant_id}")

        tenant.plan = plan
        tenant.limits = tenant._get_default_limits()

        logger.info(f"Updated tenant plan: {tenant_id} -> {plan}")

    def suspend_tenant(self, tenant_id: str):
        """Suspend tenant."""
        tenant = self.get_tenant(tenant_id)

        if tenant:
            tenant.status = TenantStatus.SUSPENDED
            logger.info(f"Suspended tenant: {tenant_id}")

    def activate_tenant(self, tenant_id: str):
        """Activate tenant."""
        tenant = self.get_tenant(tenant_id)

        if tenant:
            tenant.status = TenantStatus.ACTIVE
            logger.info(f"Activated tenant: {tenant_id}")

    def list_tenants(self) -> List[Dict[str, Any]]:
        """List all tenants."""
        return [t.to_dict() for t in self.tenants.values()]


class TenantContext:
    """Tenant context for request handling."""

    def __init__(self, tenant_id: str):
        """Initialize tenant context."""
        self.tenant_id = tenant_id
        self.tenant: Optional[Tenant] = None

    def set_tenant(self, tenant: Tenant):
        """Set tenant."""
        self.tenant = tenant

    def get_tenant_id(self) -> str:
        """Get tenant ID."""
        return self.tenant_id

    def is_active(self) -> bool:
        """Check if tenant is active."""
        return self.tenant and self.tenant.status == TenantStatus.ACTIVE


class TenantIsolation:
    """Ensure tenant data isolation."""

    def __init__(self):
        """Initialize tenant isolation."""
        self.tenant_databases: Dict[str, str] = {}

    def get_tenant_database(self, tenant_id: str) -> str:
        """Get database connection for tenant."""
        if tenant_id not in self.tenant_databases:
            # In production, create separate database or schema
            self.tenant_databases[tenant_id] = f"tenant_{tenant_id}_db"

        return self.tenant_databases[tenant_id]

    def get_tenant_table_prefix(self, tenant_id: str) -> str:
        """Get table prefix for tenant."""
        return f"t_{tenant_id}_"

    def filter_by_tenant(self, query: str, tenant_id: str) -> str:
        """Add tenant filter to query."""
        if "WHERE" in query.upper():
            return f"{query} AND tenant_id = '{tenant_id}'"
        else:
            return f"{query} WHERE tenant_id = '{tenant_id}'"


class TenantUsageTracker:
    """Track tenant resource usage."""

    def __init__(self):
        """Initialize usage tracker."""
        self.usage: Dict[str, Dict[str, int]] = {}

    def record_usage(self, tenant_id: str, resource: str, amount: int = 1):
        """Record resource usage."""
        if tenant_id not in self.usage:
            self.usage[tenant_id] = {}

        if resource not in self.usage[tenant_id]:
            self.usage[tenant_id][resource] = 0

        self.usage[tenant_id][resource] += amount

    def get_usage(self, tenant_id: str, resource: str) -> int:
        """Get resource usage."""
        if tenant_id not in self.usage:
            return 0

        return self.usage[tenant_id].get(resource, 0)

    def get_all_usage(self, tenant_id: str) -> Dict[str, int]:
        """Get all usage for tenant."""
        return self.usage.get(tenant_id, {})

    def reset_usage(self, tenant_id: str, resource: Optional[str] = None):
        """Reset usage counters."""
        if tenant_id not in self.usage:
            return

        if resource:
            self.usage[tenant_id][resource] = 0
        else:
            self.usage[tenant_id] = {}


class TenantBilling:
    """Handle tenant billing."""

    def __init__(self):
        """Initialize tenant billing."""
        self.invoices: Dict[str, List[Dict[str, Any]]] = {}

    def create_invoice(
        self,
        tenant_id: str,
        amount: float,
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Any]:
        """Create invoice for tenant."""
        invoice = {
            "invoice_id": f"INV-{datetime.utcnow().timestamp()}",
            "tenant_id": tenant_id,
            "amount": amount,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "created_at": datetime.utcnow().isoformat(),
            "status": "pending"
        }

        if tenant_id not in self.invoices:
            self.invoices[tenant_id] = []

        self.invoices[tenant_id].append(invoice)

        logger.info(
            f"Created invoice for tenant {tenant_id}",
            extra={"tenant_id": tenant_id, "amount": amount}
        )

        return invoice

    def get_tenant_invoices(self, tenant_id: str) -> List[Dict[str, Any]]:
        """Get invoices for tenant."""
        return self.invoices.get(tenant_id, [])

    def mark_invoice_paid(self, invoice_id: str):
        """Mark invoice as paid."""
        for tenant_invoices in self.invoices.values():
            for invoice in tenant_invoices:
                if invoice["invoice_id"] == invoice_id:
                    invoice["status"] = "paid"
                    invoice["paid_at"] = datetime.utcnow().isoformat()
                    logger.info(f"Invoice paid: {invoice_id}")
                    return


class TenantOnboarding:
    """Handle tenant onboarding process."""

    def __init__(self, tenant_manager: TenantManager):
        """Initialize tenant onboarding."""
        self.tenant_manager = tenant_manager

    def onboard_tenant(
        self,
        tenant_id: str,
        name: str,
        plan: str,
        admin_email: str
    ) -> Dict[str, Any]:
        """Onboard new tenant."""
        # Create tenant
        tenant = self.tenant_manager.create_tenant(tenant_id, name, plan)

        # Setup initial configuration
        tenant.settings = {
            "admin_email": admin_email,
            "onboarded_at": datetime.utcnow().isoformat(),
            "setup_completed": False
        }

        logger.info(
            f"Onboarded tenant: {tenant_id}",
            extra={"tenant_id": tenant_id, "admin_email": admin_email}
        )

        return {
            "tenant": tenant.to_dict(),
            "next_steps": [
                "Complete profile setup",
                "Invite team members",
                "Configure settings"
            ]
        }

    def complete_setup(self, tenant_id: str):
        """Mark tenant setup as complete."""
        tenant = self.tenant_manager.get_tenant(tenant_id)

        if tenant:
            tenant.settings["setup_completed"] = True
            logger.info(f"Completed setup for tenant: {tenant_id}")


class TenantMiddleware:
    """Middleware for tenant context."""

    def __init__(self, tenant_manager: TenantManager):
        """Initialize tenant middleware."""
        self.tenant_manager = tenant_manager

    async def process_request(self, request) -> TenantContext:
        """Process request and extract tenant context."""
        # Extract tenant ID from request
        tenant_id = self._extract_tenant_id(request)

        if not tenant_id:
            raise ValueError("Tenant ID not found in request")

        # Get tenant
        tenant = self.tenant_manager.get_tenant(tenant_id)

        if not tenant:
            raise ValueError(f"Tenant not found: {tenant_id}")

        if tenant.status != TenantStatus.ACTIVE:
            raise ValueError(f"Tenant not active: {tenant_id}")

        # Create context
        context = TenantContext(tenant_id)
        context.set_tenant(tenant)

        return context

    def _extract_tenant_id(self, request) -> Optional[str]:
        """Extract tenant ID from request."""
        # Try header
        tenant_id = request.headers.get("X-Tenant-ID")

        if tenant_id:
            return tenant_id

        # Try subdomain
        host = request.headers.get("Host", "")
        if "." in host:
            subdomain = host.split(".")[0]
            return subdomain

        return None


# Global instances
tenant_manager = TenantManager()
tenant_isolation = TenantIsolation()
usage_tracker = TenantUsageTracker()
tenant_billing = TenantBilling()
tenant_onboarding = TenantOnboarding(tenant_manager)
tenant_middleware = TenantMiddleware(tenant_manager)


# Helper functions
def create_tenant(tenant_id: str, name: str, plan: str = "free") -> Tenant:
    """Create new tenant."""
    return tenant_manager.create_tenant(tenant_id, name, plan)


def get_tenant(tenant_id: str) -> Optional[Tenant]:
    """Get tenant."""
    return tenant_manager.get_tenant(tenant_id)


def track_usage(tenant_id: str, resource: str, amount: int = 1):
    """Track resource usage."""
    usage_tracker.record_usage(tenant_id, resource, amount)


def check_tenant_limits(tenant_id: str, resource: str) -> bool:
    """Check if tenant is within limits."""
    tenant = get_tenant(tenant_id)
    if not tenant:
        return False

    current_usage = usage_tracker.get_usage(tenant_id, resource)
    return tenant.is_within_limits(resource, current_usage)
