"""
This program compares single-threaded execution, threading, and
multiprocessing on the same CPU-bound task (counting primes).

UPPER_BOUND and NUM_WORKERS are the two constants most worth tuning:
- UPPER_BOUND controls how long the single-threaded baseline takes. It
  should be large enough that the difference between runs is clearly
  visible, but small enough to run live in a reasonable amount of time.
- NUM_WORKERS defaults to the number of logical CPUs available, so the
  demonstration reflects the actual hardware it runs on.
"""

import multiprocessing

from benchmarks import run_single_threaded, run_threading, run_multiprocessing, run_repeated

UPPER_BOUND = 200_000
RUNS = 20


def main():
    num_workers = multiprocessing.cpu_count()

    print(f"Counting primes up to {UPPER_BOUND}, using {num_workers} workers "
          f"where applicable\n")

    run_repeated("Single-threaded", lambda: run_single_threaded(UPPER_BOUND), RUNS)
    run_repeated("Threading (GIL)", lambda: run_threading(UPPER_BOUND, num_workers), RUNS)
    run_repeated("Multiprocessing", lambda: run_multiprocessing(UPPER_BOUND, num_workers), RUNS)


if __name__ == "__main__":
    # Required on macOS and Windows, where multiprocessing uses the 'spawn'
    # start method: it re-imports this module in each child process, so code
    # that starts processes must be guarded behind this check to avoid
    # infinite recursive spawning.
    main()