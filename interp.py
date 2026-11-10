from expr import Expr, Bool, Var, Not, And, Or 


def value_of(expr : Expr, env = {}) -> bool:
    match expr: 
        case Bool(value):
            return value
        case Var(name): 
            return env[name]
        case Not(expr): 
            return not value_of(expr, env)
        case And(left, right): 
            l_var = value_of(left, env)
            r_var = value_of(right, env)
            return l_var and r_var
        case Or(left, right):
            l_var = value_of(left, env)
            r_var = value_of(right, env)
            return l_var or r_var
        case _:
            raise ValueError(f"Unknown expression: {expr}")

def variables_of(expr : Expr) -> set[str]:
    match expr: 
        case Bool(_) : return set()
        case Var(name) : return {name}
        case Not(expr) : return variables_of(expr)
        case And(left, right) : return variables_of(left) | variables_of(right) # 여기서 원소들이 합집합으로 합쳐짐
        case Or(left, right) : return variables_of(left) | variables_of(right)
        case _ : raise ValueError(f"Unknown expression: {expr}")


if __name__ == "__main__":
    # (P ∨ Q) ∧ ¬P
    formula = And( Or(Var("P"), Var("Q")), Not(Var("P")) )
    env = {"P": True, "Q": False}

    print(variables_of(formula))  # {'P', 'Q'}
    print(value_of(formula, {"P": False, "Q": True}))   # True
    print(value_of(formula, {"P": True,  "Q": True}))   # False
    print(value_of(formula, {"P": False, "Q": False}))  # False