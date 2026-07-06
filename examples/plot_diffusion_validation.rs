// Generates numerical-vs-analytical pressure data for the point-source
// diffusion validation (same setup as tests/diffusion_point_source.rs),
// across a range of radii, for plotting.
use poroelastic_solver::diffusion::solve_diffusion;
use poroelastic_solver::field::Field3D;
use poroelastic_solver::grid::Grid3D;
use poroelastic_solver::source::InjectionWell;
use std::fs::File;
use std::io::Write;

fn erfc(x: f64) -> f64 {
    let sign = if x < 0.0 { -1.0 } else { 1.0 };
    let x = x.abs();
    let t = 1.0 / (1.0 + 0.3275911 * x);
    let y = 1.0
        - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * (-x * x).exp();
    1.0 - sign * y
}

fn main() {
    let grid = Grid3D::new(31, 31, 31, 15.0, 15.0, 15.0);
    let chi = 3.0e-11_f64;
    let inv_q = 3.0e-11_f64;
    let diffusivity = chi / inv_q;
    let q_vol = 0.01_f64;
    let (x0, y0, z0) = (225.0, 225.0, 300.0);
    let well = InjectionWell { x0, y0, z0, sigma: grid.dx, schedule: vec![(0.0, q_vol)] };

    let mut p = Field3D::zeros(&grid);
    let dt = 30.0;
    let n_steps = 40; // t_final = 1200 s
    let mut t = 0.0;
    for _ in 0..n_steps {
        t += dt;
        let source = well.source_field(&grid, t);
        let (p_new, _) = solve_diffusion(&p, &p, 0.0, &source, &grid, chi, inv_q, dt, 1e-10, 5000);
        p = p_new;
    }

    let q_modulus = 1.0 / inv_q;
    let analytic = |r: f64| -> f64 {
        (q_modulus * q_vol) / (4.0 * std::f64::consts::PI * diffusivity * r) * erfc(r / (2.0 * (diffusivity * t).sqrt()))
    };

    let i0 = (x0 / grid.dx).round() as usize;
    let j0 = (y0 / grid.dy).round() as usize;
    let k0 = (z0 / grid.dz).round() as usize;

    let mut f = File::create("../validation_plots/diffusion_validation.csv").unwrap();
    writeln!(f, "r_m,numerical_Pa,analytical_Pa").unwrap();
    for di in 1..8usize {
        let r = di as f64 * grid.dx;
        let p_num = p.get(&grid, i0 + di, j0, k0);
        let p_ana = analytic(r);
        writeln!(f, "{r},{p_num},{p_ana}").unwrap();
    }
    println!("wrote ../validation_plots/diffusion_validation.csv at t={t}s");
}
