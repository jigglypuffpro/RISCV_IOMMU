# Experiment 2: Multi-Device Context Contention (interf_tbu Analog)

## Theoretical Background
In addition to caching page translations in the IOTLB, the RISC-V IOMMU also caches **Device Contexts** in the Device Directory Table Cache (DDTC). Device contexts contain essential attributes including the root Page Table Pointer (FSC) and process/domain identifiers (GSCID/PSCID).

When multiple devices attempt to perform DMA operations simultaneously, their transactions interleave. If the number of concurrently active devices exceeds the capacity of the DDTC, the devices will continuously evict each other's context entries from the cache.

This leads to a severe performance degradation where every transaction must suffer a Device Directory Walk (typically 14 cycles) to fetch the device context, *even if the target memory page translation is already cached in the IOTLB*.

## Setup
- **Target IP**: `riscv_iommu` (TempoIOMMU-RV)
- **DDTC Capacity**: We modified the instantiation parameters in `lint_checks.sv` to set `DDTC_ENTRIES = 4`.
- **Working Set**: 5 distinct devices (`device_id` = 10, 20, 30, 40, 50).
- **Test Pattern**: We programmed the testbench to issue 30 DMA requests in a round-robin interleaved fashion across the 5 devices. All devices request translations for the *exact same memory page* (IOVA `0x4000`).

## Results
The experiment successfully induced pure DDTC thrashing:
- **Total Requests**: 30
- **IOTLB Hit Rate**: 96.6% (29 hits, 1 cold miss)
- **DDT Walk Rate**: 100% (30 walks)
- **Average Latency**: 14.4 cycles

### Analysis
Because all 5 devices requested the same page and shared the same Process Context (`PSCID=0`), the translation for `0x4000` was successfully cached in the IOTLB on the very first request. Consequently, the IOTLB hit on every subsequent request (29 hits).

However, because the 5 devices were interleaved and the DDTC capacity is only 4 entries, the cache replacement policy (PLRU) continuously evicted the device contexts. 

The trace data perfectly illustrates this phenomenon:
```text
Request #21
------------------------------------------------------------
Device ID             : 10
IOVA                  : 0x0000000000004000
IOTLB                 : HIT
DDT walk              : YES
Latency               : 14 cycles
```

Even though the memory translation was instantly available in the IOTLB, the IOMMU *must* fetch the Device Context first to validate permissions and domain identity. Because the DDTC thrashed, every transaction suffered the 14-cycle DDT walk penalty. 

This experiment proves that optimizing the IOTLB capacity is insufficient if the DDTC size does not comfortably exceed the number of actively interleaving DMA agents in the SoC.
