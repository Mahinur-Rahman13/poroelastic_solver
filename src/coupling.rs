/*Coupling Module
Time-stepping driver that couples the elasticity (Eq. 1) and diffusion
(Eq. 2) solves at each step using the fixed-stress split iteration (Kim,
Tchelepi & Juanes 2011; Mikelic & Wheeler 2013): each outer iteration first
solves the flow equation at fixed total stress -- which adds a
stabilization term beta = alpha^2/K_dr to the pressure equation's storage
coefficient -- and then resolves the mechanics with the updated pressure.
This scheme is unconditionally stable regardless of coupling strength,
unlike a plain Picard iteration (no stabilization term), which can and does
diverge for strongly-coupled media (alpha close to 1).
*/
use crate::diffusion::solve_diffusion;
use crate::elasticity::{divergence, solve_elasticity};
use crate::field::{Field3D, VectorField3D};
use crate::grid::Grid3D;
use crate::param::PoroLayer;

#[derive(Clone)]
pub struct SimState {
    pub u: VectorField3D,
    pub p: Field3D,
}

impl SimState {
    pub fn zeros(grid: &Grid3D) -> Self {
        Self { u: VectorField3D::zeros(grid), p: Field3D::zeros(grid) }
    }
}

pub struct StepReport {
    pub picard_iters: usize,
    pub last_p_change: f64,
}

pub struct SolverTolerances {
    pub picard_tol: f64,
    pub picard_max_iter: usize,
    pub cg_tol: f64,
    pub cg_max_iter: usize,
}

impl Default for SolverTolerances {
    fn default() -> Self {
        Self { picard_tol: 1e-6, picard_max_iter: 30, cg_tol: 1e-8, cg_max_iter: 2000 }
    }
}

/// alpha * grad(p), used as the source term on the RHS of the elasticity
/// equation. p = 0 is enforced at the free surface (k = 0), so the vertical
/// derivative there uses the odd-reflection ghost p(-1) = -p(1).
fn alpha_grad_p(p: &Field3D, grid: &Grid3D, alpha: f64) -> VectorField3D {
    let (nx, ny, nz) = (grid.nx, grid.ny, grid.nz);
    let (dx, dy, dz) = (grid.dx, grid.dy, grid.dz);
    let mut out = VectorField3D::zeros(grid);
    for k in 0..nz {
        for j in 0..ny {
            for i in 0..nx {
                let dpdx = if i == 0 {
                    (p.get(grid, i + 1, j, k) - p.get(grid, i, j, k)) / dx
                } else if i == nx - 1 {
                    (p.get(grid, i, j, k) - p.get(grid, i - 1, j, k)) / dx
                } else {
                    (p.get(grid, i + 1, j, k) - p.get(grid, i - 1, j, k)) / (2.0 * dx)
                };
                let dpdy = if j == 0 {
                    (p.get(grid, i, j + 1, k) - p.get(grid, i, j, k)) / dy
                } else if j == ny - 1 {
                    (p.get(grid, i, j, k) - p.get(grid, i, j - 1, k)) / dy
                } else {
                    (p.get(grid, i, j + 1, k) - p.get(grid, i, j - 1, k)) / (2.0 * dy)
                };
                let dpdz = if k == 0 {
                    p.get(grid, i, j, 1) / dz
                } else if k == nz - 1 {
                    (p.get(grid, i, j, k) - p.get(grid, i, j, k - 1)) / dz
                } else {
                    (p.get(grid, i, j, k + 1) - p.get(grid, i, j, k - 1)) / (2.0 * dz)
                };
                out.ux.set(grid, i, j, k, alpha * dpdx);
                out.uy.set(grid, i, j, k, alpha * dpdy);
                out.uz.set(grid, i, j, k, alpha * dpdz);
            }
        }
    }
    out
}

fn max_abs_diff(a: &Field3D, b: &Field3D) -> f64 {
    a.data.iter().zip(b.data.iter()).fold(0.0_f64, |m, (x, y)| m.max((x - y).abs()))
}

/// Advance the coupled system by one time step of size `dt`.
pub fn step(
    state: &mut SimState,
    grid: &Grid3D,
    params: &PoroLayer,
    q_field: &Field3D,
    dt: f64,
    tol: &SolverTolerances,
) -> StepReport {
    let g = params.g;
    let lambda = params.lambda();
    let alpha = params.alpha();
    let chi = params.chi();
    let inv_q = params.inv_q();
    let beta = alpha * alpha / params.k_dr();

    let p_n = state.p.clone();
    let div_u_n = divergence(&state.u, grid, lambda, g);

    let mut p_iter = p_n.clone();
    let mut div_u_iter = div_u_n.clone();
    let mut u_current = state.u.clone();
    let mut last_change = f64::INFINITY;
    let mut iters = 0;

    let n = grid.n();
    for it in 0..tol.picard_max_iter {
        iters = it + 1;

        // Flow step: solve for pressure at fixed total stress, using the
        // volumetric strain from the previous mechanics iterate.
        let mut source = Field3D::zeros(grid);
        for idx in 0..n {
            source.data[idx] = q_field.data[idx] - alpha * (div_u_iter.data[idx] - div_u_n.data[idx]) / dt;
        }
        let (p_new, _) =
            solve_diffusion(&p_n, &p_iter, beta, &source, grid, chi, inv_q, dt, tol.cg_tol, tol.cg_max_iter);

        // Mechanics step: resolve displacement with the updated pressure.
        let rhs = alpha_grad_p(&p_new, grid, alpha);
        let (u_new, _) = solve_elasticity(&rhs, grid, g, lambda, u_current.clone(), tol.cg_tol, tol.cg_max_iter);
        let div_u_new = divergence(&u_new, grid, lambda, g);

        let change = max_abs_diff(&p_new, &p_iter);
        p_iter = p_new;
        div_u_iter = div_u_new;
        u_current = u_new;
        last_change = change;
        if change < tol.picard_tol {
            break;
        }
    }

    state.u = u_current;
    state.p = p_iter;
    StepReport { picard_iters: iters, last_p_change: last_change }
}
