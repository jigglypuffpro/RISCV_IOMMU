import sys
from vcdvcd import VCDVCD

def analyze_iommu_dma(vcd_path):
    print(f"Loading {vcd_path}...")
    vcd = VCDVCD(vcd_path)

    # 1. Target key translation signals
    spaddr_sig = "TOP.lint_checks.i_riscv_iommu.i_rv_iommu_translation_wrapper.spaddr_o[55:0]"
    cdw_req_sig = "TOP.lint_checks.i_riscv_iommu.i_rv_iommu_translation_wrapper.cdw_axi_req_o[280:0]"

    # Search for active request/valid/ready signals (excluding static UPPERCASE parameters)
    tw_prefix = "TOP.lint_checks.i_riscv_iommu.i_rv_iommu_translation_wrapper"
    handshake_signals = [
        s for s in vcd.signals 
        if s.startswith(tw_prefix) 
        and any(kw in s.lower() for kw in ['valid', 'req', 'rdy', 'ready', 'vld']) 
        and not any(p in s for p in ['ENTRIES', 'WIDTH', 'MSITrans'])
    ]

    print("\n[+] Active Translation Handshake Signals Found:")
    for sig in sorted(handshake_signals):
        print(f"  {sig}")

    # 2. Track Physical Address (SPA) Updates and PTW Activity
    print("\n[+] Output Physical Address (spaddr_o) Transitions:")
    if spaddr_sig in vcd.signals:
        spaddr_tv = vcd[spaddr_sig].tv
        valid_transitions = [
            (t, val) for t, val in spaddr_tv 
            if val not in ('x', 'z') and int(val, 2) != 0
        ]
        
        print(f"{'TIME (ps)':<14} | {'TRANSLATED SPA (HEX)':<22} | {'NOTES'}")
        print("-" * 55)
        for time, val in valid_transitions[:20]:  # Print first 20 transitions
            hex_val = hex(int(val, 2))
            print(f"{time:<14} | {hex_val:<22} | Translated Output")
    else:
        print(f"Signal {spaddr_sig} not present in VCD trace.")

    # 3. Track Command Worker / Page Table Walker AXI Bus Assertions
    print("\n[+] Page Table Walk / Command Fetch Assertions (cdw_axi_req_o):")
    if cdw_req_sig in vcd.signals:
        cdw_tv = vcd[cdw_req_sig].tv
        active_reqs = [(t, val) for t, val in cdw_tv if val not in ('x', 'z') and int(val, 2) != 0]
        print(f"Total PTW/CDW AXI Request Events Detected: {len(active_reqs)}")
        for time, _ in active_reqs[:10]:
            print(f"  Request active at: {time} ps")
    else:
        print(f"Signal {cdw_req_sig} not present in VCD trace.")

if __name__ == '__main__':
    vcd_file = sys.argv[1] if len(sys.argv) > 1 else 'sim_trace.vcd'
    analyze_iommu_dma(vcd_file)