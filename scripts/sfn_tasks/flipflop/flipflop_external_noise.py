from __future__ import division
import jedi.jedi as jedi
from jedi.utils import plot, init_tools, seedutil, noise_gen

import numpy as np
import cPickle
import sys

def main(seed):
    # Setting Seeds
    seeds = seedutil.load_seeds("main_seeds.npy", "../../../data/stability")
    if seed is not None:
        seeds = seeds[:seed]

    #
    targets = np.load("../../../data/stability/flipflop/targets_tmax10sec.npy")
    inputs = np.load("../../../data/stability/flipflop/inputs_tmax10sec.npy")

    #Simulation parameters for FORCE
    parameters = {}
    parameters['dt'] = dt =.01      # time step
    parameters['tmax'] = tmax = 10   # simulation length
    parameters['tstop'] = tstop = 5 # learning stop time
    parameters['tstart'] = tstart = 0 # learning start
    parameters['N'] = N = 300      # size of stochastic pool
    parameters['lr'] = lr = 1   # learning rate
    parameters['rho'] = rho = 1.02 # spectral radius of J
    parameters['pE'] = pE = .8 # excitatory percent
    parameters['sparsity'] = sparsity = (.1,1,1) # weight sparsity
    parameters['t_count'] = t_count = int(tmax/dt+2)
    parameters['noise_var'] = noise_var = .3
    parameters['noise'] = noise = 'normal'

    if noise == 'normal':
        noise_mat = np.random.normal(0, noise_ext_var, t_count)
    elif noise =='pink':
        noise_mat = np.array([noise_gen.voss(N) for _ in range(t_count)])

    # Adding external noise
    targets +=  noise_mat

    errors_noise = []
    derrors_noise = []
    zs_noise = []
    dzs_noise = []

    for seedling in seeds:
        J, Wz, Wi, x0, u, w = init_tools.set_simulation_parameters(seedling, N, 1, pE=pE, p=sparsity, rho=rho)

        def model(t0, x, params):
            index = params['index']
            z = params['z']
            tanh_x = params['tanh_x']
            inp = params['inputs'][index]
            return (-x + np.dot(J, tanh_x) + np.dot(Wi, inp) + Wz*z)/dt

        x, t, z, _, wu,_ = jedi.force(targets, model, lr, dt, tmax, tstart, tstop, x0, w,
                                      inputs=inputs)

        zs_noise.append(z)
        error = z-np.array(targets)
        errors_noise.append(error)

        x, t, z, _, wu,_ = jedi.dforce(jedi.step_decode, targets, model, lr, dt, tmax, tstart, tstop, x0, w,
                                 pE=pE, inputs=inputs)

        dzs_noise.append(z)
        derror = z-np.array(targets)
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
                 open("../../../data/stability/flipflop/external_noise/noise_"
                      + str(noise_var) + ".p", "wb"))


if __name__ == "__main__":

    if len(sys.argv) > 1:
        try:
            seed = int(sys.argv[1])
        except:
            raise ValueError("Check your args; make sure arg is the ONLY arg is an int")
    else:
        seed = None

    main(seed)