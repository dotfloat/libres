import pytest
from ecl.util.util import DoubleVector
from res.util import quantile, quantile_sorted, polyfit
from ecl.util.util.rng import RandomNumberGenerator


def test_stat_quantiles():
    rng = RandomNumberGenerator()
    rng.setState("0123456789ABCDEF")
    v = DoubleVector()
    for i in range(100000):
        v.append(rng.getDouble( ))

    assert quantile(v, 0.1) == pytest.approx(0.1, 0.01)
    assert quantile_sorted(v, 0.2) == pytest.approx(0.2, 0.01)
    assert quantile_sorted(v, 0.3) == pytest.approx(0.3, 0.01)
    assert quantile_sorted(v, 0.4) == pytest.approx(0.4, 0.01)
    assert quantile_sorted(v, 0.5) == pytest.approx(0.5, 0.01)


def test_polyfit():
    x_list = DoubleVector()
    y_list = DoubleVector()
    S = DoubleVector()

    A = 7.25
    B = -4
    C = 0.025

    x = 0
    dx = 0.1
    for i in range(100):
        y = A + B * x + C * x * x
        x_list.append(x)
        y_list.append(y)

        x += dx
        S.append(1.0)

    beta = polyfit(3, x_list, y_list, None)

    assert A == pytest.approx(beta[0], 0.01)
    assert B == pytest.approx(beta[1], 0.01)
    assert C == pytest.approx(beta[2], 0.01)
