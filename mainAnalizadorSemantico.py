import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from errors     import errors_detected, clear_errors
from lexer      import Lexer
from parser     import Parser
from checker    import Checker

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        source = open(filename, encoding='utf-8').read()
    except FileNotFoundError:
        print(f"No se encontro el archivo: {filename}")
        sys.exit(1)

    clear_errors()
    lexer  = Lexer()
    parser = Parser()
    tree   = parser.parse(lexer.tokenize(source))

    if errors_detected() or tree is None:
        print(f"\nSe encontraron errores. No se genera el AST.\n")
        sys.exit(1)

    checker = Checker()
    checker.visit(tree)
    checker.symtab.print()    # muestra la tabla de símbolos
    checker.report()          # imprime errores o "success"

if __name__ == '__main__':
    main()