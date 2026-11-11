# My SAT Solver

Python으로 만든 간단한 명제 논리 SAT solver입니다. 문자열로 작성한 CNF 형태의 논리식을 AST로 변환하고, 가능한 모든 변수 할당을 탐색해 식을 참으로 만드는 해를 찾습니다.

## 요구 사항

- Python 3.10 이상
- 외부 패키지 없음

## 실행

저장소를 내려받은 뒤 다음 명령을 실행합니다.

```bash
python3 my-solver.py
```

현재 `my-solver.py`는 내장된 예제들을 실행하고 각 식의 `SAT` 또는 `UNSAT` 결과를 출력합니다.

직접 논리식을 풀려면 lexer, parser, solver를 함께 사용할 수 있습니다.

```python
from lexer import tokenize
from parser import Parser
from solver import solve

source = "(P or Q) and not P"
expression = Parser(tokenize(source)).parse_formula()
result = solve(expression)

if result is None:
    print("UNSAT")
else:
    print("SAT:", result)
```

출력 예시는 다음과 같습니다. 변수 순서는 실행 환경에 따라 달라질 수 있습니다.

```text
SAT: {'P': False, 'Q': True}
```

## 지원 문법

연산자는 소문자 `and`, `or`, `not`을 사용합니다.

```text
formula ::= clause ("and" clause)*
clause  ::= literal | "(" clause ("or" clause)* ")"
literal ::= NAME | "not" literal | "true" | "false"
```

예시:

```text
P
not P
(P or Q) and not P
A and (not A or B) and (not B or C)
(P or Q) and (not P or Q) and not Q
```

변수 이름은 영문자로 시작하며, 이후 영문자·숫자·밑줄을 사용할 수 있습니다. `and`, `or`, `not`, `true`, `false`는 예약어입니다.

## 동작 방식

1. `lexer.py`가 입력 문자열을 토큰으로 나눕니다.
2. `parser.py`가 토큰을 `expr.py`의 AST로 변환합니다.
3. `interp.py`가 주어진 변수 할당에서 식을 평가합니다.
4. `solver.py`가 모든 변수 할당을 확인하고, 만족하는 할당을 찾으면 반환합니다.

현재 solver는 완전탐색 방식이므로 변수가 `n`개일 때 최대 `2ⁿ`개의 할당을 검사합니다. 학습용 구현에 적합하며, 큰 SAT 문제에는 적합하지 않습니다.

## 파일 구성

| 파일 | 역할 |
| --- | --- |
| `expr.py` | 논리식 AST 정의 |
| `lexer.py` | 문자열 토큰화 |
| `parser.py` | 토큰을 AST로 변환 |
| `interp.py` | 논리식 평가 및 변수 수집 |
| `solver.py` | 완전탐색 SAT solver |
| `my-solver.py` | 실행 예제와 테스트 케이스 |
| `Note.md` | 구현 과정과 학습 노트 |

## 향후 개선 아이디어

- 명령행에서 논리식 입력받기
- 잘못된 문법에 대한 오류 검사 강화
- 단위 테스트 추가
- DPLL 알고리즘과 단위 전파 적용
