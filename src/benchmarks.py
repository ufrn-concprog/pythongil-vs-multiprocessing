"""
Benchmark runners comparing single-threaded execution, threading, and
multiprocessing on a CPU-bound task.
"""

import time
import threading
import multiprocessing
import statistics

from tasks import count_primes, split_range

def run_single_threaded(upper_bound):
    """
    Run count_primes once, with no concurrency, as a baseline.

    Args:
        upper_bound: Exclusive upper bound passed to count_primes.

    Returns:
        Elapsed time in seconds.
    """
    start_time = time.perf_counter()
    count_primes(0, upper_bound)
    return time.perf_counter() - start_time


def run_threading(upper_bound, num_workers):
    """
    Run count_primes split across num_workers threads.

    Expected to show little to no speedup over the single-threaded baseline
    on the standard (GIL-enabled) Python build, since the GIL allows only
    one thread to execute Python bytecode at a time.

    Args:
        upper_bound: Exclusive upper bound of the full range to process.
        num_workers: Number of threads to split the work across.

    Returns:
        Elapsed time in seconds.
    """
    ranges = split_range(upper_bound, num_workers)
    threads = []

    start_time = time.perf_counter()
    for r_start, r_end in ranges:
        t = threading.Thread(target=count_primes, args=(r_start, r_end))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return time.perf_counter() - start_time


def run_multiprocessing(upper_bound, num_workers):
    """
    Run count_primes split across num_workers processes.

    Expected to show a real speedup over both the single-threaded and
    threading runs, since each process has its own interpreter and its own
    GIL, allowing true parallel execution across CPU cores.

    Args:
        upper_bound: Exclusive upper bound of the full range to process.
        num_workers: Number of processes to split the work across.

    Returns:
        Elapsed time in seconds.
    """
    ranges = split_range(upper_bound, num_workers)

    start_time = time.perf_counter()
    with multiprocessing.Pool(processes=num_workers) as pool:
        pool.starmap(count_primes, ranges)

    return time.perf_counter() - start_time


def run_repeated(label, task, runs=5):
    """
    Run task repeatedly and report the mean and standard deviation of its
    elapsed time.

    Args:
        label: Descriptive label printed alongside the result.
        task: A zero-argument callable returning elapsed seconds.
        runs: Number of times to repeat the run.
    """
    times = [task() for _ in range(runs)]
    mean = statistics.mean(times)
    std_dev = statistics.stdev(times) if runs > 1 else 0.0
    print(f"{label:<20}| Mean: {mean:.3f} s | Std Dev: {std_dev:.3f} s")