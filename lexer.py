import re
from dataclasses import dataclass


@dataclass 
class Token: 
    kind: str
    text: str
    pos: int


KEYWORDS = {
    "true": "TRUE", 
    "false": "FALSE",
    "not": "NOT",
    "and": "AND",
    "or": "OR",
}

SYMBOLS = {
    "(": "LPAREN",
    ")": "RPAREN",
    ",": "COMMA",
}

TOKEN_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_]*|[(),]")

def tokenize(input_string: str) -> list[Token]: 
    tokens = []
    pos = 0 
    while pos < len(input_string):

        # Skip whitespace
        if input_string[pos].isspace():
            pos += 1
            continue

        # 현재 위치 pos에서 시작하는 토큰을 찾는다. 
        match = TOKEN_PATTERN.match(input_string, pos)

        if match is None: 
            raise ValueError(f"Unexpected character at position {pos+1}: {input_string[pos]}")

        text = match.group() #정규식 전체에 매칭된 텍스트를 가져옴

        # 읽은 문자열의 종류를 결정한다. 
        # "and" -> "AND", "or" -> "OR", "(" -> "LPAREN", ...
        # 예약어나 기호가 아니면 일반 이름("NAME")으로 처리한다.
        kind = KEYWORDS.get(text, SYMBOLS.get(text, "NAME") ) 

        tokens.append(Token(kind, text, pos))
        pos = match.end() # 다음 토큰을 찾기 위해 pos를 이동시킨다.

    tokens.append(Token("EOF", "", pos)) # 입력의 끝을 나타내는 토큰을 추가한다.
    return tokens