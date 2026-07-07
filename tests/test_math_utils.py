import pytest

from eval.samples.math_utils import clamp, factorial, is_prime, lerp


def test_clamp_valid_range():
    assert clamp(5.0, 1.0, 10.0) == 5.0
    assert clamp(0.0, 1.0, 10.0) == 1.0
    assert clamp(15.0, 1.0, 10.0) == 10.0


def test_clamp_equal_bounds():
    assert clamp(5.0, 5.0, 5.0) == 5.0
    assert clamp(3.0, 5.0, 5.0) == 5.0
    assert clamp(7.0, 5.0, 5.0) == 5.0


def test_clamp_invalid_range():
    with pytest.raises(ValueError, match="low must be <= high"):
        clamp(5.0, 10.0, 1.0)


def test_lerp_basic():
    assert lerp(0.0, 10.0, 0.0) == 0.0
    assert lerp(0.0, 10.0, 1.0) == 10.0
    assert lerp(0.0, 10.0, 0.5) == 5.0
    assert lerp(1.0, 5.0, 0.25) == 2.0


def test_lerp_extremes():
    assert lerp(-10.0, 10.0, 0.0) == -10.0
    assert lerp(-10.0, 10.0, 1.0) == 10.0
    assert lerp(100.0, 200.0, 0.0) == 100.0
    assert lerp(100.0, 200.0, 1.0) == 200.0


def test_lerp_negative_values():
    assert lerp(-5.0, -1.0, 0.5) == -3.0
    assert lerp(-10.0, -5.0, 0.2) == -9.0


def test_lerp_out_of_range_t():
    assert lerp(0.0, 10.0, -1.0) == -10.0
    assert lerp(0.0, 10.0, 2.0) == 20.0
    assert lerp(1.0, 5.0, 1.5) == 7.0


def test_is_prime_small_numbers():
    assert is_prime(2) is True
    assert is_prime(3) is True
    assert is_prime(4) is False
    assert is_prime(5) is True
    assert is_prime(6) is False
    assert is_prime(7) is True
    assert is_prime(8) is False
    assert is_prime(9) is False
    assert is_prime(10) is False
    assert is_prime(11) is True


def test_is_prime_edge_cases():
    assert is_prime(0) is False
    assert is_prime(1) is False
    assert is_prime(-1) is False
    assert is_prime(-5) is False


def test_is_prime_large_primes():
    assert is_prime(13) is True
    assert is_prime(17) is True
    assert is_prime(19) is True
    assert is_prime(23) is True
    assert is_prime(29) is True


def test_is_prime_large_composites():
    assert is_prime(100) is False
    assert is_prime(121) is False
    assert is_prime(143) is False
    assert is_prime(169) is False
    assert is_prime(221) is False


def test_factorial_zero():
    assert factorial(0) == 1


def test_factorial_small_numbers():
    assert factorial(1) == 1
    assert factorial(2) == 2
    assert factorial(3) == 6
    assert factorial(4) == 24
    assert factorial(5) == 120


def test_factorial_medium_numbers():
    assert factorial(6) == 720
    assert factorial(7) == 5040
    assert factorial(8) == 40320
    assert factorial(9) == 362880
    assert factorial(10) == 3628800


def test_factorial_large_numbers():
    assert factorial(12) == 479001600
    assert factorial(15) == 1307674368000


def test_factorial_negative():
    with pytest.raises(ValueError, match="n must be non-negative"):
        factorial(-1)
    with pytest.raises(ValueError, match="n must be non-negative"):
        factorial(-5)
    with pytest.raises(ValueError, match="n must be non-negative"):
        factorial(-10)
