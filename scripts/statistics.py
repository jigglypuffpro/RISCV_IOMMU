import sys
import json
import statistics
import os

def calculate_stats(data, name):
    if not data:
        return f"{name:<25} 0     -       -       -       -       -"
    
    n = len(data)
    mean = statistics.mean(data)
    median = statistics.median(data)
    p90 = sorted(data)[int(n * 0.90)] if n > 0 else 0
    p95 = sorted(data)[int(n * 0.95)] if n > 0 else 0
    p99 = sorted(data)[int(n * 0.99)] if n > 0 else 0
    max_val = max(data)
    
    return f"{name:<25} {n:<5} {mean:<7.1f} {median:<7.1f} {p95:<7.1f} {p99:<7.1f} {max_val:<7.1f}"

def generate_stats(json_file):
    try:
        with open(json_file, 'r') as f:
            reqs = json.load(f)
    except Exception as e:
        print(f"Failed to load {json_file}: {e}")
        return

    # Filter out requests with no latency (e.g. unfinished)
    valid_reqs = [r for r in reqs if r.get('latency_cycles') is not None]

    all_lats = [r['latency_cycles'] for r in valid_reqs]
    hit_lats = [r['latency_cycles'] for r in valid_reqs if r['iotlb_hit'] == 'YES' or r['iotlb_miss'] == 'NO']
    miss_lats = [r['latency_cycles'] for r in valid_reqs if r['iotlb_miss'] == 'YES']
    ddt_lats = [r['latency_cycles'] for r in valid_reqs if r['ddt_walk'] == 'YES']
    ptw_s1_lats = [r['latency_cycles'] for r in valid_reqs if r['s1_ptw'] == 'YES']
    ptw_s2_lats = [r['latency_cycles'] for r in valid_reqs if r['s2_ptw'] == 'YES']
    succ_lats = [r['latency_cycles'] for r in valid_reqs if r['success'] == 'YES']
    fail_lats = [r['latency_cycles'] for r in valid_reqs if r['success'] == 'NO']

    print("TempoIOMMU-RV Latency Statistics")
    print()
    print(f"{'Category':<25} {'N':<5} {'Mean':<7} {'P50':<7} {'P95':<7} {'P99':<7} {'Max':<7}")
    print("-" * 65)
    print(calculate_stats(hit_lats, "IOTLB hit"))
    print(calculate_stats(miss_lats, "IOTLB miss"))
    print(calculate_stats(ddt_lats, "DDT walk"))
    print(calculate_stats(ptw_s1_lats, "Stage-1 PTW"))
    print(calculate_stats(ptw_s2_lats, "Stage-2 PTW"))
    print(calculate_stats(succ_lats, "Successful"))
    print(calculate_stats(fail_lats, "Failed"))
    print(calculate_stats(all_lats, "All translations"))

if __name__ == '__main__':
    json_path = sys.argv[1] if len(sys.argv) > 1 else 'results/translation_trace.json'
    generate_stats(json_path)
