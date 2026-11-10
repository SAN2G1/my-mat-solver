from interp import value_of, variables_of
from expr import Expr, Bool, Var, Not, And, Or



def solve(expr) : 
    vars = variables_of(expr) 
    n = len(vars)
    for i in range(2**n) : 
        env = {} 
        for j, var in enumerate(vars) : 
            env[var] = bool((i >> (n-j-1) ) & 1) 
        if value_of(expr, env) : 
            return env
    return None


if __name__ == "__main__":
    # (P ∨ Q) ∧ ¬P
    formula = And( Or(Var("P"), Var("Q")), Not(Var("P")) )
    result = solve(formula)
    if result is not None : 
        print("SAT:", result)
    else : 
        print("UNSAT")