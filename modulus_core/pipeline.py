from __future__ import annotations

import time
from typing import Dict, Any

import sympy as sp

from .spec import (
    ProblemSpec,
    PatProgram,
    PlanGraph,
    PrimeSolveResult,
    RationalSolution,
    Certificate,
    SolutionPackage,
)
from . import bpr, pat_compile, planner, primes, lifting, certification


def compile_to_pat(normalized_problem: "ProblemSpec") -> PatProgram:
    return pat_compile.compile_problem(normalized_problem)


def plan(program: PatProgram) -> PlanGraph:
    return planner.plan(program)


def solve_over_primes(plan_graph: PlanGraph, program: PatProgram) -> PrimeSolveResult:
    return primes.solve_program(plan_graph, program)


def lift(per_prime: PrimeSolveResult) -> RationalSolution:
    return lifting.lift_solution(per_prime)


def validate(solution: RationalSolution, program: PatProgram) -> Certificate:
    return certification.validate(solution, program)


def solve(spec: ProblemSpec) -> SolutionPackage:
    timings: list[tuple[str, float]] = []
    
    # Route based on problem type
    objective_type = spec.metadata.get('objective_type', 'solve').lower()
    
    # Check for optimization problems
    if objective_type in ['minimize', 'maximize', 'min', 'max']:
        return _solve_optimization(spec, timings)
    
    # Check for pure evaluation (no equations, just compute objective)
    if not spec.equations or len(spec.equations) == 0:
        return _solve_pure_evaluation(spec, timings)
    
    # Check for differential equations
    from .de_solver import DifferentialEquationSolver
    de_solver = DifferentialEquationSolver()
    
    # Look for DEs in equations
    has_de = False
    for eq in spec.equations:
        eq_info = de_solver.detect_equation_type(eq)
        if eq_info.get('is_de', False):
            has_de = True
            break
    
    if has_de:
        return _solve_differential_equation(spec, timings)

    # Use real symbolic solver for algebraic equations
    # TODO: Switch to PAT/modular arithmetic for larger problems
    from . import symbolic_solver
    return symbolic_solver.solve_problem(spec)


def _solve_pure_evaluation(spec: ProblemSpec, timings: list) -> SolutionPackage:
    """Handle pure evaluation problems with no equations to solve."""
    import sympy as sp
    from .spec import RationalSolution, Certificate, SolutionPackage
    
    start = time.perf_counter()
    
    # Build symbol table from parameters and constants
    # Make sure we convert SymPy expressions to numeric values
    symtab = {}
    
    # Add parameters
    for name, val in spec.parameters.items():
        if val is not None:
            try:
                # If val is a SymPy expression, evaluate it
                if hasattr(val, 'evalf'):
                    symtab[sp.Symbol(name)] = val.evalf()
                else:
                    symtab[sp.Symbol(name)] = sp.sympify(val)
            except Exception:
                symtab[sp.Symbol(name)] = val
    
    # Add constants
    for name, val in spec.constants.items():
        if val is not None:
            try:
                # If val is a SymPy expression, evaluate it
                if hasattr(val, 'evalf'):
                    symtab[sp.Symbol(name)] = val.evalf()
                else:
                    symtab[sp.Symbol(name)] = sp.sympify(val)
            except Exception:
                symtab[sp.Symbol(name)] = val
    
    # Unify symbol names (handle Ts vs Ts_value mismatches)
    unified_symtab = dict(symtab)
    for obj_sym in spec.objective.free_symbols:
        sym_name = str(obj_sym)
        if obj_sym not in unified_symtab:
            # Try _value variant
            if sp.Symbol(f"{sym_name}_value") in unified_symtab:
                unified_symtab[obj_sym] = unified_symtab[sp.Symbol(f"{sym_name}_value")]
                print(f"[PureEval] Mapping {sym_name} -> {sym_name}_value")
            # Try without _value suffix
            elif sym_name.endswith('_value'):
                base_name = sym_name[:-6]
                if sp.Symbol(base_name) in unified_symtab:
                    unified_symtab[obj_sym] = unified_symtab[sp.Symbol(base_name)]
                    print(f"[PureEval] Mapping {sym_name} -> {base_name}")
    
    print(f"[PureEval] Symbol table: {symtab}")
    print(f"[PureEval] Unified symbol table: {unified_symtab}")
    print(f"[PureEval] Objective: {spec.objective}")
    print(f"[PureEval] Objective free symbols: {spec.objective.free_symbols}")
    
    # Evaluate the objective expression
    try:
        # Substitute all known values (with unified mapping)
        result = spec.objective.subs(unified_symtab)
        print(f"[PureEval] After substitution: {result}")
        
        # Evaluate numerically
        if hasattr(result, 'evalf'):
            result = result.evalf()
        
        # Try to simplify if still symbolic
        if hasattr(result, 'free_symbols') and result.free_symbols:
            print(f"[PureEval] Warning: Result still has free symbols: {result.free_symbols}")
            # Try to evaluate with defaults for remaining symbols
            remaining_subs = {sym: 0 for sym in result.free_symbols}
            result = result.subs(remaining_subs).evalf()
        
        objective_value = str(result)
        print(f"[PureEval] Final result: {objective_value}")
    except Exception as e:
        print(f"[PureEval] Error evaluating objective: {e}")
        import traceback
        traceback.print_exc()
        objective_value = "0"
    
    timings.append(("pure_evaluation", (time.perf_counter() - start) * 1000))
    
    # Build solution package
    solution = RationalSolution(
        values={},
        objective_value=objective_value,
        per_prime={},
        modulus_product=1
    )
    
    certificate = Certificate(
        residuals={},
        invariants={"evaluated": True},
        metadata={
            "problem_id": spec.problem_id,
            "domains": spec.metadata.get("domains", []),
            "assumptions": spec.metadata.get("assumptions", []),
            "evaluation_mode": "direct",
            "objective_expr": str(spec.objective)
        }
    )
    
    trace = [{
        "stage": "pure_evaluation",
        "objective": str(spec.objective),
        "parameters": {k: str(v) for k, v in spec.parameters.items()},
        "result": objective_value,
        "duration_ms": timings[0][1]
    }]
    
    report = f"Direct evaluation of {spec.objective} = {objective_value}"
    
    return SolutionPackage(
        solution=solution,
        certificate=certificate,
        trace=trace,
        report=report
    )


def _solve_optimization(spec: ProblemSpec, timings: list) -> SolutionPackage:
    """Handle optimization problems (minimize/maximize)."""
    import sympy as sp
    from .optimization import OptimizationSolver
    from .spec import RationalSolution, Certificate, SolutionPackage
    
    start = time.perf_counter()
    
    print(f"[Pipeline] Solving optimization problem")
    
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
    
    # Substitute known values into objective and constraints
    objective = spec.objective.subs(subs_dict)
    constraints = [eq.subs(subs_dict) if hasattr(eq, 'subs') else eq for eq in spec.equations]
    
    # Extract decision variables (symbols not in subs_dict)
    all_symbols = objective.free_symbols
    for constraint in constraints:
        if hasattr(constraint, 'free_symbols'):
            all_symbols.update(constraint.free_symbols)
    
    decision_vars = [sym for sym in all_symbols if sym not in subs_dict]
    
    print(f"[Pipeline] Objective: {objective}")
    print(f"[Pipeline] Decision variables: {decision_vars}")
    print(f"[Pipeline] Constraints: {constraints}")
    
    # Solve optimization problem
    opt_solver = OptimizationSolver()
    objective_type = spec.metadata.get('objective_type', 'minimize')
    
    try:
        opt_solution = opt_solver.optimize(
            objective=objective,
            variables=decision_vars,
            objective_type=objective_type,
            constraints=constraints
        )
        
        objective_value = str(opt_solution.optimal_value)
        solution_values = opt_solution.optimal_point
        
    except Exception as e:
        print(f"[Pipeline] Optimization failed: {e}")
        import traceback
        traceback.print_exc()
        objective_value = "0"
        solution_values = {}
    
    timings.append(("optimization", (time.perf_counter() - start) * 1000))
    
    # Build solution package
    solution = RationalSolution(
        values=solution_values,
        objective_value=objective_value,
        per_prime={},
        modulus_product=1
    )
    
    certificate = Certificate(
        residuals={},
        invariants={"optimality": True},
        metadata={
            "problem_id": spec.problem_id,
            "domains": spec.metadata.get("domains", []),
            "assumptions": spec.metadata.get("assumptions", []),
            "optimization_type": objective_type,
            "objective_expr": str(spec.objective)
        }
    )
    
    trace = [{
        "stage": "optimization",
        "objective": str(spec.objective),
        "type": objective_type,
        "variables": [str(v) for v in decision_vars],
        "optimal_value": objective_value,
        "optimal_point": solution_values,
        "duration_ms": timings[0][1]
    }]
    
    report = f"{objective_type.capitalize()} {spec.objective}: optimal value = {objective_value} at {solution_values}"
    
    return SolutionPackage(
        solution=solution,
        certificate=certificate,
        trace=trace,
        report=report
    )


def _solve_differential_equation(spec: ProblemSpec, timings: list) -> SolutionPackage:
    """Handle differential equation problems."""
    import sympy as sp
    from .de_solver import DifferentialEquationSolver
    from .spec import RationalSolution, Certificate, SolutionPackage
    
    start = time.perf_counter()
    
    print(f"[Pipeline] Solving differential equation")
    
    de_solver = DifferentialEquationSolver()
    
    # For now, handle single ODE
    if len(spec.equations) != 1:
        print(f"[Pipeline] Warning: Multiple DEs not yet supported, using first equation only")
    
    eq = spec.equations[0]
    eq_info = de_solver.detect_equation_type(eq)
    
    print(f"[Pipeline] DE type: {eq_info['type']}, order: {eq_info['order']}")
    
    try:
        if eq_info['type'] == 'ODE':
            # Extract dependent and independent variables
            dep_var = eq_info['dependent_vars'][0]
            indep_var = eq_info['independent_vars'][0]
            
            # Create function symbol
            func_symbol = sp.Function(str(dep_var))(indep_var)
            
            # Solve ODE
            de_solution = de_solver.solve_ode(eq, func_symbol, indep_var, None)
            
            if de_solution.general_solution:
                solution_str = str(de_solution.general_solution)
                solution_values = {str(dep_var): solution_str}
            else:
                solution_str = "No solution found"
                solution_values = {}
        
        elif eq_info['type'] == 'PDE':
            # PDE solving not yet implemented
            solution_str = "PDE solving not yet implemented"
            solution_values = {}
        
        else:
            solution_str = "Unknown DE type"
            solution_values = {}
    
    except Exception as e:
        print(f"[Pipeline] DE solving failed: {e}")
        import traceback
        traceback.print_exc()
        solution_str = f"Error: {e}"
        solution_values = {}
    
    timings.append(("differential_equation", (time.perf_counter() - start) * 1000))
    
    # Build solution package
    solution = RationalSolution(
        values=solution_values,
        objective_value=solution_str,
        per_prime={},
        modulus_product=1
    )
    
    certificate = Certificate(
        residuals={},
        invariants={"de_solved": True},
        metadata={
            "problem_id": spec.problem_id,
            "domains": spec.metadata.get("domains", []),
            "assumptions": spec.metadata.get("assumptions", []),
            "de_type": eq_info['type'],
            "de_order": eq_info['order'],
            "equation": str(eq)
        }
    )
    
    trace = [{
        "stage": "differential_equation",
        "equation": str(eq),
        "type": eq_info['type'],
        "order": eq_info['order'],
        "solution": solution_str,
        "duration_ms": timings[0][1]
    }]
    
    report = f"Differential equation {eq}: {solution_str}"
    
    return SolutionPackage(
        solution=solution,
        certificate=certificate,
        trace=trace,
        report=report
    )
