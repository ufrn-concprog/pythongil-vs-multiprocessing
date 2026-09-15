# Threading vs. Multiprocessing Under the GIL in Python

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/downloads/)
![Build](https://img.shields.io/badge/build-manual-lightgrey)

This benchmark compares single-threaded execution, `threading`, and `multiprocessing` on the same CPU-bound task, to demonstrate empirically how Python's Global Interpreter Lock (GIL) limits threading's benefit for CPU-bound work, and why `multiprocessing` is the standard workaround.

This project is part of the Concurrent Programming module at the [Federal University of Rio Grande do Norte (UFRN)](https://www.ufrn.br), Natal, Brazil.

## 📃 Description

All three approaches run the same task: counting prime numbers in a range, split into equal chunks across workers where applicable. The task is deliberately CPU-bound (a plain nested loop, no I/O, no sleeping). The GIL specifically serializes execution of Python bytecode, and is released during I/O or sleep, so a task involving either of those would not demonstrate its effect.

Each approach is run 5 times, and the mean and standard deviation of the elapsed time are reported:

1. **Single-threaded** — the task runs once, with no concurrency, as a baseline.
2. **Threading** — the task is split across a number of threads equal to the number of logical CPUs available. On the standard (GIL-enabled) Python build, expect little to no speedup over the baseline as the GIL allows only one thread to execute Python bytecode at a time.
3. **Multiprocessing** — the task is split the same way, but across separate processes instead of threads. Each process has its own interpreter and its own GIL, so this can provide a meaningful speedup when the workload is large enough to outweigh process-management overhead.

**Note:** this benchmark uses the standard Python build. Python 3.13+ also supports an experimental, separately-installed *free-threaded* build (`3.13t`/`3.14t`, per [PEP 703](https://peps.python.org/pep-0703/)) that can remove the GIL entirely. However, as of Python 3.14, that build is officially supported and still opt-in, not the default, and is not used in this benchmark.

## 📂 Repository Structure

```text
.
├── src/                 # Example source code
│   ├── benchmarks.py    # The three benchmark runners and the repeated-run/statistics helper
│   ├── main.py          # Entry point: runs all three benchmarks and prints results
│   ├── README.md        # This documentation
│   └── tasks.py         # Prime-counting task and range-splitting helper
└── README.md            # Project overview
```

## 🚀 Getting Started

### ✅ Prerequisites

- [Python 3.9+](https://www.python.org)

Install [pdoc](https://pdoc.dev) only if you want to regenerate the HTML documentation:

```bash
python3 -m pip install pdoc
```

## ▶️ Running

```bash
python3 src/main.py
```

`UPPER_BOUND` (the range searched for primes) and `RUNS` (number of repeated runs) are constants at the top of `[src/main.py`](src/main.py). Adjust `UPPER_BOUND` if the single-threaded baseline runs too quickly or too slowly to clearly show the differences on the machine.

### Expected output

```text
Counting primes up to 200000, using <logical CPU count> workers where applicable

Single-threaded    | Mean: 1.842 s | Std Dev: 0.031 s
Threading (GIL)    | Mean: 1.897 s | Std Dev: 0.045 s
Multiprocessing    | Mean: 0.312 s | Std Dev: 0.028 s
```

`threading` is expected to land close to (or slightly worse than) the single-threaded baseline, despite using multiple threads, as the extra time reflects thread-creation and context-switching overhead with no real parallel benefit on CPU-bound work. `multiprocessing` is expected to show a clear speedup, since each process runs on its own interpreter and its own GIL.

If the machine has few CPU cores, or `UPPER_BOUND` is set too low, `multiprocessing`'s process-startup overhead can outweigh its benefit, making it look worse than `threading`. This is a real and explainable result (overhead dominating a small workload) rather than a bug. Try increasing `UPPER_BOUND` if the expected speedup is not seen.

### 🗒️ Generating Documentation

The documentation can be generated with [`pdoc`](https://pdoc.dev). From the repository root, render it as HTML with:

```bash
pdoc ./src -o ./doc
```

This generates documentation for the source files in [`src`](src) under a new [`doc`](doc) directory. To preview the documentation with a local server and reload it as source files change, run:

```bash
pdoc ./src
```

Next, open the localhost URL printed by `pdoc` in a browser. The generated landing page will be available at [`doc/index.html`](doc/index.html) after the HTML build command completes.

## 🤝 Contributing

Contributions are welcome! Fork this repository and submit a pull request 🚀
