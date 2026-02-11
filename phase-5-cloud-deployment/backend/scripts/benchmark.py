"""
Performance Benchmarking Script

Benchmarks API endpoint performance and generates reports.
"""

import time
import statistics
import requests
from typing import List, Dict
import json


class APIBenchmark:
    """Benchmark API endpoints."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize benchmark.

        Args:
            base_url: Base URL of the API
        """
        self.base_url = base_url
        self.results = []

    def benchmark_endpoint(
        self,
        method: str,
        endpoint: str,
        data: Dict = None,
        iterations: int = 100
    ) -> Dict:
        """
        Benchmark a single endpoint.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request data (for POST/PATCH)
            iterations: Number of iterations

        Returns:
            Benchmark results
        """
        url = f"{self.base_url}{endpoint}"
        response_times = []
        errors = 0

        print(f"\nBenchmarking {method} {endpoint} ({iterations} iterations)...")

        for i in range(iterations):
            start_time = time.time()

            try:
                if method == "GET":
                    response = requests.get(url)
                elif method == "POST":
                    response = requests.post(url, json=data)
                elif method == "PATCH":
                    response = requests.patch(url, json=data)
                elif method == "DELETE":
                    response = requests.delete(url)

                duration_ms = (time.time() - start_time) * 1000

                if response.status_code < 400:
                    response_times.append(duration_ms)
                else:
                    errors += 1

            except Exception as e:
                errors += 1
                print(f"Error in iteration {i}: {e}")

            # Progress indicator
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i + 1}/{iterations}")

        # Calculate statistics
        if response_times:
            results = {
                "endpoint": f"{method} {endpoint}",
                "iterations": iterations,
                "successful": len(response_times),
                "errors": errors,
                "min_ms": round(min(response_times), 2),
                "max_ms": round(max(response_times), 2),
                "mean_ms": round(statistics.mean(response_times), 2),
                "median_ms": round(statistics.median(response_times), 2),
                "p95_ms": round(sorted(response_times)[int(len(response_times) * 0.95)], 2),
                "p99_ms": round(sorted(response_times)[int(len(response_times) * 0.99)], 2),
                "stdev_ms": round(statistics.stdev(response_times), 2) if len(response_times) > 1 else 0
            }
        else:
            results = {
                "endpoint": f"{method} {endpoint}",
                "iterations": iterations,
                "successful": 0,
                "errors": errors,
                "error": "All requests failed"
            }

        self.results.append(results)
        return results

    def print_results(self, results: Dict):
        """
        Print benchmark results.

        Args:
            results: Benchmark results
        """
        print(f"\n{'='*60}")
        print(f"Results for {results['endpoint']}")
        print(f"{'='*60}")
        print(f"Iterations:  {results['iterations']}")
        print(f"Successful:  {results['successful']}")
        print(f"Errors:      {results['errors']}")

        if "error" not in results:
            print(f"\nResponse Times (ms):")
            print(f"  Min:       {results['min_ms']}")
            print(f"  Max:       {results['max_ms']}")
            print(f"  Mean:      {results['mean_ms']}")
            print(f"  Median:    {results['median_ms']}")
            print(f"  P95:       {results['p95_ms']}")
            print(f"  P99:       {results['p99_ms']}")
            print(f"  Std Dev:   {results['stdev_ms']}")

    def save_results(self, filename: str = "benchmark_results.json"):
        """
        Save results to JSON file.

        Args:
            filename: Output filename
        """
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to {filename}")


def main():
    """Run benchmarks."""
    benchmark = APIBenchmark()

    # Benchmark health check
    results = benchmark.benchmark_endpoint("GET", "/health", iterations=100)
    benchmark.print_results(results)

    # Benchmark list todos
    results = benchmark.benchmark_endpoint("GET", "/api/v2/todos", iterations=100)
    benchmark.print_results(results)

    # Benchmark create todo
    todo_data = {
        "title": "Benchmark test todo",
        "description": "Created during benchmark",
        "priority": "medium"
    }
    results = benchmark.benchmark_endpoint("POST", "/api/v2/todos", data=todo_data, iterations=50)
    benchmark.print_results(results)

    # Benchmark search
    search_data = {"query": "test", "limit": 10}
    results = benchmark.benchmark_endpoint("POST", "/api/v2/todos/search", data=search_data, iterations=100)
    benchmark.print_results(results)

    # Save results
    benchmark.save_results()

    print("\n" + "="*60)
    print("Benchmark complete!")
    print("="*60)


if __name__ == "__main__":
    main()
