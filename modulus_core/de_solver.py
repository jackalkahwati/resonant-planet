"""
Differential Equations Solver for Modulus.

Handles ODEs (Ordinary Differential Equations) and PDEs (Partial Differential Equations)
using SymPy's dsolve and custom finite difference methods.
"""

import sympy as sp
from sympy import Function, Derivative, Eq, dsolve, symbols
from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
from dataclasses import dataclass


@dataclass
class BoundaryCondition:
    """Represents a boundary condition for differential equations."""
    variable: str  # e.g., 'x', 't'
    value: float  # location of boundary
    condition_type: str  # 'dirichlet', 'neumann', 'robin'
    expression: Union[sp.Expr, float]  # value or derivative value


@dataclass
class DESolution:
    """Solution to a differential equation."""
    general_solution: Optional[sp.Expr]  # Symbolic general solution
    particular_solution: Optional[sp.Expr]  # Solution satisfying BCs
    numerical_solution: Optional[np.ndarray]  # Numerical solution array
    grid: Optional[Dict[str, np.ndarray]]  # Grid points for numerical solution
    method: str  # Solving method used
    metadata: Dict[str, Any]  # Additional info


class DifferentialEquationSolver:
    """
    Solver for ordinary and partial differential equations.
    """
    
    def __init__(self):
        """Initialize the DE solver."""
        self.supported_ode_types = [
            'separable', 'linear', 'exact', 'homogeneous',
            'bernoulli', 'riccati', 'first_order', 'second_order',
            'nth_order_linear', 'cauchy_euler'
        ]
    
    def detect_equation_type(self, equation: sp.Eq) -> Dict[str, Any]:
        """
        Analyze a differential equation to determine its type and characteristics.
        
        Returns:
            Dictionary with equation metadata
        """
        # Extract derivatives
        derivatives = equation.atoms(Derivative)
        
        if not derivatives:
            return {'type': 'algebraic', 'is_de': False}
        
        # Get dependent and independent variables
        dep_vars = set()
        indep_vars = set()
        
        for deriv in derivatives:
            func = deriv.expr
            if isinstance(func, sp.Function):
                dep_vars.add(func.func)
            elif hasattr(func, 'func'):
                dep_vars.add(func.func)
            
            # Get variables being differentiated with respect to
            for var in deriv.variables:
                indep_vars.add(var)
        
        # Determine if ODE or PDE
        num_indep_vars = len(indep_vars)
        
        if num_indep_vars == 1:
            eq_type = 'ODE'
        elif num_indep_vars > 1:
            eq_type = 'PDE'
        else:
            eq_type = 'unknown'
        
        # Find maximum derivative order
        max_order = 0
        for deriv in derivatives:
            order = len(deriv.variables)
            max_order = max(max_order, order)
        
        # Check linearity (simplified check)
        is_linear = self._check_linearity(equation, dep_vars, derivatives)
        
        return {
            'type': eq_type,
            'is_de': True,
            'order': max_order,
            'dependent_vars': list(dep_vars),
            'independent_vars': list(indep_vars),
            'num_equations': 1,
            'is_linear': is_linear,
            'derivatives': list(derivatives)
        }
    
    def _check_linearity(self, equation: sp.Eq, dep_vars: set, derivatives: set) -> bool:
        """Check if equation is linear in dependent variables and derivatives."""
        try:
            # Get all terms involving dependent variables
            lhs = equation.lhs - equation.rhs
            
            # Check if polynomial in dependent variables and derivatives
            all_funcs = list(dep_vars) + list(derivatives)
            
            for func in all_funcs:
                degree = sp.degree(lhs, func)
                if degree > 1:
                    return False
            
            return True
        except Exception:
            return False  # Conservative: assume nonlinear if can't determine
    
    def solve_ode(
        self,
        equation: sp.Eq,
        dependent_var: sp.Function,
        independent_var: sp.Symbol,
        initial_conditions: Optional[Dict[str, float]] = None,
        boundary_conditions: Optional[List[BoundaryCondition]] = None
    ) -> DESolution:
        """
        Solve an ordinary differential equation.
        
        Args:
            equation: The ODE in sympy.Eq form
            dependent_var: The dependent variable (function)
            independent_var: The independent variable
            initial_conditions: Initial conditions {y(x0): y0, y'(x0): y0_prime, ...}
            boundary_conditions: Boundary conditions for BVP
            
        Returns:
            DESolution object
        """
        print(f"[DESolver] Solving ODE: {equation}")
        print(f"[DESolver] Dependent var: {dependent_var}, Independent var: {independent_var}")
        
        metadata = {'ode_type': 'general'}
        
        try:
            # Try symbolic solution with SymPy's dsolve
            general_sol = dsolve(equation, dependent_var, ics=None)
            print(f"[DESolver] General solution: {general_sol}")
            
            # Extract the solution expression
            if isinstance(general_sol, list):
                general_expr = general_sol[0].rhs
            elif hasattr(general_sol, 'rhs'):
                general_expr = general_sol.rhs
            else:
                general_expr = general_sol
            
            # Apply initial conditions if provided
            particular_expr = None
            if initial_conditions:
                try:
                    # Convert ICs to SymPy format
                    ics_dict = {}
                    for key, val in initial_conditions.items():
                        if isinstance(key, str):
                            # Parse string like "y(0)" or "y'(0)"
                            if "'" in key:
                                # Derivative IC
                                order = key.count("'")
                                x0 = self._extract_ic_point(key)
                                ics_dict[dependent_var(independent_var).diff(independent_var, order).subs(independent_var, x0)] = val
                            else:
                                # Function value IC
                                x0 = self._extract_ic_point(key)
                                ics_dict[dependent_var(x0)] = val
                        else:
                            ics_dict[key] = val
                    
                    # Solve with ICs
                    particular_sol = dsolve(equation, dependent_var, ics=ics_dict)
                    if hasattr(particular_sol, 'rhs'):
                        particular_expr = particular_sol.rhs
                    else:
                        particular_expr = particular_sol
                    
                    print(f"[DESolver] Particular solution with ICs: {particular_expr}")
                except Exception as e:
                    print(f"[DESolver] Could not apply ICs: {e}")
                    particular_expr = general_expr
            else:
                particular_expr = general_expr
            
            return DESolution(
                general_solution=general_expr,
                particular_solution=particular_expr,
                numerical_solution=None,
                grid=None,
                method='sympy_dsolve',
                metadata=metadata
            )
            
        except Exception as e:
            print(f"[DESolver] Symbolic solution failed: {e}")
            
            # Fall back to numerical method
            return self._solve_ode_numerical(
                equation, dependent_var, independent_var,
                initial_conditions, boundary_conditions
            )
    
    def _extract_ic_point(self, ic_string: str) -> float:
        """Extract the point from an IC string like 'y(0)' or 'y'(1)'."""
        import re
        match = re.search(r'\(([^)]+)\)', ic_string)
        if match:
            return float(match.group(1))
        return 0.0
    
    def _solve_ode_numerical(
        self,
        equation: sp.Eq,
        dependent_var: sp.Function,
        independent_var: sp.Symbol,
        initial_conditions: Optional[Dict[str, float]],
        boundary_conditions: Optional[List[BoundaryCondition]]
    ) -> DESolution:
        """Numerical ODE solver using finite differences or Runge-Kutta."""
        print("[DESolver] Attempting numerical solution (not yet implemented)")
        
        # TODO: Implement numerical ODE solver
        # - Extract ODE as callable function
        # - Use scipy.integrate.odeint or similar
        # - Return numerical solution on grid
        
        return DESolution(
            general_solution=None,
            particular_solution=None,
            numerical_solution=None,
            grid=None,
            method='numerical_fallback_not_implemented',
            metadata={'error': 'Numerical ODE solver not yet implemented'}
        )
    
    def solve_pde(
        self,
        equation: sp.Eq,
        dependent_var: sp.Function,
        independent_vars: List[sp.Symbol],
        boundary_conditions: Optional[List[BoundaryCondition]] = None,
        domain: Optional[Dict[str, Tuple[float, float]]] = None
    ) -> DESolution:
        """
        Solve a partial differential equation.
        
        Args:
            equation: The PDE in sympy.Eq form
            dependent_var: The dependent variable (function)
            independent_vars: List of independent variables [x, t] or [x, y] etc.
            boundary_conditions: Boundary conditions
            domain: Domain for each variable {var: (min, max)}
            
        Returns:
            DESolution object
        """
        print(f"[DESolver] Solving PDE: {equation}")
        print(f"[DESolver] Dependent var: {dependent_var}, Independent vars: {independent_vars}")
        
        # Try symbolic solution first (works for simple cases)
        try:
            # SymPy's pdsolve is experimental
            from sympy import pdsolve
            solution = pdsolve(equation, dependent_var)
            print(f"[DESolver] Symbolic PDE solution: {solution}")
            
            return DESolution(
                general_solution=solution,
                particular_solution=solution,
                numerical_solution=None,
                grid=None,
                method='sympy_pdsolve',
                metadata={'pde_type': 'general'}
            )
        except Exception as e:
            print(f"[DESolver] Symbolic PDE solution failed: {e}")
        
        # Fall back to finite difference method
        return self._solve_pde_finite_difference(
            equation, dependent_var, independent_vars,
            boundary_conditions, domain
        )
    
    def _solve_pde_finite_difference(
        self,
        equation: sp.Eq,
        dependent_var: sp.Function,
        independent_vars: List[sp.Symbol],
        boundary_conditions: Optional[List[BoundaryCondition]],
        domain: Optional[Dict[str, Tuple[float, float]]]
    ) -> DESolution:
        """Solve PDE using finite difference method."""
        print("[DESolver] Attempting finite difference solution (not yet fully implemented)")
        
        # TODO: Implement finite difference PDE solver
        # - Discretize spatial and temporal domains
        # - Build finite difference stencil
        # - Solve resulting linear system or time-step
        # - Return solution on grid
        
        return DESolution(
            general_solution=None,
            particular_solution=None,
            numerical_solution=None,
            grid=None,
            method='finite_difference_not_implemented',
            metadata={'error': 'Finite difference PDE solver not yet implemented'}
        )
    
    def classify_pde(self, equation: sp.Eq) -> str:
        """
        Classify a 2nd order linear PDE as elliptic, parabolic, or hyperbolic.
        
        For equation: A*u_xx + B*u_xy + C*u_yy + ... = 0
        Discriminant: D = B^2 - 4*A*C
        - D < 0: Elliptic (e.g., Laplace, Poisson)
        - D = 0: Parabolic (e.g., heat equation)
        - D > 0: Hyperbolic (e.g., wave equation)
        """
        # TODO: Implement PDE classification
        return 'unknown'


def test_de_solver():
    """Test the differential equation solver."""
    solver = DifferentialEquationSolver()
    
    print("=== Testing Differential Equation Solver ===\n")
    
    # Test 1: Simple ODE - dy/dx = y
    print("Test 1: dy/dx = y")
    x = sp.Symbol('x')
    y = sp.Function('y')
    ode1 = Eq(y(x).diff(x), y(x))
    
    info1 = solver.detect_equation_type(ode1)
    print(f"  Type: {info1}")
    
    sol1 = solver.solve_ode(ode1, y(x), x)
    print(f"  General solution: {sol1.general_solution}\n")
    
    # Test 2: Second order ODE - y'' + y = 0
    print("Test 2: y'' + y = 0")
    ode2 = Eq(y(x).diff(x, 2) + y(x), 0)
    
    info2 = solver.detect_equation_type(ode2)
    print(f"  Type: {info2}")
    
    sol2 = solver.solve_ode(ode2, y(x), x)
    print(f"  General solution: {sol2.general_solution}\n")
    
    # Test 3: PDE - heat equation
    print("Test 3: ∂u/∂t = α*∂²u/∂x²")
    t = sp.Symbol('t')
    x = sp.Symbol('x')
    u = sp.Function('u')
    alpha = sp.Symbol('alpha', positive=True)
    
    heat_eq = Eq(u(x, t).diff(t), alpha * u(x, t).diff(x, 2))
    
    info3 = solver.detect_equation_type(heat_eq)
    print(f"  Type: {info3}\n")


if __name__ == '__main__':
    test_de_solver()


