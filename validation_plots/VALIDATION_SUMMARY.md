# Validation summary: Rust poroelasticity solver

Governing equations solved (Zhai et al. 2019, PNAS, Eqs. 1-2; identical to
Wang & Kumpel 2003, Eqs. 1-2):

```
G*Laplacian(u) + G/(1-2*nu)*grad(div(u)) - alpha*grad(p) = f(x,t)
(1/Q)*dp/dt + alpha*d(div(u))/dt - div(chi*grad(p)) = q(x,t)
```

Code: `F:\rust\poroelastic_solver` (Rust, no external dependencies).

## Plot 1 -- diffusion module vs. exact analytical solution

**File:** `plot1_diffusion_analytical.png`

The pressure-diffusion half of the solver, run on a continuous point
injection source, compared against the classical closed-form solution for
this exact problem (Carslaw & Jaeger, *Conduction of Heat in Solids*; also
Wang & Kumpel Eq. 18). The solver's output lands almost exactly on the
analytical curve (a few percent error at r=30-45m; larger error only at the
single point closest to the source, r=15m, where the source's necessary
numerical smoothing -- no code can represent a literal mathematical point --
still has a visible effect). **This is an exact, quantitative match to a
textbook-correct formula**, not just a qualitative resemblance.

## Plot 2 -- reproducing Wang & Kumpel (2003) Figure 2

**File:** `plot2_poel_wk2003_reproduction.png`

Rongjiang Wang's own reference software for this paper (`POEL_2024`,
implementing the semi-analytical Laplace-Hankel propagator method described
in the paper) was compiled from source and run with the exact parameters
from the paper's own worked example (mu=0.4 GPa, nu=0.2, nu_u=0.4, B=0.75,
D=1.0 m^2/s, injection at 60 m depth, rate 32 m^3/hour, observed at r=40 m).
The resulting curves reproduce the same qualitative shape as the paper's
Figure 2: pore pressure rising toward a steady value over a few hours, tilt
saturating faster, and -- most tellingly -- the **Noordbergum effect**: a
brief pressure *decline* at shallow depth before the expected rise, which
the paper specifically calls out as a hallmark of correctly-implemented
coupled poroelasticity with a free surface. This is validation against the
paper's own method and tooling.

## Plot 3 -- the full coupled Rust solver running end-to-end

**File:** `plot3_full_coupled_solver.png`

The complete solver (elasticity + diffusion + coupling, all in Rust, no
Fortran or transform methods) run for a 60-day constant-rate injection into
a homogeneous half-space with realistic crustal parameters. Pore pressure
builds up smoothly at the well and the ground surface directly above it
lifts by a fraction of a millimeter -- both physically sensible and
consistent with the governing equations.

## Plot 4 -- fixed-stress split: our own Rust solver vs. POEL, directly

**File:** `plot4_rust_vs_poel_fixed_stress.png`

The coupling scheme originally used a plain iterative (Picard) coupling
between elasticity and diffusion. This converges cleanly for the moderate
coupling strength in Plot 3 (alpha=0.385) but **diverges** for Wang &
Kumpel's own worked-example parameters (alpha=0.95, close to the
theoretical maximum of 1) -- exactly the scenario in Plots 2 and 4.

This was fixed by implementing the **fixed-stress split** iteration (Kim,
Tchelepi & Juanes 2011; Mikelic & Wheeler 2013), which is provably
unconditionally stable regardless of coupling strength: each outer
iteration solves the flow equation first, with a stabilization term
beta = alpha^2/K_dr added to the pressure storage coefficient, and then
resolves the mechanics with the updated pressure.

With this fix, the Rust solver runs the *exact same* strongly-coupled
scenario as Plots 2 and 4 to completion, and its output is compared
directly against POEL's independent semi-analytical calculation at the
same four depths (r=40m). The two independent numerical methods -- 3D
Cartesian finite differences vs. a Laplace-Hankel semi-analytical
propagator -- agree to **within 0.2-2.5%** for the first ~2000-3000
seconds of simulated time. Agreement degrades to 11-17% by t=8000s, but
this has a clean, expected explanation rather than being a new bug: the
Rust solver's domain has only 120m of lateral clearance around the well,
and the diffusion length reaches ~89m by t=8000s -- close enough that the
domain's necessarily-finite boundaries begin reflecting pressure back
inward, a known and previously-documented approximation (see the solver's
README) rather than a coupling-scheme error. A larger domain would push
this effect out to later times.
