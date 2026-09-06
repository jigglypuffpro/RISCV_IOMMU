# Experiment 1: IOTLB Capacity Thrashing

## Theoretical Background
In IOMMUs (such as the ARM SMMU or the RISC-V IOMMU), the I/O Translation Lookaside Buffer (IOTLB) caches recently used page translations to avoid expensive multi-cycle Page Table Walks (PTWs) to main memory.

When a device streams data sequentially or accesses a working set of memory that fits entirely within the IOTLB (the "fast path"), latency is typically very low (e.g., 2 cycles). 

However, if a device generates interleaved requests across a working set of $N+1$ unique pages (where $N$ is the maximum number of entries in the IOTLB), the IOMMU's cache replacement policy (typically LRU or FIFO) will begin to thrash. Every new request will cause a cache miss and evict the oldest entry. By the time the device loops back to the first page, its translation will have been evicted. This drops the hit rate to 0%, penalizing every transaction with the full PTW latency.

## Setup
- **Target IP**: `riscv_iommu` (TempoIOMMU-RV)
- **IOTLB Capacity** (`IOTLB_ENTRIES`): Set to `16` in `riscv_iommu.sv`.
- **Working Set**: $N+1 = 17$ unique 4KB pages allocated to Device 10.
- **Test Pattern**: The testbench issues 17 sequential translation requests, followed by the exact same 17 sequential translation requests again, for a total of 34 requests.

## Expected Behavior
- **Pass 1 (Requests 0-16)**: All 17 requests will encounter a cold IOTLB miss and trigger a PTW. (Hit rate: 0%).
- **Pass 2 (Requests 17-33)**: Because the working set (17) > cache capacity (16), the translation needed for the 18th request (the first request of pass 2) was evicted when the 17th request came in. Thus, all 17 requests on the second pass will *also* miss. (Hit rate: 0%).

## Results
The experiment successfully validated the contention model:
- **Total Requests**: 34
- **IOTLB Hits**: 0
- **IOTLB Misses**: 34
- **Average Latency**: 15.4 cycles (PTW bound)

By demonstrating that the fully-associative cache drops instantly to a 0% hit rate when the working set exceeds capacity by exactly 1, we established a baseline for how unoptimized caching policies react to interleaved peripheral traffic patterns.
