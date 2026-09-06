import sys
from vcdvcd import VCDVCD

def analyze_vcd(vcd_path):
    print(f"Loading {vcd_path}...")
    vcd = VCDVCD(vcd_path)

    # ---------------------------------------------------------
    # 1. Analyze Software MMIO / Programming Interface Latency
    # ---------------------------------------------------------
    prog_araddr  = "TOP.lint_checks.i_riscv_iommu.i_rv_iommu_prog_if.i_axi2apb_64_32_iommu.ARADDR[63:0]"
    prog_arvalid = "TOP.lint_checks.i_riscv_iommu.i_rv_iommu_prog_if.i_axi2apb_64_32_iommu.ARVALID"
    prog_rvalid  = "TOP.lint_checks.i_riscv_iommu.i_rv_iommu_prog_if.i_axi2apb_64_32_iommu.RVALID"

    print("\n[+] MMIO Register Access Latency (Programming Interface):")
    if all(s in vcd.signals for s in [prog_araddr, prog_arvalid, prog_rvalid]):
        ar_valid = vcd[prog_arvalid]
        ar_addr  = vcd[prog_araddr]
        r_valid  = vcd[prog_rvalid]

        pending_reads = []
        r_valid_times = [t for t, val in r_valid.tv if val == '1']

        for time, val in ar_valid.tv:
            if val == '1':
                addr_val = next((a_val for a_time, a_val in reversed(ar_addr.tv) if a_time <= time and a_val not in ('x', 'z')), '0')
                addr_hex = hex(int(addr_val, 2)) if addr_val.isdigit() else addr_val
                pending_reads.append({'start': time, 'addr': addr_hex})

        print(f"{'START (ps)':<12} | {'END (ps)':<12} | {'REGISTER ADDR':<18} | {'LATENCY (ps)':<12}")
        print("-" * 60)
        for req in pending_reads:
            resp_time = next((rt for rt in r_valid_times if rt >= req['start']), None)
            if resp_time:
                latency = resp_time - req['start']
                print(f"{req['start']:<12} | {resp_time:<12} | {req['addr']:<18} | {latency:<12}")
    else:
        print("MMIO programming signals not fully resolved in VCD.")

    # ---------------------------------------------------------
    # 2. Discover Inbound DMA Request & Latency Signals
    # ---------------------------------------------------------
    print("\n[+] Scanning for Inbound DMA Request/Valid signals in Translation Wrapper:")
    tw_signals = [s for s in vcd.signals if 'i_rv_iommu_translation_wrapper' in s]
    
    # Filter for potential handshakes (valid, req, ready, enable)
    req_signals = [s for s in tw_signals if any(kw in s.lower() for kw in ['req', 'valid', 'en', 'strobe']) and not 'bad_' in s.lower()]
    
    for sig in sorted(req_signals)[:15]:
        print(f"  {sig}")

if __name__ == '__main__':
    vcd_file = sys.argv[1] if len(sys.argv) > 1 else 'sim_trace.vcd'
    analyze_vcd(vcd_file)