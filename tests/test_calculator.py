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
    """Test add with zero."""
    assert add(0, 5) == 5
    assert add(5, 0) == 5
    assert add(0, 0) == 0


def test_add_large_numbers():
    """Test add with large numbers."""
    assert add(1000000, 2000000) == 3000000


# Tests for subtract() function
def test_subtract_positive_integers():
    """Test subtract with two positive integers."""
    assert subtract(5, 3) == 2


def test_subtract_negative_integers():
    """Test subtract with two negative integers."""
    assert subtract(-5, -3) == -2
    assert subtract(-3, -5) == 2


def test_subtract_positive_and_negative_integers():
    """Test subtract with a positive and a negative integer."""
    assert subtract(5, -3) == 8
    assert subtract(-5, 3) == -8


def test_subtract_with_zero():
    """Test subtract with zero."""
    assert subtract(5, 0) == 5
    assert subtract(0, 5) == -5
    assert subtract(0, 0) == 0


def test_subtract_result_is_zero():
    """Test subtract where the result is zero."""
    assert subtract(5, 5) == 0


def test_subtract_large_numbers():
    """Test subtract with large numbers."""
    assert subtract(2000000, 1000000) == 1000000


# Tests for AdvancedCalculator class


# Tests for __init__()
def test_advanced_calculator_init_default_value():
    """Test AdvancedCalculator initialization with default value."""
    calc = AdvancedCalculator()
    assert calc.value == 0.0


def test_advanced_calculator_init_custom_value():
    """Test AdvancedCalculator initialization with a custom value."""
    calc = AdvancedCalculator(10.5)
    assert calc.value == 10.5


def test_advanced_calculator_init_negative_value():
    """Test AdvancedCalculator initialization with a negative value."""
    calc = AdvancedCalculator(-5.0)
    assert calc.value == -5.0


def test_advanced_calculator_init_zero_value():
    """Test AdvancedCalculator initialization with zero."""
    calc = AdvancedCalculator(0.0)
    assert calc.value == 0.0


# Tests for multiply()
def test_advanced_calculator_multiply_positive_factor():
    """Test multiply with a positive factor."""
    calc = AdvancedCalculator(5.0)
    assert calc.multiply(2.0) == pytest.approx(10.0)
    assert calc.value == pytest.approx(10.0)  # Check internal state


def test_advanced_calculator_multiply_negative_factor():
    """Test multiply with a negative factor."""
    calc = AdvancedCalculator(5.0)
    assert calc.multiply(-2.0) == pytest.approx(-10.0)
    assert calc.value == pytest.approx(-10.0)


def test_advanced_calculator_multiply_zero_factor():
    """Test multiply with a zero factor."""
    calc = AdvancedCalculator(5.0)
    assert calc.multiply(0.0) == pytest.approx(0.0)
    assert calc.value == pytest.approx(0.0)


def test_advanced_calculator_multiply_by_one():
    """Test multiply by one."""
    calc = AdvancedCalculator(7.5)
    assert calc.multiply(1.0) == pytest.approx(7.5)
    assert calc.value == pytest.approx(7.5)


def test_advanced_calculator_multiply_float_factor():
    """Test multiply with a float factor."""
    calc = AdvancedCalculator(2.5)
    assert calc.multiply(1.5) == pytest.approx(3.75)
    assert calc.value == pytest.approx(3.75)


def test_advanced_calculator_multiply_chaining():
    """Test chaining multiple multiply operations."""
    calc = AdvancedCalculator(2.0)
    calc.multiply(3.0)
    assert calc.multiply(0.5) == pytest.approx(3.0)
    assert calc.value == pytest.approx(3.0)


def test_advanced_calculator_multiply_initial_zero():
    """Test multiply when initial value is zero."""
    calc = AdvancedCalculator(0.0)
    assert calc.multiply(100.0) == pytest.approx(0.0)
    assert calc.value == pytest.approx(0.0)


# Tests for divide()
def test_advanced_calculator_divide_positive_divisor():
    """Test divide with a positive divisor."""
    calc = AdvancedCalculator(10.0)
    assert calc.divide(2.0) == pytest.approx(5.0)
    assert calc.value == pytest.approx(5.0)


def test_advanced_calculator_divide_negative_divisor():
    """Test divide with a negative divisor."""
    calc = AdvancedCalculator(10.0)
    assert calc.divide(-2.0) == pytest.approx(-5.0)
    assert calc.value == pytest.approx(-5.0)


def test_advanced_calculator_divide_float_divisor():
    """Test divide with a float divisor."""
    calc = AdvancedCalculator(10.0)
    assert calc.divide(2.5) == pytest.approx(4.0)
    assert calc.value == pytest.approx(4.0)


def test_advanced_calculator_divide_by_one():
    """Test divide by one."""
    calc = AdvancedCalculator(7.5)
    assert calc.divide(1.0) == pytest.approx(7.5)
    assert calc.value == pytest.approx(7.5)


def test_advanced_calculator_divide_by_self():
    """Test divide by the current value."""
    calc = AdvancedCalculator(5.0)
    assert calc.divide(5.0) == pytest.approx(1.0)
    assert calc.value == pytest.approx(1.0)


def test_advanced_calculator_divide_chaining():
    """Test chaining multiple divide operations."""
    calc = AdvancedCalculator(20.0)
    calc.divide(2.0)
    assert calc.divide(2.5) == pytest.approx(4.0)
    assert calc.value == pytest.approx(4.0)


def test_advanced_calculator_divide_initial_zero():
    """Test divide when initial value is zero."""
    calc = AdvancedCalculator(0.0)
    assert calc.divide(5.0) == pytest.approx(0.0)
    assert calc.value == pytest.approx(0.0)


def test_advanced_calculator_divide_by_zero_raises_error():
    """Test divide by zero raises ValueError."""
    calc = AdvancedCalculator(10.0)
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calc.divide(0.0)
    # Ensure value remains unchanged after error
    assert calc.value == pytest.approx(10.0)


def test_advanced_calculator_divide_by_zero_initial_zero():
    """Test divide by zero when initial value is zero."""
    calc = AdvancedCalculator(0.0)
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calc.divide(0.0)
    # Ensure value remains unchanged after error
    assert calc.value == pytest.approx(0.0)


# Combined operations test
def test_advanced_calculator_combined_operations():
    """Test a sequence of multiply and divide operations."""
    calc = AdvancedCalculator(100.0)
    calc.multiply(2.0)  # 200.0
    calc.divide(4.0)  # 50.0
    calc.multiply(0.5)  # 25.0
    assert calc.divide(-2.5) == pytest.approx(-10.0)
    assert calc.value == pytest.approx(-10.0)
