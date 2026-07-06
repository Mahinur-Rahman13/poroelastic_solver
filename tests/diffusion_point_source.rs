// Validates the diffusion module against the classical analytical solution
// for a continuous point source of fluid switched on at t=0 in an infinite
// homogeneous medium (e.g. Carslaw & Jaeger, "Conduction of Heat in
// Solids"):
//
//   p(r, t) = (Q * q_vol) / (4*pi*D*r) * erfc(r / (2*sqrt(D*t)))
//
// where D = chi * Q is the hydraulic diffusivity. The source here is
// injected deep inside a domain that is large relative to the diffusion
// length sqrt(D*t) reached during the test, and far from the drained
// (Dirichlet) top boundary, so the finite domain approximates the infinite
// medium the analytical solution assumes.
use poroelastic_solver::diffusion::solve_diffusion;
use poroelastic_solver::field::Field3D;
use poroelastic_solver::grid::Grid3D;
use poroelastic_solver::source::InjectionWell;

fn erfc(x: f64) -> f64 {
    // Abramowitz & Stegun 7.1.26 rational approximation, accurate to ~1.5e-7.
    let sign = if x < 0.0 { -1.0 } else { 1.0 };
    let x = x.abs();
    let t = 1.0 / (1.0 + 0.3275911 * x);
    let y = 1.0
        - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * (-x * x).exp();
    1.0 - sign * y
}

#[test]
fn matches_analytical_continuous_point_source() {
    let grid = Grid3D::new(31, 31, 31, 15.0, 15.0, 15.0);
    let chi = 3.0e-11_f64; // mobility, m^2/(Pa*s)
    let inv_q = 3.0e-11_f64; // 1/Q, 1/Pa -- chosen so D = chi/inv_q = 1.0 m^2/s
    let diffusivity = chi / inv_q;

    let q_vol = 0.01_f64; // m^3/s
    let (x0, y0, z0) = (225.0, 225.0, 300.0); // 300 m from the drained top boundary
    let well = InjectionWell { x0, y0, z0, sigma: grid.dx, schedule: vec![(0.0, q_vol)] };

    let mut p = Field3D::zeros(&grid);
    let dt = 30.0;
    let n_steps = 40; // t_final = 1200 s, diffusion length sqrt(D*t) = 34.6 m
    let mut t = 0.0;
    for _ in 0..n_steps {
        t += dt;
        let source = well.source_field(&grid, t);
        let (p_new, _) = solve_diffusion(&p, &p, 0.0, &source, &grid, chi, inv_q, dt, 1e-10, 5000);
        p = p_new;
    }

    let q_modulus = 1.0 / inv_q; // Biot modulus Q
    let analytic = |r: f64| -> f64 {
        (q_modulus * q_vol) / (4.0 * std::f64::consts::PI * diffusivity * r) * erfc(r / (2.0 * (diffusivity * t).sqrt()))
    };

    // Compare along the x-direction at a couple of radii, well inside the
    // domain and far from any boundary.
    let i0 = (x0 / grid.dx).round() as usize;
    let j0 = (y0 / grid.dy).round() as usize;
    let k0 = (z0 / grid.dz).round() as usize;

    for &di in &[2usize, 3usize] {
        let r = di as f64 * grid.dx;
        let p_num = p.get(&grid, i0 + di, j0, k0);
        let p_ana = analytic(r);
        let rel_err = (p_num - p_ana).abs() / p_ana;
        assert!(
            rel_err < 0.2,
            "at r={r} m: numerical p={p_num:.4e} Pa vs analytical p={p_ana:.4e} Pa (rel. err {rel_err:.2})"
        );
    }
}
