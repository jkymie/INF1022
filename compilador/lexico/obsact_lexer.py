"""
Analisador Léxico para a linguagem ObsAct
Utiliza PLY (Python Lex-Yacc)
"""

import ply.lex as lex

# Palavras reservadas da linguagem ObsAct
reserved = {
    'dispositivos': 'DISPOSITIVOS',
    'fimdispositivos': 'FIMDISPOSITIVOS',
    'def': 'DEF',
    'quando': 'QUANDO',
    'senao': 'SENAO',
    'execute': 'EXECUTE',
    'em': 'EM',
    'alerta': 'ALERTA',
    'para': 'PARA',
    'difundir': 'DIFUNDIR',
    'ligar': 'LIGAR',
    'desligar': 'DESLIGAR',
    'TRUE': 'TRUE',
    'FALSE': 'FALSE',
    'AND': 'AND',
}

# Lista de tokens
tokens = [
    'ID_DEV_ICE',
    'ID_OBS',
    'NUM',
    'MSG',
    'OP_LOGIC',
    'COLON',
    'SEMICOLON',
    'COMMA',
    'LBRACKET',
    'RBRACKET',
    'EQUALS',
    'ARROW',
] + list(reserved.values())

# Regras de expressões regulares para tokens simples
t_COLON = r':'
t_SEMICOLON = r';'
t_COMMA = r','
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_EQUALS = r'='
t_ARROW = r'->'

# Operadores lógicos (ordem importante: >= e <= antes de > e <)
def t_OP_LOGIC(t):
    r'>=|<=|==|!=|>|<'
    return t

# Mensagens (strings entre aspas duplas)
def t_MSG(t):
    r'"[^"]{1,100}"'
    t.value = t.value[1:-1]  # Remove as aspas
    return t

# Números inteiros não negativos
def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Identificadores: ID_OBS (começa com letra, pode ter letras e números)
# ID_DEV_ICE (apenas letras)
def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    # Verifica se é palavra reservada
    t.type = reserved.get(t.value, 'ID_OBS')
    
    # Se não é palavra reservada, determina se é ID_DEV_ICE ou ID_OBS
    if t.type == 'ID_OBS':
        # ID_DEV_ICE: apenas letras
        if t.value.isalpha():
            # Pode ser tanto ID_DEV_ICE quanto ID_OBS
            # O parser decidirá baseado no contexto
            # Por padrão, tratamos como ID_OBS e o parser converterá se necessário
            pass
        # ID_OBS: começa com letra, pode ter números
        else:
            t.type = 'ID_OBS'
    
    return t

# Ignora espaços e tabs
t_ignore = ' \t'

# Ignora quebras de linha, mas rastreia números de linha
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Ignora comentários (linha única com //)
def t_COMMENT(t):
    r'//.*'
    pass  # Não retorna nada, apenas ignora

# Tratamento de erros
def t_error(t):
    print(f"Caractere ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

# Constrói o lexer
def build_lexer():
    return lex.lex()

# Função para testar o lexer
def test_lexer(data):
    lexer = build_lexer()
    lexer.input(data)
    
    tokens_list = []
    for tok in lexer:
        tokens_list.append(tok)
        print(f"{tok.type}: {tok.value}")
    
    return tokens_list

if __name__ == '__main__':
    # Teste básico
    test_data = '''
    dispositivos:
        Lampada
        Sensor[temperatura]
    fimdispositivos
    
    def temperatura = 25;
    quando temperatura > 30: execute ligar em Lampada;
    '''
    
    test_lexer(test_data)
