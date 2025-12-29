"""
Performance benchmarking tool for search engines.

Measures and compares the performance of different search engines
including response time, success rate, and result quality.
"""

import time
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from ixmachina.tools.web import search_web


@dataclass
class SearchEngineMetrics:
    """Metrics for a single search engine."""
    engine_name: str
    total_queries: int
    successful_queries: int
    failed_queries: int
    average_response_time: float
    median_response_time: float
    min_response_time: float
    max_response_time: float
    average_results_count: float
    success_rate: float
    response_times: List[float]
    errors: List[str]


def measure_search_performance(
    queries: List[str],
    search_engines: List[str],
    max_results: int = 10,
    domain_filter: Optional[str] = None,
) -> Dict[str, SearchEngineMetrics]:
    """
    Measure performance of multiple search engines across multiple queries.
    
    Args:
        queries: List of search queries to test.
        search_engines: List of search engine names to test (e.g., ["bing", "yandex", "startpage"]).
        max_results: Maximum number of results per query. Default: 10.
        domain_filter: Optional domain filter to apply to all queries.
    
    Returns:
        Dictionary mapping search engine names to their metrics.
    """
    metrics = {}
    
    for engine in search_engines:
        print(f"\n{'='*60}")
        print(f"Testing {engine.upper()}...")
        print(f"{'='*60}")
        
        response_times = []
        results_counts = []
        errors = []
        successful = 0
        failed = 0
        
        for i, query in enumerate(queries, 1):
            print(f"  Query {i}/{len(queries)}: {query[:50]}...", end=" ", flush=True)
            
            start_time = time.time()
            try:
                result = search_web(
                    query=query,
                    search_engine=engine,
                    max_results=max_results,
                    domain_filter=domain_filter,
                )
                elapsed = time.time() - start_time
                response_times.append(elapsed)
                
                if result["success"]:
                    successful += 1
                    results_counts.append(result["count"])
                    print(f"✓ ({elapsed:.2f}s, {result['count']} results)")
                else:
                    failed += 1
                    error_msg = result.get("error", "Unknown error")
                    errors.append(error_msg)
                    print(f"✗ ({elapsed:.2f}s, Error: {error_msg[:50]})")
            except Exception as e:
                elapsed = time.time() - start_time
                response_times.append(elapsed)
                failed += 1
                error_msg = str(e)
                errors.append(error_msg)
                print(f"✗ ({elapsed:.2f}s, Exception: {error_msg[:50]})")
        
        # Calculate statistics
        if response_times:
            avg_time = statistics.mean(response_times)
            median_time = statistics.median(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
        else:
            avg_time = median_time = min_time = max_time = 0.0
        
        avg_results = statistics.mean(results_counts) if results_counts else 0.0
        success_rate = (successful / len(queries)) * 100 if queries else 0.0
        
        metrics[engine] = SearchEngineMetrics(
            engine_name=engine,
            total_queries=len(queries),
            successful_queries=successful,
            failed_queries=failed,
            average_response_time=avg_time,
            median_response_time=median_time,
            min_response_time=min_time,
            max_response_time=max_time,
            average_results_count=avg_results,
            success_rate=success_rate,
            response_times=response_times,
            errors=errors,
        )
    
    return metrics


def print_performance_report(metrics: Dict[str, SearchEngineMetrics]) -> None:
    """
    Print a formatted performance report comparing all search engines.
    
    Args:
        metrics: Dictionary of search engine metrics.
    """
    print("\n" + "="*80)
    print("SEARCH ENGINE PERFORMANCE REPORT")
    print("="*80)
    
    # Sort by average response time (fastest first)
    sorted_engines = sorted(
        metrics.items(),
        key=lambda x: x[1].average_response_time,
    )
    
    print(f"\n{'Engine':<15} {'Success Rate':<15} {'Avg Time':<12} {'Median Time':<15} {'Avg Results':<15}")
    print("-" * 80)
    
    for engine_name, metric in sorted_engines:
        print(
            f"{engine_name:<15} "
            f"{metric.success_rate:>6.1f}%      "
            f"{metric.average_response_time:>6.2f}s      "
            f"{metric.median_response_time:>6.2f}s      "
            f"{metric.average_results_count:>6.1f}"
        )
    
    print("\n" + "="*80)
    print("DETAILED METRICS")
    print("="*80)
    
    for engine_name, metric in sorted_engines:
        print(f"\n{engine_name.upper()}:")
        print(f"  Total Queries: {metric.total_queries}")
        print(f"  Successful: {metric.successful_queries}")
        print(f"  Failed: {metric.failed_queries}")
        print(f"  Success Rate: {metric.success_rate:.1f}%")
        print(f"  Response Times:")
        print(f"    Average: {metric.average_response_time:.2f}s")
        print(f"    Median: {metric.median_response_time:.2f}s")
        print(f"    Min: {metric.min_response_time:.2f}s")
        print(f"    Max: {metric.max_response_time:.2f}s")
        print(f"  Average Results per Query: {metric.average_results_count:.1f}")
        
        if metric.errors:
            print(f"  Errors ({len(metric.errors)}):")
            unique_errors = list(set(metric.errors))[:5]  # Show first 5 unique errors
            for error in unique_errors:
                print(f"    - {error[:100]}")


def run_benchmark(
    queries: Optional[List[str]] = None,
    search_engines: Optional[List[str]] = None,
    max_results: int = 10,
) -> Dict[str, SearchEngineMetrics]:
    """
    Run a comprehensive benchmark of search engines.
    
    Args:
        queries: List of test queries. If None, uses default test queries.
        search_engines: List of engines to test. If None, tests all available.
        max_results: Maximum results per query.
    
    Returns:
        Dictionary of metrics for each search engine.
    """
    if queries is None:
        queries = [
            "python programming",
            "machine learning",
            "web development",
            "data science",
            "artificial intelligence",
            "software engineering",
            "cloud computing",
            "cybersecurity",
        ]
    
    if search_engines is None:
        search_engines = ["bing", "yandex", "startpage", "duckduckgo"]
    
    print(f"Running benchmark with {len(queries)} queries across {len(search_engines)} search engines...")
    print(f"Queries: {', '.join(queries)}")
    print(f"Engines: {', '.join(search_engines)}")
    
    metrics = measure_search_performance(
        queries=queries,
        search_engines=search_engines,
        max_results=max_results,
    )
    
    print_performance_report(metrics)
    
    return metrics


if __name__ == "__main__":
    # Run benchmark
    metrics = run_benchmark()
    
    # Optionally save results to a file
    print("\n" + "="*80)
    print("Benchmark complete!")
    print("="*80)

