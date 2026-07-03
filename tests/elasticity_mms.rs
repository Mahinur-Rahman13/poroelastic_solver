// Method-of-manufactured-solutions check for the Navier-Cauchy stencil.
//
// Central differences are exact for quadratic polynomials, so plugging a
// quadratic displacement field into the discrete operator at a strictly
// interior node (no ghost/boundary logic involved) must reproduce the exact
// analytic value of G*Laplacian(u) + (lambda+G)*grad(div(u)) to floating
// point precision. This isolates and validates the hand-derived stencil
// coefficients independently of the free-surface / far-field boundary code.
use poroelastic_solver::elasticity::apply_elastic_operator;
use poroelastic_solver::grid::Grid3D;

#[test]
fn quadratic_field_matches_analytic_navier_operator() {
    let grid = Grid3D::new(9, 9, 9, 10.0, 10.0, 10.0);
    let n = grid.n();
    let g = 3.0e10_f64;
    let lambda = 2.0e10_f64;

    // ux = x^2 + 2xy + 3xz, uy = y^2 + 2yz + 3xy, uz = z^2 + 2xz + 3yz
    let mut u = vec![0.0; 3 * n];
    for (i, j, k) in grid.iter_nodes() {
        let (x, y, z) = grid.coords(i, j, k);
        let idx = grid.idx(i, j, k);
        u[idx] = x * x + 2.0 * x * y + 3.0 * x * z;
        u[n + idx] = y * y + 2.0 * y * z + 3.0 * x * y;
        u[2 * n + idx] = z * z + 2.0 * x * z + 3.0 * y * z;
    }

    let out = apply_elastic_operator(&u, &grid, g, lambda);

    // Analytic value (same for all three components, by construction).
    let expected = 7.0 * lambda + 9.0 * g;

    // Check a handful of strictly interior nodes (away from any boundary).
    for &(i, j, k) in &[(4usize, 4usize, 4usize), (3, 5, 4), (5, 3, 6), (4, 6, 3)] {
        let idx = grid.idx(i, j, k);
        let rel = |v: f64| (v - expected).abs() / expected.abs();
        assert!(rel(out[idx]) < 1e-8, "Lx mismatch at ({i},{j},{k}): got {}, expected {}", out[idx], expected);
        assert!(rel(out[n + idx]) < 1e-8, "Ly mismatch at ({i},{j},{k}): got {}, expected {}", out[n + idx], expected);
        assert!(rel(out[2 * n + idx]) < 1e-8, "Lz mismatch at ({i},{j},{k}): got {}, expected {}", out[2 * n + idx], expected);
    }
}
