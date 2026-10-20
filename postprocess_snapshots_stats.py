#!/usr/bin/env python3
import argparse
import csv
import glob
import os
import re
import time
import numpy as np

def timestep_from_name(path):
    m = re.search(r"snapshot_(\d+)\.dat$", os.path.basename(path))
    if not m:
        return None
    return int(m.group(1))

def compute_stats(snapshot_path):
    # columns: x y z p
    data = np.loadtxt(snapshot_path)
    p = data[:, 3].astype(np.float64)

    pmin = float(np.min(p))
    pmax = float(np.max(p))
    mean = float(np.mean(p))
    var  = float(np.var(p)) # population variance (same as our in-situ formula)
    energy = float(np.sum(p * p)) # sum p^2

    return pmin, pmax, mean, var, energy

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshots", default="snapshots", help="Snapshots folder")
    ap.add_argument("--out", default="pressure_adhoc_stats.csv", help="Output CSV")
    ap.add_argument("--dt", type=float, default=0.001, help="dt used in simulation (for time_s column)")
    ap.add_argument("--pattern", default="snapshot_*.dat", help="Filename pattern")
    args = ap.parse_args()

    t0 = time.perf_counter()

    files = sorted(glob.glob(os.path.join(args.snapshots, args.pattern)))
    files = [(f, timestep_from_name(f)) for f in files]
    files = [(f, ts) for (f, ts) in files if ts is not None]
    files.sort(key=lambda x: x[1])

    if not files:
        raise SystemExit(f"No snapshots found in {args.snapshots} matching {args.pattern}")

    with open(args.out, "w", newline="") as fout:
        w = csv.writer(fout)
        w.writerow(["timestep", "time_s", "min_p", "max_p", "mean_p", "var_p", "energy_sum_p2"])

        for fpath, ts in files:
            pmin, pmax, mean, var, energy = compute_stats(fpath)
            time_s = ts * args.dt
            w.writerow([ts, f"{time_s:.6f}", f"{pmin:.6f}", f"{pmax:.6f}", f"{mean:.6f}", f"{var:.6f}", f"{energy:.6f}"])

    t1 = time.perf_counter()
    elapsed = t1 - t0
    print(f"Postprocess done: wrote {args.out}")
    print(f"Postprocess_time_s: {elapsed:.6f}")

if __name__ == "__main__":
    main()