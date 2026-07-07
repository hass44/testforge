import pytest

from examples.calculator import AdvancedCalculator, add, subtract


# Tests for add() function
def test_add_positive_integers():
    """Test add with two positive integers."""
    assert add(2, 3) == 5


def test_add_negative_integers():
    """Test add with two negative integers."""
    assert add(-2, -3) == -5


def test_add_positive_and_negative_integers():
    """Test add with a positive and a negative integer."""
    assert add(5, -3) == 2
    assert add(-5, 3) == -2


def test_add_with_zero():
    """Test add with one or both numbers being zero."""
    assert add(0, 5) == 5
    assert add(5, 0) == 5
    assert add(0, 0) == 0


def test_add_large_numbers():
    """Test add with large integers."""
    assert add(1000000, 2000000) == 3000000


# Tests for subtract() function
def test_subtract_positive_integers():
    """Test subtract with two positive integers."""
    assert subtract(5, 2) == 3


def test_subtract_negative_integers():
    """Test subtract with two negative integers."""
    assert subtract(-5, -2) == -3


def test_subtract_positive_and_negative_integers():
    """Test subtract with a positive and a negative integer."""
    assert subtract(5, -2) == 7
    assert subtract(-5, 2) == -7


def test_subtract_with_zero():
    """Test subtract with one or both numbers being zero."""
    assert subtract(0, 5) == -5
    assert subtract(5, 0) == 5
    assert subtract(0, 0) == 0


def test_subtract_large_numbers():
    """Test subtract with large integers."""
    assert subtract(2000000, 1000000) == 1000000


# Tests for AdvancedCalculator class


# Test __init__()
def test_advanced_calculator_init_default_value():
    """Test AdvancedCalculator initializes with default value 0.0."""
    calc = AdvancedCalculator()
    assert calc.value == 0.0


def test_advanced_calculator_init_custom_value():
    """Test AdvancedCalculator initializes with a custom initial value."""
    calc = AdvancedCalculator(10.5)
    assert calc.value == 10.5


def test_advanced_calculator_init_negative_value():
    """Test AdvancedCalculator initializes with a negative value."""
    calc = AdvancedCalculator(-7.2)
    assert calc.value == -7.2


# Test multiply()
def test_advanced_calculator_multiply_positive_factor():
    """Test multiply with a positive factor."""
    calc = AdvancedCalculator(5.0)
    assert calc.multiply(2.0) == 10.0
    assert calc.value == 10.0


def test_advanced_calculator_multiply_negative_factor():
    """Test multiply with a negative factor."""
    calc = AdvancedCalculator(5.0)
    assert calc.multiply(-2.0) == -10.0
    assert calc.value == -10.0


def test_advanced_calculator_multiply_by_zero():
    """Test multiply by zero."""
    calc = AdvancedCalculator(5.0)
    assert calc.multiply(0.0) == 0.0
    assert calc.value == 0.0


def test_advanced_calculator_multiply_by_one():
    """Test multiply by one."""
    calc = AdvancedCalculator(7.5)
    assert calc.multiply(1.0) == 7.5
    assert calc.value == 7.5


def test_advanced_calculator_multiply_float_factor():
    """Test multiply with a float factor."""
    calc = AdvancedCalculator(2.5)
    assert calc.multiply(1.5) == pytest.approx(3.75)
    assert calc.value == pytest.approx(3.75)


def test_advanced_calculator_multiply_chaining():
    """Test chaining multiply operations."""
    calc = AdvancedCalculator(2.0)
    calc.multiply(3.0)
    assert calc.multiply(0.5) == 3.0
    assert calc.value == 3.0


# Test divide()
def test_advanced_calculator_divide_positive_divisor():
    """Test divide with a positive divisor."""
    calc = AdvancedCalculator(10.0)
    assert calc.divide(2.0) == 5.0
    assert calc.value == 5.0


def test_advanced_calculator_divide_negative_divisor():
    """Test divide with a negative divisor."""
    calc = AdvancedCalculator(10.0)
    assert calc.divide(-2.0) == -5.0
    assert calc.value == -5.0


def test_advanced_calculator_divide_by_one():
    """Test divide by one."""
    calc = AdvancedCalculator(7.5)
    assert calc.divide(1.0) == 7.5
    assert calc.value == 7.5


def test_advanced_calculator_divide_float_divisor():
    """Test divide with a float divisor."""
    calc = AdvancedCalculator(10.0)
    assert calc.divide(4.0) == 2.5
    assert calc.value == 2.5


def test_advanced_calculator_divide_into_zero():
    """Test dividing zero by a non-zero number."""
    calc = AdvancedCalculator(0.0)
    assert calc.divide(5.0) == 0.0
    assert calc.value == 0.0


def test_advanced_calculator_divide_by_zero_raises_error():
    """Test that dividing by zero raises a ValueError."""
    calc = AdvancedCalculator(10.0)
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calc.divide(0.0)
    # Ensure the value remains unchanged after an error
    assert calc.value == 10.0


def test_advanced_calculator_divide_chaining():
    """Test chaining divide operations."""
    calc = AdvancedCalculator(20.0)
    calc.divide(2.0)  # value becomes 10.0
    assert calc.divide(4.0) == 2.5  # value becomes 2.5
    assert calc.value == 2.5


# Test combined operations
def test_advanced_calculator_combined_operations():
    """Test a sequence of multiply and divide operations."""
    calc = AdvancedCalculator(10.0)
    calc.multiply(3.0)  # value = 30.0
    calc.divide(2.0)  # value = 15.0
    calc.multiply(0.5)  # value = 7.5
    assert calc.value == 7.5
    calc.divide(-1.5)  # value = -5.0
    assert calc.value == pytest.approx(-5.0)


def test_advanced_calculator_combined_operations_with_error():
    """Test combined operations where an error occurs mid-sequence."""
    calc = AdvancedCalculator(100.0)
    calc.multiply(2.0)  # value = 200.0
    with pytest.raises(ValueError):
        calc.divide(0.0)  # Error here
    assert calc.value == 200.0  # Value should be unchanged after error
    calc.divide(10.0)  # Continue operations
    assert calc.value == 20.0
