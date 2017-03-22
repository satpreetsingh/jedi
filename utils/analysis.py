import numpy as np
import numpy.linalg as la
from scipy.optimize import minimize
import functools
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt


def _make_fix_point_aux_func(F, inputs=False):
    if inputs:
        def q(inp, x):
            return .5 * (la.norm(functools.partial(F, inp)(x)) ** 2)
    else:
        def q(x):
            return .5*(la.norm(F(x)) ** 2)
    return q


def fixed_points(F, x, n_samps, inputs=None, plot=True):
    pca = PCA(n_components=2)
    pca.fit(x)
    pca_x = pca.transform(x).T

    q = _make_fix_point_aux_func(F, inputs is not None)

    ics = x[np.random.randint(0, len(x), n_samps)]

    minima = []
    indices = np.random.randint(0, len(x), n_samps)

    for ind in indices:
        ic = x[ind]
        inp = inputs[ind]

        if inputs is None:
            minima.append(minimize(q, ic).x)
        else:
            minima.append(minimize(functools.partial(q, inp), ic).x)

    pca_minima = pca.transform(np.array(minima)).T
    pca_ics = pca.transform(np.array(ics)).T

    if plot:
        plt.figure()
        plt.plot(pca_x[0], pca_x[1], 'ko', alpha=.1);
        plt.plot(pca_minima[0], pca_minima[1], 'ro', alpha=.8, label='Minima');
        plt.plot(pca_ics[0], pca_ics[1], 'bo', alpha=.2, label='Seeds');
        plt.legend()
        plt.show()

    return minima