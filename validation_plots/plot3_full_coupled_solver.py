import csv
import matplotlib.pyplot as plt

t, p_well, uz = [], [], []
with open("../poroelastic_solver/injection_timeseries.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        t.append(float(row["time_days"]))
        p_well.append(float(row["p_at_well_Pa"]))
        uz.append(-float(row["uz_surface_above_well_m"]) * 1000.0)  # -uz: uplift positive, m -> mm

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].plot(t, p_well, color="crimson")
axes[0].set_xlabel("Time [days]")
axes[0].set_ylabel("Pore pressure at injection point [Pa]")
axes[0].set_title("Pore pressure buildup at the well")
axes[0].grid(alpha=0.3)

axes[1].plot(t, uz, color="steelblue")
axes[1].set_xlabel("Time [days]")
axes[1].set_ylabel("Surface uplift [mm]")
axes[1].set_title("Ground-surface uplift above the well")
axes[1].grid(alpha=0.3)

fig.suptitle("Full coupled Rust solver: 60-day constant-rate injection, homogeneous half-space\n"
             "(G=20 GPa, nu=0.25, nu_u=0.30, B=0.6, D=1.5 m^2/s -- moderate coupling, alpha=0.385)")
fig.tight_layout()
fig.savefig("plot3_full_coupled_solver.png", dpi=150)
print("wrote plot3_full_coupled_solver.png")
