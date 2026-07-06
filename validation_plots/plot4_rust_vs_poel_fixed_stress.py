import csv
import numpy as np
import matplotlib.pyplot as plt

t_rust, p_rust = [], {0: [], 1: [], 2: [], 3: []}
with open("rust_solver_wk2003.csv") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        t_rust.append(float(row[0]))
        for i in range(4):
            p_rust[i].append(float(row[i + 1]))

poel = np.loadtxt("wk2003_pp.dat", skiprows=1)
t_poel, p_poel = poel[:, 0], poel[:, 1:5]

depths = ["z = 5 m", "z = 15 m", "z = 45 m", "z = 75 m"]
colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

fig, ax = plt.subplots(figsize=(9, 6))
for i, (label, c) in enumerate(zip(depths, colors)):
    ax.plot(t_poel, p_poel[:, i], "-", color=c, linewidth=2, alpha=0.6, label=f"POEL (paper's method): {label}")
    ax.plot(t_rust, p_rust[i], "o", color=c, markersize=4, label=f"Rust FD (fixed-stress split): {label}")

ax.axvline(2000, color="gray", linestyle=":", linewidth=1)
ax.text(2100, ax.get_ylim()[1] * 0.93, "boundary effects\ngrow past here", fontsize=9, color="#333333",
        va="top", ha="left", bbox=dict(facecolor="white", edgecolor="gray", alpha=0.9, pad=3))
ax.set_xlabel("Time [s]")
ax.set_ylabel("Excess pore pressure [Pa]")
ax.set_title(
    "Independent verification: Rust FD solver (fixed-stress split) vs.\n"
    "POEL2024 (Wang & Kumpel's own semi-analytical method), r = 40 m"
)
ax.legend(fontsize=8, ncol=2)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("plot4_rust_vs_poel_fixed_stress.png", dpi=150)
print("wrote plot4_rust_vs_poel_fixed_stress.png")
