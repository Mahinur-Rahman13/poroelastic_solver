import csv
import matplotlib.pyplot as plt

r, num, ana = [], [], []
with open("diffusion_validation.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        r.append(float(row["r_m"]))
        num.append(float(row["numerical_Pa"]))
        ana.append(float(row["analytical_Pa"]))

fig, ax = plt.subplots(figsize=(7, 5))
ax.plot(r, ana, "-", color="black", linewidth=2, label="Analytical (Carslaw & Jaeger)")
ax.plot(r, num, "o", color="crimson", markersize=8, label="Rust FD solver (this project)")
ax.set_xlabel("Distance from injection point, r [m]")
ax.set_ylabel("Excess pore pressure, p [Pa]")
ax.set_title("Diffusion module validation\ncontinuous point source, t = 1200 s")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig("plot1_diffusion_analytical.png", dpi=150)
print("wrote plot1_diffusion_analytical.png")
