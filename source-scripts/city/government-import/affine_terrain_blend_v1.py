"""Dimensionless transition weights in local XZ, independent of face-area cutoffs."""
import numpy as np


def sector(xz, weights):
    xz = np.asarray(xz, dtype=float)
    weights = np.asarray(weights, dtype=float)
    assert xz.shape == (3, 2) and weights.shape == (3,)
    assert np.isfinite(xz).all() and np.isfinite(weights).all()
    origin = xz[0].copy()
    delta = xz[1:] - origin
    scale = np.max(np.abs(delta), axis=0)
    assert np.all(scale > 0), 'Collinear blend sector'
    matrix = delta / scale
    assert np.linalg.det(matrix) != 0, 'Collinear blend sector'
    coefficients = np.linalg.solve(matrix, weights[1:] - weights[0])
    result = dict(origin=origin.tolist(), scale=scale.tolist(), coefficients=coefficients.tolist(), intercept=float(weights[0]))
    assert np.isfinite(coefficients).all()
    assert np.max(np.abs(evaluate(xz, result, clip=False) - weights)) <= 1e-12
    return result


def evaluate(xz, value, clip=True):
    xz = np.asarray(xz, dtype=float)
    weights = ((xz - value['origin']) / value['scale']) @ value['coefficients'] + value['intercept']
    assert np.isfinite(weights).all()
    return np.clip(weights, 0, 1) if clip else weights
