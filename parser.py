import ply.yacc as yacc
from lexer import tokens

# AST simples: usaremos dicionários e listas

# programa: { 'devices': [ (id, obs?)... ], 'defs': [ (id, val) ... ], 'cmds': [ ... ] }

def p_PROGRAM(p):
    'PROGRAM : DEV_SEC CMD_SEC'
    p[0] = {
        'devices': p[1],
        'cmds': p[2]
    }

# DEV_SEC
def p_DEV_SEC(p):
    'DEV_SEC : DISPOSITIVOS DP DEV_LIST FIMDISPOSITIVOS'
    p[0] = p[3]

def p_DEV_LIST_single(p):
    'DEV_LIST : DEV_ITEM'
    p[0] = [p[1]]

def p_DEV_LIST_many(p):
    'DEV_LIST : DEV_LIST DEV_ITEM'
    p[0] = p[1] + [p[2]]

def p_DEV_ITEM_noobs(p):
    'DEV_ITEM : ID_DEV'
    p[0] = (p[1], None)

def p_DEV_ITEM_obs(p):
    "DEV_ITEM : ID_DEV LSQB ID_OBS RSQB"
    p[0] = (p[1], p[3])

# CMD_SEC -> lista de comandos e defs

def p_CMD_SEC_empty(p):
    'CMD_SEC : '
    p[0] = {'defs': [], 'cmds': []}

def p_CMD_SEC(p):
    'CMD_SEC : CMD_LIST'
    # CMD_LIST retorna lista de comandos e defs misturadas
    defs = []
    cmds = []
    for item in p[1]:
        if item[0] == 'def':
            defs.append((item[1], item[2]))
        else:
            cmds.append(item)
    p[0] = {'defs': defs, 'cmds': cmds}

# CMD_LIST -> sequência terminada por ponto e vírgula

def p_CMD_LIST_single(p):
    'CMD_LIST : CMD PONTOV'
    p[0] = [p[1]]

def p_CMD_LIST_many(p):
    'CMD_LIST : CMD_LIST CMD PONTOV'
    p[0] = p[1] + [p[2]]

# CMD -> ATTR | OBSACT | ACT

def p_CMD_ATTR(p):
    'CMD : DEF ID_OBS EQ VAL'
    # Atribuição: def ID = VAL
    p[0] = ('def', p[2], p[4])

def p_CMD_ACT(p):
    'CMD : ACT'
    # Ação standalone (fora de quando)
    p[0] = p[1]

def p_CMD_OBSACT_simple(p):
    'CMD : QUANDO OBS DP ACT'
    p[0] = ('quando', p[2], p[4], None)

def p_CMD_OBSACT_else(p):
    'CMD : QUANDO OBS DP ACT SENAO ACT'
    p[0] = ('quando', p[2], p[4], p[6])

# OBS -> SIMPLE_OBS | SIMPLE_OBS AND OBS

def p_OBS_simple(p):
    'OBS : SIMPLE_OBS'
    p[0] = p[1]

def p_OBS_and(p):
    'OBS : SIMPLE_OBS AND OBS'
    p[0] = ('and', p[1], p[3])

def p_SIMPLE_OBS(p):
    'SIMPLE_OBS : ID_OBS OP_LOGIC VAL'
    p[0] = ('cmp', p[1], p[2], p[3])

# VAL -> NUM | BOOL

def p_VAL_NUM(p):
    'VAL : NUM'
    p[0] = ('num', p[1])

def p_VAL_BOOL(p):
    'VAL : BOOL'
    p[0] = ('bool', p[1])

# ACT -> execute ACTION em ID_DEV | alerta para ID_DEV : MSG [, ID_OBS] | difundir ...

def p_ACT_execute(p):
    'ACT : EXECUTE ACTION EM ID_DEV'
    p[0] = ('execute', p[2], p[4])

def p_ACT_alerta_simple(p):
    'ACT : ALERTA PARA ID_DEV DP MSG'
    p[0] = ('alerta', p[3], p[5], None)

def p_ACT_alerta_obs(p):
    'ACT : ALERTA PARA ID_DEV DP MSG VIRG ID_OBS'
    p[0] = ('alerta', p[3], p[5], p[7])

def p_ACT_difundir(p):
    'ACT : DIFUNDIR DP MSG SETAB LSB_DEVLIST'
    # Rótulo: difundir : "msg" -> [ dev , dev ]
    p[0] = ('difundir', p[3], p[5])


def p_ACT_difundir_msg_obs(p):
    'ACT : DIFUNDIR DP MSG ID_OBS SETAB LSB_DEVLIST'
    # Rótulo: difundir : "msg" ID_OBS -> [ dev , dev ]
    # Permite incluir um identificador de observável após a mensagem
    p[0] = ('difundir', (p[3], p[4]), p[6])

# Para simplificar, implementamos DEV_LIST_N (LSB/RSB são tokens '[' ']' para difundir)

def p_LSB_DEVLIST(p):
    'LSB_DEVLIST : LSQB DEV_LIST_N RSQB'
    p[0] = p[2]

def p_DEV_LIST_N_single(p):
    'DEV_LIST_N : ID_DEV'
    p[0] = [p[1]]

def p_DEV_LIST_N_many(p):
    'DEV_LIST_N : DEV_LIST_N VIRG ID_DEV'
    p[0] = p[1] + [p[3]]


# tokens auxiliares (ACTION)

def p_ACTION(p):
    'ACTION : LIGAR'
    p[0] = 'ligar'

def p_ACTION_desligar(p):
    'ACTION : DESLIGAR'
    p[0] = 'desligar'

def p_error(p):
    if p:
        raise SyntaxError(f"Erro sintático: token inesperado '{p.value}' (linha {p.lineno})")
    else:
        raise SyntaxError("Erro sintático: fim de arquivo inesperado")

parser = yacc.yacc()

# validar se o parser funciona corretamente em um determinado exemplo
"""
if __name__ == '__main__':
    data = open('exemplos/ex2.obsact').read()
    ast = parser.parse(data)
    import pprint; pprint.pprint(ast)
"""

# validar se o parser funciona corretamente em todos os exemplos
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
            ast = parser.parse(data)
            print("✓ Parser executado com sucesso!")
            import pprint
            pprint.pprint(ast)
        except Exception as e:
            print(f"✗ Erro: {e}")