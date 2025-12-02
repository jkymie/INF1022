#!/usr/bin/env python3
"""
Compilador ObsAct -> C
Uso: python main.py <arquivo.obsact> [-o <saida.c>]
"""
import sys
import os
import argparse
from parser.obsact_parser import parse_program
from c_generator import generate_c_code

def compile_obsact(input_file, output_file=None):
    """Compila um arquivo ObsAct para C"""
    
    # Define nome do arquivo de saída
    if output_file is None:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}.c"
    
    print(f"Compilando {input_file} -> {output_file}")
    
    # Lê o arquivo de entrada
    try:
        with open(input_file, 'r') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"Erro: arquivo '{input_file}' não encontrado")
        return False
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return False
    
    # Parse
    print("Analisando sintaxe...")
    ast = parse_program(code)
    
    if not ast:
        print("Erro: análise sintática falhou")
        return False
    
    print("✓ Análise sintática OK")
    
    # Geração de código
    print("Gerando código C...")
    try:
        c_code = generate_c_code(ast)
    except Exception as e:
        print(f"Erro ao gerar código: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Escreve arquivo de saída
    try:
        with open(output_file, 'w') as f:
            f.write(c_code)
    except Exception as e:
        print(f"Erro ao escrever arquivo: {e}")
        return False
    
    print(f"✓ Código C gerado em {output_file}")
    return True

def main():
    parser = argparse.ArgumentParser(
        description='Compilador ObsAct para C'
    )
    parser.add_argument(
        'input',
        help='Arquivo .obsact de entrada'
    )
    parser.add_argument(
        '-o', '--output',
        help='Arquivo .c de saída (opcional)',
        default=None
    )
    
    args = parser.parse_args()
    
    success = compile_obsact(args.input, args.output)
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
