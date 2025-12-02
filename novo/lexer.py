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
    'ID_DEV', 'ID_OBS', 'NUM', 'MSG', 'OP_LOGIC', 'EQ', 'VIRG', 'DP', 'SETAB', 'PONTOV', 'LSQB', 'RSQB'
] + list(set(keywords.values()))

# símbolos simples
t_VIRG = r','
t_DP = r':'
t_SETAB = r'->'
t_PONTOV = r';'
t_LSQB = r'\['
t_RSQB = r'\]'

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
    if val in keywords:
        t.type = keywords[val]
        # se keyword 'BOOL', converte value para True/False
        if t.type == 'BOOL':
            t.value = True if val == 'true' else False
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

# validar se o lexer funciona corretamente
if __name__ == '__main__':
    data = open('exemplos/ex7.obsact').read()
    lexer.input(data)
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)