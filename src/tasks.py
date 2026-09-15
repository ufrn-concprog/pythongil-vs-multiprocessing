"""
Task definitions used by the benchmark.

The task must be genuinely CPU-bound (not I/O-bound or sleep-based) to make
the comparison meaningful by highlighting the impact of the Global 
Interpreter Locker (GIL) on concurrent execution. The GIL specifically 
serializes Python bytecode execution, and is released during I/O or sleep. 
A sleep-based task would make threading look artificially unaffected by the 
GIL, which would not be consistent with the purpose of this benchmark.
"""

def count_primes(start, end):
    """
    Count how many prime numbers exist in the range [start, end).

    Deliberately implemented with a plain nested loop rather than a faster
    algorithm or a library call, to keep the interpreter busy executing
    Python bytecode for a measurable amount of time.

    Args:
        start: Inclusive lower bound of the range.
        end: Exclusive upper bound of the range.

    Returns:
        The number of primes found in the range.
    """
    count = 0
    for n in range(start, end):
        if n < 2:
            continue
        is_prime = True
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                is_prime = False
                break
        if is_prime:
            count += 1
    return count


def split_range(total, num_chunks):
    """
    Split [0, total) into num_chunks contiguous, roughly equal ranges.

    Used to divide work among threads or processes so each worker handles
    an independent chunk with no shared state and no need to merge partial
    results beyond counting.

    Args:
        total: The exclusive upper bound of the full range to split.
        num_chunks: The number of ranges to split it into.

    Returns:
        A list of (start, end) tuples, one per chunk.
    """
    chunk_size = total // num_chunks
    ranges = []
    for i in range(num_chunks):
        start = i * chunk_size
        end = total if i == num_chunks - 1 else start + chunk_size
        ranges.append((start, end))
    return ranges