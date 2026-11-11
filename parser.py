from lexer import Token
from expr import Expr, Bool, Var, Not, And, Or 



"""
논리식 ::= 절 ("and" 절)* 

절 ::= 리터럴
    | "(" 절 ("or" 절)* ")"

리터럴 ::= NAME
    | "not" NAME
    | "true"
    | "false"
"""
# `A and (not P or R ) and (P or not R)` 
class Parser : 
    def __init__(self, tokens: list[Token] ) -> None : 
        self.tokens = tokens 
        self.pos = 0 


    def parse_formula(self) -> Expr : 
        if self.tokens[self.pos].kind == "EOF" : 
            raise ValueError("Empty formula")

        #첫번째 절을 읽는다. 
        left = self.parse_clause()

        while self.tokens[self.pos].kind == "AND" : 
            self.pos += 1 # "and" 토큰을 소비한다. 
            right = self.parse_clause()
            left = And(left, right) 

        if self.tokens[self.pos].kind != "EOF" :
            raise ValueError(f"잘못된 토큰입니다. {self.tokens[self.pos]}")
        return left
        

    """
    절 ::= 리터럴
        | "(" 절 ("or" 절)* ")" 
    """
    def parse_clause(self) -> Expr: 
        # 괄호가 없으면 리터럴 하나가 절이다. 
        if self.tokens[self.pos].kind != "LPAREN" :
            return self.parse_literal()
        if self.tokens[self.pos].kind == "LPAREN" :
            self.pos += 1 # "(" 토큰을 소비한다.

            left = self.parse_clause()

            while self.tokens[self.pos].kind == "OR" : 
                self.pos += 1 # "or" 토큰을 소비한다. 
                right = self.parse_clause()
                left = Or(left, right)

            # ")" 로 끝나는지 확인하고 ")" 토큰을 소비한다.

            if self.tokens[self.pos].kind != "RPAREN" :
                raise ValueError("닫는 괄호가 없습니다.")
            self.pos += 1 # ")" 토큰을 소비한다.
            return left
        else : 
            raise ValueError(f"절이 잘못되었습니다. {self.tokens[self.pos]}")

    """
   리터럴 ::= NAME
         | "not" NAME
         | "true"
         | "false"
    """
    def parse_literal(self) -> Expr: 
        if self.tokens[self.pos].kind == "NOT" : 
            self.pos += 1 # "not" 토큰을 소비 
            return Not(self.parse_literal()) # not not을 허용하지만, 그냥 함
        elif self.tokens[self.pos].kind == "NAME" :
            name = self.tokens[self.pos].text
            self.pos += 1 # NAME 토큰을 소비 
            return Var(name)
        elif self.tokens[self.pos].kind == "TRUE" : 
            self.pos += 1 # "true" 토큰을 소비 
            return Bool(True)
        elif self.tokens[self.pos].kind == "FALSE" :
            self.pos += 1 # "false" 토큰을 소비 
            return Bool(False)
        else :
            raise ValueError(f"리터럴이 잘못되었습니다. {self.tokens[self.pos]}")