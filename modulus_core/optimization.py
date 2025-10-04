"""
Optimization solver for Modulus.

Handles minimization and maximization problems with and without constraints.
"""

import sympy as sp
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import numpy as np


@dataclass
class OptimizationSolution:
    """Solution to an optimization problem."""
    optimal_value: float
    optimal_point: Dict[str, float]
    method: str
    is_constrained: bool
    lagrange_multipliers: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = None


class OptimizationSolver:
    """
    Solver for optimization problems (minimization and maximization).
    """
    
    def __init__(self):
        """Initialize the optimization solver."""
        self.supported_types = ['minimize', 'maximize', 'min', 'max']
    
    def detect_optimization_type(self, objective_type: str, constraints: List[sp.Expr]) -> Dict[str, Any]:
        """
        Analyze an optimization problem to determine its characteristics.
        
        Returns:
            Dictionary with problem metadata
        """
        is_minimize = objective_type.lower() in ['minimize', 'min']
        is_maximize = objective_type.lower() in ['maximize', 'max']
        
        if not (is_minimize or is_maximize):
            return {'is_optimization': False}
        
        has_constraints = len(constraints) > 0
        
        # Classify constraints
        equality_constraints = []
        inequality_constraints = []
        
        for constraint in constraints:
            if isinstance(constraint, sp.Eq):
                equality_constraints.append(constraint)
            elif isinstance(constraint, (sp.StrictLessThan, sp.LessThan, sp.StrictGreaterThan, sp.GreaterThan)):
                inequality_constraints.append(constraint)
        
        return {
            'is_optimization': True,
            'type': 'minimize' if is_minimize else 'maximize',
            'is_constrained': has_constraints,
            'num_equality_constraints': len(equality_constraints),
            'num_inequality_constraints': len(inequality_constraints),
            'constraints': constraints
        }
    
    def optimize(
        self,
        objective: sp.Expr,
        variables: List[sp.Symbol],
        objective_type: str = 'minimize',
        constraints: Optional[List[sp.Expr]] = None,
        bounds: Optional[Dict[str, Tuple[float, float]]] = None
    ) -> OptimizationSolution:
        """
        Solve an optimization problem.
        
        Args:
            objective: The objective function to optimize
            variables: List of decision variables
            objective_type: 'minimize' or 'maximize'
            constraints: Optional list of constraint expressions
            bounds: Optional bounds for variables {var_name: (min, max)}
            
        Returns:
            OptimizationSolution object
        """
        print(f"[OptimizationSolver] Optimizing: {objective}")
        print(f"[OptimizationSolver] Type: {objective_type}, Variables: {variables}")
        print(f"[OptimizationSolver] Constraints: {constraints}")
        
        # Convert maximize to minimize by negating objective
        if objective_type.lower() in ['maximize', 'max']:
            objective = -objective
            is_maximization = True
        else:
            is_maximization = False
        
        constraints = constraints or []
        
        # Try different solving strategies based on problem type
        if not constraints:
            # Unconstrained optimization - use calculus
            return self._solve_unconstrained(objective, variables, is_maximization)
        else:
            # Constrained optimization - use Lagrange multipliers or numerical
            return self._solve_constrained(objective, variables, constraints, is_maximization, bounds)
    
    def _solve_unconstrained(
        self,
        objective: sp.Expr,
        variables: List[sp.Symbol],
        is_maximization: bool
    ) -> OptimizationSolution:
        """Solve unconstrained optimization using calculus."""
        print("[OptimizationSolver] Solving unconstrained problem with calculus")
        
        try:
            # Compute gradient (first-order conditions)
            gradient = [sp.diff(objective, var) for var in variables]
            
            # Solve for critical points (∇f = 0)
            critical_points = sp.solve(gradient, variables, dict=True)
            
            if not critical_points:
                print("[OptimizationSolver] No critical points found")
                return OptimizationSolution(
                    optimal_value=float('inf') if not is_maximization else float('-inf'),
                    optimal_point={},
                    method='calculus_no_solution',
                    is_constrained=False,
                    metadata={'error': 'No critical points found'}
                )
            
            # Evaluate objective at each critical point
            best_value = float('inf') if not is_maximization else float('-inf')
            best_point = {}
            
            for point in critical_points:
                try:
                    value = float(objective.subs(point).evalf())
                    
                    # For minimization, want smallest value
                    # For maximization, we negated objective, so still want smallest
                    if value < best_value:
                        best_value = value
                        best_point = {str(var): float(val.evalf()) for var, val in point.items()}
                except Exception as e:
                    print(f"[OptimizationSolver] Could not evaluate at point {point}: {e}")
                    continue
            
            # If maximization, negate value back
            if is_maximization:
                best_value = -best_value
            
            # Check second-order conditions (Hessian for verification)
            try:
                hessian = sp.hessian(objective, variables)
                eigenvals = hessian.eigenvals()
                
                if all(ev > 0 for ev in eigenvals.keys()):
                    verification = "local_minimum_confirmed"
                elif all(ev < 0 for ev in eigenvals.keys()):
                    verification = "local_maximum_confirmed"
                else:
                    verification = "saddle_point_or_inconclusive"
            except Exception:
                verification = "second_order_check_failed"
            
            return OptimizationSolution(
                optimal_value=best_value,
                optimal_point=best_point,
                method='calculus_critical_points',
                is_constrained=False,
                metadata={
                    'num_critical_points': len(critical_points),
                    'verification': verification
                }
            )
            
        except Exception as e:
            print(f"[OptimizationSolver] Calculus method failed: {e}")
            # Fall back to numerical optimization
            return self._solve_numerical(objective, variables, None, is_maximization, None)
    
    def _solve_constrained(
        self,
        objective: sp.Expr,
        variables: List[sp.Symbol],
        constraints: List[sp.Expr],
        is_maximization: bool,
        bounds: Optional[Dict[str, Tuple[float, float]]]
    ) -> OptimizationSolution:
        """Solve constrained optimization using Lagrange multipliers or numerical methods."""
        print("[OptimizationSolver] Solving constrained problem")
        
        # Extract equality constraints for Lagrange multipliers
        equality_constraints = [c for c in constraints if isinstance(c, sp.Eq)]
        
        if equality_constraints and not any(isinstance(c, (sp.StrictLessThan, sp.LessThan, sp.StrictGreaterThan, sp.GreaterThan)) for c in constraints):
            # Pure equality constraints - try Lagrange multipliers
            try:
                return self._solve_lagrange(objective, variables, equality_constraints, is_maximization)
            except Exception as e:
                print(f"[OptimizationSolver] Lagrange method failed: {e}")
        
        # Fall back to numerical optimization
        return self._solve_numerical(objective, variables, constraints, is_maximization, bounds)
    
    def _solve_lagrange(
        self,
        objective: sp.Expr,
        variables: List[sp.Symbol],
        constraints: List[sp.Eq],
        is_maximization: bool
    ) -> OptimizationSolution:
        """Solve using Lagrange multipliers."""
        print("[OptimizationSolver] Using Lagrange multipliers")
        
        # Create Lagrange multipliers
        lambdas = [sp.Symbol(f'lambda_{i}') for i in range(len(constraints))]
        
        # Build Lagrangian: L = f + Σ λᵢ·gᵢ
        lagrangian = objective
        for lam, constraint in zip(lambdas, constraints):
            # constraint is Eq(lhs, rhs), so g = lhs - rhs
            g = constraint.lhs - constraint.rhs
            lagrangian += lam * g
        
        # Compute gradient of Lagrangian
        all_vars = variables + lambdas
        grad_lagrangian = [sp.diff(lagrangian, var) for var in all_vars]
        
        # Solve ∇L = 0
        solutions = sp.solve(grad_lagrangian, all_vars, dict=True)
        
        if not solutions:
            raise RuntimeError("No solutions found for Lagrange system")
        
        # Evaluate objective at solutions
        best_value = float('inf') if not is_maximization else float('-inf')
        best_point = {}
        best_multipliers = {}
        
        for sol in solutions:
            try:
                # Extract variable values
                point = {str(var): float(sol[var].evalf()) for var in variables if var in sol}
                multipliers = {str(lam): float(sol[lam].evalf()) for lam in lambdas if lam in sol}
                
                # Evaluate objective
                value = float(objective.subs(sol).evalf())
                
                if (not is_maximization and value < best_value) or (is_maximization and value > best_value):
                    best_value = value
                    best_point = point
                    best_multipliers = multipliers
            except Exception as e:
                print(f"[OptimizationSolver] Could not evaluate solution: {e}")
                continue
        
        # If maximization, negate value back
        if is_maximization:
            best_value = -best_value
        
        return OptimizationSolution(
            optimal_value=best_value,
            optimal_point=best_point,
            method='lagrange_multipliers',
            is_constrained=True,
            lagrange_multipliers=best_multipliers,
            metadata={'num_solutions': len(solutions)}
        )
    
    def _solve_numerical(
        self,
        objective: sp.Expr,
        variables: List[sp.Symbol],
        constraints: Optional[List[sp.Expr]],
        is_maximization: bool,
        bounds: Optional[Dict[str, Tuple[float, float]]]
    ) -> OptimizationSolution:
        """Numerical optimization using scipy (placeholder)."""
        print("[OptimizationSolver] Numerical optimization not yet fully implemented")
        
        # TODO: Integrate scipy.optimize.minimize
        # - Convert SymPy expressions to callable functions
        # - Set up constraint dict for scipy
        # - Choose appropriate method (SLSQP for constrained, BFGS for unconstrained)
        # - Return numerical solution
        
        return OptimizationSolution(
            optimal_value=0.0,
            optimal_point={},
            method='numerical_not_implemented',
            is_constrained=constraints is not None and len(constraints) > 0,
            metadata={'error': 'Numerical optimization not yet implemented'}
        )


def test_optimization_solver():
    """Test the optimization solver."""
    solver = OptimizationSolver()
    
    print("=== Testing Optimization Solver ===\n")
    
    # Test 1: Minimize f(x) = x² + 2x + 1
    print("Test 1: Minimize f(x) = x² + 2x + 1")
    x = sp.Symbol('x')
    objective1 = x**2 + 2*x + 1
    
    sol1 = solver.optimize(objective1, [x], 'minimize')
    print(f"  Optimal value: {sol1.optimal_value}")
    print(f"  Optimal point: {sol1.optimal_point}\n")
    
    # Test 2: Maximize f(x,y) = -(x² + y²)
    print("Test 2: Maximize f(x,y) = -(x² + y²)")
    y = sp.Symbol('y')
    objective2 = -(x**2 + y**2)
    
    sol2 = solver.optimize(objective2, [x, y], 'maximize')
    print(f"  Optimal value: {sol2.optimal_value}")
    print(f"  Optimal point: {sol2.optimal_point}\n")
    
    # Test 3: Minimize f(x,y) = x² + y² subject to x + y = 1
    print("Test 3: Minimize x² + y² subject to x + y = 1")
    objective3 = x**2 + y**2
    constraint = sp.Eq(x + y, 1)
    
    sol3 = solver.optimize(objective3, [x, y], 'minimize', [constraint])
    print(f"  Optimal value: {sol3.optimal_value}")
    print(f"  Optimal point: {sol3.optimal_point}")
    print(f"  Lagrange multipliers: {sol3.lagrange_multipliers}\n")


if __name__ == '__main__':
    test_optimization_solver()


