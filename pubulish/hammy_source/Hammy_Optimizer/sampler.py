
import numpy as np
np.set_printoptions(suppress=True)

from scipy.stats import qmc
from scipy.stats.qmc import LatinHypercube as lhs
TOL = 1e-4


def lhs_sampler(iVars, T, seed = None):
    # modify bounds
    print(iVars)
    iVars = np.asarray(iVars)

    l_bounds = iVars[:, 0]
    u_bounds = iVars[:, 1]
    steps = iVars[:, 2]
    id_int = np.where(steps == 1)
    id_float = np.where(steps != 1)
    u_bounds[id_int] += 1
    u_bounds[id_float] += TOL
    
    # sample by quasi monte carlo
    sampler = lhs(d = len(iVars),seed=seed)
    sample = sampler.random(T)
    scaled_sample = qmc.scale(sample, l_bounds, u_bounds)
    
    # get integer
    scaled_sample[:, id_int] = np.floor(scaled_sample[:, id_int])
    
    return scaled_sample.tolist()



