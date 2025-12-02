import sys
import io
from lexico.obsact_lexer import lexer
from parser.obsact_parser import parser, device_list, observation_list, c_statements

def main():
    if len(sys.argv) != 3:
        print("Uso: python main.py entrada.obsact saida.c")
        sys.exit(1)
    entrada, saida = sys.argv[1], sys.argv[2]

    # 1) Leia usando utf-8-sig para descartar BOM automaticamente
    try:
        with io.open(entrada, 'r', encoding='utf-8-sig') as fin:
            data = fin.read()
    except UnicodeDecodeError:
        print(f"Erro de codificação ao ler {entrada}. Utilize UTF-8 (sem BOM) ou instale o codec utf-8-sig.")
        sys.exit(1)

    # 2) Remova espaços em branco no início (caso alguém tenha deixado linhas em branco)
    data = data.lstrip()

    # 3) Limpe o estado global antes do parse
    device_list.clear()
    observation_list.clear()
    c_statements.clear()

    # 4) Parse
    c_code = parser.parse(data, lexer=lexer)
    if c_code is None:
        print("Não foi possível gerar código C devido a erros de sintaxe.") 
        sys.exit(1)

    # 5) Grave o .c resultante
    with io.open(saida, 'w', encoding='utf-8') as f:
        f.write(c_code)

    print(f"Arquivo C gerado: {saida}")

if __name__ == '__main__':
    main()
