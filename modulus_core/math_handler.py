"""
Comprehensive mathematical expression handler for Modulus.

Handles transcendental functions, special functions, complex numbers,
and ensures robust evaluation across all STEM domains.
"""

import sympy as sp
from typing import Dict, Any, Union, List, Optional
import re


class MathExpressionHandler:
    """
    Robust handler for mathematical expressions from natural language or Grok schemas.
    """
    
    def __init__(self):
        """Initialize with function mappings and normalization rules."""
        
        # Transcendental function mappings
        self.transcendental_map = {
            'log10': lambda x: sp.log(x, 10),
            'log2': lambda x: sp.log(x, 2),
            'ln': sp.log,
            'exp': sp.exp,
            'sqrt': sp.sqrt,
            'cbrt': lambda x: x**(sp.Rational(1, 3)),
        }
        
        # Trigonometric functions (already in SymPy but ensure normalization)
        self.trig_map = {
            'sin': sp.sin,
            'cos': sp.cos,
            'tan': sp.tan,
            'cot': sp.cot,
            'sec': sp.sec,
            'csc': sp.csc,
            'asin': sp.asin,
            'acos': sp.acos,
            'atan': sp.atan,
            'atan2': sp.atan2,
        }
        
        # Hyperbolic functions
        self.hyperbolic_map = {
            'sinh': sp.sinh,
            'cosh': sp.cosh,
            'tanh': sp.tanh,
            'coth': sp.coth,
            'sech': lambda x: 1/sp.cosh(x),
            'csch': lambda x: 1/sp.sinh(x),
            'asinh': sp.asinh,
            'acosh': sp.acosh,
            'atanh': sp.atanh,
        }
        
        # Special functions
        self.special_map = {
            'abs': sp.Abs,
            'factorial': sp.factorial,
            'gamma': sp.gamma,
            'erf': sp.erf,
            'erfc': sp.erfc,
            'floor': sp.floor,
            'ceil': sp.ceiling,
            'round': lambda x: sp.floor(x + sp.Rational(1, 2)),
            'sign': sp.sign,
            'Max': sp.Max,
            'Min': sp.Min,
        }
        
        # Build comprehensive symbol table with all functions
        self.function_namespace = {
            **{name: func for name, func in self.transcendental_map.items()},
            **{name: func for name, func in self.trig_map.items()},
            **{name: func for name, func in self.hyperbolic_map.items()},
            **{name: func for name, func in self.special_map.items()},
            'pi': sp.pi,
            'e': sp.E,
            'I': sp.I,  # Imaginary unit
            'oo': sp.oo,  # Infinity
        }
    
    def normalize_expression(self, expr_str: str, custom_symbols: Optional[Dict[str, sp.Symbol]] = None) -> sp.Expr:
        """
        Convert a string expression to a normalized SymPy expression.
        
        Args:
            expr_str: String representation of mathematical expression
            custom_symbols: Additional symbols to include in namespace
            
        Returns:
            SymPy expression ready for manipulation
        """
        if not expr_str or not isinstance(expr_str, str):
            return sp.Integer(0)
        
        # Build complete namespace
        namespace = dict(self.function_namespace)
        if custom_symbols:
            namespace.update(custom_symbols)
        
        try:
            # Parse with SymPy
            expr = sp.sympify(expr_str, locals=namespace)
            return expr
        except Exception as e:
            print(f"[MathHandler] Warning: Could not parse '{expr_str}': {e}")
            return sp.Symbol(str(expr_str))  # Fallback to symbol
    
    def substitute_and_evaluate(
        self, 
        expr: sp.Expr, 
        substitutions: Dict[Union[str, sp.Symbol], Union[float, int, sp.Expr]],
        numeric: bool = True,
        precision: int = 15
    ) -> Union[sp.Expr, str]:
        """
        Substitute values into expression and optionally evaluate numerically.
        
        Args:
            expr: SymPy expression
            substitutions: Dictionary of symbol -> value mappings
            numeric: If True, evaluate to numeric value
            precision: Decimal precision for numeric evaluation
            
        Returns:
            Evaluated expression (symbolic or numeric string)
        """
        # Normalize substitution keys to SymPy symbols
        subs_dict = {}
        for key, val in substitutions.items():
            if isinstance(key, str):
                key = sp.Symbol(key)
            
            # Convert value to SymPy expression if needed
            if isinstance(val, (int, float)):
                val = sp.sympify(val)
            
            subs_dict[key] = val
        
        # Perform substitution
        try:
            result = expr.subs(subs_dict)
            
            # Simplify if possible
            result = sp.simplify(result)
            
            # Evaluate numerically if requested and no free symbols remain
            if numeric and (not result.free_symbols or all(isinstance(s, sp.Number) for s in result.free_symbols)):
                if hasattr(result, 'evalf'):
                    result = result.evalf(precision)
            
            return str(result) if numeric else result
            
        except Exception as e:
            print(f"[MathHandler] Error in substitute_and_evaluate: {e}")
            return "0"
    
    def detect_function_types(self, expr: sp.Expr) -> Dict[str, bool]:
        """
        Analyze expression to detect what types of functions it contains.
        
        Returns:
            Dictionary with boolean flags for each function type
        """
        expr_str = str(expr)
        
        return {
            'transcendental': any(f in expr_str for f in ['log', 'exp', 'ln']),
            'trigonometric': any(f in expr_str for f in ['sin', 'cos', 'tan']),
            'hyperbolic': any(f in expr_str for f in ['sinh', 'cosh', 'tanh']),
            'special': any(f in expr_str for f in ['gamma', 'erf', 'factorial']),
            'complex': 'I' in expr_str or 'im' in expr_str.lower(),
            'polynomial': expr.is_polynomial() if hasattr(expr, 'is_polynomial') else False,
            'rational': expr.is_rational_function() if hasattr(expr, 'is_rational_function') else False,
        }
    
    def validate_expression(self, expr: sp.Expr) -> tuple[bool, Optional[str]]:
        """
        Validate that an expression is well-formed and computable.
        
        Returns:
            (is_valid, error_message)
        """
        try:
            # Check for undefined symbols that look like functions
            undefined = []
            for atom in expr.atoms(sp.Symbol):
                name = str(atom)
                # Check if it looks like a function call but isn't defined
                if name.endswith('(') or '(' in name:
                    undefined.append(name)
            
            if undefined:
                return False, f"Undefined functions: {', '.join(undefined)}"
            
            # Try to evaluate with dummy values to check syntax
            test_subs = {sym: 1.0 for sym in expr.free_symbols}
            try:
                expr.subs(test_subs).evalf()
            except Exception as e:
                return False, f"Expression cannot be evaluated: {e}"
            
            return True, None
            
        except Exception as e:
            return False, f"Validation error: {e}"
    
    def extract_symbols(self, expr: sp.Expr) -> List[sp.Symbol]:
        """
        Extract all user-defined symbols from an expression.
        Excludes built-in constants and functions.
        """
        builtin = {sp.pi, sp.E, sp.I, sp.oo}
        return sorted(
            [s for s in expr.free_symbols if s not in builtin],
            key=lambda s: str(s)
        )
    
    def unify_symbol_names(
        self,
        equations: List[sp.Expr],
        symbols_dict: Dict[str, Any],
        parameters_dict: Dict[str, Any]
    ) -> Dict[sp.Symbol, sp.Expr]:
        """
        Create unified mapping between symbol names in equations and parameter values.
        
        Handles cases where Grok uses different names (e.g., 'Ts' vs 'Ts_value').
        
        Returns:
            Dictionary mapping symbols to their values
        """
        unified = {}
        
        # Get all symbols from equations
        all_symbols = set()
        for eq in equations:
            all_symbols.update(eq.free_symbols)
        
        # Try to match each symbol to a parameter
        for sym in all_symbols:
            sym_name = str(sym)
            
            # Direct match
            if sym_name in parameters_dict:
                unified[sym] = parameters_dict[sym_name]
                continue
            
            # Try with _value suffix
            if f"{sym_name}_value" in parameters_dict:
                unified[sym] = parameters_dict[f"{sym_name}_value"]
                continue
            
            # Try removing _value suffix
            if sym_name.endswith('_value'):
                base_name = sym_name[:-6]
                if base_name in parameters_dict:
                    unified[sym] = parameters_dict[base_name]
                    continue
            
            # Check symbols_dict for unit/description info
            if sym_name in symbols_dict:
                sym_info = symbols_dict[sym_name]
                if isinstance(sym_info, dict) and 'value' in sym_info:
                    unified[sym] = sym_info['value']
                    continue
        
        return unified


def test_math_handler():
    """Test the math handler with various expressions."""
    handler = MathExpressionHandler()
    
    print("=== Testing MathExpressionHandler ===\n")
    
    # Test 1: Transcendental functions
    print("Test 1: log10(100)")
    expr1 = handler.normalize_expression("log10(100)")
    result1 = handler.substitute_and_evaluate(expr1, {})
    print(f"  Result: {result1}\n")
    
    # Test 2: With substitution
    print("Test 2: log10(x/y) with x=410, y=1.9")
    expr2 = handler.normalize_expression("log10(x/y)")
    result2 = handler.substitute_and_evaluate(expr2, {'x': 410, 'y': 1.9})
    print(f"  Result: {result2}\n")
    
    # Test 3: Complex expression
    print("Test 3: sin(pi/2) + exp(0)")
    expr3 = handler.normalize_expression("sin(pi/2) + exp(0)")
    result3 = handler.substitute_and_evaluate(expr3, {})
    print(f"  Result: {result3}\n")
    
    # Test 4: Detection
    print("Test 4: Function type detection")
    types = handler.detect_function_types(expr2)
    print(f"  Types: {types}\n")


if __name__ == '__main__':
    test_math_handler()


