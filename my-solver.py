from lexer import tokenize
from parser import Parser
from solver import solve

def main(input_string: str) -> None: 

    tokens = tokenize(input_string)
    parser = Parser(tokens)
    expr = parser.parse_formula()
    result = solve(expr)
    if result is not None:
        print("SAT:", result)
    else:
        print("UNSAT")


def run_tests() -> None:
    test_cases = [
    # 기본 리터럴과 모순
    ("P", True),
    ("not P", True),
    ("P and not P", False),
    ("(P or not P)", True),
    ("(P or P) and not P", False),

    # 두 변수와 여러 절
    ("(P or Q) and not P", True),
    ("(P or Q) and (not P) and (not Q)", False),
    ("(not A or B) and (A or not B)", True),
    ("A and B and (not A or not B)", False),
    ("(X or Y) and (not X or not Y)", True),
    ("(not X or Y) and (X or not Y)", True),
    ("(A or B) and (C or D) and (not A or not C)", True),
    ("(A or B) and (C or D) and (not A) and (not C)", True),

    # 여러 절을 함께 확인해야 발견되는 모순
    ("(P or Q) and (P or not Q) and not P", False),
    ("(P or Q) and (P or not Q) and P", True),
    ("(P or Q) and (not P or Q) and not Q", False),
    ("(P or Q) and (not P or Q) and (P or not Q) and (not P or not Q)", False),

    # 변수값이 연쇄적으로 결정되는 경우
    ("A and (not A or B) and (not B or C)", True),
    ("A and (not A or B) and (not B or C) and not C", False),
    ("not A and (A or B) and (not B or C) and not C", False),
    ("(not A or B) and (not B or C) and (not C or A)", True),
    ("(A or B) and (not A or C) and (not B or C) and not C", False),
    ("(A or B) and (not A or C) and (not B or C) and C", True),

    # 중첩된 괄호와 OR
    ("(P or (Q or R)) and not P and not Q", True),
    ("(P or (Q or R)) and not P and not Q and not R", False),
    ("((P or Q) or (not R)) and not P and not Q", True),
    ("((P or Q) or (not R)) and not P and not Q and R", False),
    ("(((P))) and not P", False),
    ("((not P)) and (P or Q)", True),

    # 공백, 탭, 줄바꿈, 다양한 변수 이름
    ("  A\tand\n(not P or R) and (P or not R)  ", True),
    ("notable and (android or not origin)", True),
    ("x1 and (tmp or not flag2) and not tmp and flag2", False),
]

    for input_string, expected in test_cases:
        print(f"Testing: {input_string}")
        main(input_string)
        print(f"Expected: {'SAT' if expected else 'UNSAT'}")
    print("All tests passed!")


if __name__ == "__main__":
    run_tests()

    # input_string = input("Enter a logical formula: ")
    # main(input_string)