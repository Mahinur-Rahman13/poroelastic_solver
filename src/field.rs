/*Field Module
Scalar and vector fields living on a Grid3D, stored as flat Vec<f64> in
x-fastest order (matches Grid3D::idx).
*/
use crate::grid::Grid3D;

#[derive(Clone, Debug)]
pub struct Field3D {
    pub data: Vec<f64>,
}

impl Field3D {
    pub fn zeros(grid: &Grid3D) -> Self {
        Self { data: vec![0.0; grid.n()] }
    }

    #[inline]
    pub fn get(&self, grid: &Grid3D, i: usize, j: usize, k: usize) -> f64 {
        self.data[grid.idx(i, j, k)]
    }

    #[inline]
    pub fn set(&mut self, grid: &Grid3D, i: usize, j: usize, k: usize, v: f64) {
        self.data[grid.idx(i, j, k)] = v;
    }

    pub fn max_abs(&self) -> f64 {
        self.data.iter().fold(0.0_f64, |m, &v| m.max(v.abs()))
    }
}

#[derive(Clone, Debug)]
pub struct VectorField3D {
    pub ux: Field3D,
    pub uy: Field3D,
    pub uz: Field3D,
}

impl VectorField3D {
    pub fn zeros(grid: &Grid3D) -> Self {
        Self { ux: Field3D::zeros(grid), uy: Field3D::zeros(grid), uz: Field3D::zeros(grid) }
    }

    /// Pack into a single flat vector [ux | uy | uz] for use with the generic linear solver.
    pub fn to_flat(&self) -> Vec<f64> {
        let n = self.ux.data.len();
        let mut v = Vec::with_capacity(3 * n);
        v.extend_from_slice(&self.ux.data);
        v.extend_from_slice(&self.uy.data);
        v.extend_from_slice(&self.uz.data);
        v
    }

    pub fn from_flat(grid: &Grid3D, flat: &[f64]) -> Self {
        let n = grid.n();
        assert_eq!(flat.len(), 3 * n);
        Self {
            ux: Field3D { data: flat[0..n].to_vec() },
            uy: Field3D { data: flat[n..2 * n].to_vec() },
            uz: Field3D { data: flat[2 * n..3 * n].to_vec() },
        }
    }
}
