# Algorithmic State-Machine Model for Discontinuous Lunisolar & Solar Calendrical Systems

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)

An open-source research implementation and empirical micro-benchmarking suite providing a deterministic finite-state automaton (FSA) formulation for non-synchronous solar sidereal and lunisolar calendrical frameworks—specifically **Bikram Sambat (BS)** and **Nepal Sambat (NS)**.

## Academic Abstract & Motivation
Conventional open-source implementations for South Asian civil calendars rely predominantly on static, memory-inefficient lookup arrays with bounded operational time horizons (typically 1970–2090). These solutions fail to model the underlying celestial state mechanics, introducing lookup failures and high relative memory overhead on resource-constrained embedded systems.

This repository implements:
1. **Nirayana Solar State Transition Engine:** Deterministically computes solar sidereal transit boundaries (*Sankranti*) and discrete month lengths (29–32 days) via continuous orbital coordinates.
2. **Lunisolar Phase Automaton:** Evaluates synodic lunar phases (*Tithis*) and detects intercalary leap cycles (*Adhik Maas / Malamas*) without empirical lookup tables.
3. **Benchmarking Suite:** Evaluates execution latency, memory footprint, and edge-case accuracy against status-quo table-lookup packages across $10^6$ continuous conversions.

## Project Structure
- `src/`: Core finite-state automaton implementations and orbital coordinate solvers.
- `benchmarks/`: Runtime profiling and memory overhead comparison against baseline array models.
- `data/`: Ground-truth historical civil dates verified against official gazette records (*Nepal Rajpatra*).
- `tests/`: Automated unit tests for edge-case transitions.

## Citation
If you utilize this codebase or algorithmic formulation in your research, please cite our corresponding manuscript:
```bibtex
@article{yourname2026calendrical,
  title={A Deterministic Finite-State Model and Benchmarking Suite for Discontinuous Lunisolar and Solar Calendrical Systems},
  author={Your Name and Co-Author Name},
  journal={arXiv preprint},
  year={2026}
}