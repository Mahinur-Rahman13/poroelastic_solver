/*Elasticity Module
Finite-difference discretization of the quasi-static Navier-Cauchy equation
(Eq. 1 in Zhai et al. 2019):

    G * Laplacian(u) + G/(1-2*nu) * grad(div(u)) - alpha*grad(p) = f(x,t)

Rearranged with lambda = 2*G*nu/(1-2*nu) (so G/(1-2*nu) = lambda + G):

    G * Laplacian(u) + (lambda + G) * grad(div(u)) = alpha*grad(p) - f

Boundary conditions (see README):
  * x = 0, x = Lx, y = 0, y = Ly, z = Lz (bottom): fixed zero displacement
    ("far field" truncation of the half-space).
  * z = 0 (free surface): zero traction (sigma_xz = sigma_yz = sigma_zz = 0),
    assuming p = 0 there (enforced separately by the pressure Dirichlet BC).
*/
use crate::grid::Grid3D;
use crate::field::{Field3D, VectorField3D};
use crate::linalg::bicgstab;

#[inline]
fn is_fixed(grid: &Grid3D, i: usize, j: usize, k: usize) -> bool {
    i == 0 || i == grid.nx - 1 || j == 0 || j == grid.ny - 1 || k == grid.nz - 1
}

#[inline]
fn get(field: &[f64], grid: &Grid3D, i: usize, j: usize, k: usize) -> f64 {
    field[grid.idx(i, j, k)]
}

/// Ghost value of ux just above the free surface (k = -1), from sigma_xz = 0.
/// Returns 0 at the lateral edges, where the fixed zero-displacement
/// boundary dominates over the free-surface condition.
fn ghost_ux(ux: &[f64], uz: &[f64], grid: &Grid3D, i: usize, j: usize) -> f64 {
    if i == 0 || i == grid.nx - 1 || j == 0 || j == grid.ny - 1 {
        return 0.0;
    }
    let duz_dx = (get(uz, grid, i + 1, j, 0) - get(uz, grid, i - 1, j, 0)) / (2.0 * grid.dx);
    get(ux, grid, i, j, 1) + 2.0 * grid.dz * duz_dx
}

/// Ghost value of uy just above the free surface, from sigma_yz = 0.
fn ghost_uy(uy: &[f64], uz: &[f64], grid: &Grid3D, i: usize, j: usize) -> f64 {
    if i == 0 || i == grid.nx - 1 || j == 0 || j == grid.ny - 1 {
        return 0.0;
    }
    let duz_dy = (get(uz, grid, i, j + 1, 0) - get(uz, grid, i, j - 1, 0)) / (2.0 * grid.dy);
    get(uy, grid, i, j, 1) + 2.0 * grid.dz * duz_dy
}

/// Ghost value of uz just above the free surface, from sigma_zz = 0 (p = 0 there).
fn ghost_uz(ux: &[f64], uy: &[f64], uz: &[f64], grid: &Grid3D, lambda: f64, g: f64, i: usize, j: usize) -> f64 {
    if i == 0 || i == grid.nx - 1 || j == 0 || j == grid.ny - 1 {
        return 0.0;
    }
    let dux_dx = (get(ux, grid, i + 1, j, 0) - get(ux, grid, i - 1, j, 0)) / (2.0 * grid.dx);
    let duy_dy = (get(uy, grid, i, j + 1, 0) - get(uy, grid, i, j - 1, 0)) / (2.0 * grid.dy);
    get(uz, grid, i, j, 1) + 2.0 * grid.dz * (lambda / (lambda + 2.0 * g)) * (dux_dx + duy_dy)
}

/// Apply the discrete Navier-Cauchy operator to a flat [ux | uy | uz] vector.
pub fn apply_elastic_operator(u_flat: &[f64], grid: &Grid3D, g: f64, lambda: f64) -> Vec<f64> {
    let n = grid.n();
    let ux = &u_flat[0..n];
    let uy = &u_flat[n..2 * n];
    let uz = &u_flat[2 * n..3 * n];
    let mut out = vec![0.0; 3 * n];

    let (nx, ny, nz) = (grid.nx, grid.ny, grid.nz);
    let (dx, dy, dz) = (grid.dx, grid.dy, grid.dz);
    let (dx2, dy2, dz2) = (dx * dx, dy * dy, dz * dz);
    let lg = lambda + g;
    let l2g = lambda + 2.0 * g;

    for k in 0..nz {
        for j in 0..ny {
            for i in 0..nx {
                let idx = grid.idx(i, j, k);
                if is_fixed(grid, i, j, k) {
                    out[idx] = ux[idx];
                    out[n + idx] = uy[idx];
                    out[2 * n + idx] = uz[idx];
                    continue;
                }

                let ux_c = ux[idx];
                let uy_c = uy[idx];
                let uz_c = uz[idx];

                let ux_ip1 = get(ux, grid, i + 1, j, k);
                let ux_im1 = get(ux, grid, i - 1, j, k);
                let ux_jp1 = get(ux, grid, i, j + 1, k);
                let ux_jm1 = get(ux, grid, i, j - 1, k);
                let uy_ip1 = get(uy, grid, i + 1, j, k);
                let uy_im1 = get(uy, grid, i - 1, j, k);
                let uy_jp1 = get(uy, grid, i, j + 1, k);
                let uy_jm1 = get(uy, grid, i, j - 1, k);
                let uz_ip1 = get(uz, grid, i + 1, j, k);
                let uz_im1 = get(uz, grid, i - 1, j, k);
                let uz_jp1 = get(uz, grid, i, j + 1, k);
                let uz_jm1 = get(uz, grid, i, j - 1, k);

                let ux_kp1 = get(ux, grid, i, j, k + 1);
                let uy_kp1 = get(uy, grid, i, j, k + 1);
                let uz_kp1 = get(uz, grid, i, j, k + 1);
                let (ux_km1, uy_km1, uz_km1) = if k == 0 {
                    (
                        ghost_ux(ux, uz, grid, i, j),
                        ghost_uy(uy, uz, grid, i, j),
                        ghost_uz(ux, uy, uz, grid, lambda, g, i, j),
                    )
                } else {
                    (get(ux, grid, i, j, k - 1), get(uy, grid, i, j, k - 1), get(uz, grid, i, j, k - 1))
                };

                let d2ux_dx2 = (ux_ip1 - 2.0 * ux_c + ux_im1) / dx2;
                let d2ux_dy2 = (ux_jp1 - 2.0 * ux_c + ux_jm1) / dy2;
                let d2ux_dz2 = (ux_kp1 - 2.0 * ux_c + ux_km1) / dz2;

                let d2uy_dx2 = (uy_ip1 - 2.0 * uy_c + uy_im1) / dx2;
                let d2uy_dy2 = (uy_jp1 - 2.0 * uy_c + uy_jm1) / dy2;
                let d2uy_dz2 = (uy_kp1 - 2.0 * uy_c + uy_km1) / dz2;

                let d2uz_dx2 = (uz_ip1 - 2.0 * uz_c + uz_im1) / dx2;
                let d2uz_dy2 = (uz_jp1 - 2.0 * uz_c + uz_jm1) / dy2;
                let d2uz_dz2 = (uz_kp1 - 2.0 * uz_c + uz_km1) / dz2;

                // in-plane cross derivatives (no ghosts needed)
                let d2uy_dxdy = (get(uy, grid, i + 1, j + 1, k) - get(uy, grid, i + 1, j - 1, k)
                    - get(uy, grid, i - 1, j + 1, k)
                    + get(uy, grid, i - 1, j - 1, k))
                    / (4.0 * dx * dy);
                let d2ux_dxdy = (get(ux, grid, i + 1, j + 1, k) - get(ux, grid, i + 1, j - 1, k)
                    - get(ux, grid, i - 1, j + 1, k)
                    + get(ux, grid, i - 1, j - 1, k))
                    / (4.0 * dx * dy);

                // cross derivatives involving z (ghost needed at k == 0)
                let (uz_ip1_km1, uz_im1_km1) = if k == 0 {
                    (ghost_uz(ux, uy, uz, grid, lambda, g, i + 1, j), ghost_uz(ux, uy, uz, grid, lambda, g, i - 1, j))
                } else {
                    (get(uz, grid, i + 1, j, k - 1), get(uz, grid, i - 1, j, k - 1))
                };
                let d2uz_dxdz = (get(uz, grid, i + 1, j, k + 1) - get(uz, grid, i - 1, j, k + 1) - uz_ip1_km1 + uz_im1_km1)
                    / (4.0 * dx * dz);

                let (uz_jp1_km1, uz_jm1_km1) = if k == 0 {
                    (ghost_uz(ux, uy, uz, grid, lambda, g, i, j + 1), ghost_uz(ux, uy, uz, grid, lambda, g, i, j - 1))
                } else {
                    (get(uz, grid, i, j + 1, k - 1), get(uz, grid, i, j - 1, k - 1))
                };
                let d2uz_dydz = (get(uz, grid, i, j + 1, k + 1) - get(uz, grid, i, j - 1, k + 1) - uz_jp1_km1 + uz_jm1_km1)
                    / (4.0 * dy * dz);

                let (ux_ip1_km1, ux_im1_km1) = if k == 0 {
                    (ghost_ux(ux, uz, grid, i + 1, j), ghost_ux(ux, uz, grid, i - 1, j))
                } else {
                    (get(ux, grid, i + 1, j, k - 1), get(ux, grid, i - 1, j, k - 1))
                };
                let d2ux_dxdz = (get(ux, grid, i + 1, j, k + 1) - get(ux, grid, i - 1, j, k + 1) - ux_ip1_km1 + ux_im1_km1)
                    / (4.0 * dx * dz);

                let (uy_jp1_km1, uy_jm1_km1) = if k == 0 {
                    (ghost_uy(uy, uz, grid, i, j + 1), ghost_uy(uy, uz, grid, i, j - 1))
                } else {
                    (get(uy, grid, i, j + 1, k - 1), get(uy, grid, i, j - 1, k - 1))
                };
                let d2uy_dydz = (get(uy, grid, i, j + 1, k + 1) - get(uy, grid, i, j - 1, k + 1) - uy_jp1_km1 + uy_jm1_km1)
                    / (4.0 * dy * dz);

                let lx = l2g * d2ux_dx2 + g * d2ux_dy2 + g * d2ux_dz2 + lg * d2uy_dxdy + lg * d2uz_dxdz;
                let ly = lg * d2ux_dxdy + l2g * d2uy_dy2 + g * d2uy_dx2 + g * d2uy_dz2 + lg * d2uz_dydz;
                let lz = lg * d2ux_dxdz + lg * d2uy_dydz + l2g * d2uz_dz2 + g * d2uz_dx2 + g * d2uz_dy2;

                out[idx] = lx;
                out[n + idx] = ly;
                out[2 * n + idx] = lz;
            }
        }
    }
    out
}

/// Solve the quasi-static elasticity equation for u given a right-hand side
/// (typically alpha*grad(p) - f), starting from an initial guess `x0`.
pub fn solve_elasticity(
    rhs: &VectorField3D,
    grid: &Grid3D,
    g: f64,
    lambda: f64,
    x0: VectorField3D,
    tol: f64,
    max_iter: usize,
) -> (VectorField3D, usize) {
    let n = grid.n();
    let mut b = rhs.to_flat();
    // Zero the RHS at fixed boundary DOFs to keep them locked at zero.
    for k in 0..grid.nz {
        for j in 0..grid.ny {
            for i in 0..grid.nx {
                if is_fixed(grid, i, j, k) {
                    let idx = grid.idx(i, j, k);
                    b[idx] = 0.0;
                    b[n + idx] = 0.0;
                    b[2 * n + idx] = 0.0;
                }
            }
        }
    }
    let (sol, iters) = bicgstab(|v| apply_elastic_operator(v, grid, g, lambda), &b, x0.to_flat(), tol, max_iter);
    (VectorField3D::from_flat(grid, &sol), iters)
}

/// Divergence of the displacement field, evaluated everywhere on the grid
/// (needed as a source term for the pressure diffusion equation). Uses the
/// same free-surface ghost as the elastic operator so the two stay consistent.
pub fn divergence(u: &VectorField3D, grid: &Grid3D, lambda: f64, g: f64) -> Field3D {
    let (nx, ny, nz) = (grid.nx, grid.ny, grid.nz);
    let (dx, dy, dz) = (grid.dx, grid.dy, grid.dz);
    let ux = &u.ux.data;
    let uy = &u.uy.data;
    let uz = &u.uz.data;
    let mut out = Field3D::zeros(grid);

    for k in 0..nz {
        for j in 0..ny {
            for i in 0..nx {
                let dux_dx = if i == 0 {
                    get(ux, grid, 1, j, k) / dx
                } else if i == nx - 1 {
                    -get(ux, grid, nx - 2, j, k) / dx
                } else {
                    (get(ux, grid, i + 1, j, k) - get(ux, grid, i - 1, j, k)) / (2.0 * dx)
                };
                let duy_dy = if j == 0 {
                    get(uy, grid, i, 1, k) / dy
                } else if j == ny - 1 {
                    -get(uy, grid, i, ny - 2, k) / dy
                } else {
                    (get(uy, grid, i, j + 1, k) - get(uy, grid, i, j - 1, k)) / (2.0 * dy)
                };
                let duz_dz = if k == 0 {
                    let ghost = ghost_uz(ux, uy, uz, grid, lambda, g, i, j);
                    (get(uz, grid, i, j, 1) - ghost) / (2.0 * dz)
                } else if k == nz - 1 {
                    -get(uz, grid, i, j, nz - 2) / dz
                } else {
                    (get(uz, grid, i, j, k + 1) - get(uz, grid, i, j, k - 1)) / (2.0 * dz)
                };
                out.data[grid.idx(i, j, k)] = dux_dx + duy_dy + duz_dz;
            }
        }
    }
    out
}
