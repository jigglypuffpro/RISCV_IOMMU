# Experiment 3: Interconnect Memory Contention

## Theoretical Background
In standard simulations, memory responses from the testbench often arrive with fixed, minimal latencies (e.g., a static 3-cycle delay). However, in real-world Systems-on-Chip (SoCs), the AXI interconnect is shared among numerous high-bandwidth masters (e.g., GPUs, Network Interfaces, PCIe controllers).

When the IOMMU performs a Page Table Walk (PTW) or Device Directory Walk (DDT), it must fetch data structures from main memory. If the interconnect is heavily congested, the memory controller will stall the IOMMU's read requests. The ARM SMMU paper describes this phenomenon as "non-deterministic execution spikes", where contention drastically stretches walk latencies and introduces massive variance in completion times.

## Setup
- **Target IP**: `riscv_iommu` (TempoIOMMU-RV)
- **Workload**: The same Multi-Device DDTC thrashing sequence from Experiment 2 (5 interleaved devices forcing recurrent DDT walks).
- **Testbench Modification**: We upgraded the `DeterministicMemoryModel` in `tb_iommu.cpp` to simulate a congested interconnect. Instead of returning data after a flat 3 cycles, the memory model injects an artificial **30-cycle interconnect burst stall** into the pipeline for every 4th read request.

## Results
The experiment successfully replicated the severe latency spikes characteristic of memory contention:
- **Total Requests**: 30
- **Base DDT Walk Latency**: 14 cycles
- **Contended DDT Walk Latency**: 44 cycles
- **Cold Miss Latency (DDT + PTW)**: 57 cycles (up from 27 cycles in Exp 2)

### Analysis
The injected interconnect contention dramatically altered the latency profile. Compare the statistics from Experiment 2 (Uncontended) to Experiment 3 (Contended):

| Metric | Uncontended (Exp 2) | Contended (Exp 3) |
|--------|---------------------|-------------------|
| P50 Latency | 14 cycles | 14 cycles |
| P90 Latency | 14 cycles | **44 cycles** |
| Max Latency | 27 cycles | **57 cycles** |
| Std. Deviation | 2.3 | **14.2** |

As demonstrated by the massive jump in the P90 latency and the standard deviation, interconnect contention introduces severe non-determinism. 

The trace data captures these execution spikes flawlessly. For instance, Request #21 (Device 10) suffered a stall during its DDT walk:
```text
Request #21
------------------------------------------------------------
Device ID             : 10
IOVA                  : 0x0000000000004000
IOTLB                 : HIT
DDT walk              : YES
Latency               : 44 cycles
```

Even though the memory translation was already safely cached in the IOTLB (IOTLB: HIT), the required Device Context fetch suffered a 30-cycle stall on the AXI bus, stretching the transaction completion from 14 cycles to 44 cycles.

This validates the core premise of contention modeling: **The IOMMU's performance is strictly bound by the latency of the interconnect it resides on.** In congested SoCs, the IOMMU's internal PTW logic can stall the entire pipeline, severely degrading peripheral throughput.
