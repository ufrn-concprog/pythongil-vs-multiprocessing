# `threading` vs. `multiprocessing` under the GIL in Python

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Build](https://img.shields.io/badge/build-manual-lightgrey)

This benchmark compares single-threaded execution, `threading`, and `multiprocessing` on two CPU-bound tasks to demonstrate empirically how Python's Global Interpreter Lock (GIL) limits threading's benefit for CPU-bound work — and why `multiprocessing` is the standard workaround.

This project is part of the Concurrent Programming module at the [Federal University of Rio Grande do Norte (UFRN)](https://www.ufrn.br), Natal, Brazil.

## 📃 Description

Both tasks are CPU-bound (no I/O, no sleeping). The GIL serializes Python bytecode execution and releases during I/O or sleep, so a task involving either would not show its effect.

**1. Prime counting** — a parallel workload. The search range is split into independent chunks, each worker (thread or process) counts primes in its chunk, and the partial counts are simply summed. Splitting the work does not change the total amount of computation, only who performs it, so this example cleanly isolates the effect of concurrency itself. It is compared against a plain single-threaded baseline.

**2. Factorial computation** — a workload with a genuine sequential bottleneck, with specific controls for splitting the range into chunks changes the total amount of computation, not just who performs it. Naively accumulating *n*! as one long, ever-growing product is algorithmically more expensive than splitting the range into chunks, computing smaller partial products, and merging them. Because of this, factorial **is not** compared against a naive, unchunked single-threaded run since that would conflate the benefit of restructuring the algorithm with the benefit of concurrency and produce a misleading result. Instead, all three factorial runs (sequential, threading, multiprocessing) **use the same chunking and merge strategy**, differing only in whether the chunks run one after another, on separate threads, or on separate processes.

Across both tasks, expect:

- `threading` on the standard (GIL-enabled) Python build to show negligible to no speedup over its baseline because the GIL allows only one thread to execute Python bytecode at a time.
- `multiprocessing` to show a real speedup over its baseline since each process has its own interpreter and its own GIL.

⚠️ **Note:** This benchmark uses the standard Python build. Python 3.13+ also supports an experimental, separately-installed *free-threaded* build (`3.13t`/`3.14t`, per [PEP 703](https://peps.python.org/pep-0703/)) that can remove the GIL entirely. As of Python 3.14, that build is officially supported, but it is still opt-in, not the default, so this benchmark does not use it.

## 📂 Repository Structure

```text
.
├── common.py            # Generic benchmark harness: splitting, timing, sequential/threaded/multiprocess runners
├── tasks_primes.py      # Prime-counting task and its combine function (sum)
├── tasks_factorial.py   # Factorial task and its combine function (pairwise product merge)
├── main.py              # Entry point: runs both examples and prints results
└── README.md
```

## 🚀 Getting Started

Prerequisites:

- Python 3.9 or later (uses only the standard library, no external dependencies)

## ▶️ Running

```bash
python src/main.py
```

### Tuning workload size

`PRIMES_UPPER_BOUND` and `FACTORIAL_N` (constants at the top of [`main.py`](src/main.py)) control how long each task's baseline run takes. A large enough value clearly shows differences between approaches, and a small enough value lets it run live in a reasonable amount of time. The two tasks have different cost profiles and should be tuned independently.

## 📊 Results

Measured with 20 runs each:

```text
Prime counting up to 500000
Sequential          | Mean: 0.665 s | Std Dev: 0.015 s
Threading (GIL)     | Mean: 0.651 s | Std Dev: 0.011 s
Multiprocessing     | Mean: 0.209 s | Std Dev: 0.014 s

Factorial of 100000
Sequential (chunked)  | Mean: 0.448 s | Std Dev: 0.007 s
Threading (GIL)       | Mean: 0.449 s | Std Dev: 0.005 s
Multiprocessing       | Mean: 0.291 s | Std Dev: 0.011 s
```

These results demonstrate that:

- For prime counting, `threading` shows no real improvement over single-threaded, while `multiprocessing` shows a clear ~3x speedup since each process runs on its own interpreter with its own GIL.

- For factorial, sequential (chunked) and `threading` are essentially identical. In contrast, `multiprocessing` improves meaningfully on both since it is the only approach among the three that achieves genuine parallel execution.

It is important to highlight that, when adopting a naive, unchunked single-threaded approach as the baseline, `threading` would give a significant speedup that is inconsistent with the actual behavior of the GIL. Splitting the factorial computation into smaller partial products and merging them is algorithmically cheaper than one long, ever-growing accumulation, independent of concurrency. That is why this benchmark compares factorial's `threading` and `multiprocessing` runs only against the chunked-sequential baseline, not the naive one.

**The takeaway:** when interpreting a concurrency benchmark, always check whether splitting the work changed *how much* work there is, not just *who* does it. Otherwise, there is a risk of mistaking an algorithmic improvement for a concurrency one.

## 🤝 Contributing

Contributions are welcome! Fork this repository and submit a pull request 🚀

## 📜 License

This project is licensed under the [MIT License](LICENSE).
