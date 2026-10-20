import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def load_snapshot(path):
    data = np.loadtxt(path)
    x, y, z, p = data[:,0], data[:,1], data[:,2], data[:,3]
    return x, y, z, p

def plot_midplane_z(snapshot_path, out_png, title=""):
    x, y, z, p = load_snapshot(snapshot_path)

    z_unique = np.unique(z)
    z_mid = z_unique[len(z_unique)//2]
    mask = (z == z_mid)

    xs, ys, ps = x[mask], y[mask], p[mask]

    xg = np.unique(xs)
    yg = np.unique(ys)

    P = np.empty((len(yg), len(xg)), dtype=float)
    P[:] = np.nan

    xi = {v:i for i,v in enumerate(xg)}
    yi = {v:i for i,v in enumerate(yg)}
    for X, Y, val in zip(xs, ys, ps):
        P[yi[Y], xi[X]] = val

    plt.figure()
    plt.imshow(
        P,
        origin="lower",
        aspect="auto",
        extent=[xg.min(), xg.max(), yg.min(), yg.max()],
    )
    plt.colorbar(label="Pressure (Pa)")
    plt.xlabel("x (m)")
    plt.ylabel("y (m)")
    plt.title(title if title else f"{snapshot_path.name} (z={z_mid:.3f} m)")
    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.close()

if __name__ == "__main__":
    snap_dir = Path("snapshots")

    s1 = snap_dir / "snapshot_000200.dat"
    s2 = snap_dir / "snapshot_000800.dat"
    s3 = snap_dir / "snapshot_000500.dat"
    assert s1.exists(), f"Missing {s1}"
    assert s2.exists(), f"Missing {s2}"
    assert s3.exists(), f"Missing {s3}"

    plot_midplane_z(s1, "pressure_t1.png", title="Pressure field (early time)")
    plot_midplane_z(s3, "pressure_t3.png", title="Pressure field (mid time)")
    plot_midplane_z(s2, "pressure_t2.png", title="Pressure field (later time)")

    print("Wrote: pressure_t1.png, pressure_t2.png ...")