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
        1.0 / self.inv_q()
    }
    /// 1/Q, the specific storage coefficient at constant strain that multiplies
    /// dp/dt in Eq. 2 of Zhai et al. (2019).
    pub fn inv_q(&self) -> f64{
        (9.0/2.0)*(1.0-(2.0*self.nu_u))*(self.nu_u-self.nu)/((1.0-(2.0*self.nu))*(1.0+self.nu_u).powi(2)*self.g*self.b.powi(2))
    }
    pub fn chi(&self)-> f64{
        (9.0/2.0)*(1.0-self.nu_u)*(self.nu_u-self.nu)*self.d/((1.0-self.nu)*(1.0+self.nu_u).powi(2)*self.g*self.b.powi(2))
    }
    /// Drained bulk modulus K = lambda + 2G/3.
    pub fn k_dr(&self) -> f64 {
        self.lambda() + 2.0 * self.g / 3.0
    }
}