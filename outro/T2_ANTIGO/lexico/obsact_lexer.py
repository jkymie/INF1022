import ply.lex as lex

# --------------------------------------------------
# 1) lista de nomes de tokens
#    inclua aqui TODOS os tokens, exceto os keywords
tokens = (
    'DISPOSITIVOS','FIMDISPOSITIVOS','DEF','QUANDO','EXECUTE',
    'EM','LIGAR','DESLIGAR','ALERTA','PARA','DIFUNDIR','SENAO','AND',
    
    'SEMICOLON','COLON','COMMA','EQUAL',
    'LBRACKET','RBRACKET','ARROW',

    'OPLOGIC',

    'NUMBER','BOOL','MSG','ID_DEV_ICE','ID_OBS',
)
# --------------------------------------------------

# --------------------------------------------------
# 2) dicionário de palavras-reservadas
reserved = {
    'dispositivos': 'DISPOSITIVOS',
    'fimdispositivos': 'FIMDISPOSITIVOS',
    'def': 'DEF',
    'quando': 'QUANDO',
    'senao': 'SENAO',
    'execute': 'EXECUTE',
    'em': 'EM',
    'ligar': 'LIGAR',
    'desligar': 'DESLIGAR',
    'alerta': 'ALERTA',
    'para': 'PARA',
    'difundir': 'DIFUNDIR',
    'AND': 'AND',
}
# --------------------------------------------------

# --------------------------------------------------
# 3) regex para literais e símbolos
t_SEMICOLON = r';'
t_COLON     = r':'
t_COMMA     = r','
t_EQUAL     = r'='
t_LBRACKET  = r'\['
t_RBRACKET  = r'\]'
t_ARROW     = r'->'
t_OPLOGIC   = r'<=|>=|==|!=|<|>'
# --------------------------------------------------

# --------------------------------------------------
# 4) tokens compostos com função (para poder dar t.type dinâmico)
def t_MSG(t):
    r'"([^"]{0,100})"'
    t.value = t.value[1:-1]
    if len(t.value) > 100:
        print(f"Erro léxico: mensagem excede 100 caracteres")
        t.lexer.skip(1)
        return None
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    if t.value < 0:
        print(f"Erro léxico: número negativo não permitido")
        t.lexer.skip(1)
        return None
    return t

def t_BOOL(t):
    r'TRUE|FALSE'
    t.value = (t.value == 'TRUE')
    return t

def t_ID(t):
    r'[A-Za-z][A-Za-z0-9]*'
    # se for palavra-reservada, sobrescreve o tipo
    lower_val = t.value.lower()
    if lower_val in reserved:
        t.type = reserved[lower_val]
    else:
        # Determina se é ID_DEV_ICE (só letras) ou ID_OBS (letras e números)
        if t.value.isalpha():
            t.type = 'ID_DEV_ICE'
        else:
            t.type = 'ID_OBS'
    return t
# --------------------------------------------------

# --------------------------------------------------
# 5) ignorar espaços e quebras de linha
t_ignore = ' \t\r\n'

def t_error(t):
    print(f"Lex error em '{t.value[0]}'")
    t.lexer.skip(1)
# --------------------------------------------------

lexer = lex.lex()
