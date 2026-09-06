from vcdvcd import VCDVCD

vcd = VCDVCD('sim_trace.vcd')

# Filters for AXI4 & APB bus signals under the RISC-V IOMMU hierarchy
relevant_keywords = ['araddr', 'arvalid', 'arready', 'rvalid', 'awaddr', 'awvalid', 'bvalid', 'paddr']
matching_signals = [sig for sig in vcd.signals if 'i_riscv_iommu' in sig and any(kw in sig.lower() for kw in relevant_keywords)]

print("Matched IOMMU Bus Signals:")
for sig in sorted(matching_signals):
    print(f"  {sig}")