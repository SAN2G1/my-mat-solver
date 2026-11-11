# Python으로 만들어보는 SAT solver 

EOPL 방식을 참고해서 SAT 문제를 푸는 python solver 


구분되어 생각할 것은 인터프리터와 SAT solver의 역할이다. 

**인터프리터** : 주어진 환경에서 식을 평가함
    `value_of(formula, {"P" : False, "Q" : True})`

**SAT solver** : 식을 참으로 만드는 환경을 찾는다. 
    `solve(formula)`

[letlang](https://github.com/kwanghoon/Lecture_EOPL/tree/master/ch3/app/letlang)을 참고하여 Python 코드를 작성한다. 


## 처음 시작 

먼저, 고려해야 할 것들을 생각해보자면

1. AST의 구성 
2. 환경을 평가하는 함수
3. lexer, parser 추가
4. DPLL로 발전시키기

이렇게 생각된다. 

### 1) 논리식의 AST

우리가 표현해야 하는 명제 논리 구문은 다음과 같다. 
$$
\varphi ::= x \mid \varphi \land \varphi
\mid \varphi \lor \varphi \mid \neg\varphi \mid T \mid F
$$

Python에서는 다음 다섯 종류의 AST로 표현할 수 있다. 

| AST | 의미 | 예시 |
|---|---|---|
| `Bool(value)` | 참·거짓 상수 | `Bool(True)` |
| `Var(name)` | 논리 변수 | `Var("P")` |
| `Not(expr)` | 부정 | `Not(Var("P"))` |
| `And(left, right)` | 논리곱 | `And(Var("P"), Var("Q"))` |
| `Or(left, right)` | 논리합 | `Or(Var("P"), Var("Q"))` |

다시 말해, $$(P \lor Q) \land \neg P$$ 이러한 식이 있다고 한다면 AST를 아래와 같이 만들어 볼 수 있다. 

```
formula = And(
    Or(
        Var("P"), 
        Var("Q")
        ), 
    Not(Var("P"))
    )
```

이러한 데이터 AST에 관한 구현은 `expr.py`에 존재한다. 

### 2) 평가 함수 

주어진 AST를 탐색하면서 그 식의 결과를 가져오는 `value_of` 함수를 만들어야 한다. 

python의 match-case를 사용하면 하스켈과 비슷하게 만들어 볼 수 있다. 

```python 
def value_of(expr : Expr, env = {}) -> bool :
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
```


이렇게 만든 함수를 가지고 아래와 같이 테스트를 해볼 수 있다. 

```python
if __name__ == "__main__":
    # (P ∨ Q) ∧ ¬P
    formula = And( Or(Var("P"), Var("Q")), Not(Var("P")) )
    env = {"P": True, "Q": False}

    print(value_of(formula, {"P": False, "Q": True}))   # True
    print(value_of(formula, {"P": True,  "Q": True}))   # False
    print(value_of(formula, {"P": False, "Q": False}))  # False
```

`value_of` 내부에서는 다음 과정이 진행된다. 

1. `formula`가 `And` 객체이므로 `case And(left, right)`에 들어간다. 
2. `left`에는 `Or(Var("P"), Var("Q"))`, `right`에는 `Not(Var("P"))`가 들어간다. 
3. 각각 left, right를 `value_of`를 다시 호출해서 값을 찾아오게 한다. 
4. left, right가 각각 구해지면 본 식도 계산해 최종 True/False를 출력한다. 


### 3) 환경을 만들어 평가하기 

다음으로 AST에 등장하는 변수 이름을 모으는 `variables_of(expr)`를 만든다. 

기대되는 행동은 `{"P", "Q"}`와 같은 변수들의 이름을 모아오는 것이다. 

변수가 `P`, `Q`라면 가능한 환경은 네 개이다. 

| P | Q | `(P ∨ Q) ∧ ¬P` |
|---|---|---|
| False | False | False |
| False | True | True |
| True | False | False |
| True | True | False |

이중 하나라도 식을 참으로 만들면 SAT을 반환하면 되고 전부 확인했는데 없으면 UNSAT을 반환하면 된다. 

그렇기에 어떤 변수들을 가지고 있는지 모아야 한다. 

```python
def variables_of(expr : Expr) -> set[str]:
    match expr: 
        case Bool(_) : return set()
        case Var(name) : return {name}
        case Not(expr) : return variables_of(expr)
        case And(left, right) : return variables_of(left) | variables_of(right) # 여기서 원소들이 합집합으로 합쳐짐
        case Or(left, right) : return variables_of(left) | variables_of(right)
        case _ : raise ValueError(f"Unknown expression: {expr}")
```

### 4) 만족하는 환경 탐색

이제 환경에 무엇이 있는지 탐색할 수 있으니. 
문제를 풀 수 있는 변수 값이 무엇이 있을지 탐색을 해야 한다. 

일단 처음에는 모든 경우의 수를 대입하여 풀어보는 brute-force하게 접근하는 solver를 생각해 볼 수 있다. 

알고리즘을 생각해 본다면
1. 위에서 제작한 `varialbes_of`를 이용하여 변수들을 구한다. 
2. 변수들에게 모든 경우의 수의 T/F를 대입한다. 
3. 대입한 환경을 가지고 `value_of` 함수로 평가한다. 
4. 반환된 값이 True면 SAT이고 그 외는 UNSAT으로 리턴한다. 

위 과정을 python코드로 옮기는 것은 쉬운 일이지만, 변수들을 어떻게 알고리즘으로 초기화를 할 것인가는 조금 생각해 볼만한 거리이다. 

내가 생각한 방법은 가능한 경우의 수가 2^n이므로 이만큼의 반복문을 돌아야 한다. 이때 이 횟수를 이진수로 변환 시켜 각 자리 숫자의 0과 1을 변수들에 대입한다면 모든 경우의 수를 빠짐 없이 대입할 수 있다는 것이다. 
"""
i가 0이면 0000 -> P=False, Q=False, R=False, S=False
i가 1이면 0001 -> P=False, Q=False, R=False, S=True
....
"""

```python 
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
```
여기서 주의 할 것은 `env[var] = bool((i >> (n-j-1) ) & 1)` 이 부분이다. 쉬프트 연산을 할때 1을 빼주는 것은 range가 0~3까지의 범위를 표현하고 있기 때문이다. `(j+1)`을 해주어야 4번째 자릿 숫자를 가져올 수 있다. 

### 5) Lexer와 Parser

먼저, 어떤 입력을 받게 하고 싶을지 그 언어를 어떻게 하고 싶을지 생각을 해보았다. 

일단 기본 전제는 입력은 CNF 논리식 형태를 띄어야 한다는 것이다. 

`A and (not P or R ) and (P or not R)` 
이게 내가 기술하고 싶은 언어라고 하자. 

이 언어의 패턴을 정의 하여 기술 하는데 정규식을 사용하여 기술하고자 한다. 

위 언어를 토큰으로 나눠 Lexer가 문자열을 읽으며 각 토큰이 변수인지 연산자인지 괄호인지 구분하게 하고 싶다. 

먼저 토큰의 종류를 생각해보자. 위 언어에서 생각해 볼 수 있는 토큰들의 종류는 다음과 같다. 

`NAME`, `AND`, `OR`, `NOT`, `LPAREN`, `RPAREN`, `공백`  

이때 변수 이름을 읽는 정규식을 생각해보자. `[A-Za-z][A-Za-z0-9_]*` 이렇게 될 것이다. 
    이 정규식의 뜻은 첫 글자는 영문자이고 그 뒤에는 다시 영문자가 오거나 숫자가 오거나 `_`기호가 올 수 있다는 뜻이다. 
이 패턴으로 읽으면 `Q`, `R`, `value1`이와 같은 변수들을 읽을 수 있다.
그러나 다만 내가 원하는 `and`, `or`, `not`도 위 패턴에 속하게 된다. 

그래서 단어 전체를 읽은 뒤 예약어인지 확인하는 작업이 필요하다. 

이제 파서를 위한 문법을 정의 해야 한다. 

다시 위 예제로 이야기를 해보자. 
`A`, `(not P or R)`, `(P or not R)` 이걸 하나의 절로 보았을 때 
이 세가지 절들은 `and` 로만 연결되어야 하고 절 내부에는 `or`로 되어 있어야 한다. 

이를 입력 문법으로 적으면 다음과 같다. 


"""
논리식 ::= 절 ("and" 절)* 

절 ::= 리터럴
    | "(" 절 ("or" 절)* ")"

리터럴 ::= NAME
    | "not" NAME
"""

시작은 논리식이여야 한다. 
그리고 논리식은 하나의 항이 오고 `"and" 절`이 0번 이상 이어질 수 있다. 
절은 리터럴이 될 수 있고 `"(" 절`이 오고 `"or" 절`이 0번 이상 이어질 수 있고 `")"`로 마무리 된다. 
다시 리터럴은 `NAME`이 되거나 `"not" NAME`이 되거나 한다. 


Lexer의 역할은 문자열을 읽고 변수, 연산자, 괄호 등의 토큰으로 나누는 역할을 해야 한다. 
Parser는 토큰의 순서가 CNF 문법에 맞는지 검사하고 AST를 만들면 된다. 

이제 Lexer를 만들어보자. 
구현의 자세한 내용은 `lexer.py`에 있다. 

여기서 살펴볼 주요 내용은 두가지다. 

먼저, 긴 string 문자열에서 토큰으로 잘게 나누는 작업이다.
` match = TOKEN_PATTERN.match(input_string, pos)` 이 내용은 현재 위치 `pos`에서 시작하는 토큰을 찾는 부분이다. 
해당 위치에서 읽을 수 없으면, 우리가 정규 표현식으로 만들어둔 `r"[A-Za-z][A-Za-z0-9_]*|[(),]"`에 해당하지 않아서 일치하지 않은 것이다. 

이렇게 읽으면 "and", "a", "value"와 같은 하나의 토큰으로 반환하게 된다. 

그 다음 해야할 일은 방금 읽은 토큰의 종류를 결정하는 것이다. 
`kind = KEYWORDS.get(text, SYMBOLS.get(text, "NAME"))` 이 내용이 읽은 문자열의 종류를 결정한다. 
이 코드는 파이썬 딕셔너리의 `get()` 메서드를 중첩하여 사용한 코드로 우선 순위에 따라 특정 단어(`text`)가 어떤 종류의 토큰인지 분류하게 된다. 

`dict.get(key, default)`의 구조를 가지고 있는데 `get()`함수는 딕셔너리에 `key`가 존재하면 그 값을 반환한다. 
만약 `key`가 존재하지 않으면 에러를 내는 대신, 뒤에 적어둔 `default`값을 반환한다. 

먼저 `KEYWORDS.get()`을 먼저 시도해서 `KEYWORD`에 작성해 둔 문자열인지 검사를 한다. 
여기에 해당사항이 없으면 `SYMBOLS.get()`을 살펴보고 여기도 없으면 `NAME`으로 배정한다. 

이렇게 탐색한 토큰들은 리스트로 반환된다. 

이 다음으로 해야할 일은 토큰의 순서가 CNF 문법에 맞는지 확인하고 AST를 만드는 작업이다. 

기억해야 할 것은 위에서 작성했던 우리의 문법이다. 

구현 사항은 `parser.py`에 구현되어 있다. 


## 통합하기 

이제 입력을 우리의 문법을 가진 언어로 입력을 주어 풀 수 있게 해보자. 

my-solver.py를 만들고 거기에 입력을 넣으면 lexer와 parser가 ast를 만들고
그 입력이 solver에게 들어가서 solver가 모든 경우의 수에 대해 value_of함수로 값을 구해보고 
구해지는 값의 환경을 반환해 주면 SAT이고 아니면 UNSAT일 것이다. 

