from dataclasses import dataclass

"""
Expr ::= Bool | Var | Not | And | Or
"""
class Expr:
    """Base class for all expressions."""
    pass

@dataclass
class Bool(Expr): 
    """Represents a boolean literal."""
    value: bool

@dataclass
class Var(Expr): 
    """Represents a variable."""
    name: str

@dataclass 
class Not(Expr):
    """Represents a logical NOT operation."""
    expr: Expr 


@dataclass
class And(Expr): 
    """Represents a logical AND operation."""
    left : Expr 
    right : Expr

@dataclass
class Or(Expr):
    """Represents a logical OR operation."""
    left : Expr 
    right : Expr


    