"""
Compliance and Audit System

Ensure compliance with regulations and audit requirements.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import hashlib
import json

logger = logging.getLogger(__name__)


class ComplianceStandard(str, Enum):
    """Compliance standards."""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"


class AuditEvent:
    """Audit event entity."""

    def __init__(
        self,
        event_type: str,
        user_id: Optional[int],
        resource_type: str,
        resource_id: str,
        action: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize audit event."""
        self.event_id = self._generate_event_id()
        self.event_type = event_type
        self.user_id = user_id
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.action = action
        self.details = details or {}
        self.timestamp = datetime.utcnow()
        self.ip_address: Optional[str] = None
        self.user_agent: Optional[str] = None

    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        import uuid
        return str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "user_id": self.user_id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "action": self.action,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent
        }

    def calculate_hash(self) -> str:
        """Calculate event hash for integrity."""
        data = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()


class AuditLogger:
    """Audit logging system."""

    def __init__(self):
        """Initialize audit logger."""
        self.events: List[AuditEvent] = []
        self.retention_days = 365

    def log_event(
        self,
        event_type: str,
        user_id: Optional[int],
        resource_type: str,
        resource_id: str,
        action: str,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """Log audit event."""
        event = AuditEvent(
            event_type,
            user_id,
            resource_type,
            resource_id,
            action,
            details
        )

        self.events.append(event)

        logger.info(
            f"Audit event: {action} on {resource_type}",
            extra={
                "event_id": event.event_id,
                "user_id": user_id,
                "action": action,
                "resource": f"{resource_type}:{resource_id}"
            }
        )

        return event

    def get_events(
        self,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[AuditEvent]:
        """Get audit events with filters."""
        filtered_events = self.events

        if user_id:
            filtered_events = [e for e in filtered_events if e.user_id == user_id]

        if resource_type:
            filtered_events = [e for e in filtered_events if e.resource_type == resource_type]

        if start_date:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_date]

        if end_date:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_date]

        return filtered_events[-limit:]

    def export_audit_trail(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Export audit trail for period."""
        events = self.get_events(start_date=start_date, end_date=end_date)
        return [e.to_dict() for e in events]


class ComplianceChecker:
    """Check compliance with standards."""

    def __init__(self):
        """Initialize compliance checker."""
        self.standards: Dict[ComplianceStandard, Dict[str, Any]] = {}

    def register_standard(
        self,
        standard: ComplianceStandard,
        requirements: List[str]
    ):
        """Register compliance standard."""
        self.standards[standard] = {
            "requirements": requirements,
            "checks": []
        }

    def add_check(
        self,
        standard: ComplianceStandard,
        check_name: str,
        check_func: callable
    ):
        """Add compliance check."""
        if standard not in self.standards:
            return

        self.standards[standard]["checks"].append({
            "name": check_name,
            "function": check_func
        })

    async def run_compliance_check(
        self,
        standard: ComplianceStandard
    ) -> Dict[str, Any]:
        """Run compliance checks."""
        if standard not in self.standards:
            return {"error": "Standard not registered"}

        results = {
            "standard": standard.value,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": [],
            "passed": 0,
            "failed": 0
        }

        for check in self.standards[standard]["checks"]:
            try:
                passed = await check["function"]()
                results["checks"].append({
                    "name": check["name"],
                    "passed": passed,
                    "timestamp": datetime.utcnow().isoformat()
                })

                if passed:
                    results["passed"] += 1
                else:
                    results["failed"] += 1

            except Exception as e:
                logger.error(f"Compliance check failed: {check['name']}: {e}")
                results["checks"].append({
                    "name": check["name"],
                    "passed": False,
                    "error": str(e)
                })
                results["failed"] += 1

        results["compliance_score"] = (
            results["passed"] / (results["passed"] + results["failed"]) * 100
            if (results["passed"] + results["failed"]) > 0 else 0
        )

        return results


class DataRetentionPolicy:
    """Manage data retention policies."""

    def __init__(self):
        """Initialize data retention policy."""
        self.policies: Dict[str, int] = {}

    def set_retention_period(self, data_type: str, days: int):
        """Set retention period for data type."""
        self.policies[data_type] = days
        logger.info(f"Set retention policy: {data_type} = {days} days")

    def get_retention_period(self, data_type: str) -> Optional[int]:
        """Get retention period."""
        return self.policies.get(data_type)

    def should_delete(self, data_type: str, created_at: datetime) -> bool:
        """Check if data should be deleted."""
        retention_days = self.get_retention_period(data_type)

        if not retention_days:
            return False

        age_days = (datetime.utcnow() - created_at).days
        return age_days > retention_days


class DataPrivacyManager:
    """Manage data privacy and GDPR compliance."""

    def __init__(self):
        """Initialize data privacy manager."""
        self.consent_records: Dict[int, Dict[str, Any]] = {}
        self.deletion_requests: List[Dict[str, Any]] = []

    def record_consent(
        self,
        user_id: int,
        consent_type: str,
        granted: bool
    ):
        """Record user consent."""
        if user_id not in self.consent_records:
            self.consent_records[user_id] = {}

        self.consent_records[user_id][consent_type] = {
            "granted": granted,
            "timestamp": datetime.utcnow().isoformat()
        }

        logger.info(
            f"Recorded consent: user={user_id}, type={consent_type}, granted={granted}"
        )

    def has_consent(self, user_id: int, consent_type: str) -> bool:
        """Check if user has granted consent."""
        if user_id not in self.consent_records:
            return False

        consent = self.consent_records[user_id].get(consent_type)
        return consent and consent["granted"]

    def request_data_deletion(self, user_id: int, reason: str):
        """Request data deletion (GDPR right to be forgotten)."""
        request = {
            "user_id": user_id,
            "reason": reason,
            "requested_at": datetime.utcnow().isoformat(),
            "status": "pending"
        }

        self.deletion_requests.append(request)

        logger.info(
            f"Data deletion requested: user={user_id}",
            extra={"user_id": user_id, "reason": reason}
        )

    def export_user_data(self, user_id: int) -> Dict[str, Any]:
        """Export user data (GDPR data portability)."""
        # In production, collect all user data from various sources
        return {
            "user_id": user_id,
            "exported_at": datetime.utcnow().isoformat(),
            "data": {
                "consent_records": self.consent_records.get(user_id, {}),
                # Add other user data here
            }
        }


class AccessControlAuditor:
    """Audit access control and permissions."""

    def __init__(self):
        """Initialize access control auditor."""
        self.access_logs: List[Dict[str, Any]] = []

    def log_access_attempt(
        self,
        user_id: int,
        resource: str,
        action: str,
        granted: bool,
        reason: Optional[str] = None
    ):
        """Log access attempt."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "granted": granted,
            "reason": reason
        }

        self.access_logs.append(log_entry)

        if not granted:
            logger.warning(
                f"Access denied: user={user_id}, resource={resource}, action={action}",
                extra=log_entry
            )

    def get_failed_access_attempts(
        self,
        user_id: Optional[int] = None,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get failed access attempts."""
        cutoff = datetime.utcnow().timestamp() - (hours * 3600)

        failed = [
            log for log in self.access_logs
            if not log["granted"] and
            datetime.fromisoformat(log["timestamp"]).timestamp() > cutoff
        ]

        if user_id:
            failed = [log for log in failed if log["user_id"] == user_id]

        return failed


class ComplianceReporter:
    """Generate compliance reports."""

    def __init__(
        self,
        audit_logger: AuditLogger,
        compliance_checker: ComplianceChecker
    ):
        """Initialize compliance reporter."""
        self.audit_logger = audit_logger
        self.compliance_checker = compliance_checker

    async def generate_compliance_report(
        self,
        standard: ComplianceStandard,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate compliance report."""
        # Run compliance checks
        compliance_results = await self.compliance_checker.run_compliance_check(standard)

        # Get audit events
        audit_events = self.audit_logger.get_events(
            start_date=start_date,
            end_date=end_date
        )

        return {
            "standard": standard.value,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "compliance_results": compliance_results,
            "audit_summary": {
                "total_events": len(audit_events),
                "event_types": self._count_event_types(audit_events)
            },
            "generated_at": datetime.utcnow().isoformat()
        }

    def _count_event_types(self, events: List[AuditEvent]) -> Dict[str, int]:
        """Count events by type."""
        counts = {}
        for event in events:
            counts[event.event_type] = counts.get(event.event_type, 0) + 1
        return counts


class EncryptionAuditor:
    """Audit encryption usage."""

    def __init__(self):
        """Initialize encryption auditor."""
        self.encryption_status: Dict[str, bool] = {}

    def register_data_store(self, name: str, encrypted: bool):
        """Register data store encryption status."""
        self.encryption_status[name] = encrypted

    def audit_encryption(self) -> Dict[str, Any]:
        """Audit encryption status."""
        total = len(self.encryption_status)
        encrypted = sum(1 for e in self.encryption_status.values() if e)

        return {
            "total_data_stores": total,
            "encrypted": encrypted,
            "unencrypted": total - encrypted,
            "encryption_rate": (encrypted / total * 100) if total > 0 else 0,
            "details": self.encryption_status
        }


class SecurityIncidentTracker:
    """Track security incidents."""

    def __init__(self):
        """Initialize security incident tracker."""
        self.incidents: List[Dict[str, Any]] = []

    def report_incident(
        self,
        incident_type: str,
        severity: str,
        description: str,
        affected_users: Optional[List[int]] = None
    ) -> str:
        """Report security incident."""
        import uuid
        incident_id = str(uuid.uuid4())

        incident = {
            "incident_id": incident_id,
            "type": incident_type,
            "severity": severity,
            "description": description,
            "affected_users": affected_users or [],
            "reported_at": datetime.utcnow().isoformat(),
            "status": "open"
        }

        self.incidents.append(incident)

        logger.error(
            f"Security incident reported: {incident_type}",
            extra={
                "incident_id": incident_id,
                "severity": severity,
                "affected_users": len(affected_users) if affected_users else 0
            }
        )

        return incident_id

    def get_open_incidents(self) -> List[Dict[str, Any]]:
        """Get open incidents."""
        return [i for i in self.incidents if i["status"] == "open"]


# Global instances
audit_logger = AuditLogger()
compliance_checker = ComplianceChecker()
data_retention_policy = DataRetentionPolicy()
data_privacy_manager = DataPrivacyManager()
access_control_auditor = AccessControlAuditor()
compliance_reporter = ComplianceReporter(audit_logger, compliance_checker)
encryption_auditor = EncryptionAuditor()
security_incident_tracker = SecurityIncidentTracker()


# Helper functions
def log_audit_event(
    event_type: str,
    user_id: Optional[int],
    resource_type: str,
    resource_id: str,
    action: str,
    details: Optional[Dict[str, Any]] = None
) -> AuditEvent:
    """Log audit event."""
    return audit_logger.log_event(
        event_type,
        user_id,
        resource_type,
        resource_id,
        action,
        details
    )


def record_user_consent(user_id: int, consent_type: str, granted: bool):
    """Record user consent."""
    data_privacy_manager.record_consent(user_id, consent_type, granted)


def request_data_deletion(user_id: int, reason: str):
    """Request data deletion."""
    data_privacy_manager.request_data_deletion(user_id, reason)


async def generate_compliance_report(
    standard: ComplianceStandard,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """Generate compliance report."""
    return await compliance_reporter.generate_compliance_report(
        standard,
        start_date,
        end_date
    )
