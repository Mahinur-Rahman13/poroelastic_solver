/*Paramter Module
A poroelastic layer is fully defined by 5 parameters, in this module, i will calculate these 5 parameters
G = mu = Shear Modulus, stiffness against shape change (Pa)
nu = drained Poisson's ratio
nu_u = undrained Poisson's ratio
B = Skempton coefficient
D = Hydraulic diffusivity (m^2/s)
From these five, the coefficients in the equations are computed
*/

pub struct PoroLayer{
    pub g: f64,
    pub nu:f64, 
    pub nu_u:f64, 
    pub b: f64, 
    pub d:f64
}
impl PoroLayer{
    pub fn lambda(&self) -> f64{
        2.0*self.nu*self.g / (1.0-(2.0*self.nu))
    }
    pub fn alpha(&self) -> f64{
        3.0*(self.nu_u - self.nu)/((1.0-(2.0*self.nu))*(1.0+self.nu_u)*self.b)
    }
    pub fn q(&self) -> f64{
        let inv_q = (9.0/2.0)*(1.0-(2.0*self.nu_u))*(self.nu_u-self.nu)/((1.0-(2.0*self.nu))*(1.0+self.nu_u).powi(2)*self.g*self.b.powi(2));
        1.0/inv_q
    }
    pub fn chi(&self)-> f64{
        (9.0/2.0)*(1.0-self.nu_u)*(self.nu_u-self.nu)*self.d/((1.0-self.nu)*(1.0+self.nu_u).powi(2)*self.g*self.b.powi(2))
    }
}