#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from dataclasses import dataclass
from typing import List, Optional

KEYWORDS = {
    "ስም",       # var
    "እንደሆነ",  # if
    "ካልሆነ",   # else
    "እስከ",     # while
    "ስራ",      # def
    "መመለስ",    # return
    "ጻፍ",      # print
    "ከዚያ",     # block start
    "በቃ",      # block end
}

SINGLE_CHAR_OPS = {"+", "-", "*", "/", "<", ">"}
PUNCT = {"(", ")", ",", "="}


@dataclass
class Token:
    type: str
    value: str
    line: int
    col: int


class LexError(Exception):
    pass


class ParseError(Exception):
    pass


class Lexer:
    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.line = 1
        self.col = 1

    def _current(self) -> Optional[str]:
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]

    def _advance(self) -> Optional[str]:
        ch = self._current()
        if ch is None:
            return None
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _peek(self) -> Optional[str]:
        if self.pos + 1 >= len(self.text):
            return None
        return self.text[self.pos + 1]

    def _error(self, message: str) -> None:
        raise LexError(f"ስህተት: {message} (መስመር {self.line}, አምድ {self.col})")

    def _skip_comment(self) -> None:
        while True:
            ch = self._current()
            if ch is None or ch == "\n":
                return
            self._advance()

    def _read_number(self) -> Token:
        start_line, start_col = self.line, self.col
        value = ""
        dot_seen = False
        while True:
            ch = self._current()
            if ch is None:
                break
            if ch.isdigit():
                value += self._advance()
                continue
            if ch == "." and not dot_seen:
                dot_seen = True
                value += self._advance()
                continue
            break
        return Token("NUMBER", value, start_line, start_col)

    def _read_identifier(self) -> Token:
        start_line, start_col = self.line, self.col
        value = ""
        ch = self._current()
        if ch is None:
            self._error("ባዶ መለያ")
        while True:
            ch = self._current()
            if ch is None:
                break
            if ch.isalpha() or ch.isdigit() or ch == "_":
                value += self._advance()
                continue
            break
        if value in KEYWORDS:
            return Token("KEYWORD", value, start_line, start_col)
        return Token("IDENT", value, start_line, start_col)

    def _read_string(self) -> Token:
        start_line, start_col = self.line, self.col
        quote = self._advance()
        value = ""
        while True:
            ch = self._current()
            if ch is None:
                self._error("ያልተዘጋ ጽሑፍ")
            if ch == quote:
                self._advance()
                break
            if ch == "\\":
                self._advance()
                esc = self._current()
                if esc is None:
                    self._error("ያልተሟላ ሸሽተኛ")
                mapping = {"n": "\n", "t": "\t", "\\": "\\", "\"": "\"", "'": "'"}
                value += mapping.get(esc, esc)
                self._advance()
                continue
            value += self._advance()
        return Token("STRING", value, start_line, start_col)

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while True:
            ch = self._current()
            if ch is None:
                break
            if ch in " \t\r":
                self._advance()
                continue
            if ch == "\n":
                tokens.append(Token("NEWLINE", "\n", self.line, self.col))
                self._advance()
                continue
            if ch == "#":
                self._skip_comment()
                continue
            if ch.isdigit():
                tokens.append(self._read_number())
                continue
            if ch == "\"" or ch == "'":
                tokens.append(self._read_string())
                continue
            if ch.isalpha() or ch == "_":
                tokens.append(self._read_identifier())
                continue
            if ch == "=" and self._peek() == "=":
                start_line, start_col = self.line, self.col
                self._advance()
                self._advance()
                tokens.append(Token("OP", "==", start_line, start_col))
                continue
            if ch in SINGLE_CHAR_OPS:
                start_line, start_col = self.line, self.col
                tokens.append(Token("OP", self._advance(), start_line, start_col))
                continue
            if ch in PUNCT:
                start_line, start_col = self.line, self.col
                tokens.append(Token("PUNCT", self._advance(), start_line, start_col))
                continue
            self._error(f"ያልተፈቀደ ምልክት: {ch}")
        tokens.append(Token("EOF", "", self.line, self.col))
        return tokens


@dataclass
class Number:
    value: str


@dataclass
class String:
    value: str


@dataclass
class Var:
    name: str


@dataclass
class BinaryOp:
    left: object
    op: str
    right: object


@dataclass
class UnaryOp:
    op: str
    expr: object


@dataclass
class Call:
    name: str
    args: List[object]


@dataclass
class VarDecl:
    name: str
    expr: object


@dataclass
class Assign:
    name: str
    expr: object


@dataclass
class IfStmt:
    cond: object
    then_body: List[object]
    else_body: Optional[List[object]]


@dataclass
class WhileStmt:
    cond: object
    body: List[object]


@dataclass
class FuncDef:
    name: str
    params: List[str]
    body: List[object]


@dataclass
class ReturnStmt:
    expr: object


@dataclass
class PrintStmt:
    args: List[object]


@dataclass
class ExprStmt:
    expr: object


class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    def _current(self) -> Token:
        return self.tokens[self.pos]

    def _peek(self) -> Token:
        return self.tokens[self.pos + 1]

    def _advance(self) -> Token:
        tok = self._current()
        if tok.type != "EOF":
            self.pos += 1
        return tok

    def _error(self, tok: Token, message: str) -> None:
        raise ParseError(f"ስህተት: {message} (መስመር {tok.line}, አምድ {tok.col})")

    def _match(self, type_: str, value: Optional[str] = None) -> Optional[Token]:
        tok = self._current()
        if tok.type != type_:
            return None
        if value is not None and tok.value != value:
            return None
        self._advance()
        return tok

    def _expect(self, type_: str, value: Optional[str] = None) -> Token:
        tok = self._current()
        if tok.type != type_:
            self._error(tok, f"'{type_}' ይጠበቃል")
        if value is not None and tok.value != value:
            self._error(tok, f"'{value}' ይጠበቃል")
        self._advance()
        return tok

    def _skip_newlines(self) -> None:
        while self._match("NEWLINE"):
            pass

    def parse_program(self) -> List[object]:
        statements: List[object] = []
        while self._current().type != "EOF":
            self._skip_newlines()
            if self._current().type == "EOF":
                break
            statements.append(self._parse_statement())
            self._skip_newlines()
        return statements

    def _parse_statement(self) -> object:
        tok = self._current()
        if tok.type == "KEYWORD" and tok.value == "ስም":
            return self._parse_var_decl()
        if tok.type == "KEYWORD" and tok.value == "እንደሆነ":
            return self._parse_if()
        if tok.type == "KEYWORD" and tok.value == "እስከ":
            return self._parse_while()
        if tok.type == "KEYWORD" and tok.value == "ስራ":
            return self._parse_func_def()
        if tok.type == "KEYWORD" and tok.value == "መመለስ":
            return self._parse_return()
        if tok.type == "KEYWORD" and tok.value == "ጻፍ":
            return self._parse_print()
        if tok.type == "IDENT" and self._peek().type == "PUNCT" and self._peek().value == "=":
            return self._parse_assign()
        expr = self._parse_expression()
        return ExprStmt(expr)

    def _parse_var_decl(self) -> VarDecl:
        self._expect("KEYWORD", "ስም")
        name = self._expect("IDENT").value
        self._expect("PUNCT", "=")
        expr = self._parse_expression()
        return VarDecl(name, expr)

    def _parse_assign(self) -> Assign:
        name = self._expect("IDENT").value
        self._expect("PUNCT", "=")
        expr = self._parse_expression()
        return Assign(name, expr)

    def _parse_if(self) -> IfStmt:
        self._expect("KEYWORD", "እንደሆነ")
        cond = self._parse_expression()
        self._expect("KEYWORD", "ከዚያ")
        self._skip_newlines()
        then_body = self._parse_block(stop_keywords={"ካልሆነ", "በቃ"})
        else_body = None
        if self._current().type == "KEYWORD" and self._current().value == "ካልሆነ":
            self._advance()
            self._expect("KEYWORD", "ከዚያ")
            self._skip_newlines()
            else_body = self._parse_block(stop_keywords={"በቃ"})
        self._expect("KEYWORD", "በቃ")
        return IfStmt(cond, then_body, else_body)

    def _parse_while(self) -> WhileStmt:
        self._expect("KEYWORD", "እስከ")
        cond = self._parse_expression()
        self._expect("KEYWORD", "ከዚያ")
        self._skip_newlines()
        body = self._parse_block(stop_keywords={"በቃ"})
        self._expect("KEYWORD", "በቃ")
        return WhileStmt(cond, body)

    def _parse_func_def(self) -> FuncDef:
        self._expect("KEYWORD", "ስራ")
        name = self._expect("IDENT").value
        self._expect("PUNCT", "(")
        params: List[str] = []
        if not (self._current().type == "PUNCT" and self._current().value == ")"):
            params.append(self._expect("IDENT").value)
            while self._match("PUNCT", ","):
                params.append(self._expect("IDENT").value)
        self._expect("PUNCT", ")")
        self._expect("KEYWORD", "ከዚያ")
        self._skip_newlines()
        body = self._parse_block(stop_keywords={"በቃ"})
        self._expect("KEYWORD", "በቃ")
        return FuncDef(name, params, body)

    def _parse_return(self) -> ReturnStmt:
        self._expect("KEYWORD", "መመለስ")
        expr = self._parse_expression()
        return ReturnStmt(expr)

    def _parse_print(self) -> PrintStmt:
        self._expect("KEYWORD", "ጻፍ")
        self._expect("PUNCT", "(")
        args: List[object] = []
        if not (self._current().type == "PUNCT" and self._current().value == ")"):
            args.append(self._parse_expression())
            while self._match("PUNCT", ","):
                args.append(self._parse_expression())
        self._expect("PUNCT", ")")
        return PrintStmt(args)

    def _parse_block(self, stop_keywords: set) -> List[object]:
        statements: List[object] = []
        while True:
            tok = self._current()
            if tok.type == "EOF":
                self._error(tok, "ያልተዘጋ ብሎክ")
            if tok.type == "KEYWORD" and tok.value in stop_keywords:
                break
            statements.append(self._parse_statement())
            self._skip_newlines()
        return statements

    def _parse_expression(self) -> object:
        return self._parse_comparison()

    def _parse_comparison(self) -> object:
        left = self._parse_term()
        while self._current().type == "OP" and self._current().value in {"==", "<", ">"}:
            op = self._advance().value
            right = self._parse_term()
            left = BinaryOp(left, op, right)
        return left

    def _parse_term(self) -> object:
        left = self._parse_factor()
        while self._current().type == "OP" and self._current().value in {"+", "-"}:
            op = self._advance().value
            right = self._parse_factor()
            left = BinaryOp(left, op, right)
        return left

    def _parse_factor(self) -> object:
        left = self._parse_unary()
        while self._current().type == "OP" and self._current().value in {"*", "/"}:
            op = self._advance().value
            right = self._parse_unary()
            left = BinaryOp(left, op, right)
        return left

    def _parse_unary(self) -> object:
        if self._current().type == "OP" and self._current().value == "-":
            op = self._advance().value
            expr = self._parse_unary()
            return UnaryOp(op, expr)
        return self._parse_primary()

    def _parse_primary(self) -> object:
        tok = self._current()
        if tok.type == "NUMBER":
            self._advance()
            return Number(tok.value)
        if tok.type == "STRING":
            self._advance()
            return String(tok.value)
        if tok.type == "IDENT":
            name = self._advance().value
            if self._current().type == "PUNCT" and self._current().value == "(":
                self._advance()
                args: List[object] = []
                if not (self._current().type == "PUNCT" and self._current().value == ")"):
                    args.append(self._parse_expression())
                    while self._match("PUNCT", ","):
                        args.append(self._parse_expression())
                self._expect("PUNCT", ")")
                return Call(name, args)
            return Var(name)
        if tok.type == "PUNCT" and tok.value == "(":
            self._advance()
            expr = self._parse_expression()
            self._expect("PUNCT", ")")
            return expr
        self._error(tok, "ያልተጠበቀ አገላለጽ")


class PythonTranslator:
    def __init__(self) -> None:
        self.lines: List[str] = []
        self.indent = 0

    def translate(self, statements: List[object]) -> str:
        self.lines = ["# -*- coding: utf-8 -*-"]
        for stmt in statements:
            self._emit_stmt(stmt)
        return "\n".join(self.lines) + "\n"

    def _emit(self, line: str) -> None:
        self.lines.append("    " * self.indent + line)

    def _emit_stmt(self, stmt: object) -> None:
        if isinstance(stmt, VarDecl):
            self._emit(f"{stmt.name} = {self._emit_expr(stmt.expr)}")
            return
        if isinstance(stmt, Assign):
            self._emit(f"{stmt.name} = {self._emit_expr(stmt.expr)}")
            return
        if isinstance(stmt, IfStmt):
            self._emit(f"if {self._emit_expr(stmt.cond)}:")
            self.indent += 1
            self._emit_block(stmt.then_body)
            self.indent -= 1
            if stmt.else_body is not None:
                self._emit("else:")
                self.indent += 1
                self._emit_block(stmt.else_body)
                self.indent -= 1
            return
        if isinstance(stmt, WhileStmt):
            self._emit(f"while {self._emit_expr(stmt.cond)}:")
            self.indent += 1
            self._emit_block(stmt.body)
            self.indent -= 1
            return
        if isinstance(stmt, FuncDef):
            params = ", ".join(stmt.params)
            self._emit(f"def {stmt.name}({params}):")
            self.indent += 1
            self._emit_block(stmt.body)
            self.indent -= 1
            return
        if isinstance(stmt, ReturnStmt):
            self._emit(f"return {self._emit_expr(stmt.expr)}")
            return
        if isinstance(stmt, PrintStmt):
            args = ", ".join(self._emit_expr(arg) for arg in stmt.args)
            self._emit(f"print({args})")
            return
        if isinstance(stmt, ExprStmt):
            self._emit(self._emit_expr(stmt.expr))
            return
        raise ParseError("ስህተት: ያልታወቀ ንግግር")

    def _emit_block(self, statements: List[object]) -> None:
        if not statements:
            self._emit("pass")
            return
        for stmt in statements:
            self._emit_stmt(stmt)

    def _emit_expr(self, expr: object) -> str:
        if isinstance(expr, Number):
            return expr.value
        if isinstance(expr, String):
            return repr(expr.value)
        if isinstance(expr, Var):
            return expr.name
        if isinstance(expr, BinaryOp):
            return f"{self._emit_expr(expr.left)} {expr.op} {self._emit_expr(expr.right)}"
        if isinstance(expr, UnaryOp):
            return f"{expr.op}{self._emit_expr(expr.expr)}"
        if isinstance(expr, Call):
            args = ", ".join(self._emit_expr(arg) for arg in expr.args)
            return f"{expr.name}({args})"
        raise ParseError("ስህተት: ያልታወቀ አገላለጽ")


def translate_source(source: str) -> str:
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    program = parser.parse_program()
    translator = PythonTranslator()
    return translator.translate(program)


def main() -> int:
    if len(sys.argv) != 2:
        print("አጠቃቀም: python translator.py program.yl", file=sys.stderr)
        return 1
    source_path = sys.argv[1]
    try:
        with open(source_path, "r", encoding="utf-8") as handle:
            source = handle.read()
        output = translate_source(source)
    except (OSError, LexError, ParseError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if source_path.endswith("."):
        target_path = source_path + "py"
    else:
        base = source_path.rsplit(".", 1)[0]
        target_path = base + ".py"
    with open(target_path, "w", encoding="utf-8") as handle:
        handle.write(output)
    print(f"ተተርጎመ፣ {target_path} ተፈጠረ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
