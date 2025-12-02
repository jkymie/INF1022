from lexer import lexer
from parser import parser
from gera_cod import gerar_c

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('Uso: python main.py exemplos/nome.obsact')
        sys.exit(1)
    path = sys.argv[1]
    with open(path, 'r') as f:
        data = f.read()

    # analisar
    ast = parser.parse(data)

    # gerar C
    csrc = gerar_c(ast)
    out = path.rsplit('.',1)[0] + '.c'
    with open(out, 'w') as f:
        f.write(csrc)
    print(f'Gerado: {out}')