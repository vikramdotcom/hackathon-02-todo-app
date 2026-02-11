"""
Health Check Script

Performs comprehensive health checks on the application and its dependencies.
"""

import requests
import sys
from typing import Dict, List
import time


class HealthChecker:
    """Perform health checks on application components."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize health checker.

        Args:
            base_url: Base URL of the application
        """
        self.base_url = base_url
        self.checks = []

    def check_api_health(self) -> Dict:
        """
        Check API health endpoint.

        Returns:
            Health check result
        """
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)

            if response.status_code == 200:
                data = response.json()
                return {
                    "name": "API Health",
                    "status": "healthy" if data.get("status") == "healthy" else "unhealthy",
                    "details": data
                }
            else:
                return {
                    "name": "API Health",
                    "status": "unhealthy",
                    "details": {"status_code": response.status_code}
                }
        except Exception as e:
            return {
                "name": "API Health",
                "status": "unhealthy",
                "details": {"error": str(e)}
            }

    def check_api_ready(self) -> Dict:
        """
        Check API readiness endpoint.

        Returns:
            Readiness check result
        """
        try:
            response = requests.get(f"{self.base_url}/ready", timeout=5)

            if response.status_code == 200:
                return {
                    "name": "API Readiness",
                    "status": "ready",
                    "details": response.json()
                }
            else:
                return {
                    "name": "API Readiness",
                    "status": "not_ready",
                    "details": {"status_code": response.status_code}
                }
        except Exception as e:
            return {
                "name": "API Readiness",
                "status": "not_ready",
                "details": {"error": str(e)}
            }

    def check_api_response_time(self) -> Dict:
        """
        Check API response time.

        Returns:
            Response time check result
        """
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=5)
            duration_ms = (time.time() - start_time) * 1000

            status = "healthy" if duration_ms < 1000 else "slow"

            return {
                "name": "API Response Time",
                "status": status,
                "details": {
                    "response_time_ms": round(duration_ms, 2),
                    "threshold_ms": 1000
                }
            }
        except Exception as e:
            return {
                "name": "API Response Time",
                "status": "unhealthy",
                "details": {"error": str(e)}
            }

    def check_database(self) -> Dict:
        """
        Check database connectivity via API.

        Returns:
            Database check result
        """
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)

            if response.status_code == 200:
                data = response.json()
                components = data.get("components", {})
                db_status = components.get("database", "unknown")

                return {
                    "name": "Database",
                    "status": db_status,
                    "details": {"component_status": db_status}
                }
            else:
                return {
                    "name": "Database",
                    "status": "unknown",
                    "details": {"status_code": response.status_code}
                }
        except Exception as e:
            return {
                "name": "Database",
                "status": "unhealthy",
                "details": {"error": str(e)}
            }

    def run_all_checks(self) -> List[Dict]:
        """
        Run all health checks.

        Returns:
            List of check results
        """
        print("Running health checks...\n")

        checks = [
            self.check_api_health(),
            self.check_api_ready(),
            self.check_api_response_time(),
            self.check_database()
        ]

        self.checks = checks
        return checks

    def print_results(self):
        """Print health check results."""
        print("="*60)
        print("Health Check Results")
        print("="*60)

        all_healthy = True

        for check in self.checks:
            status = check["status"]
            name = check["name"]

            # Status symbol
            if status in ["healthy", "ready"]:
                symbol = "✓"
                status_text = "HEALTHY"
            elif status == "slow":
                symbol = "⚠"
                status_text = "SLOW"
                all_healthy = False
            else:
                symbol = "✗"
                status_text = "UNHEALTHY"
                all_healthy = False

            print(f"\n{symbol} {name}: {status_text}")

            # Print details
            if check["details"]:
                for key, value in check["details"].items():
                    print(f"  {key}: {value}")

        print("\n" + "="*60)

        if all_healthy:
            print("Overall Status: HEALTHY ✓")
            return 0
        else:
            print("Overall Status: UNHEALTHY ✗")
            return 1


def main():
    """Main health check script."""
    import argparse

    parser = argparse.ArgumentParser(description="Run health checks")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the application"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    checker = HealthChecker(base_url=args.url)
    checks = checker.run_all_checks()

    if args.json:
        import json
        print(json.dumps(checks, indent=2))
        sys.exit(0)
    else:
        exit_code = checker.print_results()
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
