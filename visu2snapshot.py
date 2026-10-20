import argparse
import re
from pathlib import Path
import math

import numpy as np
import matplotlib.pyplot as plt


def timestep_from_name(p: Path) -> int:
    m = re.search(r"snapshot_(\d+)\.dat$", p.name)
    return int(m.group(1)) if m else -1


def load_snapshot(path: Path):
    data = np.loadtxt(path)
    if data.ndim != 2 or data.shape[1] < 4:
        raise ValueError(f"Invalid format: {path}")
    x, y, z, p = data[:, 0], data[:, 1], data[:, 2], data[:, 3]
    return x, y, z, p


def extract_xy_slice(x, y, z, p):
    """Take the slice at the median z (ez=1)."""
    z0 = np.median(z)
    mask = np.isclose(z, z0, atol=1e-8)
    if mask.sum() < 10:
        mask = np.isclose(z, z0, atol=1e-3)
    return x[mask], y[mask], p[mask]


def main():
    ap = argparse.ArgumentParser(
        description="Display ALL snapshots of a folder with a common color scale"
    )
    ap.add_argument("folder", help="Folder containing snapshot_*.dat")
    ap.add_argument("--cols", type=int, default=4, help="Number of columns in the grid")
    args = ap.parse_args()

    folder = Path(args.folder)
    if not folder.exists():
        raise SystemExit(f"Folder not found: {folder}")

    snaps = sorted(folder.glob("snapshot_*.dat"), key=timestep_from_name)
    if len(snaps) == 0:
        raise SystemExit(f"No snapshot found in {folder}")

    print(f"Loading {len(snaps)} snapshots...")

    # Load all snapshots
    slices = []
    p_min, p_max = float("inf"), float("-inf")

    for s in snaps:
        x, y, z, p = load_snapshot(s)
        xs, ys, ps = extract_xy_slice(x, y, z, p)
        slices.append((xs, ys, ps, s))
        p_min = min(p_min, ps.min())
        p_max = max(p_max, ps.max())

    print(f"Global pressure range: min={p_min:.3e}, max={p_max:.3e}")

    # Plot grid
    n = len(slices)
    cols = args.cols
    rows = math.ceil(n / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 4 * rows), squeeze=False)

    for idx, (xs, ys, ps, s) in enumerate(slices):
        r = idx // cols
        c = idx % cols
        ax = axes[r][c]

        t = timestep_from_name(s)
        sc = ax.scatter(xs, ys, c=ps, s=6, vmin=p_min, vmax=p_max)
        ax.set_title(f"t = {t}")
        ax.set_xlabel("x")
        ax.set_ylabel("y")

    # Disable empty axes
    for idx in range(n, rows * cols):
        r = idx // cols
        c = idx % cols
        axes[r][c].axis("off")

    # Common colorbar
    cbar = fig.colorbar(sc, ax=axes.ravel().tolist(), shrink=0.8)
    cbar.set_label("Pressure")

    plt.suptitle(f"Snapshots — {folder.name}", fontsize=14)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()