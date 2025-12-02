import ply.lex as lex

# lista de palavras
keywords = {
'def': 'DEF',
'quando': 'QUANDO',
'senao': 'SENAO',
'dispositivos': 'DISPOSITIVOS',
'fimdispositivos': 'FIMDISPOSITIVOS',
'execute': 'EXECUTE',
'em': 'EM',
'alerta': 'ALERTA',
'para': 'PARA',
'difundir': 'DIFUNDIR',
'ligar': 'LIGAR',
'desligar': 'DESLIGAR',
'true': 'BOOL',
'false': 'BOOL',
'AND': 'AND'
}

# lista de tokens
tokens = [
    'ID_DEV', 'ID_OBS', 'NUM', 'MSG', 'OP_LOGIC', 'EQ', 'VIRG', 'DP', 'SETAB', 'PONTOV', 'LSQB', 'RSQB',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN'
] + list(set(keywords.values()))

# símbolos simples
t_VIRG = r','
t_DP = r':'
t_PONTOV = r';'
t_LSQB = r'\['
t_RSQB = r'\]'
t_PLUS = r'\+'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'

# operador -> deve vir antes de - (ordem de definição de funções importa)
def t_SETAB(t):
    r'->'
    return t

def t_MINUS(t):
    r'-'
    return t

# operadores lógicos (inclui '=' para atribuição usada como OP_LOGIC no parser)
t_OP_LOGIC = r'(==|!=|>=|<=|>|<)'

# operador de atribuição
t_EQ = r'='

# Mensagem entre aspas (não-gulosa)
def t_MSG(t):
    r'".*?"'
    t.value = t.value[1:-1]
    return t

# Número inteiro

def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

# identificadores (serão classificados em ID_DEV ou ID_OBS)
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    val = t.value
    # primeiro tenta match exato (preserva chaves como 'AND' se estiverem em maiúsculas)
    if val in keywords:
        t.type = keywords[val]
        if t.type == 'BOOL':
            t.value = True if val == 'true' else False
        return t

    # tenta match case-insensitive para palavras-chave (aceita 'True'/'False')
    val_lower = val.lower()
    if val_lower in keywords:
        t.type = keywords[val_lower]
        if t.type == 'BOOL':
            t.value = True if val_lower == 'true' else False
        return t

    # heurística: nomes com primeira letra maiúscula => dispositivo
    if val[0].isupper():
        t.type = 'ID_DEV'
        t.value = val
    else:
        t.type = 'ID_OBS'
        t.value = val
    return t


# comentários (linha)
def t_COMMENT(t):
    r'//.*'
    pass

# ignorar espaços e tabs
t_ignore = ' \t\r'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Erro léxico na linha {t.lineno}: caractere inesperado '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()

# validar se o lexer funciona corretamente em um determinado exemplo
"""
if __name__ == '__main__':
    data = open('exemplos/ex7.obsact').read()
    lexer.input(data)
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)
"""

# validar se o lexer funciona corretamente em todos os exemplos
if __name__ == '__main__':
    import glob
    import os
    
    exemplos = sorted(glob.glob('exemplos/ex*.obsact'))
    
    for arquivo in exemplos:
        nome = os.path.basename(arquivo)
        print(f"\n{'='*60}")
        print(f"Testando: {nome}")
        print('='*60)
        
        try:
            data = open(arquivo).read()
            lexer.input(data)
            tokens_list = []
            while True:
                tok = lexer.token()
                if not tok:
                    break
                tokens_list.append(tok)
            
            print(f"✓ Lexer executado com sucesso! ({len(tokens_list)} tokens)")
            for tok in tokens_list:
                print(tok)
        except Exception as e:
            print(f"✗ Erro: {e}")