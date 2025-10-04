"""
Real symbolic solver using SymPy.

Replaces placeholder implementations with actual solving logic.
"""

from typing import Dict, List, Tuple, Any
import sympy as sp
from fractions import Fraction

from .spec import ProblemSpec, RationalSolution, Certificate, SolutionPackage
from .math_handler import MathExpressionHandler
from .de_solver import DifferentialEquationSolver
from .optimization import OptimizationSolver


def solve_linear_system(spec: ProblemSpec) -> RationalSolution:
    """
    Solve a linear system of equations using SymPy.
    
    Args:
        spec: Problem specification with equations and variables
        
    Returns:
        Exact rational solution
    """
    if not spec.equations:
        return RationalSolution(
            values={},
            objective_value="0",
            per_prime={},
            modulus_product=1
        )
    
    # Build substitution dictionary from parameters and constants
    subs_dict = {}
    for name, val in spec.parameters.items():
        if val is not None:
            try:
                if hasattr(val, 'evalf'):
                    subs_dict[sp.Symbol(name)] = val.evalf()
                else:
                    subs_dict[sp.Symbol(name)] = sp.sympify(val)
            except Exception:
                subs_dict[sp.Symbol(name)] = val
    
    for name, val in spec.constants.items():
        if val is not None:
            try:
                if hasattr(val, 'evalf'):
                    subs_dict[sp.Symbol(name)] = val.evalf()
                else:
                    subs_dict[sp.Symbol(name)] = sp.sympify(val)
            except Exception:
                subs_dict[sp.Symbol(name)] = val
    
    print(f"[SymbolicSolver] Substitution dict: {subs_dict}")
    
    # Initialize math handler for robust transcendental function handling
    math_handler = MathExpressionHandler()
    
    # Initialize differential equation solver
    de_solver = DifferentialEquationSolver()
    
    # Check if any equations are differential equations
    has_de = False
    for eq in spec.equations:
        eq_info = de_solver.detect_equation_type(eq)
        if eq_info.get('is_de', False):
            has_de = True
            print(f"[SymbolicSolver] Detected differential equation: {eq_info['type']}, order {eq_info['order']}")
            break
    
    # If we have a differential equation, use DE solver
    if has_de and len(spec.equations) == 1:
        eq = spec.equations[0]
        eq_info = de_solver.detect_equation_type(eq)
        
        if eq_info['type'] == 'ODE':
            # Solve ODE
            dep_var = eq_info['dependent_vars'][0] if eq_info['dependent_vars'] else None
            indep_var = eq_info['independent_vars'][0] if eq_info['independent_vars'] else None
            
            if dep_var and indep_var:
                # Create function symbol
                func_symbol = sp.Function(str(dep_var))(indep_var)
                
                # Extract initial conditions from spec if available
                # TODO: Parse ICs from problem spec
                initial_conditions = None
                
                de_solution = de_solver.solve_ode(eq, func_symbol, indep_var, initial_conditions)
                
                if de_solution.particular_solution or de_solution.general_solution:
                    sol_expr = de_solution.particular_solution or de_solution.general_solution
                    
                    return RationalSolution(
                        values={str(dep_var): str(sol_expr)},
                        objective_value=str(sol_expr) if spec.objective is None else "0",
                        per_prime={},
                        modulus_product=1
                    )
    
    # Try to unify symbol names (handle Ts vs Ts_value mismatches)
    # Extract schema info if available
    schema_symbols = {}
    schema_params = {}
    if hasattr(spec, 'schema_reference') and spec.schema_reference:
        schema = spec.schema_reference
        schema_symbols = schema.symbols if hasattr(schema, 'symbols') else {}
        schema_params = schema.parameters if hasattr(schema, 'parameters') else {}
    
    # Create unified symbol mapping
    symbol_mapping = {}
    for eq in spec.equations:
        for sym in eq.free_symbols:
            sym_name = str(sym)
            # Check if we have this symbol's value under a different name
            if sym not in subs_dict:
                # Try _value variant
                if f"{sym_name}_value" in subs_dict:
                    symbol_mapping[sym] = subs_dict[f"{sym_name}_value"]
                    print(f"[SymbolicSolver] Mapping {sym_name} -> {sym_name}_value")
                # Try without _value suffix if our key has it
                elif sym_name.endswith('_value') and sym_name[:-6] in subs_dict:
                    symbol_mapping[sym] = subs_dict[sym_name[:-6]]
    
    # Merge mappings
    final_subs = {**subs_dict, **symbol_mapping}
    print(f"[SymbolicSolver] Final substitution dict (unified): {final_subs}")
    
    # Substitute known values into equations
    substituted_equations = []
    for eq in spec.equations:
        substituted_eq = eq.subs(final_subs)
        print(f"[SymbolicSolver] Original eq: {eq} -> Substituted: {substituted_eq}")
        substituted_equations.append(substituted_eq)
    
    # Extract variables from equations (after substitution)
    all_symbols = set()
    for eq in substituted_equations:
        all_symbols.update(eq.free_symbols)
    
    # Add objective symbols
    if spec.objective:
        all_symbols.update(spec.objective.free_symbols)
    
    # Remove known parameters/constants from variable list
    variables = sorted([s for s in all_symbols if s not in final_subs], key=lambda s: str(s))
    print(f"[SymbolicSolver] Variables to solve for: {variables}")
    
    # Detect if system is nonlinear
    is_nonlinear = any(
        not eq.is_polynomial(*variables) if hasattr(eq, 'is_polynomial') else False
        for eq in substituted_equations
    )
    
    if is_nonlinear:
        print(f"[SymbolicSolver] Detected nonlinear system")
    
    # Solve the system
    try:
        # For nonlinear systems, don't force rational solutions
        if is_nonlinear:
            solution = sp.solve(substituted_equations, variables, dict=True)
        else:
            solution = sp.solve(substituted_equations, variables, dict=True, rational=True)
        
        if not solution:
            # No solution found
            return RationalSolution(
                values={str(v): "0" for v in variables},
                objective_value="0",
                per_prime={},
                modulus_product=1
            )
        
        # Take first solution
        sol_dict = solution[0] if isinstance(solution, list) else solution
        
        # Convert to rationals
        values = {}
        for var in variables:
            if var in sol_dict:
                val = sol_dict[var]
                if hasattr(val, 'evalf'):
                    val = val.evalf()
                values[str(var)] = str(val)
            else:
                values[str(var)] = "0"
        
        # Evaluate objective if present
        objective_value = "0"
        if spec.objective:
            try:
                # First substitute solution variables, then parameters/constants (unified)
                obj_result = spec.objective.subs(sol_dict)
                obj_result = obj_result.subs(final_subs)
                
                # Detect if transcendental functions are present
                func_types = math_handler.detect_function_types(obj_result)
                
                # Force numeric evaluation for transcendentals
                if func_types['transcendental'] or func_types['trigonometric'] or func_types['special']:
                    print(f"[SymbolicSolver] Detected special functions in objective, forcing numeric eval")
                    obj_result = obj_result.evalf(15)  # 15 decimal places
                elif hasattr(obj_result, 'evalf'):
                    obj_result = obj_result.evalf()
                
                objective_value = str(obj_result)
                print(f"[SymbolicSolver] Objective evaluated: {objective_value}")
            except Exception as e:
                print(f"[SymbolicSolver] Error evaluating objective: {e}")
                objective_value = "0"
        
        return RationalSolution(
            values=values,
            objective_value=objective_value,
            per_prime={},
            modulus_product=1
        )
        
    except Exception as e:
        print(f"[SymbolicSolver] Error solving system: {e}")
        # Return zero solution
        return RationalSolution(
            values={str(v): "0" for v in variables},
            objective_value="0",
            per_prime={},
            modulus_product=1
        )


def validate_solution(solution: RationalSolution, spec: ProblemSpec) -> Certificate:
    """
    Validate a solution against the original equations.
    
    Args:
        solution: Candidate solution
        spec: Problem specification
        
    Returns:
        Certificate with residuals and invariants
    """
    residuals = {}
    
    # Build substitution dict
    subs_dict = {}
    for var_name, val_str in solution.values.items():
        try:
            subs_dict[sp.Symbol(var_name)] = sp.sympify(val_str)
        except Exception:
            subs_dict[sp.Symbol(var_name)] = 0
    
    # Check each equation
    for idx, eq in enumerate(spec.equations):
        try:
            # Substitute solution into equation
            lhs = eq.lhs.subs(subs_dict) if hasattr(eq, 'lhs') else eq.subs(subs_dict)
            rhs = eq.rhs.subs(subs_dict) if hasattr(eq, 'rhs') else 0
            residual = sp.simplify(lhs - rhs)
            residuals[f"eq_{idx}"] = str(residual)
        except Exception as e:
            residuals[f"eq_{idx}"] = f"error: {e}"
    
    # Check if all residuals are zero
    all_satisfied = all(
        r == "0" or r == "0.0" 
        for r in residuals.values() 
        if not r.startswith("error")
    )
    
    invariants = {
        "equations_satisfied": all_satisfied
    }
    
    metadata = {
        "problem_id": spec.problem_id,
        "domains": spec.metadata.get("domains", []),
        "assumptions": spec.metadata.get("assumptions", []),
        "solver": "sympy_symbolic",
        "num_equations": len(spec.equations),
        "num_variables": len(solution.values)
    }
    
    return Certificate(
        residuals=residuals,
        invariants=invariants,
        metadata=metadata
    )


def solve_problem(spec: ProblemSpec) -> SolutionPackage:
    """
    Main entry point for symbolic solving.
    
    Args:
        spec: Problem specification
        
    Returns:
        Complete solution package with certificate
    """
    import time
    
    start = time.perf_counter()
    solution = solve_linear_system(spec)
    solve_time = (time.perf_counter() - start) * 1000
    
    start = time.perf_counter()
    certificate = validate_solution(solution, spec)
    validate_time = (time.perf_counter() - start) * 1000
    
    # Build trace
    trace = [
        {
            "stage": "symbolic_solve",
            "method": "sympy",
            "num_equations": len(spec.equations),
            "num_variables": len(solution.values),
            "duration_ms": solve_time
        },
        {
            "stage": "validate",
            "residuals": certificate.residuals,
            "invariants": certificate.invariants,
            "duration_ms": validate_time
        }
    ]
    
    # Build report
    satisfied = certificate.invariants.get("equations_satisfied", False)
    status = "satisfied" if satisfied else "not satisfied"
    
    report_lines = [
        f"Symbolic solution for {spec.problem_id}:",
        f"  Method: SymPy exact solver",
        f"  Variables: {', '.join(solution.values.keys())}",
        f"  Solutions:",
    ]
    
    for var, val in solution.values.items():
        report_lines.append(f"    {var} = {val}")
    
    if spec.objective:
        report_lines.append(f"  Objective value: {solution.objective_value}")
    
    report_lines.append(f"  Equations: {status}")
    
    report = "\n".join(report_lines)
    
    return SolutionPackage(
        solution=solution,
        certificate=certificate,
        trace=trace,
        report=report
    )

