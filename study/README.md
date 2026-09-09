# TempoIOMMU-RV Study & Research Notes

This directory contains documentation, theoretical background, experimental setups, and empirical findings for micro-architectural contention modeling performed on the RISC-V IOMMU implementation (`TempoIOMMU-RV`).

These experiments are modeled after real-world IOMMU performance bottlenecks and non-deterministic latency phenomena analyzed in high-performance system research (such as the ARM SMMU architecture study).

---

## Documentation

* [Simulation Workflow & Methodology](Simulation_Workflow.md): A high-level guide on how hardware/testbench parameters are configured, and the execution flow from Verilator compilation to trace parsing and plotting.

---

## Table of Contents & Experiment Overview

### 1. [Experiment 1: IOTLB Capacity Thrashing](IOTLB_Capacity_Thrashing.md)
* **Focus**: Page Table Translation Cache Thrashing (Micro-benchmark).
* **Mechanism**: Evaluating IOTLB behavior when an I/O device working set ($N + 1$ pages) exceeds the physical capacity of the IOTLB ($N = 16$).
* **Key Finding**: Working set overflow drops the IOTLB hit rate to 0%, causing 100% cyclic capacity misses and increasing request latency from 2 cycles (hit path) to 15 cycles (PTW penalty).

---

### 2. [Experiment 2: Multi-Device Context Contention](Multi_Device_Contention.md)
* **Focus**: Device Directory Table Cache (DDTC) thrashing under multi-tenant I/O workloads (`interf_tbu` analog).
* **Mechanism**: Interleaving DMA translation requests across 5 active virtual devices (`device_id` = 10, 20, 30, 40, 50) when the DDTC capacity is constrained ($N = 4$).
* **Key Finding**: Even with a **96.6% IOTLB page hit rate**, concurrent device context evictions force a 14-cycle Device Directory Walk on 100% of transactions. Proves that DDTC sizing is a critical bottleneck in multi-tenant SoCs.

---

### 3. [Experiment 3: Interconnect Memory Contention](Interconnect_Memory_Contention.md)
* **Focus**: Impact of System Interconnect Latency & Congestion on IOMMU walks.
* **Mechanism**: Injecting periodic 30-cycle AXI interconnect burst stalls on the memory slave interface during Device Directory and Page Table walks.
* **Key Finding**: Interconnect congestion causes non-deterministic execution spikes: DDT walk latencies stretch from 14 to 44 cycles, and cold miss latencies jump to 57 cycles, illustrating extreme latency tail inflation under shared bus pressure.

---

## Summary Matrix

| Experiment | Metric Evaluated | Baseline Latency | Contended / Thrashing Latency | Critical Takeaway |
| :--- | :--- | :--- | :--- | :--- |
| **Exp 1: IOTLB Thrashing** | Page Translation Hit Rate | 2 cycles (Hit) | 15 cycles (Miss) | $N+1$ page working sets drop hit rate to 0%. |
| **Exp 2: Multi-Device Contention** | DDTC Context Cache Evictions | 2 cycles (Hit path) | 14 cycles (DDT Walk) | Context thrashing penalizes transactions despite IOTLB hits. |
| **Exp 3: Interconnect Stalls** | Memory Bus Latency Variance | 14 cycles (DDT Walk) | 44 - 57 cycles (Stalled Walk) | Interconnect congestion inflates tail latencies exponentially. |
