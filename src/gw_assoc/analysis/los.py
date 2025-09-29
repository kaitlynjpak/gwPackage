zinterp = np.linspace(0,0.5,5000)
dz = zinterp[1] - zinterp[0]
speed_of_light = constants.c.to('km/s').value
H0Planck = Planck15.H0.value
Om0Planck = Planck15.Om0

def dL_at_z_H0(z,h0,Om0):
    cosmo = FlatLambdaCDM(H0=h0, Om0=Om0)
    dLs = cosmo.luminosity_distance(z).to(u.Mpc).value
    return dLs

def z_at_dL_H0(dL,h0,Om0):
    cosmo = FlatLambdaCDM(H0=h0, Om0=Om0)
    dLs = cosmo.luminosity_distance(zinterp).to(u.Mpc).value  
    z_at_dL = interp1d(dLs,zinterp)
    return z_at_dL(dL)

def E(z,Om):
    return np.sqrt(Om*(1+z)**3 + (1.0-Om))

def dz_by_dL_H0(z,dL,h0,Om0):
    return 1/(dL/(1+z) + speed_of_light*(1+z)/(h0*E(z,Om0)))

def dL_by_z_H0(z,dL,h0,Om0):
    return dL/(1+z) + speed_of_light*(1+z)/(h0*E(z,Om0))

def dvdz(z, H0, Om0):
    cosmo = FlatLambdaCDM(H0=H0, Om0=Om0)
    dvdz = 4*np.pi*cosmo.differential_comoving_volume(z).to(u.Gpc**3/u.sr).value
    return dvdz

