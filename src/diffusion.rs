/*Diffusion Module
Backward-Euler finite-difference discretization of the pore-pressure
diffusion equation (Eq. 2 in Zhai et al. 2019):

    (1/Q) dp/dt + alpha d(div u)/dt - div(chi * grad p) = q(x,t)

Rearranged as an implicit solve for p^{n+1} given p^n and a source term that
folds in q and the (already time-differenced) mechanical coupling term:

    (1/(Q*dt)) p^{n+1} - div(chi * grad p^{n+1}) = source + (1/(Q*dt)) p^n

Boundary conditions:
  * z = 0 (free surface): drained, p = 0 (Dirichlet).
  * all other faces: no-flow (homogeneous Neumann), approximating a domain
    much larger than the pressure diffusion length scale.
*/
use crate::field::Field3D;
use crate::grid::Grid3D;
use crate::linalg::conjugate_gradient;

#[inline]
fn get(field: &[f64], grid: &Grid3D, i: usize, j: usize, k: usize) -> f64 {
    field[grid.idx(i, j, k)]
}

/// Apply A(p) = coeff*p - div(chi*grad p), where coeff = 1/(Q*dt).
pub fn apply_diffusion_operator(p: &[f64], grid: &Grid3D, chi: f64, coeff: f64) -> Vec<f64> {
    let (nx, ny, nz) = (grid.nx, grid.ny, grid.nz);
    let (dx, dy, dz) = (grid.dx, grid.dy, grid.dz);
    let (dx2, dy2, dz2) = (dx * dx, dy * dy, dz * dz);
    let mut out = vec![0.0; grid.n()];

    for k in 0..nz {
        for j in 0..ny {
            for i in 0..nx {
                let idx = grid.idx(i, j, k);
                if k == 0 {
                    // drained free surface: p = 0 (Dirichlet)
                    out[idx] = p[idx];
                    continue;
                }
                let p_c = p[idx];

                let p_ip1 = if i == nx - 1 { get(p, grid, nx - 2, j, k) } else { get(p, grid, i + 1, j, k) };
                let p_im1 = if i == 0 { get(p, grid, 1, j, k) } else { get(p, grid, i - 1, j, k) };
                let p_jp1 = if j == ny - 1 { get(p, grid, i, ny - 2, k) } else { get(p, grid, i, j + 1, k) };
                let p_jm1 = if j == 0 { get(p, grid, i, 1, k) } else { get(p, grid, i, j - 1, k) };
                let (p_kp1, p_km1) = if k == nz - 1 {
                    let mirror = get(p, grid, i, j, nz - 2);
                    (mirror, mirror)
                } else {
                    (get(p, grid, i, j, k + 1), get(p, grid, i, j, k - 1))
                };

                let lap = chi
                    * ((p_ip1 - 2.0 * p_c + p_im1) / dx2
                        + (p_jp1 - 2.0 * p_c + p_jm1) / dy2
                        + (p_kp1 - 2.0 * p_c + p_km1) / dz2);

                out[idx] = coeff * p_c - lap;
            }
        }
    }
    out
}

/// Solve the implicit pressure update for one time step.
///
/// `source` should already contain q(x, t^{n+1}) minus the mechanical
/// coupling term alpha*(div(u^{n+1}) - div(u^n))/dt.
pub fn solve_diffusion(
    p_n: &Field3D,
    source: &Field3D,
    grid: &Grid3D,
    chi: f64,
    inv_q: f64,
    dt: f64,
    tol: f64,
    max_iter: usize,
) -> (Field3D, usize) {
    let coeff = inv_q / dt;
    let n = grid.n();
    let mut b = vec![0.0; n];
    for idx in 0..n {
        b[idx] = source.data[idx] + coeff * p_n.data[idx];
    }
    for j in 0..grid.ny {
        for i in 0..grid.nx {
            b[grid.idx(i, j, 0)] = 0.0;
        }
    }
    let (sol, iters) = conjugate_gradient(
        |v| apply_diffusion_operator(v, grid, chi, coeff),
        &b,
        p_n.data.clone(),
        tol,
        max_iter,
    );
    (Field3D { data: sol }, iters)
}
