
# bminor_rd2.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Iterator, Optional, List, Union
from rich import print
import re

# ===================================================
# AST (dataclasses) - basado en grammar.txt
# ===================================================

# ---------- Types ----------
class Type: ...

@dataclass(frozen=True)
class SimpleType(Type):
	name: str  # INTEGER, FLOAT, BOOLEAN, CHAR, STRING, VOID

@dataclass(frozen=True)
class ArrayType(Type):
	# type_array ::= ARRAY [ ] type_simple | ARRAY [ ] type_array
	elem: Type

@dataclass(frozen=True)
class ArraySizedType(Type):
	# type_array_sized ::= ARRAY index type_simple | ARRAY index type_array_sized
	size_expr: "Expr"
	elem: Type  # SimpleType o ArraySizedType (recursivo)

@dataclass(frozen=True)
class FuncType(Type):
	# type_func ::= FUNCTION type_simple '(' opt_param_list ')'
	#           |  FUNCTION type_array_sized '(' opt_param_list ')'
	ret: Type
	params: List["Param"]

@dataclass(frozen=True)
class Param:
	name: str
	typ: Type

# ---------- Program / Decl ----------
class Decl: ...

@dataclass
class Program:
	decls: List[Decl]

@dataclass
class DeclTyped(Decl):
	# decl ::= ID ':' type_simple ';' | ID ':' type_array_sized ';' | ID ':' type_func ';'
	name: str
	typ: Type

@dataclass
class DeclInit(Decl):
	# decl_init ::= ID ':' type_simple '=' expr ';'
	#            |  ID ':' type_array_sized '=' '{' opt_expr_list '}' ';'
	#            |  ID ':' type_func '=' '{' opt_stmt_list '}'
	name: str
	typ: Type
	init: Any  # Expr | List[Expr] | List[Stmt]

# ---------- Stmt ----------
class Stmt: ...

@dataclass
class Print(Stmt):
	values: List["Expr"]

@dataclass
class Return(Stmt):
	value: Optional["Expr"]

@dataclass
class Block(Stmt):
	stmts: List[Union[Stmt, Decl]]  # en tu gramática: stmt puede ser decl (simple_stmt)

@dataclass
class ExprStmt(Stmt):
	expr: "Expr"

@dataclass
class If(Stmt):
	cond: Optional["Expr"]     # if_cond usa opt_expr
	then: Stmt
	otherwise: Optional[Stmt] = None

@dataclass
class For(Stmt):
	init: Optional["Expr"]
	cond: Optional["Expr"]
	step: Optional["Expr"]
	body: Stmt

# ---------- Expr ----------
class Expr: ...

@dataclass
class Name(Expr):
	id: str

@dataclass
class Literal(Expr):
	kind: str
	value: Any

@dataclass
class Index(Expr):
	base: Expr
	indices: List[Expr]

@dataclass
class Call(Expr):
	func: str
	args: List[Expr]

@dataclass
class Assign(Expr):
	target: Expr
	value: Expr

@dataclass
class BinOp(Expr):
	op: str
	left: Expr
	right: Expr

@dataclass
class UnaryOp(Expr):
	op: str
	expr: Expr

@dataclass
class PostfixOp(Expr):
	op: str  # INC/DEC
	expr: Expr
