import pytest

from examples.calculator import AdvancedCalculator, add, subtract


def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
    assert add(-5, -3) == -8

def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(0, 5) == -5
    assert subtract(-2, -3) == 1
    assert subtract(10, 10) == 0

def test_advanced_calculator_init():
    calc = AdvancedCalculator()
    assert calc.value == 0.0
    
    calc = AdvancedCalculator(5.5)
    assert calc.value == 5.5
    
    calc = AdvancedCalculator(-3.2)
    assert calc.value == -3.2

def test_advanced_calculator_multiply():
    calc = AdvancedCalculator(4.0)
    result = calc.multiply(3.0)
    assert result == 12.0
    assert calc.value == 12.0
    
    # Multiply by zero
    calc.multiply(0.0)
    assert calc.value == 0.0
    
    # Multiply by negative
    calc = AdvancedCalculator(6.0)
    calc.multiply(-2.0)
    assert calc.value == -12.0
    
    # Multiply by fraction
    calc.multiply(0.5)
    assert calc.value == -6.0

def test_advanced_calculator_divide():
    calc = AdvancedCalculator(12.0)
    result = calc.divide(3.0)
    assert result == 4.0
    assert calc.value == 4.0
    
    # Divide by one
    calc.divide(1.0)
    assert calc.value == 4.0
    
    # Divide by negative
    calc.divide(-2.0)
    assert calc.value == -2.0
    
    # Divide by fraction
    calc.divide(0.5)
    assert calc.value == -4.0

def test_advanced_calculator_divide_by_zero():
    calc = AdvancedCalculator(10.0)
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calc.divide(0.0)
    
    # Ensure value wasn't changed
    assert calc.value == 10.0
    
    # Test with zero initial value
    calc = AdvancedCalculator(0.0)
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calc.divide(0.0)