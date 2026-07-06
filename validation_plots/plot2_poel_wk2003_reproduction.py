import numpy as np
import matplotlib.pyplot as plt

def load_poel(path):
    data = np.loadtxt(path, skiprows=1)
    return data[:, 0], data[:, 1:5]  # time, [z5, z15, z45, z75]

t_pp, pp = load_poel("wk2003_pp.dat")
t_tlt, tlt = load_poel("wk2003_tlt.dat")

depths = ["z = 5 m", "z = 15 m", "z = 45 m", "z = 75 m"]
colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax = axes[0]
for i, (label, c) in enumerate(zip(depths, colors)):
    ax.plot(t_pp / 3600.0, pp[:, i], label=label, color=c)
ax.axhline(0, color="gray", linewidth=0.8)
ax.set_xlabel("Time [h]")
ax.set_ylabel("Excess pore pressure [Pa]")
ax.set_title("Pore pressure at r = 40 m\n(reproducing Wang & Kumpel 2003, Fig. 2)")
ax.legend()
ax.grid(alpha=0.3)

# Annotate the Noordbergum effect (early transient pressure decline at
# shallow depth, before pore pressure diffusion catches up).
mask = t_pp < 600
if np.any(pp[mask, 0] < 0):
    idx = np.argmin(pp[:, 0][t_pp < 1000])
    ax.annotate(
        "Noordbergum effect\n(transient decline)",
        xy=(t_pp[idx] / 3600.0, pp[idx, 0]),
        xytext=(0.5, pp[idx, 0] - 30),
        fontsize=9,
        arrowprops=dict(arrowstyle="->", color="black"),
    )

ax = axes[1]
for i, (label, c) in enumerate(zip(depths, colors)):
    ax.plot(t_tlt / 3600.0, tlt[:, i] * 1e6, label=label, color=c)  # rad -> microrad
ax.axhline(0, color="gray", linewidth=0.8)
ax.set_xlabel("Time [h]")
ax.set_ylabel("Radial tilt [microrad]")
ax.set_title("Vertical tilt at r = 40 m")
ax.legend()
ax.grid(alpha=0.3)

fig.suptitle("POEL2024 (Wang's own reference code) reproducing the Wang & Kumpel (2003) test case")
fig.tight_layout()
fig.savefig("plot2_poel_wk2003_reproduction.png", dpi=150)
print("wrote plot2_poel_wk2003_reproduction.png")
