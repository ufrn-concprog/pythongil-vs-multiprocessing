"""
Generic benchmark harness shared by all example tasks. Each task supplies 
its own functions for the chunk-processing and combining partial results.
The harness itself only handles splitting work across threads/processes, 
timing, and repeated-run statistics.
"""

import time
import threading
import multiprocessing
import statistics


def split_range(start, end, num_chunks):
    """
    Split [start, end) into num_chunks contiguous, roughly equal chunks.

    Args:
        start: Inclusive lower bound of the full range.
        end: Exclusive upper bound of the full range.
        num_chunks: Number of chunks to split the range into.

    Returns:
        A list of (chunk_start, chunk_end) tuples, one per chunk, each
        itself following the same [chunk_start, chunk_end) convention.
    """
    total = end - start
    chunk_size = total // num_chunks
    chunks = []
    for i in range(num_chunks):
        chunk_start = start + i * chunk_size
        chunk_end = end if i == num_chunks - 1 else chunk_start + chunk_size
        chunks.append((chunk_start, chunk_end))
    return chunks


def run_single_threaded(task_function, whole_range):
    """
    Run task_function once, on the whole range, with no concurrency, 
    as a baseline.

    Args:
        task_function: A callable taking a single (start, end) tuple.
        whole_range: The (start, end) tuple covering the entire workload.

    Returns:
        Elapsed time in seconds.
    """
    start_time = time.perf_counter()
    task_function(whole_range)
    return time.perf_counter() - start_time


def run_threading(task_function, chunks, combine_function):
    """
    Run task_function once per chunk, each in its own thread, then combine the
    partial results.

    Each thread writes its result into its own pre-assigned slot in a
    results list, rather than appending concurrently. This avoids needing
    any synchronization mechanism to collect results safely.

    Args:
        task_function: A callable taking a single (start, end) tuple, 
            returning a partial result.
        chunks: A list of (start, end) tuples, one per thread.
        combine_function: A callable taking the list of partial results 
            and returning the final combined result.

    Returns:
        Elapsed time in seconds.
    """
    results = [None] * len(chunks)

    def worker(index, chunk):
        results[index] = task_function(chunk)

    start_time = time.perf_counter()

    threads = []
    for i, chunk in enumerate(chunks):
        t = threading.Thread(target=worker, args=(i, chunk))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    combine_function(results)

    return time.perf_counter() - start_time


def run_multiprocessing(task_function, chunks, combine_function, num_workers):
    """
    Run task_function once per chunk, each in its own process, then combine the
    partial results.

    As with run_threading, the combine step runs in the parent process
    after all workers finish.

    Args:
        task_function: A callable taking a single (start, end) tuple, 
        returning a partial result. It must be a top-level function 
            (picklable), since multiprocessing needs to send it to each 
            child process.
        chunks: A list of (start, end) tuples, one per process.
        combine_function: A callable taking the list of partial results 
            and returning the final combined result.
        num_workers: Number of worker processes to use.

    Returns:
        Elapsed time in seconds.
    """
    start_time = time.perf_counter()

    with multiprocessing.Pool(processes=num_workers) as pool:
        results = pool.map(task_function, chunks)

    combine_function(results)

    return time.perf_counter() - start_time


def run_chunked_sequential(task_function, chunks, combine_function):
    """
    Sequentially run task_function once per chunk in a single thread/process 
    (no concurrency at all) then combine the partial results.

    This isolates the effect of splitting the work into chunks, which can
    itself change the total amount of computation for some tasks, from the 
    effect of running those chunks concurrently.

    Args:
        task_function: A callable taking a single (start, end) tuple, 
            returning a partial result.
        chunks: A list of (start, end) tuples.
        combine_function: A callable taking the list of partial results 
            and returning the final combined result.

    Returns:
        Elapsed time in seconds.
    """
    start_time = time.perf_counter()

    results = [task_function(chunk) for chunk in chunks]
    combine_function(results)

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