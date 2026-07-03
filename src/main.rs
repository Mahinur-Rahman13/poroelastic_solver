use poroelastic_solver::coupling::{step, SimState, SolverTolerances};
use poroelastic_solver::grid::Grid3D;
use poroelastic_solver::param::PoroLayer;
use poroelastic_solver::source::InjectionWell;
use std::fs::File;
use std::io::{BufWriter, Write};

/// Nearest grid index to a physical coordinate.
fn nearest_index(coord: f64, spacing: f64, n: usize) -> usize {
    ((coord / spacing).round() as isize).clamp(0, n as isize - 1) as usize
}

fn main() {
    // Homogeneous poroelastic medium, roughly representative of a
    // permeable basement formation (see Zhai et al. 2019, Table S2, for
    // the diffusivity range 1.5-4.0 m^2/s used for Oklahoma).
    let params = PoroLayer { g: 2.0e10, nu: 0.25, nu_u: 0.30, b: 0.6, d: 1.5 };
    println!(
        "Derived poroelastic constants: lambda = {:.3e} Pa, alpha = {:.3}, Q = {:.3e} Pa, chi (mobility) = {:.3e} m^2/(Pa*s)",
        params.lambda(),
        params.alpha(),
        params.q(),
        params.chi()
    );

    // Domain: 6 km cube, injection well at 3 km depth, centered laterally.
    // (chi/inv_q recovers the input diffusivity D = 1.5 m^2/s; the domain
    // half-width should stay well above sqrt(D * t_max) so the fixed/no-flow
    // far-field boundaries don't contaminate the solution.)
    let (nx, ny, nz) = (41, 41, 41);
    let (dx, dy, dz) = (150.0, 150.0, 150.0);
    let grid = Grid3D::new(nx, ny, nz, dx, dy, dz);

    let (x0, y0, z0) = (3000.0, 3000.0, 3000.0);
    let well = InjectionWell {
        x0,
        y0,
        z0,
        sigma: 1.5 * dx,
        schedule: vec![(0.0, 0.005)], // 0.005 m^3/s from t = 0 onward
    };

    let mut state = SimState::zeros(&grid);
    let tol = SolverTolerances::default();

    let dt = 86_400.0; // 1 day
    let n_steps = 60;

    let i0 = nearest_index(x0, dx, nx);
    let j0 = nearest_index(y0, dy, ny);
    let k_surface = 0;
    let k_well = nearest_index(z0, dz, nz);
    let i_offset = nearest_index(x0 + 500.0, dx, nx);

    let csv = File::create("injection_timeseries.csv").expect("create csv");
    let mut csv = BufWriter::new(csv);
    writeln!(csv, "time_days,p_at_well_Pa,p_above_well_Pa,uz_surface_above_well_m,p_surface_500m_offset_Pa,picard_iters").unwrap();

    for step_i in 0..n_steps {
        let t = (step_i as f64 + 1.0) * dt;
        let q_field = well.source_field(&grid, t);
        let report = step(&mut state, &grid, &params, &q_field, dt, &tol);

        let p_well = state.p.get(&grid, i0, j0, k_well);
        let p_above = state.p.get(&grid, i0, j0, k_surface);
        let uz_surface = state.u.uz.get(&grid, i0, j0, k_surface);
        let p_offset = state.p.get(&grid, i_offset, j0, k_surface);

        writeln!(
            csv,
            "{:.4},{:.6e},{:.6e},{:.6e},{:.6e},{}",
            t / 86_400.0,
            p_well,
            p_above,
            uz_surface,
            p_offset,
            report.picard_iters
        )
        .unwrap();

        println!(
            "day {:5.1}: p_well = {:+.3e} Pa, uz_surface = {:+.3e} m, picard_iters = {} (dp = {:.2e})",
            t / 86_400.0,
            p_well,
            uz_surface,
            report.picard_iters,
            report.last_p_change
        );
    }

    write_vtk("final_field.vtk", &grid, &state).expect("write vtk");
    println!("\nWrote injection_timeseries.csv and final_field.vtk (open the latter in ParaView).");
}

fn write_vtk(path: &str, grid: &Grid3D, state: &SimState) -> std::io::Result<()> {
    let mut f = BufWriter::new(File::create(path)?);
    writeln!(f, "# vtk DataFile Version 3.0")?;
    writeln!(f, "poroelastic solver output")?;
    writeln!(f, "ASCII")?;
    writeln!(f, "DATASET STRUCTURED_POINTS")?;
    writeln!(f, "DIMENSIONS {} {} {}", grid.nx, grid.ny, grid.nz)?;
    writeln!(f, "ORIGIN 0 0 0")?;
    writeln!(f, "SPACING {} {} {}", grid.dx, grid.dy, grid.dz)?;
    writeln!(f, "POINT_DATA {}", grid.n())?;
    writeln!(f, "SCALARS pressure_Pa double 1")?;
    writeln!(f, "LOOKUP_TABLE default")?;
    for v in &state.p.data {
        writeln!(f, "{:e}", v)?;
    }
    writeln!(f, "VECTORS displacement_m double")?;
    for idx in 0..grid.n() {
        writeln!(f, "{:e} {:e} {:e}", state.u.ux.data[idx], state.u.uy.data[idx], state.u.uz.data[idx])?;
    }
    Ok(())
}
