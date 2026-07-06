# poroelastic_solver

A finite-difference solver, in Rust, for the quasi-static linear Biot
poroelasticity equations used in:

> Zhai, G., Shirzaei, M., Manga, M. & Chen, X. (2019). *Pore-pressure
> diffusion, enhanced by poroelastic stresses, controls induced seismicity
> in Oklahoma.* PNAS 116(33), 16228-16233.

## Governing equations

Displacement field `u(x, t)` and pore pressure `p(x, t)` satisfy (paper's
Eqs. 1-2, Methods):

```
G*Laplacian(u) + G/(1-2*nu)*grad(div(u)) - alpha*grad(p) = f(x, t)          (1)
(1/Q)*dp/dt + alpha*d(div(u))/dt - div(chi*grad(p)) = q(x, t)               (2)
```

`G` is the shear modulus, `nu` the drained Poisson ratio, `alpha` the Biot
coefficient, `Q` the Biot modulus, and `chi` the mobility coefficient
(intrinsic permeability / fluid viscosity). Given 5 independent parameters
(`G`, `nu`, undrained Poisson ratio `nu_u`, Skempton coefficient `B`, and
hydraulic diffusivity `D`), `alpha`, `Q` and `chi` are computed with the
closed-form relations of Wang & Kumpel (2003) — see
[`src/param.rs`](src/param.rs).

## Domain and boundary conditions

The medium is homogeneous and isotropic, occupying a rectangular box that
approximates a half-space (`z` increases with depth, `z = 0` is the ground
surface):

- **z = 0 (free surface):** zero traction (`sigma_xz = sigma_yz = sigma_zz
  = 0`) and drained pore pressure (`p = 0`), matching the paper's
  half-space boundary condition.
- **All other faces (far field):** fixed zero displacement and no-flow
  (zero pressure gradient). This truncates the half-space, so the domain
  should be sized comfortably larger than the diffusion length
  `sqrt(D * t_max)` reached during a run, or the far-field approximation
  will visibly affect the solution.

The medium itself is a single homogeneous layer (unlike the paper's layered
Earth model) — see "Limitations" below.

## Numerics

- **Spatial discretization:** second-order central finite differences on a
  uniform structured grid ([`src/grid.rs`](src/grid.rs),
  [`src/field.rs`](src/field.rs)). The free-surface traction condition is
  imposed through an explicit ghost-node relation derived from
  `sigma_xz = sigma_yz = sigma_zz = 0` ([`src/elasticity.rs`](src/elasticity.rs)).
- **Time discretization:** backward Euler for the diffusion equation
  ([`src/diffusion.rs`](src/diffusion.rs)) — unconditionally stable, so
  `dt` is a resolution choice, not a stability constraint.
- **Coupling:** a Picard (block Gauss-Seidel) iteration alternates between
  the elasticity and diffusion solves each time step until the pressure
  iterate stops changing ([`src/coupling.rs`](src/coupling.rs)). This is
  simpler than the "fixed-stress split" scheme common in the poromechanics
  literature; it converges readily for the coupling strengths typical of
  crustal rock properties, at some cost in iteration count.
- **Linear solvers** ([`src/linalg.rs`](src/linalg.rs)): matrix-free
  (stencil-applied, never assembled) conjugate gradient for the
  diffusion operator (symmetric positive definite by construction) and
  BiCGSTAB for the elasticity operator (whose free-surface ghost stencil
  is not guaranteed to be exactly matrix-symmetric).
- **Source term** ([`src/source.rs`](src/source.rs)): an injection well is
  represented as a Gaussian-smoothed point source with a piecewise-constant
  rate schedule (a true delta function isn't representable on a finite
  grid).

## Running the example

```
cargo run --release
```

Simulates constant-rate fluid injection at 3 km depth in a 6 km cube for 60
days, printing pressure and surface-uplift time series, and writes:

- `injection_timeseries.csv` — pressure and displacement history at a few
  monitoring points.
- `final_field.vtk` — the full 3D pressure and displacement fields at the
  final time step (legacy VTK, open with ParaView).

## Tests

```
cargo test --release
```

- [`tests/elasticity_mms.rs`](tests/elasticity_mms.rs): a method-of-
  manufactured-solutions check — a quadratic displacement field is
  reproduced exactly (to floating-point precision) by the interior stencil,
  validating the hand-derived Navier-Cauchy coefficients independently of
  boundary treatment.
- [`tests/diffusion_point_source.rs`](tests/diffusion_point_source.rs):
  compares the diffusion solver against the classical analytical solution
  for a continuous point source in an infinite medium (Carslaw & Jaeger),
  to within the expected discretization/domain-truncation error.

## Limitations

- Single homogeneous layer, not the paper's layered Earth model.
- Far-field boundaries are a truncation approximation, not a true
  half-space (no absorbing/infinite boundary).
- The Picard coupling iteration is simple and robust but not the fastest
  option available (fixed-stress split with a stabilization term
  would converge faster for strongly coupled media).
- No Coulomb-stress or seismicity-rate modeling (Eq. 3 of the paper) — this
  crate solves the poroelastic PDE system only.
