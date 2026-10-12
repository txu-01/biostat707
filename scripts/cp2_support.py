"""Training-fold restricted cubic spline basis for BIOS 707 Checkpoint 2."""

import numpy as np
from scipy.interpolate import CubicSpline
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_array, check_is_fitted


class RestrictedCubicSpline(BaseEstimator, TransformerMixin):
    """Natural cubic cardinal basis with explicit linear tails.

    Knots are learned from training data only. Dropping the first cardinal
    basis column removes the constant redundancy with the regression intercept.
    Duplicate quantiles fall back to evenly spaced knots over the training range.
    """

    def __init__(self, quantiles=(0.05, 0.35, 0.65, 0.95)):
        self.quantiles = quantiles

    def fit(self, X, y=None):
        X = check_array(X)
        self.n_features_in_ = X.shape[1]
        self.splines_ = []
        self.knots_ = []
        for col in X.T:
            knots = np.quantile(col, self.quantiles)
            if np.unique(knots).size != len(knots):
                lo, hi = col.min(), col.max()
                if lo == hi:
                    hi = lo + 1.0
                knots = np.linspace(lo, hi, len(self.quantiles))
            self.knots_.append(knots)
            self.splines_.append(
                CubicSpline(knots, np.eye(len(knots)), bc_type="natural")
            )
        return self

    def transform(self, X):
        check_is_fitted(self, "splines_")
        X = check_array(X)
        if X.shape[1] != self.n_features_in_:
            raise ValueError("Unexpected number of spline inputs")
        blocks = []
        for col, knots, spline in zip(X.T, self.knots_, self.splines_):
            lo, hi = knots[0], knots[-1]
            basis = spline(np.clip(col, lo, hi))
            left, right = col < lo, col > hi
            basis[left] = spline(lo) + (col[left] - lo)[:, None] * spline(lo, 1)
            basis[right] = spline(hi) + (col[right] - hi)[:, None] * spline(hi, 1)
            blocks.append(basis[:, 1:])
        return np.hstack(blocks)

    def get_feature_names_out(self, input_features=None):
        check_is_fitted(self, "splines_")
        if input_features is None:
            input_features = [f"x{i}" for i in range(self.n_features_in_)]
        return np.array([
            f"{feature}_rcs{j}" for feature in input_features
            for j in range(1, len(self.quantiles))
        ], dtype=object)
