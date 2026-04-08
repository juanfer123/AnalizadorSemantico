# visualizer.py
from rich.tree import Tree
from rich      import print

from model import (
    Program, DeclTyped, DeclInit, Param,
    SimpleType, ArrayType, ArraySizedType, FuncType,
    Block, ExprStmt, Print, Return, If, For,
    Name, Literal, Index, Call, Assign, BinOp, UnaryOp, PostfixOp,
)


# =============================================================
# Entrada principal
# =============================================================

def print_rich_tree(ast):
    tree = Tree("Program")
    decls_branch = tree.add("declarations")
    for decl in ast.decls:
        _decl(decls_branch, decl)
    print(tree)


def _decl(parent, node):
    if isinstance(node, DeclInit) and isinstance(node.typ, FuncType):
        _func_decl(parent, node)
    elif isinstance(node, DeclInit):
        _var_decl_init(parent, node)
    elif isinstance(node, DeclTyped):
        _var_decl(parent, node)
    else:
        parent.add(f"[dim]{repr(node)}[/dim]")


def _func_decl(parent, node: DeclInit):
    b = parent.add("FunctionDecl")
    b.add(f"return_type: [cyan]'{node.typ.ret.name}'[/cyan]")
    b.add(f"name: [green]'{node.name}'[/green]")

    if node.typ.params:
        pb = b.add("params")
        for param in node.typ.params:
            _param(pb, param)

    body_b = b.add("body")
    _stmt(body_b, node.init)


def _var_decl(parent, node: DeclTyped):
    b = parent.add("VarDecl")
    b.add(f"type_name: [cyan]'{_type_str(node.typ)}'[/cyan]")
    b.add(f"name: [green]'{node.name}'[/green]")


def _var_decl_init(parent, node: DeclInit):
    b = parent.add("VarDecl")
    b.add(f"type_name: [cyan]'{_type_str(node.typ)}'[/cyan]")
    b.add(f"name: [green]'{node.name}'[/green]")
    init_b = b.add("initializer")
    if isinstance(node.init, list):
        for item in node.init:
            _expr(init_b, item)
    else:
        _expr(init_b, node.init)


def _param(parent, node: Param):
    b = parent.add("Param")
    b.add(f"type_name: [cyan]'{_type_str(node.typ)}'[/cyan]")
    b.add(f"name: [green]'{node.name}'[/green]")


# =============================================================
# STATEMENTS
# =============================================================

def _stmt(parent, node):
    if isinstance(node, Block):
        b = parent.add("Block")
        sb = b.add("statements")
        for s in node.stmts:
            _stmt(sb, s)

    elif isinstance(node, If):
        b = parent.add("IfStmt")
        cb = b.add("condition")
        _expr(cb, node.cond)
        tb = b.add("then_branch")
        _stmt(tb, node.then)
        if node.otherwise is not None:
            eb = b.add("else_branch")
            _stmt(eb, node.otherwise)

    elif isinstance(node, For):
        # While: init y step son None
        if node.init is None and node.step is None:
            b = parent.add("WhileStmt")
            cb = b.add("condition")
            _expr(cb, node.cond)
            bb = b.add("body")
            _stmt(bb, node.body)
        else:
            b = parent.add("ForStmt")
            if node.init is not None:
                ib = b.add("init")
                _expr(ib, node.init)
            if node.cond is not None:
                cb = b.add("condition")
                _expr(cb, node.cond)
            if node.step is not None:
                sb = b.add("step")
                _expr(sb, node.step)
            bb = b.add("body")
            _stmt(bb, node.body)

    elif isinstance(node, Return):
        b = parent.add("ReturnStmt")
        if node.value is not None:
            vb = b.add("value")
            _expr(vb, node.value)

    elif isinstance(node, Print):
        b = parent.add("PrintStmt")
        for v in node.values:
            vb = b.add("value")
            _expr(vb, v)

    elif isinstance(node, ExprStmt):
        # break / continue especiales
        if isinstance(node.expr, Name) and node.expr.id in ('__break__', '__continue__'):
            parent.add(node.expr.id.strip('_').capitalize() + "Stmt")
        else:
            b = parent.add("ExprStmt")
            eb = b.add("expression")
            _expr(eb, node.expr)

    elif isinstance(node, (DeclTyped, DeclInit)):
        _decl(parent, node)

    else:
        parent.add(f"[dim]{repr(node)}[/dim]")


def _expr(parent, node):
    if node is None:
        parent.add("[dim]None[/dim]")
        return

    if isinstance(node, Assign):
        b = parent.add("Assign")
        # target puede ser Name o Index
        if isinstance(node.target, Name):
            b.add(f"name: [green]'{node.target.id}'[/green]")
        else:
            tb = b.add("target")
            _expr(tb, node.target)
        vb = b.add("value")
        _expr(vb, node.value)

    elif isinstance(node, BinOp):
        b = parent.add("BinaryOp")
        b.add(f"op: [yellow]'{node.op}'[/yellow]")
        lb = b.add("left")
        _expr(lb, node.left)
        rb = b.add("right")
        _expr(rb, node.right)

    elif isinstance(node, UnaryOp):
        b = parent.add("UnaryOp")
        b.add(f"op: [yellow]'{node.op}'[/yellow]")
        eb = b.add("expr")
        _expr(eb, node.expr)

    elif isinstance(node, PostfixOp):
        b = parent.add("PostfixOp")
        b.add(f"op: [yellow]'{node.op}'[/yellow]")
        eb = b.add("expr")
        _expr(eb, node.expr)

    elif isinstance(node, Call):
        b = parent.add("Call")
        b.add(f"name: [green]'{node.func}'[/green]")
        if node.args:
            ab = b.add("args")
            for arg in node.args:
                _expr(ab, arg)

    elif isinstance(node, Index):
        b = parent.add("IndexExpr")
        _expr(b, node.base)
        for idx in node.indices:
            ib = b.add("index")
            _expr(ib, idx)

    elif isinstance(node, Name):
        b = parent.add("Identifier")
        b.add(f"name: [green]'{node.id}'[/green]")

    elif isinstance(node, Literal):
        kind_map = {
            'integer': 'IntLiteral',
            'float':   'FloatLiteral',
            'char':    'CharLiteral',
            'string':  'StringLiteral',
            'boolean': 'BoolLiteral',
        }
        label = kind_map.get(node.kind, 'Literal')
        b = parent.add(label)
        val = f"'{node.value}'" if isinstance(node.value, str) else node.value
        b.add(f"value: [magenta]{val}[/magenta]")

    else:
        parent.add(f"[dim]{repr(node)}[/dim]")



def _type_str(typ) -> str:
    if isinstance(typ, SimpleType):
        return typ.name
    if isinstance(typ, ArrayType):
        return f"array[] {_type_str(typ.elem)}"
    if isinstance(typ, ArraySizedType):
        return f"array[n] {_type_str(typ.elem)}"
    if isinstance(typ, FuncType):
        params = ', '.join(_type_str(p.typ) for p in typ.params)
        return f"function {_type_str(typ.ret)}({params})"
    return str(typ)


def render_graphviz(ast):
    print("]")