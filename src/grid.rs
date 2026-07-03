/*Grid Module
Uniform structured 3D grid. Node-centered: node (0,0,0) sits exactly on the
domain corner, node (nx-1,ny-1,nz-1) on the opposite corner. z increases with
depth (z=0 is the free surface / top of the half-space approximation).
*/

#[derive(Clone, Copy, Debug)]
pub struct Grid3D {
    pub nx: usize,
    pub ny: usize,
    pub nz: usize,
    pub dx: f64,
    pub dy: f64,
    pub dz: f64,
}

impl Grid3D {
    pub fn new(nx: usize, ny: usize, nz: usize, dx: f64, dy: f64, dz: f64) -> Self {
        assert!(nx >= 3 && ny >= 3 && nz >= 3, "grid needs at least 3 nodes per axis");
        Self { nx, ny, nz, dx, dy, dz }
    }

    #[inline]
    pub fn n(&self) -> usize {
        self.nx * self.ny * self.nz
    }

    #[inline]
    pub fn idx(&self, i: usize, j: usize, k: usize) -> usize {
        i + self.nx * (j + self.ny * k)
    }

    #[inline]
    pub fn coords(&self, i: usize, j: usize, k: usize) -> (f64, f64, f64) {
        (i as f64 * self.dx, j as f64 * self.dy, k as f64 * self.dz)
    }

    /// Iterate over all (i, j, k) node indices.
    pub fn iter_nodes(&self) -> impl Iterator<Item = (usize, usize, usize)> + '_ {
        let (nx, ny, nz) = (self.nx, self.ny, self.nz);
        (0..nz).flat_map(move |k| (0..ny).flat_map(move |j| (0..nx).map(move |i| (i, j, k))))
    }
}
