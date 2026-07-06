// Runs our own 3D Cartesian FD solver on (an approximation of) the Wang &
// Kumpel (2003) homogeneous half-space test case: mu=0.4 GPa, nu=0.2,
// nu_u=0.4, B=0.75, D=1.0 m^2/s, injection at 60 m depth, rate 32 m^3/hr,
// observed at r=40 m for depths z=5,15,45,75 m -- the same setup used to
// drive POEL2024 for comparison.
use poroelastic_solver::coupling::{step, SimState, SolverTolerances};
use poroelastic_solver::grid::Grid3D;
use poroelastic_solver::param::PoroLayer;
use poroelastic_solver::source::InjectionWell;
use std::fs::File;
use std::io::Write;

fn main() {
    let params = PoroLayer { g: 0.4e9, nu: 0.2, nu_u: 0.4, b: 0.75, d: 1.0 };

    let (nx, ny, nz) = (49, 49, 43);
    let (dx, dy, dz) = (5.0, 5.0, 5.0);
    let grid = Grid3D::new(nx, ny, nz, dx, dy, dz);

    let (x0, y0, z0) = (120.0, 120.0, 60.0);
    let well = InjectionWell { x0, y0, z0, sigma: 1.5 * dx, schedule: vec![(0.0, 32.0 / 3600.0)] };

    let mut state = SimState::zeros(&grid);
    let tol = SolverTolerances::default();

    let dt = 100.0;
    let n_steps = 80; // t_final = 8000 s

    let i0 = (x0 / dx).round() as usize;
    let j0 = (y0 / dy).round() as usize;
    let r_offset = (40.0 / dx).round() as usize; // r = 40 m
    let depths_m = [5.0, 15.0, 45.0, 75.0];
    let k_indices: Vec<usize> = depths_m.iter().map(|d| (d / dz).round() as usize).collect();

    let mut f = File::create("../validation_plots/rust_solver_wk2003.csv").unwrap();
    writeln!(f, "time_s,p_z5,p_z15,p_z45,p_z75").unwrap();

    for step_i in 0..n_steps {
        let t = (step_i as f64 + 1.0) * dt;
        let q_field = well.source_field(&grid, t);
        let report = step(&mut state, &grid, &params, &q_field, dt, &tol);

        let p_vals: Vec<f64> = k_indices.iter().map(|&k| state.p.get(&grid, i0 + r_offset, j0, k)).collect();
        writeln!(f, "{t},{},{},{},{}", p_vals[0], p_vals[1], p_vals[2], p_vals[3]).unwrap();

        println!(
            "t={t:6.0}s  p(z=5,15,45,75)= {:+.3e} {:+.3e} {:+.3e} {:+.3e} Pa  picard_iters={}",
            p_vals[0], p_vals[1], p_vals[2], p_vals[3], report.picard_iters
        );
    }
    println!("wrote ../validation_plots/rust_solver_wk2003.csv");
}
