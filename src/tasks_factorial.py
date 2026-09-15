"""
Factorial computation task. This task is not naturally independent across chunks
as n! is a single long chain of multiplications. To parallelize it, each chunk 
computes a partial product over its own sub-range, and the partial products 
must then be multiplied together to produce the final result. This merge step 
is itself a real, non-negligible cost, and is included in the benchmark's timing.
"""

def partial_factorial(bounds):
    """
    Compute the product of all integers in the range [start, end).

    Args:
        bounds: A (start, end) tuple. start is inclusive, end is exclusive.
            To compute n! across a full range, chunks should cover [1, n+1).

    Returns:
        The product of the range, as a (potentially very large) integer.
    """
    start, end = bounds
    product = 1
    for i in range(start, end):
        product *= i
    return product


def combine_products(partial_products):
    """
    Multiply a list of (potentially very large) integers together, using
    balanced pairwise reduction rather than a left-to-right reduction.

    Pairwise reduction keeps operand sizes more even for longer, which is
    more efficient for big integers than repeatedly multiplying a single,
    ever-growing accumulator by the next term.

    Args:
        partial_products: A list of integers to multiply together.

    Returns:
        The product of all values in partial_products.
    """
    numbers = list(partial_products)
    while len(numbers) > 1:
        merged = []
        for i in range(0, len(numbers) - 1, 2):
            merged.append(numbers[i] * numbers[i + 1])
        if len(numbers) % 2 == 1:
            merged.append(numbers[-1])
        numbers = merged
    return numbers[0] if numbers else 1