"""
Prime-counting task. Each chunk of the range is entirely independent, 
and partial results (counts) are summed together. There is no dependency 
between chunks or ordering requirement.
"""
    
def count_primes(bounds):
    """
    Count how many prime numbers exist in the range [start, end).

    Args:
        bounds: A (start, end) tuple. start is inclusive, end is exclusive.

    Returns:
        The number of primes found in the range.
    """
    start, end = bounds
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


def combine_counts(partial_counts):
    """Combine per-chunk prime counts into a single total."""
    return sum(partial_counts)