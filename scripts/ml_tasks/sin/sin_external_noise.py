from __future__ import division
import jedi.jedi as jedi
from jedi.utils import plot, init_tools, seedutil, noise_gen
import cPickle

import matplotlib.pylab as plt
import numpy as np
import sys

def main(seed):
    # Setting Seeds
    seeds = seedutil.load_seeds("main_seeds.npy", "../../../data/stability")
    if seed is not None:
        seeds = seeds[:seed]

    # sine-wave target
    target = lambda t0: np.cos(2 * np.pi * t0/.5)

    #Simulation parameters for FORCE
    parameters = {}
    parameters['dt'] = dt =.01      # time step
    parameters['tmax'] = tmax = 10   # simulation length
    parameters['tstop'] = tstop = 5 # learning stop time
    parameters['tstart'] = tstart = 0 # learning start
    parameters['N'] = N = 300      # size of stochastic pool
    parameters['lr'] = lr = 1   # learning rate
    parameters['rho'] = rho = 1.25 # spectral radius of J
    parameters['sparsity'] = sparsity = (.1,1,1) # weight sparsity
    parameters['t_count'] = t_count = int(tmax/dt+2) # number of time steps
    parameters['noise_ext_var'] = noise_ext_var = .3
    parameters['noise'] = noise = 'normal'

    #Noise matrix
    if noise == 'normal':
        ext_noise_mat = np.random.normal(0, noise_ext_var, t_count)
    elif noise =='pink':
        ext_noise_mat = np.array([noise_gen.voss(N) for _ in range(t_count)])


    targets = target(np.linspace(0, 10, t_count)) + ext_noise_mat

    errors_noise = []
    derrors_noise = []
    zs_noise = []
    dzs_noise = []

    for seedling in seeds:
        J, Wz, _, x0, u, w = init_tools.set_simulation_parameters(seedling, N, 1, p=sparsity, rho=rho)

        # inp & z are dummy variables
        def model(t0, x, params):
            tanh_x = params['tanh_x']
            z = params['z']
            return (-x + np.dot(J, tanh_x) + Wz*z)/dt

        x, t, z, _, wu,_ = jedi.force(targets, model, lr, dt, tmax, tstart, tstop, x0, w)

        zs_noise.append(z)
        error = z-targets
        errors_noise.append(error)

        x, t, z, _, wu,_ = jedi.dforce(jedi.step_decode, targets, model, lr, dt, tmax, tstart, tstop, x0, w)
        dzs_noise.append(z)
        derror = z-targets
        derrors_noise.append(derror)

    try:
        parameters['t'] = t
    except NameError:
        print "t was not defined; check seed args and script for errors"

    noise_errors = {}
    noise_errors['parameters'] = parameters
    noise_errors['force'] = (errors_noise, zs_noise)
    noise_errors['dforce'] = (derrors_noise, dzs_noise)

    cPickle.dump(noise_errors,
                 open("../../../data/stability/sin/external_noise/noise_" +
                      str(noise_ext_var) + ".p", "wb"))


if __name__ == "__main__":

    if len(sys.argv) > 1:
        try:
            seed = int(sys.argv[1])
        except:
            raise ValueError("Check your args; make sure the ONLY arg is an int")
    else:
        seed = None

    main(seed)