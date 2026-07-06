// Rung 0 verification: plug in Wang & Kumpel's (2003) own worked example
// (their TEST RESULTS section) and print the derived lambda, alpha, Q, chi
// for hand-check against Eqs. 3-6 of that paper.
use poroelastic_solver::param::PoroLayer;

fn main() {
    let layer = PoroLayer { g: 0.4e9, nu: 0.2, nu_u: 0.4, b: 0.75, d: 1.0 };

    println!("Inputs: G = {:.3e} Pa, nu = {}, nu_u = {}, B = {}, D = {} m^2/s", layer.g, layer.nu, layer.nu_u, layer.b, layer.d);
    println!();
    println!("lambda = {:.6e} Pa", layer.lambda());
    println!("alpha  = {:.6}", layer.alpha());
    println!("1/Q    = {:.6e} 1/Pa", layer.inv_q());
    println!("Q      = {:.6e} Pa", layer.q());
    println!("chi    = {:.6e} m^2/(Pa*s)", layer.chi());
}
