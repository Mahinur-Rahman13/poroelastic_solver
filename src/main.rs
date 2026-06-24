mod param;
fn main(){
    let layer = param::PoroLayer{
        g:0.4e9_f64, 
        nu:0.2, 
        nu_u:0.4,
        b:0.75, 
        d:1.0
    };
    let chi_val = layer.chi();
    let lambda_val = layer.lambda();
    let q_val = layer.q();
    let alpha_val = layer.alpha();
    println!("{}, {}, {}, {}", chi_val, lambda_val, q_val, alpha_val);
}