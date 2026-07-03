/*Source Module
Volumetric fluid injection source term q(x,t) [1/s] for the pressure
diffusion equation: a point injection well smoothed over a small Gaussian
radius (a true delta function is not representable on a finite-difference
grid), with a piecewise-constant injection-rate schedule in time.
*/
use crate::field::Field3D;
use crate::grid::Grid3D;

/// A single injection well at (x0, y0, z0) [m], smoothed by a Gaussian of
/// standard deviation `sigma` [m] (a couple of grid spacings is typical).
pub struct InjectionWell {
    pub x0: f64,
    pub y0: f64,
    pub z0: f64,
    pub sigma: f64,
    /// (start_time, rate) pairs in ascending time order [s], [m^3/s]. The
    /// rate applies from its start_time until the next entry's start_time.
    pub schedule: Vec<(f64, f64)>,
}

impl InjectionWell {
    pub fn rate_at(&self, t: f64) -> f64 {
        let mut rate = 0.0;
        for &(t0, r) in &self.schedule {
            if t >= t0 {
                rate = r;
            } else {
                break;
            }
        }
        rate
    }

    /// Volumetric source field q(x, t) = rate(t) * normalized_gaussian(x - x_well),
    /// in units of 1/s (volume injected per unit bulk volume per unit time).
    pub fn source_field(&self, grid: &Grid3D, t: f64) -> Field3D {
        let rate = self.rate_at(t);
        let mut field = Field3D::zeros(grid);
        if rate == 0.0 {
            return field;
        }
        let two_sigma2 = 2.0 * self.sigma * self.sigma;
        let norm = (2.0 * std::f64::consts::PI * self.sigma * self.sigma).powf(1.5);

        let mut total = 0.0;
        for (i, j, k) in grid.iter_nodes() {
            let (x, y, z) = grid.coords(i, j, k);
            let r2 = (x - self.x0).powi(2) + (y - self.y0).powi(2) + (z - self.z0).powi(2);
            let w = (-r2 / two_sigma2).exp() / norm;
            field.set(grid, i, j, k, w);
            total += w;
        }
        // Renormalize numerically so the discrete sum * cell volume integrates
        // to exactly 1, then scale by the injection rate.
        let cell_volume = grid.dx * grid.dy * grid.dz;
        let scale = if total * cell_volume > 0.0 { 1.0 / (total * cell_volume) } else { 0.0 };
        for v in field.data.iter_mut() {
            *v *= scale * rate;
        }
        field
    }
}
