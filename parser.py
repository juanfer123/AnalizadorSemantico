# parser.py  (grammar.py renombrado)
import logging
import sly
from rich import print

from lexer   import Lexer
from errors  import error, errors_detected
from model   import (
    Program, DeclTyped, DeclInit, Param,
    SimpleType, ArrayType, ArraySizedType, FuncType,
    Block, ExprStmt, Print, Return, If, For,
    Name, Literal, Index, Call, Assign, BinOp, UnaryOp, PostfixOp,
)


class Parser(sly.Parser):
    log = logging.getLogger()
    log.setLevel(logging.ERROR)
    expected_shift_reduce = 1
    debugfile = 'grammar.txt'

    tokens = Lexer.tokens

    # =================================================
    # PROGRAMA
    # =================================================

    @_("decl_list")
    def prog(self, p):
        return Program(decls=p.decl_list)

    # =================================================
    # LISTAS DE DECLARACIONES
    # =================================================

    @_("decl decl_list")
    def decl_list(self, p):
        return [p.decl] + p.decl_list

    @_("empty")
    def decl_list(self, p):
        return []

    # =================================================
    # DECLARACIONES
    # =================================================

    @_("ID ':' type_simple ';'")
    def decl(self, p):
        return DeclTyped(name=p.ID, typ=p.type_simple)

    @_("ID ':' type_array_sized ';'")
    def decl(self, p):
        return DeclTyped(name=p.ID, typ=p.type_array_sized)

    @_("ID ':' type_func ';'")
    def decl(self, p):
        return DeclTyped(name=p.ID, typ=p.type_func)

    @_("decl_init")
    def decl(self, p):
        return p.decl_init

    # === DECLARACIONES con inicialización

    @_("ID ':' type_simple '=' expr ';'")
    def decl_init(self, p):
        return DeclInit(name=p.ID, typ=p.type_simple, init=p.expr)

    @_("ID ':' CONSTANT '=' expr ';'")
    def decl_init(self, p):
        return DeclInit(name=p.ID, typ=SimpleType('constant'), init=p.expr)

    @_("ID ':' type_array_sized '=' '{' opt_expr_list '}' ';'")
    def decl_init(self, p):
        return DeclInit(name=p.ID, typ=p.type_array_sized, init=p.opt_expr_list)

    @_("ID ':' type_func '=' '{' opt_stmt_list '}'")
    def decl_init(self, p):
        return DeclInit(name=p.ID, typ=p.type_func, init=Block(stmts=p.opt_stmt_list))

    # =================================================
    # STATEMENTS
    # =================================================

    @_("stmt_list")
    def opt_stmt_list(self, p):
        return p.stmt_list

    @_("empty")
    def opt_stmt_list(self, p):
        return []

    @_("stmt stmt_list")
    def stmt_list(self, p):
        return [p.stmt] + p.stmt_list

    @_("stmt")
    def stmt_list(self, p):
        return [p.stmt]

    @_("open_stmt")
    def stmt(self, p):
        return p.open_stmt

    @_("closed_stmt")
    def stmt(self, p):
        return p.closed_stmt

    @_("if_stmt_closed")
    def closed_stmt(self, p):
        return p.if_stmt_closed

    @_("for_stmt_closed")
    def closed_stmt(self, p):
        return p.for_stmt_closed

    @_("while_stmt_closed")
    def closed_stmt(self, p):
        return p.while_stmt_closed

    @_("simple_stmt")
    def closed_stmt(self, p):
        return p.simple_stmt

    @_("if_stmt_open")
    def open_stmt(self, p):
        return p.if_stmt_open

    @_("for_stmt_open")
    def open_stmt(self, p):
        return p.for_stmt_open

    @_("while_stmt_open")
    def open_stmt(self, p):
        return p.while_stmt_open

    # -------------------------------------------------
    # IF
    # -------------------------------------------------

    @_("IF '(' opt_expr ')'")
    def if_cond(self, p):
        return p.opt_expr

    @_("if_cond closed_stmt ELSE closed_stmt")
    def if_stmt_closed(self, p):
        return If(cond=p.if_cond, then=p.closed_stmt0, otherwise=p.closed_stmt1)

    @_("if_cond stmt")
    def if_stmt_open(self, p):
        return If(cond=p.if_cond, then=p.stmt)

    @_("if_cond closed_stmt ELSE if_stmt_open")
    def if_stmt_open(self, p):
        return If(cond=p.if_cond, then=p.closed_stmt, otherwise=p.if_stmt_open)

    # -------------------------------------------------
    # FOR
    # -------------------------------------------------

    @_("FOR '(' opt_expr ';' opt_expr ';' opt_expr ')'")
    def for_header(self, p):
        return (p.opt_expr0, p.opt_expr1, p.opt_expr2)

    @_("for_header open_stmt")
    def for_stmt_open(self, p):
        init, cond, step = p.for_header
        return For(init=init, cond=cond, step=step, body=p.open_stmt)

    @_("for_header closed_stmt")
    def for_stmt_closed(self, p):
        init, cond, step = p.for_header
        return For(init=init, cond=cond, step=step, body=p.closed_stmt)

    # -------------------------------------------------
    # WHILE
    # -------------------------------------------------

    @_("WHILE '(' opt_expr ')'")
    def while_cond(self, p):
        return p.opt_expr

    @_("while_cond open_stmt")
    def while_stmt_open(self, p):
        # Reutilizamos For con init/step=None para While
        return For(init=None, cond=p.while_cond, step=None, body=p.open_stmt)

    @_("while_cond closed_stmt")
    def while_stmt_closed(self, p):
        return For(init=None, cond=p.while_cond, step=None, body=p.closed_stmt)

    # -------------------------------------------------
    # SIMPLE STATEMENTS
    # -------------------------------------------------

    @_("print_stmt")
    def simple_stmt(self, p):
        return p.print_stmt

    @_("return_stmt")
    def simple_stmt(self, p):
        return p.return_stmt

    @_("break_stmt")
    def simple_stmt(self, p):
        return p.break_stmt

    @_("continue_stmt")
    def simple_stmt(self, p):
        return p.continue_stmt

    @_("block_stmt")
    def simple_stmt(self, p):
        return p.block_stmt

    @_("decl")
    def simple_stmt(self, p):
        return p.decl

    @_("expr ';'")
    def simple_stmt(self, p):
        return ExprStmt(expr=p.expr)

    # PRINT
    @_("PRINT opt_expr_list ';'")
    def print_stmt(self, p):
        return Print(values=p.opt_expr_list)

    # RETURN
    @_("RETURN opt_expr ';'")
    def return_stmt(self, p):
        return Return(value=p.opt_expr)

    @_("BREAK ';'")
    def break_stmt(self, p):
        return ExprStmt(expr=Name('__break__'))

    @_("CONTINUE ';'")
    def continue_stmt(self, p):
        return ExprStmt(expr=Name('__continue__'))

    # BLOCK  — opt_stmt_list permite bloques vacíos {}
    @_("'{' opt_stmt_list '}'")
    def block_stmt(self, p):
        return Block(stmts=p.opt_stmt_list)

    # =================================================
    # EXPRESIONES
    # =================================================

    @_("empty")
    def opt_expr_list(self, p):
        return []

    @_("expr_list")
    def opt_expr_list(self, p):
        return p.expr_list

    @_("expr ',' expr_list")
    def expr_list(self, p):
        return [p.expr] + p.expr_list

    @_("expr")
    def expr_list(self, p):
        return [p.expr]

    @_("empty")
    def opt_expr(self, p):
        return None

    @_("expr")
    def opt_expr(self, p):
        return p.expr

    # -------------------------------------------------
    # ASIGNACIÓN  (expr2 como lval — evita conflicto)
    # -------------------------------------------------

    @_("expr1")
    def expr(self, p):
        return p.expr1

    @_("expr2 '=' expr1")
    def expr1(self, p):
        return Assign(target=p.expr2, value=p.expr1)

    @_("expr2 ADDEQ expr1")
    def expr1(self, p):
        return Assign(target=p.expr2,
                      value=BinOp(op='+', left=p.expr2, right=p.expr1))

    @_("expr2 SUBEQ expr1")
    def expr1(self, p):
        return Assign(target=p.expr2,
                      value=BinOp(op='-', left=p.expr2, right=p.expr1))

    @_("expr2 MULEQ expr1")
    def expr1(self, p):
        return Assign(target=p.expr2,
                      value=BinOp(op='*', left=p.expr2, right=p.expr1))

    @_("expr2 DIVEQ expr1")
    def expr1(self, p):
        return Assign(target=p.expr2,
                      value=BinOp(op='/', left=p.expr2, right=p.expr1))

    @_("expr2 MODEQ expr1")
    def expr1(self, p):
        return Assign(target=p.expr2,
                      value=BinOp(op='%', left=p.expr2, right=p.expr1))

    @_("expr2")
    def expr1(self, p):
        return p.expr2

    # -------------------------------------------------
    # OPERADORES BINARIOS
    # -------------------------------------------------

    @_("expr2 LOR expr3")
    def expr2(self, p):
        return BinOp(op='||', left=p.expr2, right=p.expr3)

    @_("expr3")
    def expr2(self, p):
        return p.expr3

    @_("expr3 LAND expr4")
    def expr3(self, p):
        return BinOp(op='&&', left=p.expr3, right=p.expr4)

    @_("expr4")
    def expr3(self, p):
        return p.expr4

    @_("expr4 EQ expr5")
    def expr4(self, p):
        return BinOp(op='==', left=p.expr4, right=p.expr5)

    @_("expr4 NE expr5")
    def expr4(self, p):
        return BinOp(op='!=', left=p.expr4, right=p.expr5)

    @_("expr4 LT expr5")
    def expr4(self, p):
        return BinOp(op='<',  left=p.expr4, right=p.expr5)

    @_("expr4 LE expr5")
    def expr4(self, p):
        return BinOp(op='<=', left=p.expr4, right=p.expr5)

    @_("expr4 GT expr5")
    def expr4(self, p):
        return BinOp(op='>',  left=p.expr4, right=p.expr5)

    @_("expr4 GE expr5")
    def expr4(self, p):
        return BinOp(op='>=', left=p.expr4, right=p.expr5)

    @_("expr5")
    def expr4(self, p):
        return p.expr5

    @_("expr5 '+' expr6")
    def expr5(self, p):
        return BinOp(op='+', left=p.expr5, right=p.expr6)

    @_("expr5 '-' expr6")
    def expr5(self, p):
        return BinOp(op='-', left=p.expr5, right=p.expr6)

    @_("expr6")
    def expr5(self, p):
        return p.expr6

    @_("expr6 '*' expr7")
    def expr6(self, p):
        return BinOp(op='*', left=p.expr6, right=p.expr7)

    @_("expr6 '/' expr7")
    def expr6(self, p):
        return BinOp(op='/', left=p.expr6, right=p.expr7)

    @_("expr6 '%' expr7")
    def expr6(self, p):
        return BinOp(op='%', left=p.expr6, right=p.expr7)

    @_("expr7")
    def expr6(self, p):
        return p.expr7

    @_("expr7 '^' expr8")
    def expr7(self, p):
        return BinOp(op='^', left=p.expr7, right=p.expr8)

    @_("expr8")
    def expr7(self, p):
        return p.expr8

    @_("'-' expr8")
    def expr8(self, p):
        return UnaryOp(op='-', expr=p.expr8)

    @_("'!' expr8")
    def expr8(self, p):
        return UnaryOp(op='!', expr=p.expr8)

    @_("expr9")
    def expr8(self, p):
        return p.expr9

    @_("postfix")
    def expr9(self, p):
        return p.postfix

    @_("primary")
    def postfix(self, p):
        return p.primary

    @_("postfix INC")
    def postfix(self, p):
        return PostfixOp(op='++', expr=p.postfix)

    @_("postfix DEC")
    def postfix(self, p):
        return PostfixOp(op='--', expr=p.postfix)

    @_("prefix")
    def primary(self, p):
        return p.prefix

    @_("INC prefix")
    def prefix(self, p):
        return UnaryOp(op='++', expr=p.prefix)

    @_("DEC prefix")
    def prefix(self, p):
        return UnaryOp(op='--', expr=p.prefix)

    @_("group")
    def prefix(self, p):
        return p.group

    @_("'(' expr ')'")
    def group(self, p):
        return p.expr

    @_("ID '(' opt_expr_list ')'")
    def group(self, p):
        return Call(func=p.ID, args=p.opt_expr_list)

    @_("ID index")
    def group(self, p):
        return Index(base=Name(id=p.ID), indices=[p.index])

    @_("factor")
    def group(self, p):
        return p.factor

    # ÍNDICE DE ARREGLO
    @_("'[' expr ']'")
    def index(self, p):
        return p.expr

    # -------------------------------------------------
    # FACTORES
    # -------------------------------------------------

    @_("ID")
    def factor(self, p):
        return Name(id=p.ID)

    @_("INTEGER_LITERAL")
    def factor(self, p):
        return Literal(kind='integer', value=p.INTEGER_LITERAL)

    @_("FLOAT_LITERAL")
    def factor(self, p):
        return Literal(kind='float', value=p.FLOAT_LITERAL)

    @_("CHAR_LITERAL")
    def factor(self, p):
        return Literal(kind='char', value=p.CHAR_LITERAL)

    @_("STRING_LITERAL")
    def factor(self, p):
        return Literal(kind='string', value=p.STRING_LITERAL)

    @_("TRUE")
    def factor(self, p):
        return Literal(kind='boolean', value=True)

    @_("FALSE")
    def factor(self, p):
        return Literal(kind='boolean', value=False)

    # =================================================
    # TIPOS
    # =================================================

    @_("INTEGER")
    def type_simple(self, p):
        return SimpleType('integer')

    @_("FLOAT")
    def type_simple(self, p):
        return SimpleType('float')

    @_("BOOLEAN")
    def type_simple(self, p):
        return SimpleType('boolean')

    @_("CHAR")
    def type_simple(self, p):
        return SimpleType('char')

    @_("STRING")
    def type_simple(self, p):
        return SimpleType('string')

    @_("VOID")
    def type_simple(self, p):
        return SimpleType('void')

    @_("ARRAY '[' ']' type_simple")
    def type_array(self, p):
        return ArrayType(elem=p.type_simple)

    @_("ARRAY '[' ']' type_array")
    def type_array(self, p):
        return ArrayType(elem=p.type_array)

    @_("ARRAY index type_simple")
    def type_array_sized(self, p):
        return ArraySizedType(size_expr=p.index, elem=p.type_simple)

    @_("ARRAY index type_array_sized")
    def type_array_sized(self, p):
        return ArraySizedType(size_expr=p.index, elem=p.type_array_sized)

    @_("FUNCTION type_simple '(' opt_param_list ')'")
    def type_func(self, p):
        return FuncType(ret=p.type_simple, params=p.opt_param_list)

    @_("FUNCTION type_array_sized '(' opt_param_list ')'")
    def type_func(self, p):
        return FuncType(ret=p.type_array_sized, params=p.opt_param_list)

    @_("empty")
    def opt_param_list(self, p):
        return []

    @_("param_list")
    def opt_param_list(self, p):
        return p.param_list

    @_("param_list ',' param")
    def param_list(self, p):
        return p.param_list + [p.param]

    @_("param")
    def param_list(self, p):
        return [p.param]

    @_("ID ':' type_simple")
    def param(self, p):
        return Param(name=p.ID, typ=p.type_simple)

    @_("ID ':' type_array")
    def param(self, p):
        return Param(name=p.ID, typ=p.type_array)

    @_("ID ':' type_array_sized")
    def param(self, p):
        return Param(name=p.ID, typ=p.type_array_sized)

    # =================================================
    # UTILIDAD: EMPTY
    # =================================================

    @_("")
    def empty(self, p):
        return None

    def error(self, p):
        lineno = p.lineno if p else 'EOF'
        value  = repr(p.value) if p else 'EOF'
        error(f'Syntax error at {value}', lineno)