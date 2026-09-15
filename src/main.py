"""
Entry point: runs two CPU-bound examples, prime counting (parallel) and 
factorial computation (partition + sequential merge), each compared across 
relevant execution strategies.

Prime counting is compared against a plain single-threaded baseline since
chunking does not change the total amount of work for that task.

Factorial is compared against a chunked (sequential) baseline instead of
a naive single-threaded one. Naively accumulating *n*! as one long product is
algorithmically more expensive than the chunked-and-merged approach used by
the threading and multiprocessing runs, independent of concurrency. Using
the naive version as a baseline would conflate that algorithmic effect with
the effect of concurrency.

PRIMES_UPPER_BOUND and FACTORIAL_N control workload size for each example
separately, since the two tasks have very different cost profiles and must
be tuned independently for the running machine.
"""

import multiprocessing

from common import (
    split_range,
    run_single_threaded,
    run_chunked_sequential,
    run_threading,
    run_multiprocessing,
    run_repeated,
)
from tasks_primes import count_primes, combine_counts
from tasks_factorial import partial_factorial, combine_products

PRIMES_UPPER_BOUND = 500_000
FACTORIAL_N = 100_000
RUNS = 20

def run_primes_example(num_workers):
    whole_range = (0, PRIMES_UPPER_BOUND)
    chunks = split_range(0, PRIMES_UPPER_BOUND, num_workers)

    print(f"--- Prime counting up to {PRIMES_UPPER_BOUND} ---")
    run_repeated("Sequential",
                 lambda: run_single_threaded(count_primes, whole_range), RUNS)
    run_repeated("Threading (GIL)",
                 lambda: run_threading(count_primes, chunks, combine_counts), RUNS)
    run_repeated("Multiprocessing",
                 lambda: run_multiprocessing(count_primes, chunks, combine_counts, num_workers), RUNS)
    print()


def run_factorial_example(num_workers):
    chunks = split_range(1, FACTORIAL_N + 1, num_workers)

    print(f"--- Factorial of {FACTORIAL_N} ---")
    run_repeated("Sequential (chunked)",
                 lambda: run_chunked_sequential(partial_factorial, chunks, combine_products), RUNS)
    run_repeated("Threading (GIL)",
                 lambda: run_threading(partial_factorial, chunks, combine_products), RUNS)
    run_repeated("Multiprocessing",
                 lambda: run_multiprocessing(partial_factorial, chunks, combine_products, num_workers), RUNS)
    print()


def main():
    num_workers = multiprocessing.cpu_count()
    print(f"Using {num_workers} workers where applicable\n")

    run_primes_example(num_workers)
    run_factorial_example(num_workers)


if __name__ == "__main__":
    main()