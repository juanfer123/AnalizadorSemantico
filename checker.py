# checker.py
from __future__ import annotations

from multimethod import multimeta
from model import (
    Program, DeclTyped, DeclInit,
    Name, Literal, BinOp, UnaryOp, PostfixOp,
    Assign, Call, Index,
    Print, Return, Block, ExprStmt, If, For,
    FuncType, SimpleType, ArrayType, ArraySizedType,
    Type, Expr, Stmt, Decl
)
from symtab import Symtab

# ─────────────────────────────────────────
#  Patrón Visitor con multimethod
# ─────────────────────────────────────────

class Visitor(metaclass=multimeta):
    pass

class Checker(Visitor):

    def __init__(self):
        self.errors: list[str] = []
        # Creamos el scope global al iniciar
        self.symtab: Symtab = Symtab("global")

    # ── Errores ───────────────────────────

    def error(self, msg: str):
        self.errors.append(msg)

    def report(self):
        if self.errors:
            for e in self.errors:
                print(e)
            print(f"\nsemantic check: failed ({len(self.errors)} error(s))")
        else:
            print("semantic check: success")

    # ══════════════════════════════════════
    #  FASE 1: Declaraciones + uso de Names
    # ══════════════════════════════════════

    def visit(self, node: Program):
        """Punto de entrada: recorre todas las declaraciones globales."""
        for decl in node.decls:
            self.visit(decl)

    # ── Declaraciones ─────────────────────

    def visit(self, node: DeclTyped):
        """
        x : integer;
        Registra el nombre con su tipo en la tabla.
        Sin valor inicial.
        """
        try:
            self.symtab.add(node.name, node)
        except Symtab.SymbolDefinedError:
            self.error(f"error: '{node.name}' ya fue declarado en este scope")
        except Symtab.SymbolConflictError:
            self.error(f"error: '{node.name}' redeclarado con tipo distinto en este scope")

    def visit(self, node: DeclInit):
        """
        x : integer = 10;
        f : function integer (x: integer) = { ... }
        Registra el nombre y luego visita el inicializador.
        """
        try:
            self.symtab.add(node.name, node)
        except Symtab.SymbolDefinedError:
            self.error(f"error: '{node.name}' ya fue declarado en este scope")
        except Symtab.SymbolConflictError:
            self.error(f"error: '{node.name}' redeclarado con tipo distinto en este scope")

        # Visitar el inicializador para detectar Names no definidos dentro
        if isinstance(node.init, list):
            for item in node.init:
                self.visit(item)
        elif node.init is not None:
            self.visit(node.init)

    # ── Expresiones ───────────────────────

    def visit(self, node: Name):
        """
        Uso de un identificador → buscar en symtab.
        Si no existe: error de símbolo no definido.
        """
        sym = self.symtab.get(node.id)
        if sym is None:
            self.error(f"error: símbolo '{node.id}' no definido")

    def visit(self, node: Literal):
        """Los literales no necesitan chequeo en Fase 1."""
        pass

    def visit(self, node: BinOp):
        """Visitar ambos operandos para detectar Names no definidos."""
        self.visit(node.left)
        self.visit(node.right)

    def visit(self, node: UnaryOp):
        self.visit(node.expr)

    def visit(self, node: PostfixOp):
        self.visit(node.expr)

    def visit(self, node: Assign):
        self.visit(node.target)
        self.visit(node.value)

    def visit(self, node: Call):
        """Llamada a función: verificar que el nombre exista."""
        sym = self.symtab.get(node.func)
        if sym is None:
            self.error(f"error: función '{node.func}' no definida")
        for arg in node.args:
            self.visit(arg)

    def visit(self, node: Index):
        self.visit(node.base)
        for idx in node.indices:
            if not isinstance(idx, int):
                self.visit(idx)

    # ── Sentencias ────────────────────────

    def visit(self, node: Print):
        for val in node.values:
            self.visit(val)

    def visit(self, node: Return):
        if node.value is not None:
            self.visit(node.value)

    def visit(self, node: Block):
        for stmt in node.stmts:
            self.visit(stmt)

    def visit(self, node: ExprStmt):
        self.visit(node.expr)

    def visit(self, node: If):
        if node.cond is not None:
            self.visit(node.cond)
        self.visit(node.then)
        if node.otherwise is not None:
            self.visit(node.otherwise)

    def visit(self, node: For):
        if node.init is not None:
            self.visit(node.init)
        if node.cond is not None:
            self.visit(node.cond)
        if node.step is not None:
            self.visit(node.step)
        self.visit(node.body)

    # ── Tipos (no se chequean en Fase 1) ──

    def visit(self, node: SimpleType):      pass
    def visit(self, node: ArrayType):       pass
    def visit(self, node: ArraySizedType):  pass
    def visit(self, node: FuncType):        pass
