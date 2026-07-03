/*Poroelastic Solver
A finite-difference solver for the quasi-static, linear Biot poroelasticity
equations (Eqs. 1-2 of Zhai, Shirzaei, Manga & Chen, "Pore-pressure diffusion,
enhanced by poroelastic stresses, controls induced seismicity in Oklahoma",
PNAS 2019):

    G*Laplacian(u) + G/(1-2*nu)*grad(div(u)) - alpha*grad(p) = f(x,t)
    (1/Q) dp/dt + alpha d(div(u))/dt - div(chi*grad(p)) = q(x,t)

on a homogeneous, isotropic half-space approximated by a large rectangular
box: a traction-free, drained (p=0) surface at z=0, and fixed zero
displacement / no-flow far-field boundaries elsewhere.
*/
pub mod coupling;
pub mod diffusion;
pub mod elasticity;
pub mod field;
pub mod grid;
pub mod linalg;
pub mod param;
pub mod source;

pub use coupling::{SimState, SolverTolerances, StepReport};
pub use field::{Field3D, VectorField3D};
pub use grid::Grid3D;
pub use param::PoroLayer;
pub use source::InjectionWell;
