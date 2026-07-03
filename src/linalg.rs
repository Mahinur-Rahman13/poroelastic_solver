/*Linear Algebra Module
Matrix-free iterative solvers. The elasticity and diffusion operators never
materialize a matrix; they are applied as stencil functions on flat Vec<f64>
unknown vectors. Conjugate gradient (CG) is used for the diffusion operator,
which is provably symmetric positive-definite with our boundary treatment.
BiCGSTAB is used for the elasticity operator, whose free-surface (traction-
free) boundary stencil is not guaranteed to be exactly matrix-symmetric, so a
solver that tolerates mild non-symmetry is the safer choice.
*/

#[inline]
fn dot(a: &[f64], b: &[f64]) -> f64 {
    a.iter().zip(b).map(|(x, y)| x * y).sum()
}

#[inline]
fn norm(a: &[f64]) -> f64 {
    dot(a, a).sqrt()
}

/// Solve A x = b for a symmetric positive-definite operator `apply_a`.
pub fn conjugate_gradient<F>(
    apply_a: F,
    b: &[f64],
    x0: Vec<f64>,
    tol: f64,
    max_iter: usize,
) -> (Vec<f64>, usize)
where
    F: Fn(&[f64]) -> Vec<f64>,
{
    let n = b.len();
    let mut x = x0;
    let ax0 = apply_a(&x);
    let mut r: Vec<f64> = (0..n).map(|i| b[i] - ax0[i]).collect();
    let mut p = r.clone();
    let mut rs_old = dot(&r, &r);

    let b_norm = norm(b).max(1e-300);
    if rs_old.sqrt() / b_norm < tol {
        return (x, 0);
    }

    for it in 0..max_iter {
        let ap = apply_a(&p);
        let p_ap = dot(&p, &ap);
        if p_ap.abs() < 1e-300 {
            break;
        }
        let alpha = rs_old / p_ap;
        for i in 0..n {
            x[i] += alpha * p[i];
            r[i] -= alpha * ap[i];
        }
        let rs_new = dot(&r, &r);
        if rs_new.sqrt() / b_norm < tol {
            return (x, it + 1);
        }
        let beta = rs_new / rs_old;
        for i in 0..n {
            p[i] = r[i] + beta * p[i];
        }
        rs_old = rs_new;
    }
    (x, max_iter)
}

/// Solve A x = b for a general (possibly non-symmetric) operator `apply_a`
/// using stabilized biconjugate gradients.
pub fn bicgstab<F>(apply_a: F, b: &[f64], x0: Vec<f64>, tol: f64, max_iter: usize) -> (Vec<f64>, usize)
where
    F: Fn(&[f64]) -> Vec<f64>,
{
    let n = b.len();
    let mut x = x0;
    let ax0 = apply_a(&x);
    let mut r: Vec<f64> = (0..n).map(|i| b[i] - ax0[i]).collect();
    let r_hat0 = r.clone();

    let b_norm = norm(b).max(1e-300);
    if norm(&r) / b_norm < tol {
        return (x, 0);
    }

    let mut rho_prev = 1.0;
    let mut alpha = 1.0;
    let mut omega = 1.0;
    let mut v = vec![0.0; n];
    let mut p = vec![0.0; n];

    for it in 0..max_iter {
        let rho = dot(&r_hat0, &r);
        if rho.abs() < 1e-300 {
            break;
        }
        if it == 0 {
            p.copy_from_slice(&r);
        } else {
            let beta = (rho / rho_prev) * (alpha / omega);
            for i in 0..n {
                p[i] = r[i] + beta * (p[i] - omega * v[i]);
            }
        }
        v = apply_a(&p);
        let r_hat0_v = dot(&r_hat0, &v);
        if r_hat0_v.abs() < 1e-300 {
            break;
        }
        alpha = rho / r_hat0_v;
        let mut h = vec![0.0; n];
        let mut s = vec![0.0; n];
        for i in 0..n {
            h[i] = x[i] + alpha * p[i];
            s[i] = r[i] - alpha * v[i];
        }
        if norm(&s) / b_norm < tol {
            x = h;
            return (x, it + 1);
        }
        let t = apply_a(&s);
        let t_dot_t = dot(&t, &t);
        omega = if t_dot_t.abs() < 1e-300 { 0.0 } else { dot(&t, &s) / t_dot_t };
        for i in 0..n {
            x[i] = h[i] + omega * s[i];
            r[i] = s[i] - omega * t[i];
        }
        if norm(&r) / b_norm < tol {
            return (x, it + 1);
        }
        rho_prev = rho;
        if omega.abs() < 1e-300 {
            break;
        }
    }
    (x, max_iter)
}
