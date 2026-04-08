import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from errors     import errors_detected, clear_errors
from lexer      import Lexer
from parser     import Parser
from visualizer import print_rich_tree

def main():
    if len(sys.argv) != 2:
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
    ast    = parser.parse(lexer.tokenize(source))

    if errors_detected() or ast is None:
        print(f"\nSe encontraron errores. No se genera el AST.\n")
        sys.exit(1)

    print(f"Analisis exitoso.\n")
    print_rich_tree(ast)

if __name__ == '__main__':
    main()