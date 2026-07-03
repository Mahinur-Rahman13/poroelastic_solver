/*Coupling Module
Time-stepping driver that couples the elasticity (Eq. 1) and diffusion
(Eq. 2) solves at each step using a Picard (block Gauss-Seidel) iteration:
given a guess of p, solve for u, recompute the strain-rate source this
implies for the pressure equation, resolve p, and repeat until p stops
changing. This is a simpler (if not maximally fast-converging) alternative
to the "fixed-stress split" scheme used in the poromechanics literature; it
is easy to reason about and converges for the moderate coupling strengths
typical of crustal rock properties.
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

    let p_n = state.p.clone();
    let div_u_n = divergence(&state.u, grid, lambda, g);

    let mut p_star = p_n.clone();
    let mut u_current = state.u.clone();
    let mut last_change = f64::INFINITY;
    let mut iters = 0;

    for it in 0..tol.picard_max_iter {
        iters = it + 1;

        let rhs = alpha_grad_p(&p_star, grid, alpha);
        let (u_new, _) = solve_elasticity(&rhs, grid, g, lambda, u_current.clone(), tol.cg_tol, tol.cg_max_iter);

        let div_u_new = divergence(&u_new, grid, lambda, g);

        let n = grid.n();
        let mut source = Field3D::zeros(grid);
        for idx in 0..n {
            source.data[idx] = q_field.data[idx] - alpha * (div_u_new.data[idx] - div_u_n.data[idx]) / dt;
        }
        let (p_new, _) = solve_diffusion(&p_n, &source, grid, chi, inv_q, dt, tol.cg_tol, tol.cg_max_iter);

        let change = max_abs_diff(&p_new, &p_star);
        p_star = p_new;
        u_current = u_new;
        last_change = change;
        if change < tol.picard_tol {
            break;
        }
    }

    state.u = u_current;
    state.p = p_star;
    StepReport { picard_iters: iters, last_p_change: last_change }
}
