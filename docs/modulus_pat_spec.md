# Modulus Architecture Specification (PAT-First, BPR-Centered)

## 0. Design Goals
- **One core engine**: All problems compile into **Prime Algebra Transformer (PAT)** form.
- **Exact arithmetic only**: Operate over integers, rationals, or algebraic fields via modular arithmetic, CRT, and Hensel lifting.
- **Resonance-first worldview**: Use **Boundary Phase Resonance (BPR)** as the organizing principle, ensuring every operator and solution respects resonance invariants.
- **No floating-point approximations.**
- **Deterministic, auditable, reproducible results** with machine-checkable certificates.

## 1. High-Level Flow
1. **Input Spec**
   - Structured JSON: variables, equations, constraints, objectives, boundary conditions, tolerances, invariants.
   - Examples: PDE, ODE, optimization, algebraic systems.
2. **BPR Encoding**
   - Map the problem into resonance form (boundaries, phases, invariants, conservation laws).
3. **PAT Compilation**
   - Translate into discrete operator algebra over integers/rationals.
   - Build exact BPR-preserving lattice operators (grad, div, curl, Laplacian, boundary traces).
4. **Planning**
   - Detect structure (circulant → NTT, sparse → finite-field LU/Wiedemann, nonlinear → algebraic fixed point or Newton with symbolic bounds).
   - Encode optimization as exact **KKT polynomial systems**.
5. **Finite-Field Solve**
   - Choose multiple large primes.
   - Solve each subproblem modulo p using exact algebra.
   - Combine results via CRT, lift to integers/rationals via Hensel lifting.
6. **Validation**
   - Residuals = 0 in ℤ/ℚ.
   - Verify resonance invariants (flux, energy, phase continuity).
   - Optimization: primal/dual feasible, zero duality gap.
   - Nonlinear: contraction constant + tail bound proofs.
7. **Certificates & Reports**
   - Emit machine-checkable certificate JSON.
   - Produce a human-readable explanation trace (built solely from certified facts).

## 2. Interfaces
```python
solve(spec) -> SolutionPackage
compile_to_pat(spec) -> PatProgram
plan(program) -> PlanGraph
solve_over_primes(plan, program) -> {per_prime_solutions}
lift(per_prime_solutions) -> RationalSolution
validate(solution, program, invariants) -> Certificate
explain(trace, certificate) -> Report
```

## 3. Supported Problem Classes
- Linear PDEs (elliptic, parabolic, hyperbolic) on structured lattices.
- Linear ODEs with rational coefficients.
- Optimization: LP/QP (rational data) with convex KKT encoding.
- Polynomial systems over ℚ.
- Nonlinear problems via exact series expansions and contraction proofs.

## 4. Checklist for Accepting Problems
- [ ] Constants are integers, rationals, or algebraic numbers (with minimal polynomial).
- [ ] Transcendentals have certified series expansions and remainder bounds.
- [ ] Operators (grad, div, Laplacian, etc.) map into the PAT IR.
- [ ] Domain discretization uses BPR-preserving stencils.
- [ ] Boundary conditions encoded as algebraic boundary operators.
- [ ] Nonlinear problems include contraction/Newton region proof.
- [ ] Prime modulus bounds ensure unique CRT lifting.
- [ ] Dimension and unit checks pass intake.

## 5. Behavior on Unsupported Input
- Operator missing in IR → **UNSUPPORTED_OPERATOR** (include offending expression).
- Irrational constant without support → **NEEDS_MINIMAL_POLYNOMIAL** or **NEEDS_SERIES_BOUND**.
- Missing convergence proof → **INCOMPLETE_PROOF**.
- Never approximate numerically; fail with actionable error.

## 6. Validation Rules
- PDE/ODE: residual = 0, invariants (flux, energy) conserved.
- Optimization: primal & dual feasible, zero duality gap, rational dual certificate.
- Nonlinear: certified tail bound, symbolic remainder inequality verified.
- Certificates must be cryptographically signed and externally verifiable.

## 7. Extending to “Any Math”
1. Algebraic number fields ℚ(α).
2. Exact Discrete Exterior Calculus for curved manifolds.
3. SOS/moment certificates for polynomial & nonlinear optimization.
4. Certified transcendental library (exp, log, trig, special functions).
5. Stochastic calculus via discrete martingale transforms.

## 8. Output Contracts
**SolutionPackage** must provide:
- `solution`: exact rationals/algebraic numbers.
- `certificate`: machine-checkable JSON capturing invariants.
- `trace`: DAG of operations with content hashes.
- `report`: human-readable explanation.

## Bottom Line
- Compile every problem into PAT form.
- Solve exactly over finite fields; never approximate.
- Validate against resonance invariants.
- Return a certificate or structured failure.
- Extend coverage with algebraic operators/libraries, not floating-point fallbacks.

