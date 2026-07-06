import csv
import numpy as np
import matplotlib.pyplot as plt

t_rust, p_rust = [], {0: [], 1: [], 2: [], 3: []}
with open("rust_solver_wk2003.csv") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        t_rust.append(float(row[0]) / 3600.0)  # s -> h
        for i in range(4):
            p_rust[i].append(float(row[i + 1]) / 1000.0)  # Pa -> kPa

poel = np.loadtxt("wk2003_pp.dat", skiprows=1)
t_poel, p_poel = poel[:, 0] / 3600.0, poel[:, 1:5] / 1000.0

depths = ["z = 5 m", "z = 15 m", "z = 45 m", "z = 75 m"]
ylims = [(-0.5, 6), (-0.5, 6), (0, 9), (0, 9)]

fig, axes = plt.subplots(4, 1, figsize=(4.2, 11), sharex=True)
for i, (ax, label, ylim) in enumerate(zip(axes, depths, ylims)):
    ax.plot(t_poel, p_poel[:, i], "-", color="black", linewidth=1.8, label="POEL2024 (paper's method)")
    ax.plot(t_rust, p_rust[i], "o", color="crimson", markersize=3.5, label="Our Rust FD solver")
    ax.text(0.04, 0.90, label, fontsize=13, fontweight="bold", transform=ax.transAxes,
            va="top", ha="left", bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=2))
    ax.set_ylabel("kPa")
    ax.set_ylim(*ylim)
    ax.set_xlim(0, 6)
    ax.grid(alpha=0.3)
    if i == 0:
        ax.legend(loc="upper right", fontsize=8, framealpha=0.9)

axes[-1].set_xlabel("Time [h]")
fig.suptitle("Our Rust solver (dots)\nvs. paper's method (line)", fontsize=13)
fig.tight_layout()
fig.savefig("plot5_paper_style_match.png", dpi=150)
print("wrote plot5_paper_style_match.png")
