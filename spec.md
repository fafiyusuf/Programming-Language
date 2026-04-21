# FidelScript (አማርኛ ቀላል ቋንቋ) — Language Specification

## 1) Overview
FidelScript is a small beginner-friendly programming language that uses Amharic keywords.
It targets Python 3 through a source-to-source translator. The language is intentionally
minimal and focuses on clarity rather than complexity. Programs are written in plain text
files with the extension `.yl` ("Ye Local"), then translated into readable Python.

## 2) Design Goals
- Use Amharic keywords to reduce the initial language barrier.
- Keep syntax consistent and simple.
- Support essential programming constructs only.
- Provide error messages in Amharic to help beginners.

## 3) Keywords and Meanings
| Keyword | Meaning |
|---|---|
| ስም | variable declaration (let) |
| እንደሆነ | if |
| ካልሆነ | else |
| እስከ | while |
| ስራ | function definition |
| መመለስ | return |
| ጻፍ | print |
| ከዚያ | block start |
| በቃ | block end |

## 4) Lexical Rules
- **Unicode**: Identifiers can use any Unicode letters (including Amharic), digits, and `_`.
- **Numbers**: Integers or decimals (e.g., `10`, `3.14`).
- **Strings**: Single or double quotes (e.g., `'ሰላም'`, `"hello"`).
- **Comments**: Start with `#` and run to end of line.
- **Whitespace**: Newlines separate statements. Indentation is ignored.

## 5) Syntax (EBNF-like)
```
program        := { statement NEWLINE }
statement      := var_decl
               | assignment
               | if_stmt
               | while_stmt
               | func_def
               | return_stmt
               | print_stmt
               | expr_stmt

var_decl       := 'ስም' IDENT '=' expression
assignment     := IDENT '=' expression

if_stmt        := 'እንደሆነ' expression 'ከዚያ' NEWLINE
                   block
                 [ 'ካልሆነ' 'ከዚያ' NEWLINE block ]
                 'በቃ'

while_stmt     := 'እስከ' expression 'ከዚያ' NEWLINE
                   block
                 'በቃ'

func_def       := 'ስራ' IDENT '(' [ params ] ')' 'ከዚያ' NEWLINE
                   block
                 'በቃ'

return_stmt    := 'መመለስ' expression
print_stmt     := 'ጻፍ' '(' [ arguments ] ')'
expr_stmt      := expression

block          := { statement NEWLINE }
params         := IDENT { ',' IDENT }
arguments      := expression { ',' expression }

expression     := comparison
comparison     := term { ('==' | '<' | '>') term }
term           := factor { ('+' | '-') factor }
factor         := unary { ('*' | '/') unary }
unary          := [ '-' ] primary
primary        := NUMBER | STRING | IDENT | call | '(' expression ')'
call           := IDENT '(' [ arguments ] ')'
```

## 6) Semantics
- Variables are dynamically typed and can hold numbers or strings.
- `if` executes the first block when the condition is true; otherwise it executes `else`.
- `while` repeats the block while the condition remains true.
- Functions return a value with `መመለስ`.
- `ጻፍ(...)` prints values.

## 7) Beginner-Friendly Features
- **Natural-language keywords** (Amharic) replace English terms.
- **Explicit block markers** (`ከዚያ` / `በቃ`) avoid indentation errors.
- **Error messages in Amharic** help users understand mistakes quickly.

## 8) Example Programs
### Example A: Variables and Math
```
ስም a = 8
ስም b = 4
ስም c = a * b + 2
ጻፍ(c)
```

### Example B: Control Flow
```
ስም x = 0
እስከ x < 3 ከዚያ
    ጻፍ(x)
    x = x + 1
በቃ
እንደሆነ x == 3 ከዚያ
    ጻፍ("ተጠናቀቀ")
ካልሆነ ከዚያ
    ጻፍ("አልተጠናቀቀም")
በቃ
```

### Example C: Functions
```
ስራ ድምር(a, b) ከዚያ
    መመለስ a + b
በቃ
ስም ውጤት = ድምር(3, 5)
ጻፍ(ውጤት)
```

## 9) Translation Target
- **Target language**: Python 3
- Output is formatted with standard Python indentation and is executable as-is.
