# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"F:\rust\poroelastic_solver\validation_plots\pptx_build")
from deckutil import *

PLOTS = r"F:\rust\poroelastic_solver\validation_plots"
FIGS = r"F:\rust\poroelastic_solver\validation_plots\paper_figs"

# Charcoal + Rust-orange palette (a Rust programmer's own study notes)
GRAPHITE = "232323"
SLATE = "3A3F44"
RUST = "CE422B"
RUST_DK = "9E3220"
BG = "FFFFFF"
PANEL = "F4F5F6"
INK = "1E2124"
MUTED = "6B7280"
CODE_BG = "1E1E1E"
CODE_FG = "D4D4D4"

prs = new_presentation()
SLIDE_COUNT = {"n": 0}  # filled at the end


def header(slide, kicker, title, kicker_color=RUST, title_color=INK):
    add_text(slide, kicker.upper(), 0.6, 0.35, 11, 0.32, size=12, bold=True, color=kicker_color)
    add_text(slide, title, 0.6, 0.65, 12.1, 0.7, size=25, bold=True, color=title_color, font="Cambria")


def loc_tag(slide, path):
    add_rect(slide, 0.6, 1.28, 6.6, 0.34, fill_color=PANEL, rounded=True)
    add_text(slide, f"📁  {path}", 0.78, 1.30, 6.3, 0.3, size=12, color=SLATE, font="Consolas", valign="middle")


def divider(prs, part_no, title, subtitle):
    s = add_slide(prs)
    set_background(s, GRAPHITE)
    add_text(s, f"PART {part_no}", 0.9, 2.9, 4, 0.4, size=15, bold=True, color=RUST)
    add_text(s, title, 0.9, 3.3, 11.5, 1.1, size=36, bold=True, color="FFFFFF", font="Cambria")
    add_text(s, subtitle, 0.9, 4.35, 10.5, 0.8, size=15, color="B9BEC3", line_spacing=1.3)
    return s


def content_slide(prs, kicker, title):
    s = add_slide(prs)
    set_background(s, BG)
    header(s, kicker, title)
    return s


pages = []  # track for page numbering at the end

# ================================================================ TITLE
s = add_slide(prs)
set_background(s, GRAPHITE)
add_text(s, "MY STUDY NOTES", 0.9, 2.1, 8, 0.4, size=14, bold=True, color=RUST)
add_text(s, "Building a Poroelasticity Solver in Rust", 0.9, 2.55, 11.5, 1.3, size=38, bold=True, color="FFFFFF", font="Cambria")
add_text(s,
         "Theory, numerical methods, the full workflow, and a block-by-block walkthrough of every\n"
         "file in the project — written so I can explain any part of this to my professor.",
         0.9, 3.8, 10.8, 1.0, size=14.5, color="C7CBCF", line_spacing=1.35)
add_rect(s, 0.9, 5.0, 11.5, 1.35, fill_color="2E2E2E", rounded=True)
add_text(s, "Projects covered:", 1.15, 5.18, 3, 0.3, size=11, bold=True, color=RUST)
add_text(s,
         "F:\\rust\\poroelastic_solver   (the main Rust crate)\n"
         "F:\\rust\\wang2003            (Rung 0 learning project)\n"
         "F:\\rust\\POEL_2024-main      (reference Fortran code, compiled & run, not written by me)",
         1.15, 5.5, 10.8, 0.8, size=12.5, color="D8DBDE", font="Consolas", line_spacing=1.3)
pages.append(s)

# ================================================================ PART 1: THEORY
pages.append(divider(prs, 1, "Theory", "What poroelasticity is, the governing equations, the five parameters, and the boundary conditions."))

# --- A1: what is poroelasticity
s = content_slide(prs, "Part 1 · Theory", "What Is Poroelasticity?")
add_bullets(s, [
    ("Rock underground is not solid — it's a porous skeleton with fluid (water) filling the pore space.", 0),
    ("Two things can happen when you inject fluid: (1) pore pressure rises, and (2) the rock skeleton deforms.", 0),
    ("The key idea of poroelasticity: these two effects are coupled, not independent.", 0, True),
    ("Squeezing the rock (deformation) changes the pore pressure. Raising the pore pressure pushes the rock apart (deformation). You cannot solve one without the other.", 1),
    ("This is exactly the physics behind injection-induced earthquakes (the PNAS paper's subject): wastewater injection raises pressure, which reduces the effective stress holding a fault locked, which can trigger slip.", 0),
], 0.6, 1.65, 11.7, 4.9, size=16, color=INK, bullet_color=RUST, space_after=16, line_spacing=1.25)
pages.append(s)

# --- A2: governing equations
s = content_slide(prs, "Part 1 · Theory", "The Governing Equations")
add_code_block(s, [
    "Eq. 1 (momentum balance / quasi-static elasticity):",
    "  G*Laplacian(u) + G/(1-2*nu)*grad(div(u)) - alpha*grad(p) = f(x,t)",
    "",
    "Eq. 2 (pore-pressure diffusion, coupled to strain rate):",
    "  (1/Q)*dp/dt + alpha*d(div(u))/dt - div(chi*grad(p)) = q(x,t)",
], 0.6, 1.55, 12.1, 1.85, font_size=14, title="Zhai et al. (2019) Eqs. 1-2  ==  Wang & Kumpel (2003) Eqs. 1-2")
add_bullets(s, [
    ("u(x,t) — displacement vector (how much the rock moves).  p(x,t) — excess pore pressure.", 0),
    ("Eq. 1 says: elastic restoring forces (Laplacian + grad-div terms) balance the pressure gradient's push (alpha*grad(p)).", 0),
    ("Eq. 2 says: pressure changes (dp/dt) come from two sources — fluid diffusing in (div(chi*grad p)) and the rock's own volume changing (d(div u)/dt) — the coupling term.", 0),
    ("Setting alpha=0 decouples them into ordinary elasticity + ordinary diffusion; the physics of interest is entirely in the alpha terms.", 0, True),
], 0.6, 3.6, 12.1, 3.3, size=14.5, color=INK, bullet_color=RUST, space_after=10, line_spacing=1.2)
pages.append(s)

# --- A3: five parameters
s = content_slide(prs, "Part 1 · Theory", "The Five Independent Parameters")
data = [
    ["Symbol", "Name", "Meaning"],
    ["G", "Shear modulus", "Stiffness against shape change (Pa)"],
    ["ν", "Drained Poisson ratio", "Elastic response when fluid can freely escape"],
    ["νᵤ", "Undrained Poisson ratio", "Elastic response when fluid is trapped (νᵤ > ν always)"],
    ["B", "Skempton coefficient", "Pore-pressure rise per unit confining-pressure rise, undrained"],
    ["D", "Hydraulic diffusivity", "How fast pressure disturbances spread (m²/s)"],
]
add_table(s, data, 0.6, 1.6, 12.1, 3.5, header_fill=SLATE, col_widths=[1.4, 3.2, 7.5], font_size=14.5, header_size=14.5)
add_text(s, "Everything else (α, Q, χ, λ) is computed from these five — see the next slide.",
         0.6, 5.35, 11.5, 0.5, size=13.5, italic=True, color=MUTED)
pages.append(s)

# --- A4: parameter conversion
s = content_slide(prs, "Part 1 · Theory", "Deriving the Coupling Constants")
add_code_block(s, [
    "lambda = 2*nu*G / (1 - 2*nu)                                          (Eq. 3)",
    "alpha  = 3*(nu_u - nu) / [(1-2*nu)*(1+nu_u)*B]                        (Eq. 4)",
    "1/Q    = (9/2)*(1-2*nu_u)*(nu_u-nu) / [(1-2*nu)*(1+nu_u)^2*G*B^2]     (Eq. 5)",
    "chi    = (9/2)*(1-nu_u)*(nu_u-nu)*D / [(1-nu)*(1+nu_u)^2*G*B^2]       (Eq. 6)",
], 0.6, 1.55, 12.1, 1.85, font_size=13, title="Wang & Kumpel (2003), Eqs. 3-6 -- implemented verbatim in src/param.rs")
add_bullets(s, [
    ("lambda — the first Lame parameter; ordinary elasticity, no fluid coupling at all.", 0),
    ("alpha (Biot-Willis coefficient) — fraction of a pore-pressure change that shows up as effective stress. Close to 1 means very strong coupling.", 0),
    ("Q (Biot modulus) — how much pressure builds up per unit of fluid volume added at constant strain (a stiffness for the fluid+pore system).", 0),
    ("chi (mobility = permeability / viscosity) — NOT the same as D! D = chi * Q. Units are m^2/(Pa*s), not m^2/s.", 0, True),
], 0.6, 3.6, 12.1, 3.3, size=14, color=INK, bullet_color=RUST, space_after=10, line_spacing=1.2)
pages.append(s)

# --- A5: boundary conditions
s = content_slide(prs, "Part 1 · Theory", "Boundary Conditions: Approximating a Half-Space")
add_bullets(s, [
    ("z = 0 (the ground surface, free surface):", 0, True),
    ("Traction-free: sigma_xz = sigma_yz = sigma_zz = 0 (nothing is pushing on the surface from above)", 1),
    ("Drained: p = 0 (pressure equilibrates instantly with the atmosphere)", 1),
    ("All other faces (far-field, the domain's necessary truncation of an infinite half-space):", 0, True),
    ("Fixed zero displacement (rock far away doesn't move)", 1),
    ("No-flow / zero pressure gradient (no fluid crosses the boundary)", 1),
    ("Caveat: domain must be much larger than the diffusion length sqrt(D*t) reached during a run, or these truncation boundaries contaminate the answer — this is exactly what we saw happen at late times in the validation.", 0),
], 0.6, 1.65, 12.1, 5.25, size=15.5, color=INK, bullet_color=RUST, space_after=13, line_spacing=1.2)
pages.append(s)

# --- A6: two solution philosophies
s = content_slide(prs, "Part 1 · Theory", "Two Ways to Solve the Same Equations")
add_rect(s, 0.6, 1.6, 5.85, 4.9, fill_color=PANEL, rounded=True)
add_text(s, "THE PAPER'S WAY (semi-analytical)", 0.9, 1.85, 5.2, 0.35, size=13, bold=True, color=RUST_DK)
add_bullets(s, [
    ("Laplace transform removes time (t -> s)", 0),
    ("Hankel transform removes radius (r -> k, wavenumber)", 0),
    ("Left with an ODE in depth z only -> solve with Haskell's propagator matrix", 0),
    ("Numerically invert both transforms to get back to (r, z, t)", 0),
    ("Exact for axisymmetric point sources in layered media; POEL2024 implements this", 0),
], 0.9, 2.3, 5.2, 4.0, size=13, color=INK, bullet_color=RUST_DK, space_after=10, line_spacing=1.2)

add_rect(s, 6.65, 1.6, 5.85, 4.9, fill_color=PANEL, rounded=True)
add_text(s, "OUR WAY (direct numerical)", 6.95, 1.85, 5.2, 0.35, size=13, bold=True, color=RUST_DK)
add_bullets(s, [
    ("No transforms at all -- discretize x, y, z, and t directly", 0),
    ("Finite differences on a uniform 3D grid", 0),
    ("Backward Euler in time (unconditionally stable)", 0),
    ("Iterate elasticity <-> diffusion each time step until pressure stops changing", 0),
    ("Simpler to implement and reason about; costs more compute, needs a large domain", 0),
], 6.95, 2.3, 5.2, 4.0, size=13, color=INK, bullet_color=RUST_DK, space_after=10, line_spacing=1.2)
pages.append(s)

# ================================================================ PART 2: NUMERICAL METHOD
pages.append(divider(prs, 2, "Our Numerical Method", "How the finite-difference discretization, linear solvers, and coupling scheme actually work."))

# --- B1: overview
s = content_slide(prs, "Part 2 · Numerical Method", "Overview: Grid, Time, Iteration")
add_bullets(s, [
    ("Grid: a uniform structured 3D grid (Grid3D). Nodes at (i,j,k), physical position (i*dx, j*dy, k*dz). z increases with depth.", 0),
    ("Every field (pressure, each displacement component) is a flat Vec<f64> the same length as the grid, indexed via idx(i,j,k) = i + nx*(j + ny*k).", 0),
    ("Time stepping: backward Euler -- fully implicit, so any time step size dt is numerically stable (though large dt loses temporal accuracy).", 0),
    ("Each time step is NOT a single linear solve: elasticity and diffusion are coupled equations, so we iterate between the two (an 'outer' or 'Picard-type' loop) until they agree.", 0, True),
], 0.6, 1.65, 12.1, 5.25, size=15.5, color=INK, bullet_color=RUST, space_after=14, line_spacing=1.25)
pages.append(s)

# --- B2: elasticity discretization
s = content_slide(prs, "Part 2 · Numerical Method", "Discretizing the Elasticity Equation")
add_text(s, "Expanding G*Laplacian(u) + (lambda+G)*grad(div(u)) for the x-component gives:", 0.6, 1.5, 12, 0.4, size=13.5, color=INK)
add_code_block(s, [
    "Lx = (lambda+2G)*d2ux/dx2 + G*d2ux/dy2 + G*d2ux/dz2",
    "      + (lambda+G)*d2uy/dxdy + (lambda+G)*d2uz/dxdz",
], 0.6, 1.95, 12.1, 1.05, font_size=13.5, title="Same pattern (cyclically) for Ly, Lz")
add_bullets(s, [
    ("Every second derivative uses standard central differences: d2f/dx2 = (f[i+1] - 2f[i] + f[i-1]) / dx^2", 0),
    ("Cross derivatives (like d2uy/dxdy) need a 4-point stencil: (f[i+1,j+1] - f[i+1,j-1] - f[i-1,j+1] + f[i-1,j-1]) / (4*dx*dy)", 0),
    ("This couples all three displacement components together at every interior grid point -- that's why elasticity alone is a 3*N unknown linear system (N = number of grid nodes).", 0, True),
], 0.6, 3.15, 12.1, 3.75, size=14, color=INK, bullet_color=RUST, space_after=12, line_spacing=1.2)
pages.append(s)

# --- B3: free surface ghost nodes
s = content_slide(prs, "Part 2 · Numerical Method", "The Free-Surface Trick: Ghost Nodes")
add_bullets(s, [
    ("The stencil at the surface (k=0) needs a neighbor 'above the surface' (k=-1) that doesn't physically exist.", 0),
    ("Solution: invent a 'ghost' value at k=-1, chosen so the traction-free condition is satisfied exactly.", 0),
], 0.6, 1.55, 12.1, 5.35, size=15, color=INK, bullet_color=RUST, space_after=10, line_spacing=1.2)
add_code_block(s, [
    "// sigma_xz = 0  =>  dux/dz = -duz/dx  =>",
    "ux_ghost(k=-1) = ux(k=1) + 2*dz * duz_dx",
    "",
    "// sigma_zz = 0 (and p=0 at surface)  =>  duz/dz = -lambda/(lambda+2G) * (dux_dx+duy_dy)  =>",
    "uz_ghost(k=-1) = uz(k=1) + 2*dz * (lambda/(lambda+2G)) * (dux_dx + duy_dy)",
], 0.6, 3.0, 12.1, 1.85, font_size=13, title="elasticity.rs :: ghost_ux / ghost_uy / ghost_uz")
add_text(s, "At the lateral edges (i=0, i=nx-1, j=0, j=ny-1) the far-field zero-displacement condition takes priority "
             "over this formula (returns 0.0) since those columns are pinned anyway.",
         0.6, 5.0, 12, 0.9, size=13, italic=True, color=MUTED, line_spacing=1.25)
pages.append(s)

# --- B4: diffusion discretization
s = content_slide(prs, "Part 2 · Numerical Method", "Discretizing the Diffusion Equation")
add_code_block(s, [
    "// backward Euler: solve for p at the NEW time step",
    "(1/(Q*dt)) * p_new  -  div(chi * grad(p_new))  =  source  +  (1/(Q*dt)) * p_old",
    "",
    "// 7-point Laplacian stencil (interior nodes):",
    "lap = chi * [ (p[i+1]-2p[i]+p[i-1])/dx^2 + (...)/dy^2 + (...)/dz^2 ]",
], 0.6, 1.55, 12.1, 1.85, font_size=13, title="diffusion.rs :: apply_diffusion_operator")
add_bullets(s, [
    ("z=0 (drained surface): p is fixed at 0 -- not solved for, just held constant.", 0),
    ("All other boundaries: no-flow -- implemented by mirroring the neighbor across the boundary node (ghost = value one node further in), giving zero gradient there.", 0),
    ("This backward-Euler operator is symmetric positive-definite, which is exactly what conjugate gradient needs.", 0, True),
], 0.6, 3.6, 12.1, 3.3, size=14, color=INK, bullet_color=RUST, space_after=11, line_spacing=1.2)
pages.append(s)

# --- B5: linear solvers
s = content_slide(prs, "Part 2 · Numerical Method", "Two Different Linear Solvers, On Purpose")
add_rect(s, 0.6, 1.6, 5.85, 4.9, fill_color=PANEL, rounded=True)
add_text(s, "Conjugate Gradient (CG)", 0.9, 1.85, 5.2, 0.4, size=16, bold=True, color=INK, font="Cambria")
add_bullets(s, [
    ("Used for: the diffusion equation", 0),
    ("Requires: the operator to be symmetric positive-definite (SPD)", 0),
    ("Why it qualifies: the 7-point stencil + Dirichlet/Neumann boundary treatment is provably symmetric", 0),
], 0.9, 2.5, 5.2, 2.8, size=13.5, color=INK, bullet_color=RUST, space_after=12, line_spacing=1.2)

add_rect(s, 6.65, 1.6, 5.85, 4.9, fill_color=PANEL, rounded=True)
add_text(s, "BiCGSTAB", 6.95, 1.85, 5.2, 0.4, size=16, bold=True, color=INK, font="Cambria")
add_bullets(s, [
    ("Used for: the elasticity equation", 0),
    ("Requires: nothing in particular -- works for general (non-symmetric) operators", 0),
    ("Why it's needed here: the free-surface ghost-node formulas are NOT guaranteed to keep the discrete operator exactly matrix-symmetric", 0),
], 6.95, 2.5, 5.2, 2.8, size=13.5, color=INK, bullet_color=RUST, space_after=12, line_spacing=1.2)
add_text(s, "Both are matrix-free: the operator is applied as a stencil function, never assembled into an explicit matrix.",
         0.6, 6.35, 12, 0.4, size=12.5, italic=True, color=MUTED, align="center")
pages.append(s)

# --- B6: Picard (first attempt)
s = content_slide(prs, "Part 2 · Numerical Method", "Coupling, Attempt 1: Plain Iteration (Picard)")
add_bullets(s, [
    ("Idea: guess a pressure field, solve elasticity for displacement, recompute the strain-rate source this implies, resolve pressure, repeat until pressure stops changing.", 0),
    ("This worked for moderate coupling (e.g. alpha=0.385, ~10 iterations to converge).", 0),
], 0.6, 1.55, 12.1, 5.35, size=15, color=INK, bullet_color=RUST, space_after=10, line_spacing=1.2)
add_rect(s, 0.6, 3.3, 12.1, 2.9, fill_color="2E1712", rounded=True)
add_text(s, "WHAT WENT WRONG", 0.9, 3.55, 5, 0.35, size=13, bold=True, color="F0A183")
add_bullets(s, [
    ("For Wang & Kumpel's own parameters (alpha=0.95, very soft/strongly-coupled rock), this iteration diverged: pressure went from -1e4 Pa to -7.7e5 Pa in a single additional step.", 0),
    ("Not slow convergence -- genuine numerical instability. This is a well-known failure mode for naive iterative coupling of Biot's equations at high alpha.", 0),
], 0.9, 4.0, 11.5, 2.0, size=13.5, color="F2D9D2", bullet_color="E8785C", space_after=10, line_spacing=1.2)
pages.append(s)

# --- B7: fixed-stress split
s = content_slide(prs, "Part 2 · Numerical Method", "Coupling, Attempt 2: Fixed-Stress Split")
add_text(s, "The fix (Kim, Tchelepi & Juanes 2011; Mikelic & Wheeler 2013): hold TOTAL stress fixed during the "
             "pressure solve, using K_dr*epsilon_v = sigma_v + alpha*p to predict how strain must shift:",
         0.6, 1.5, 12.1, 0.75, size=13.5, color=INK, line_spacing=1.25)
add_code_block(s, [
    "beta = alpha^2 / K_dr                     // stabilization coefficient, K_dr = drained bulk modulus",
    "",
    "// modified flow step (solved FIRST each iteration):",
    "(1/Q + beta)/dt * p_new - div(chi*grad(p_new))",
    "    = source + beta/dt * p_prev_iter + (1/Q)/dt * p_start_of_step",
], 0.6, 2.35, 12.1, 1.85, font_size=12.5, title="coupling.rs :: step()")
add_bullets(s, [
    ("Order flips: solve flow first (with the extra beta term), THEN mechanics with the updated pressure.", 0),
    ("Provably unconditionally stable regardless of coupling strength -- exactly what was missing.", 0, True),
    ("Result: the same alpha=0.95 case that diverged now runs cleanly and matches POEL2024 to 0.2-2.5% at early times.", 0),
], 0.6, 4.35, 12.1, 2.55, size=13.5, color=INK, bullet_color=RUST, space_after=9, line_spacing=1.2)
pages.append(s)

# ================================================================ PART 3: THE WORKFLOW
pages.append(divider(prs, 3, "The Workflow", "What we actually did, in order -- useful for retracing any step or explaining the process."))

# --- C1
s = content_slide(prs, "Part 3 · Workflow", "Step 1 — Parameter Conversion (Rung 0)")
loc_tag(s, "F:\\rust\\wang2003\\src\\main.rs")
add_bullets(s, [
    ("Before writing any solver, hand-derived lambda, alpha, 1/Q, chi for Wang & Kumpel's worked example and checked them against the code's output.", 0),
    ("Built this as a tiny standalone learning project (wang2003) using plain variables first, no structs -- the simplest possible Rust.", 0),
    ("Every number matched the hand calculation exactly: lambda=2.667e8 Pa, alpha=0.952, Q=1.47e9 Pa, chi=1.531e-9 m^2/(Pa*s).", 0, True),
    ("This 'verification ladder' idea (simplest case first, add complexity only after each step is trusted) shaped the entire project.", 0),
], 0.6, 1.85, 12.1, 4.6, size=17, color=INK, bullet_color=RUST, space_after=20, line_spacing=1.25)
pages.append(s)

# --- C2
s = content_slide(prs, "Part 3 · Workflow", "Step 2 — Core Solver Infrastructure")
loc_tag(s, "F:\\rust\\poroelastic_solver\\src\\{grid,field,param}.rs")
add_bullets(s, [
    ("Grid3D: a uniform 3D grid with node indexing, defined once, reused everywhere.", 0),
    ("Field3D / VectorField3D: scalar and vector data living on that grid, stored as flat arrays for speed.", 0),
    ("PoroLayer: the 5-parameter to lambda/alpha/Q/chi conversion, carried over from the Rung 0 project.", 0),
    ("Design choice: keep the crate dependency-free (pure Rust std library) so it builds anywhere without fighting BLAS/LAPACK installs.", 0, True),
], 0.6, 1.85, 12.1, 4.4, size=17, color=INK, bullet_color=RUST, space_after=20, line_spacing=1.25)
pages.append(s)

# --- C3
s = content_slide(prs, "Part 3 · Workflow", "Step 3 — Elasticity Solver + First Validation")
loc_tag(s, "F:\\rust\\poroelastic_solver\\src\\elasticity.rs, tests\\elasticity_mms.rs")
add_bullets(s, [
    ("Wrote the Navier-Cauchy finite-difference stencil, the free-surface ghost-node formulas, and a BiCGSTAB solver.", 0),
    ("Validation: Method of Manufactured Solutions (MMS) -- plug a known quadratic displacement field into the stencil and check it reproduces the exact analytic answer.", 0),
    ("Why quadratics: central differences are exact (to machine precision) for degree <= 2 polynomials, so this isolates stencil bugs from boundary-condition bugs.", 0, True),
    ("Result: passed to within 1e-8 relative error on the first correct attempt.", 0),
], 0.6, 1.85, 12.1, 4.6, size=17, color=INK, bullet_color=RUST, space_after=20, line_spacing=1.25)
pages.append(s)

# --- C4
s = content_slide(prs, "Part 3 · Workflow", "Step 4 — Diffusion Solver + Second Validation")
loc_tag(s, "F:\\rust\\poroelastic_solver\\src\\diffusion.rs, tests\\diffusion_point_source.rs")
add_bullets(s, [
    ("Wrote the backward-Euler pressure diffusion stencil and a conjugate-gradient solver.", 0),
    ("Validation: compared against the classical closed-form solution for a continuous point source in an infinite medium (Carslaw & Jaeger).", 0),
    ("First attempt used too short a test duration -- compared at a point so far past the diffusion front that the analytical curve's steep tail amplified small errors into a false failure.", 0),
    ("Fix: ran longer (t=1200s) so the comparison point sat in a numerically well-behaved part of the curve. Result: 0.2-2.5% error.", 0, True),
], 0.6, 1.85, 12.1, 4.6, size=17, color=INK, bullet_color=RUST, space_after=18, line_spacing=1.25)
pages.append(s)

# --- C5
s = content_slide(prs, "Part 3 · Workflow", "Step 5 — Coupling + a Working End-to-End Demo")
loc_tag(s, "F:\\rust\\poroelastic_solver\\src\\coupling.rs, source.rs, main.rs")
add_bullets(s, [
    ("Wrote InjectionWell (Gaussian-smoothed point source) and the first coupling loop (plain Picard iteration).", 0),
    ("main.rs runs a 60-day constant-rate injection into a homogeneous half-space with moderate crustal parameters (alpha=0.385) -- converges cleanly in ~10 iterations/step.", 0),
    ("This became the first fully working demonstration: pore pressure builds up at the well, the ground surface lifts a fraction of a millimeter -- physically sensible end to end.", 0, True),
], 0.6, 1.85, 12.1, 4.2, size=17, color=INK, bullet_color=RUST, space_after=20, line_spacing=1.25)
pages.append(s)

# --- C6
s = content_slide(prs, "Part 3 · Workflow", "Step 6 — Bringing In POEL2024 As Ground Truth")
loc_tag(s, "F:\\rust\\POEL_2024-main  (Fortran, not written by me)")
add_bullets(s, [
    ("POEL2024 is Rongjiang Wang's own reference implementation of the Wang & Kumpel (2003) method.", 0),
    ("Bug 1: the prebuilt .exe needed MinGW runtime DLLs that weren't installed. Fixed by installing gfortran (via MSYS2 pacman) and compiling from source.", 0),
    ("Bug 2: an idealized near-point source (tiny radius) pushed the Hankel-transform wavenumber integration to its array-size cap and segfaulted. Fixed by widening the source to a more realistic (still small) size.", 0),
    ("Bug 3: a source that jumped straight to full rate on its first time sample had no frequency content for the transform machinery to resolve, giving all-zero output. Fixed by giving it an explicit onset at t=1s.", 0, True),
], 0.6, 1.85, 12.1, 4.7, size=15.5, color=INK, bullet_color=RUST, space_after=16, line_spacing=1.25)
pages.append(s)

# --- C7
s = content_slide(prs, "Part 3 · Workflow", "Step 7 — Discovering the Picard Divergence")
loc_tag(s, "F:\\rust\\poroelastic_solver\\examples\\wk2003_comparison.rs")
add_bullets(s, [
    ("Configured our own Rust solver with Wang & Kumpel's exact test-case parameters (the same ones driving POEL2024) to compare directly.", 0),
    ("Pressure diverged: -1.07e4 Pa at t=100s, then -7.77e5 Pa at t=200s -- a ~70x jump in one step.", 0, True),
    ("Diagnosis: not a bug in the stencils (those were already validated) -- the plain Picard coupling iteration is known to be unstable for strongly-coupled media (alpha=0.95, close to the theoretical maximum of 1).", 0),
], 0.6, 1.85, 12.1, 4.2, size=17, color=INK, bullet_color=RUST, space_after=20, line_spacing=1.25)
pages.append(s)

# --- C8
s = content_slide(prs, "Part 3 · Workflow", "Step 8 — Fixed-Stress Split, Final Result")
loc_tag(s, "F:\\rust\\poroelastic_solver\\src\\diffusion.rs, coupling.rs")
add_bullets(s, [
    ("Implemented the fixed-stress split (see Part 2) -- flow solved first each iteration, with the beta=alpha^2/K_dr stabilization term.", 0),
    ("Regression check: moderate-coupling case (main.rs) produced byte-identical output to before -- confirms nothing broke.", 0),
    ("The strongly-coupled case now runs cleanly through all 80 steps, matching POEL2024 to 0.2-2.5% at early time (later drift traced to finite-domain boundary effects, not the coupling scheme).", 0, True),
], 0.6, 1.85, 12.1, 4.4, size=17, color=INK, bullet_color=RUST, space_after=20, line_spacing=1.25)
pages.append(s)

# ================================================================ PART 4: CODE WALKTHROUGH
pages.append(divider(prs, 4, "Code Walkthrough", "Every source file, block by block: what it does, where it lives, and how it works."))

# --- D0: project tree
s = content_slide(prs, "Part 4 · Code Walkthrough", "Project Layout")
add_code_block(s, [
    "F:\\rust\\poroelastic_solver\\          <- the main crate",
    "  Cargo.toml                          package manifest, zero dependencies",
    "  src\\",
    "    lib.rs                            crate root, re-exports public API",
    "    grid.rs          Grid3D           the structured 3D grid",
    "    field.rs         Field3D/VectorField3D   data living on the grid",
    "    param.rs         PoroLayer        the 5-parameter -> alpha/Q/chi conversion",
    "    linalg.rs        conjugate_gradient, bicgstab   matrix-free linear solvers",
    "    elasticity.rs    apply_elastic_operator, solve_elasticity, divergence",
    "    diffusion.rs     apply_diffusion_operator, solve_diffusion",
    "    coupling.rs      SimState, step()   the fixed-stress split time loop",
    "    source.rs        InjectionWell      Gaussian-smoothed point source",
    "    main.rs                            example: 60-day injection demo",
    "  tests\\             elasticity_mms.rs, diffusion_point_source.rs",
    "  examples\\          plot_diffusion_validation.rs, wk2003_comparison.rs, rung0_param_check.rs",
    "",
    "F:\\rust\\wang2003\\          <- Rung 0 learning project (plain-variable version)",
    "F:\\rust\\POEL_2024-main\\   <- reference Fortran code (Wang's own, compiled & run only)",
], 0.6, 1.55, 12.1, 5.5, font_size=12, title=None)
pages.append(s)

# --- D1: lib.rs
s = content_slide(prs, "Part 4 · Code Walkthrough", "lib.rs — Crate Root")
loc_tag(s, "F:\\rust\\poroelastic_solver\\src\\lib.rs")
add_code_block(s, [
    "pub mod coupling;  pub mod diffusion;  pub mod elasticity;",
    "pub mod field;     pub mod grid;       pub mod linalg;",
    "pub mod param;     pub mod source;",
    "",
    "pub use coupling::{SimState, SolverTolerances, StepReport};",
    "pub use field::{Field3D, VectorField3D};",
    "pub use grid::Grid3D;",
    "pub use param::PoroLayer;",
    "pub use source::InjectionWell;",
], 0.6, 1.7, 12.1, 2.6, font_size=14)
add_bullets(s, [
    ("Declares every module (pub mod) so the compiler includes them in the crate.", 0),
    ("Re-exports (pub use) the main types so callers can write poroelastic_solver::SimState instead of poroelastic_solver::coupling::SimState.", 0),
    ("The doc comment at the top of the file states the governing equations -- the crate's 'why' in one place.", 0),
], 0.6, 4.55, 12.1, 2.4, size=14, color=INK, bullet_color=RUST, space_after=10, line_spacing=1.2)
pages.append(s)

# --- D2: grid.rs + field.rs
s = content_slide(prs, "Part 4 · Code Walkthrough", "grid.rs + field.rs — Grid and Data Storage")
loc_tag(s, "F:\\rust\\poroelastic_solver\\src\\grid.rs  and  src\\field.rs")
add_code_block(s, [
    "pub struct Grid3D { pub nx: usize, ny: usize, nz: usize, dx: f64, dy: f64, dz: f64 }",
    "impl Grid3D {",
    "    pub fn idx(&self, i,j,k) -> usize { i + self.nx*(j + self.ny*k) }  // x-fastest flat index",
    "    pub fn coords(&self, i,j,k) -> (f64,f64,f64) { (i as f64*dx, j as f64*dy, k as f64*dz) }",
    "}",
    "",
    "pub struct Field3D { pub data: Vec<f64> }              // one scalar per grid node",
    "pub struct VectorField3D { pub ux: Field3D, uy: Field3D, uz: Field3D }",
], 0.6, 1.7, 12.1, 2.5, font_size=13)
add_bullets(s, [
    ("idx(i,j,k) maps 3D node coordinates to a position in a flat Vec<f64> -- x varies fastest, matching how the data is laid out in memory (cache-friendly for the i-loops).", 0),
    ("VectorField3D::to_flat()/from_flat() pack the 3 displacement components into one long vector [ux|uy|uz] so the generic linear solvers (which only know about flat Vec<f64>) can be reused for both scalar (pressure) and vector (displacement) unknowns.", 0),
], 0.6, 4.35, 12.1, 2.6, size=13.5, color=INK, bullet_color=RUST, space_after=10, line_spacing=1.2)
pages.append(s)

# --- D3: param.rs
s = content_slide(prs, "Part 4 · Code Walkthrough", "param.rs — The 5-Parameter Conversion")
loc_tag(s, "F:\\rust\\poroelastic_solver\\src\\param.rs")
add_code_block(s, [
    "pub struct PoroLayer { pub g: f64, nu: f64, nu_u: f64, b: f64, d: f64 }",
    "impl PoroLayer {",
    "    pub fn lambda(&self) -> f64 { 2.0*self.nu*self.g / (1.0-2.0*self.nu) }",
    "    pub fn alpha(&self)  -> f64 { 3.0*(nu_u-nu) / ((1.0-2.0*nu)*(1.0+nu_u)*b) }",
    "    pub fn inv_q(&self)  -> f64 { /* Eq. 5 */ }",
    "    pub fn chi(&self)    -> f64 { /* Eq. 6, uses d */ }",
    "    pub fn k_dr(&self)   -> f64 { self.lambda() + 2.0*self.g/3.0 }  // drained bulk modulus",
    "}",
], 0.6, 1.7, 12.1, 2.3, font_size=13)
add_bullets(s, [
    ("Every method is a direct, one-line translation of a Wang & Kumpel (2003) equation number (comments cite them).", 0),
    ("k_dr() was added later specifically to support the fixed-stress split's beta = alpha^2/K_dr stabilization term.", 0, True),
    ("This is literally the same code as Rung 0 (wang2003/src/main.rs), just wrapped in a struct so multiple layers/scenarios can each carry their own set of parameters.", 0),
], 0.6, 4.2, 12.1, 2.8, size=14, color=INK, bullet_color=RUST, space_after=10, line_spacing=1.2)
pages.append(s)

# --- D4: linalg.rs
s = content_slide(prs, "Part 4 · Code Walkthrough", "linalg.rs — Matrix-Free Linear Solvers")
loc_tag(s, "F:\\rust\\poroelastic_solver\\src\\linalg.rs")
add_code_block(s, [
    "pub fn conjugate_gradient<F: Fn(&[f64])->Vec<f64>>(apply_a: F, b: &[f64], x0: Vec<f64>, ...)",
    "    -> (Vec<f64>, usize) {",
    "    // standard CG: r = b - A*x; p = r; loop { alpha = rs/(p.Ap); x += alpha*p; ... }",
    "}",
    "",
    "pub fn bicgstab<F: Fn(&[f64])->Vec<f64>>(apply_a: F, b: &[f64], x0: Vec<f64>, ...)",
    "    -> (Vec<f64>, usize) { /* stabilized bi-conjugate gradients */ }",
], 0.6, 1.7, 12.1, 2.1, font_size=12.5)
add_bullets(s, [
    ("'Matrix-free' means apply_a is a closure that computes A*x directly via the stencil -- the matrix A is never assembled or stored, which is essential since A would be enormous (3N x 3N for elasticity, N = number of grid nodes).", 0),
    ("CG requires the operator to be symmetric positive-definite; it is used only for the diffusion equation, where that's provably true.", 0),
    ("BiCGSTAB tolerates non-symmetric operators; it is used for elasticity, where the free-surface ghost-node stencil isn't guaranteed to stay exactly symmetric.", 0),
], 0.6, 4.0, 12.1, 3.0, size=13, color=INK, bullet_color=RUST, space_after=9, line_spacing=1.2)
pages.append(s)

# --- D5: elasticity.rs part 1
s = content_slide(prs, "Part 4 · Code Walkthrough", "elasticity.rs (1/2) — Ghost Nodes & Boundary Masks")
loc_tag(s, "F:\\rust\\poroelastic_solver\\src\\elasticity.rs")
add_code_block(s, [
    "fn is_fixed(grid, i, j, k) -> bool {",
    "    i==0 || i==nx-1 || j==0 || j==ny-1 || k==nz-1   // far-field: pinned to zero",
    "}",
    "",
    "fn ghost_uz(ux, uy, uz, grid, lambda, g, i, j) -> f64 {",
    "    if edge_of_domain { return 0.0; }               // lateral edges: fixed wins",
    "    let dux_dx = /* central diff at k=0 */;",
    "    let duy_dy = /* central diff at k=0 */;",
    "    uz(i,j,1) + 2.0*dz*(lambda/(lambda+2.0*g))*(dux_dx + duy_dy)   // Eq. from Part 2",
    "}",
], 0.6, 1.7, 12.1, 2.65, font_size=12)
add_bullets(s, [
    ("is_fixed marks the far-field boundary nodes (sides + bottom) whose displacement is pinned to zero.", 0),
    ("ghost_ux / ghost_uy / ghost_uz compute the 'value above the surface' needed by the k=0 stencil, from the traction-free relations derived in Part 2.", 0),
], 0.6, 4.5, 12.1, 2.4, size=13.5, color=INK, bullet_color=RUST, space_after=10, line_spacing=1.2)
pages.append(s)

# --- D6: elasticity.rs part 2
s = content_slide(prs, "Part 4 · Code Walkthrough", "elasticity.rs (2/2) — The Stencil, Solve, Divergence")
loc_tag(s, "F:\\rust\\poroelastic_solver\\src\\elasticity.rs")
add_code_block(s, [
    "pub fn apply_elastic_operator(u_flat, grid, g, lambda) -> Vec<f64> {",
    "    for each node (i,j,k):",
    "        if is_fixed(i,j,k) { output = input; continue }   // identity row",
    "        compute 9 second derivatives + 6 cross derivatives (ghosts at k=0)",
    "        Lx = (lambda+2G)*d2ux_dx2 + G*d2ux_dy2 + ... + (lambda+G)*d2uz_dxdz",
    "        (Ly, Lz analogous)",
    "}",
    "pub fn solve_elasticity(rhs, grid, g, lambda, x0, tol, max_iter) -> (VectorField3D, usize)",
    "pub fn divergence(u, grid, lambda, g) -> Field3D    // needed as a source for pressure eqn",
], 0.6, 1.7, 12.1, 2.65, font_size=12)
add_bullets(s, [
    ("apply_elastic_operator IS the matrix A from 'A*x=b', applied one grid node at a time -- this is what bicgstab calls every iteration.", 0),
    ("divergence() reuses the exact same free-surface ghost formula so the mechanics and the pressure-equation source term stay numerically consistent.", 0),
], 0.6, 4.55, 12.1, 2.35, size=13, color=INK, bullet_color=RUST, space_after=9, line_spacing=1.2)
pages.append(s)

# --- D7: diffusion.rs
s = content_slide(prs, "Part 4 · Code Walkthrough", "diffusion.rs — Pressure Solve, With Stabilization")
loc_tag(s, "F:\\rust\\poroelastic_solver\\src\\diffusion.rs")
add_code_block(s, [
    "pub fn apply_diffusion_operator(p, grid, chi, coeff) -> Vec<f64> {",
    "    for each node: if k==0 { output = p (Dirichlet) }",
    "    else { output = coeff*p - chi*Laplacian(p) }   // 7-point stencil, Neumann elsewhere",
    "}",
    "",
    "pub fn solve_diffusion(p_n, p_iter, beta, source, grid, chi, inv_q, dt, ...) -> (Field3D, usize) {",
    "    coeff = (inv_q + beta) / dt;",
    "    b[idx] = source + (inv_q/dt)*p_n[idx] + (beta/dt)*p_iter[idx];   // fixed-stress RHS",
    "    conjugate_gradient(|v| apply_diffusion_operator(v, ...), &b, ...)",
    "}",
], 0.6, 1.7, 12.1, 2.85, font_size=12)
add_bullets(s, [
    ("beta=0.0 and p_iter=p_n recovers the plain (unstabilized) equation -- the fixed-stress version is a strict generalization, not a rewrite.", 0),
], 0.6, 4.75, 12.1, 2.15, size=13.5, color=INK, bullet_color=RUST, space_after=8, line_spacing=1.2)
pages.append(s)

# --- D8: coupling.rs part 1
s = content_slide(prs, "Part 4 · Code Walkthrough", "coupling.rs (1/2) — State and the Pressure-Gradient Source")
loc_tag(s, "F:\\rust\\poroelastic_solver\\src\\coupling.rs")
add_code_block(s, [
    "pub struct SimState { pub u: VectorField3D, pub p: Field3D }",
    "pub struct SolverTolerances { picard_tol, picard_max_iter, cg_tol, cg_max_iter }",
    "",
    "fn alpha_grad_p(p, grid, alpha) -> VectorField3D {",
    "    // alpha*grad(p), the RHS source for the elasticity solve;",
    "    // dp/dz at k=0 uses the odd-reflection ghost p(-1) = -p(1), since p=0 there exactly",
    "}",
], 0.6, 1.7, 12.1, 2.15, font_size=12.5)
add_bullets(s, [
    ("SimState bundles the two coupled unknowns (displacement, pressure) that get updated together every time step.", 0),
    ("alpha_grad_p turns the pressure field into the vector 'body force' that drives the elasticity solve -- it's the alpha*grad(p) term on the right-hand side of Eq. 1.", 0),
], 0.6, 4.1, 12.1, 2.9, size=13.5, color=INK, bullet_color=RUST, space_after=10, line_spacing=1.2)
pages.append(s)

# --- D9: coupling.rs part 2
s = content_slide(prs, "Part 4 · Code Walkthrough", "coupling.rs (2/2) — The Fixed-Stress Time Step")
loc_tag(s, "F:\\rust\\poroelastic_solver\\src\\coupling.rs :: step()")
add_code_block(s, [
    "pub fn step(state, grid, params, q_field, dt, tol) -> StepReport {",
    "    let beta = alpha*alpha / params.k_dr();",
    "    for it in 0..max_iter {",
    "        source = q - alpha*(div_u_iter - div_u_n)/dt;             // flow step first",
    "        p_new  = solve_diffusion(p_n, p_iter, beta, source, ...);",
    "        rhs    = alpha_grad_p(p_new, ...);                        // then mechanics",
    "        u_new  = solve_elasticity(rhs, ..., u_current, ...);",
    "        if |p_new - p_iter| < tol { break }",
    "    }",
    "}",
], 0.6, 1.7, 12.1, 2.85, font_size=12)
add_text(s, "This IS the fixed-stress split algorithm from Part 2, translated line for line into code.",
         0.6, 4.75, 12.1, 0.5, size=14, italic=True, color=MUTED)
pages.append(s)

# --- D10: source.rs
s = content_slide(prs, "Part 4 · Code Walkthrough", "source.rs — The Injection Well")
loc_tag(s, "F:\\rust\\poroelastic_solver\\src\\source.rs")
add_code_block(s, [
    "pub struct InjectionWell { x0, y0, z0, sigma, schedule: Vec<(f64,f64)> }",
    "",
    "pub fn source_field(&self, grid, t) -> Field3D {",
    "    let rate = self.rate_at(t);                     // look up schedule for this time",
    "    // w(x) = exp(-r^2 / (2*sigma^2)) / normalization   -- a 3D Gaussian",
    "    // renormalize numerically so sum(w)*cell_volume == 1, then scale by rate",
    "}",
], 0.6, 1.7, 12.1, 2.2, font_size=13)
add_bullets(s, [
    ("A true mathematical point source (Dirac delta) can't be represented on a finite grid -- it would need infinite pressure in a single cell.", 0),
    ("Solution: smear the injection over a small Gaussian blob (sigma ~ 1-2 grid cells) that still integrates to exactly the correct total volume.", 0),
    ("schedule is a list of (time, rate) pairs -- supports step changes, shut-ins, or any piecewise-constant history.", 0),
], 0.6, 4.15, 12.1, 2.9, size=13.5, color=INK, bullet_color=RUST, space_after=10, line_spacing=1.2)
pages.append(s)

# --- D11: main.rs
s = content_slide(prs, "Part 4 · Code Walkthrough", "main.rs — The Example Driver")
loc_tag(s, "F:\\rust\\poroelastic_solver\\src\\main.rs")
add_code_block(s, [
    "let params = PoroLayer { g: 2.0e10, nu: 0.25, nu_u: 0.30, b: 0.6, d: 1.5 };",
    "let grid = Grid3D::new(41, 41, 41, 150.0, 150.0, 150.0);       // 6 km cube",
    "let well = InjectionWell { x0:3000.0, y0:3000.0, z0:3000.0, sigma:1.5*dx,",
    "                           schedule: vec![(0.0, 0.005)] };    // 0.005 m^3/s",
    "for step_i in 0..60 {                                         // 60 daily steps",
    "    let report = step(&mut state, &grid, &params, &q_field, dt, &tol);",
    "    // write CSV row: pressure at well, uplift at surface, picard_iters",
    "}",
    "write_vtk(\"final_field.vtk\", &grid, &state)   // full 3D field, open in ParaView",
], 0.6, 1.7, 12.1, 3.0, font_size=11.5)
add_text(s, "Run with: cargo run --release  ->  writes injection_timeseries.csv and final_field.vtk",
         0.6, 4.9, 12.1, 0.5, size=13.5, italic=True, color=MUTED)
pages.append(s)

# --- D12: tests
s = content_slide(prs, "Part 4 · Code Walkthrough", "tests/ — The Two Automated Checks")
loc_tag(s, "F:\\rust\\poroelastic_solver\\tests\\elasticity_mms.rs, diffusion_point_source.rs")
add_code_block(s, [
    "// elasticity_mms.rs",
    "let u = quadratic_polynomial(x,y,z);   // e.g. ux = x^2 + 2xy + 3xz, ...",
    "assert!( (apply_elastic_operator(u,...) - analytic_value).abs() < 1e-8 );",
    "",
    "// diffusion_point_source.rs",
    "let p_num = solve_diffusion(...)  /* 40 backward-Euler steps */;",
    "let p_ana = analytical_carslaw_jaeger_formula(r, t);",
    "assert!( (p_num - p_ana).abs() / p_ana < 0.2 );",
], 0.6, 1.7, 12.1, 2.5, font_size=12.5)
add_text(s, "Run with: cargo test --release   (both currently pass)",
         0.6, 4.4, 12.1, 0.4, size=14, italic=True, color=MUTED)
pages.append(s)

# --- D13: wk2003_comparison.rs example
s = content_slide(prs, "Part 4 · Code Walkthrough", "examples/wk2003_comparison.rs — The Cross-Check")
loc_tag(s, "F:\\rust\\poroelastic_solver\\examples\\wk2003_comparison.rs")
add_code_block(s, [
    "let params = PoroLayer { g: 0.4e9, nu: 0.2, nu_u: 0.4, b: 0.75, d: 1.0 };  // W&K's own numbers",
    "let grid = Grid3D::new(49, 49, 43, 5.0, 5.0, 5.0);                        // 240m x 240m x 215m",
    "let well = InjectionWell { x0:120.0, y0:120.0, z0:60.0, ..., schedule: vec![(0.0, 32.0/3600.0)] };",
    "for step_i in 0..80 {                                                     // dt=100s, 8000s total",
    "    step(&mut state, &grid, &params, &q_field, dt, &tol);",
    "    // write p at r=40m for z = 5, 15, 45, 75 m -> rust_solver_wk2003.csv",
    "}",
], 0.6, 1.7, 12.1, 2.5, font_size=11.5)
add_text(s,
         "Run with: cargo run --release --example wk2003_comparison\n"
         "Output was compared against POEL2024's wk2003_pp.dat -- this produced the headline validation result.",
         0.6, 4.4, 12.1, 1.0, size=13.5, italic=True, color=MUTED, line_spacing=1.3)
pages.append(s)

# ================================================================ PART 5: RESULTS & TALKING POINTS
pages.append(divider(prs, 5, "Results & Talking Points", "The final numbers, how to explain them simply, and where to find everything."))

# --- E1: results table
s = content_slide(prs, "Part 5 · Results", "Final Validation Numbers")
data = [
    ["Check", "What it proves", "Result"],
    ["MMS test", "Elasticity stencil math is exact", "< 1e-8 relative error"],
    ["Analytical diffusion", "Diffusion module matches theory", "0.2-2.5% error"],
    ["POEL reproduction", "We can reproduce the paper's own tool", "Matches Fig. 2 shape + Noordbergum effect"],
    ["Rust vs. POEL (fixed-stress)", "Our full coupled code is correct", "0.2-2.5% (early time), 11-17% (late, explained)"],
]
add_table(s, data, 0.6, 1.6, 12.1, 3.0, header_fill=SLATE, col_widths=[3.1, 5.2, 3.8], font_size=13, header_size=13.5)
add_text(s, "Every number above is reproducible: re-run cargo test, cargo run --example wk2003_comparison, "
             "and the plotting scripts in poroelastic_solver/validation_plots.",
         0.6, 4.9, 12.1, 0.8, size=13, italic=True, color=MUTED, line_spacing=1.3)
pages.append(s)

# --- E2: how to explain fixed-stress split simply
s = content_slide(prs, "Part 5 · Results", "Explaining the Fixed-Stress Split Simply")
add_rich_text(s, [
    {"runs": [{"text": "If your professor asks \"why did you need this fix?\":", "size": 16, "bold": True, "color": INK}], "space_after": 14},
    {"bullet": True, "bullet_color": RUST, "space_after": 12,
     "runs": [{"text": "\"Solving pressure and deformation by just alternating between them works fine most of the time -- ", "size": 15, "color": INK},
              {"text": "but for very soft, strongly-coupled rock, that back-and-forth can amplify errors instead of shrinking them.\"", "size": 15, "color": INK}]},
    {"bullet": True, "bullet_color": RUST, "space_after": 12,
     "runs": [{"text": "\"The fix holds the ", "size": 15, "color": INK}, {"text": "total stress", "size": 15, "bold": True, "color": RUST_DK},
              {"text": " fixed while solving for pressure, which is a mathematically provable way to guarantee the iteration always converges, no matter how strong the coupling.\"", "size": 15, "color": INK}]},
    {"bullet": True, "bullet_color": RUST, "space_after": 12,
     "runs": [{"text": "\"I found this the hard way: my code diverged on the paper's own worked example, traced it to the coupling scheme (not the physics), and fixed it with a well-known technique from the poromechanics literature (Kim, Tchelepi & Juanes 2011).\"", "size": 15, "color": INK}]},
], 0.6, 1.6, 12.1, 5.0, line_spacing=1.15)
pages.append(s)

# --- E3: limitations / future work
s = content_slide(prs, "Part 5 · Results", "Known Limitations & Future Work")
add_bullets(s, [
    ("Single homogeneous layer, not the paper's layered Earth model -- would need a fundamentally different (layered propagator) numerical method, or a much more complex FD grid with per-layer properties.", 0),
    ("Finite domain approximates an infinite half-space -- must stay large relative to sqrt(D*t_max); the late-time drift in the validation traces directly to this.", 0),
    ("No Coulomb-stress or seismicity-rate modeling (Eq. 3 of the PNAS paper) -- this project solves only the poroelastic PDE system, not the earthquake-nucleation model built on top of it.", 0),
    ("Possible next step: implement a proper Laplace-Hankel-propagator solver (like POEL) for direct, non-approximate comparison to layered/axisymmetric cases.", 0),
], 0.6, 1.65, 12.1, 5.25, size=15, color=INK, bullet_color=RUST, space_after=15, line_spacing=1.2)
pages.append(s)

# --- E4: quick reference
s = content_slide(prs, "Part 5 · Results", "Quick Reference: Where Everything Lives")
add_code_block(s, [
    "Main crate:        F:\\rust\\poroelastic_solver\\",
    "Rung 0 project:    F:\\rust\\wang2003\\",
    "Reference code:    F:\\rust\\POEL_2024-main\\  (compiled with gfortran via MSYS2)",
    "Plots & report:    F:\\rust\\poroelastic_solver\\validation_plots\\  (VALIDATION_SUMMARY.md)",
    "",
    "PNAS paper:            C:\\Users\\Asus\\Downloads\\PNAS_2019.pdf",
    "Wang & Kumpel (2003):  C:\\Users\\Asus\\Downloads\\wang2003.pdf",
    "",
    "Build & test:  cargo build --release   |   cargo test --release",
    "Run demo:      cargo run --release     (writes injection_timeseries.csv, final_field.vtk)",
], 0.6, 1.7, 12.1, 4.6, font_size=13.5)
pages.append(s)

TOTAL = len(pages)
for i, s in enumerate(pages):
    pass  # page numbers already added on content slides where desired; skip renumbering dividers/title

prs.save(r"F:\rust\poroelastic_solver\validation_plots\pptx_build\My_Study_Notes.pptx")
print("saved My_Study_Notes.pptx with", len(pages), "slides")
