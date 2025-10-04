"""
Units handling for Modulus using pint.

Provides unit tracking, conversion, and dimensional analysis.
"""

import pint
from typing import Dict, Any, Optional, Union, List
import sympy as sp


class UnitsHandler:
    """
    Wrapper around pint for unit tracking and conversion.
    """
    
    def __init__(self):
        """Initialize the units registry."""
        self.ureg = pint.UnitRegistry()
        
        # Common unit aliases
        self.unit_aliases = {
            'K': 'kelvin',
            'degC': 'degC',
            'degF': 'degF',
            'J': 'joule',
            'kJ': 'kilojoule',
            'cal': 'calorie',
            'kcal': 'kilocalorie',
            'W': 'watt',
            'kW': 'kilowatt',
            'Pa': 'pascal',
            'kPa': 'kilopascal',
            'MPa': 'megapascal',
            'atm': 'atmosphere',
            'bar': 'bar',
            'mol': 'mole',
            'kmol': 'kilomole',
            'm': 'meter',
            'cm': 'centimeter',
            'km': 'kilometer',
            's': 'second',
            'min': 'minute',
            'hr': 'hour',
            'kg': 'kilogram',
            'g': 'gram',
            'N': 'newton',
            'V': 'volt',
            'A': 'ampere',
            'C': 'coulomb',
            'Ω': 'ohm',
            'F': 'farad',
            'H': 'henry',
            'Hz': 'hertz',
            'rad': 'radian',
            'deg': 'degree',
            'dimensionless': 'dimensionless'
        }
    
    def parse_unit(self, unit_str: str) -> pint.Unit:
        """
        Parse a unit string into a pint Unit object.
        
        Args:
            unit_str: Unit string (e.g., 'm/s', 'kg*m/s^2')
            
        Returns:
            pint.Unit object
        """
        if not unit_str or unit_str == 'dimensionless' or unit_str == '1':
            return self.ureg.dimensionless
        
        # Try to resolve alias
        if unit_str in self.unit_aliases:
            unit_str = self.unit_aliases[unit_str]
        
        try:
            return self.ureg(unit_str).units
        except Exception as e:
            print(f"[UnitsHandler] Warning: Could not parse unit '{unit_str}': {e}")
            return self.ureg.dimensionless
    
    def create_quantity(self, value: Union[float, int], unit_str: str) -> pint.Quantity:
        """
        Create a pint Quantity with value and units.
        
        Args:
            value: Numeric value
            unit_str: Unit string
            
        Returns:
            pint.Quantity
        """
        unit = self.parse_unit(unit_str)
        return value * unit
    
    def convert(self, value: Union[float, int], from_unit: str, to_unit: str) -> float:
        """
        Convert a value from one unit to another.
        
        Args:
            value: Numeric value in from_unit
            from_unit: Source unit
            to_unit: Target unit
            
        Returns:
            Converted value in to_unit
        """
        quantity = self.create_quantity(value, from_unit)
        converted = quantity.to(self.parse_unit(to_unit))
        return converted.magnitude
    
    def check_consistency(
        self,
        left_value: Union[float, int],
        left_unit: str,
        right_value: Union[float, int],
        right_unit: str,
        operation: str = 'add'
    ) -> Dict[str, Any]:
        """
        Check if two quantities have consistent units for a given operation.
        
        Args:
            left_value: Left operand value
            left_unit: Left operand unit
            right_value: Right operand value
            right_unit: Right operand unit
            operation: Operation type ('add', 'multiply', 'divide', 'power')
            
        Returns:
            Dictionary with consistency check results
        """
        left_qty = self.create_quantity(left_value, left_unit)
        right_qty = self.create_quantity(right_value, right_unit)
        
        try:
            if operation == 'add' or operation == 'subtract':
                # Addition/subtraction requires same dimensionality
                result = left_qty + right_qty
                return {
                    'consistent': True,
                    'result_value': result.magnitude,
                    'result_unit': str(result.units),
                    'message': f'Units {left_unit} and {right_unit} are compatible'
                }
            
            elif operation == 'multiply':
                result = left_qty * right_qty
                return {
                    'consistent': True,
                    'result_value': result.magnitude,
                    'result_unit': str(result.units),
                    'message': f'Product has units {result.units}'
                }
            
            elif operation == 'divide':
                result = left_qty / right_qty
                return {
                    'consistent': True,
                    'result_value': result.magnitude,
                    'result_unit': str(result.units),
                    'message': f'Quotient has units {result.units}'
                }
            
            elif operation == 'power':
                # For power, exponent should be dimensionless
                if not right_qty.dimensionless:
                    return {
                        'consistent': False,
                        'message': f'Exponent must be dimensionless, got {right_unit}'
                    }
                result = left_qty ** right_value
                return {
                    'consistent': True,
                    'result_value': result.magnitude,
                    'result_unit': str(result.units),
                    'message': f'Power has units {result.units}'
                }
            
            else:
                return {
                    'consistent': False,
                    'message': f'Unknown operation: {operation}'
                }
        
        except pint.DimensionalityError as e:
            return {
                'consistent': False,
                'message': f'Unit mismatch: {e}'
            }
        except Exception as e:
            return {
                'consistent': False,
                'message': f'Error checking units: {e}'
            }
    
    def get_dimensionality(self, unit_str: str) -> str:
        """
        Get the dimensionality of a unit (e.g., [length], [mass]/[time]²).
        
        Args:
            unit_str: Unit string
            
        Returns:
            Dimensionality string
        """
        try:
            unit = self.parse_unit(unit_str)
            return str(unit.dimensionality)
        except Exception as e:
            print(f"[UnitsHandler] Warning: Could not get dimensionality for '{unit_str}': {e}")
            return 'unknown'
    
    def track_through_expression(
        self,
        expr: sp.Expr,
        symbol_units: Dict[str, str]
    ) -> Optional[str]:
        """
        Track units through a SymPy expression.
        
        Args:
            expr: SymPy expression
            symbol_units: Dictionary mapping symbol names to unit strings
            
        Returns:
            Result unit string, or None if inconsistent
        """
        # This is a simplified implementation
        # For full implementation, would need to recursively traverse expression tree
        
        if isinstance(expr, sp.Symbol):
            return symbol_units.get(str(expr), 'dimensionless')
        
        elif isinstance(expr, (sp.Integer, sp.Float, sp.Rational)):
            return 'dimensionless'
        
        elif isinstance(expr, sp.Add):
            # All terms must have same units
            units = [self.track_through_expression(arg, symbol_units) for arg in expr.args]
            if len(set(units)) == 1:
                return units[0]
            else:
                print(f"[UnitsHandler] Warning: Inconsistent units in addition: {units}")
                return None
        
        elif isinstance(expr, sp.Mul):
            # Multiply units
            result_unit = 'dimensionless'
            for arg in expr.args:
                arg_unit = self.track_through_expression(arg, symbol_units)
                if arg_unit and arg_unit != 'dimensionless':
                    if result_unit == 'dimensionless':
                        result_unit = arg_unit
                    else:
                        # Would need to multiply units properly here
                        result_unit = f'{result_unit}*{arg_unit}'
            return result_unit
        
        elif isinstance(expr, sp.Pow):
            # Power: base units raised to exponent
            base_unit = self.track_through_expression(expr.args[0], symbol_units)
            exp = expr.args[1]
            
            # Exponent should be dimensionless
            if isinstance(exp, (sp.Integer, sp.Rational, sp.Float)):
                if base_unit and base_unit != 'dimensionless':
                    return f'{base_unit}^{exp}'
            return base_unit
        
        else:
            # For functions like sin, cos, exp, log - argument should be dimensionless
            # Result is also dimensionless
            return 'dimensionless'
    
    def suggest_conversion(self, from_unit: str, to_system: str = 'SI') -> Optional[str]:
        """
        Suggest a conversion target unit in a given system.
        
        Args:
            from_unit: Source unit
            to_system: Target system ('SI', 'imperial', 'cgs')
            
        Returns:
            Suggested target unit string
        """
        try:
            unit = self.parse_unit(from_unit)
            dimensionality = unit.dimensionality
            
            # Map dimensionality to preferred SI units
            si_mapping = {
                '[length]': 'meter',
                '[mass]': 'kilogram',
                '[time]': 'second',
                '[temperature]': 'kelvin',
                '[current]': 'ampere',
                '[substance]': 'mole',
                '[luminosity]': 'candela',
                '[length] / [time]': 'meter/second',
                '[length] / [time] ** 2': 'meter/second**2',
                '[mass] * [length] / [time] ** 2': 'newton',
                '[mass] / [length] / [time] ** 2': 'pascal',
                '[mass] * [length] ** 2 / [time] ** 2': 'joule',
                '[mass] * [length] ** 2 / [time] ** 3': 'watt',
            }
            
            dim_str = str(dimensionality)
            return si_mapping.get(dim_str, None)
            
        except Exception as e:
            print(f"[UnitsHandler] Could not suggest conversion: {e}")
            return None


def test_units_handler():
    """Test the units handler."""
    handler = UnitsHandler()
    
    print("=== Testing Units Handler ===\n")
    
    # Test 1: Unit parsing
    print("Test 1: Parse units")
    unit_m = handler.parse_unit('m')
    unit_m_s = handler.parse_unit('m/s')
    print(f"  Parsed 'm': {unit_m}")
    print(f"  Parsed 'm/s': {unit_m_s}\n")
    
    # Test 2: Unit conversion
    print("Test 2: Convert 5 m/s to km/h")
    result = handler.convert(5, 'm/s', 'km/h')
    print(f"  Result: {result} km/h\n")
    
    # Test 3: Consistency check
    print("Test 3: Check if 5 meters + 3 cm is consistent")
    check = handler.check_consistency(5, 'm', 3, 'cm', 'add')
    print(f"  Consistent: {check['consistent']}")
    print(f"  Result: {check.get('result_value')} {check.get('result_unit')}\n")
    
    # Test 4: Dimensionality
    print("Test 4: Get dimensionality of 'J' (joule)")
    dim = handler.get_dimensionality('J')
    print(f"  Dimensionality: {dim}\n")
    
    # Test 5: Suggest conversion
    print("Test 5: Suggest SI conversion for 'mph'")
    suggestion = handler.suggest_conversion('mph', 'SI')
    print(f"  Suggestion: {suggestion}\n")


if __name__ == '__main__':
    test_units_handler()


