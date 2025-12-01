import ply.yacc as yacc
from lexico.obsact_lexer import tokens

# globais que acumulam cada parse
device_list      = []
observation_list = []
c_statements     = []

# --- PRODUÇÕES ---

def p_program(p):
    'program : dev_sec cmd_sec'
    # monta o C final
    header = [
        '#include <stdio.h>',
        '',
        '// protótipos das funções ObsAct → C',
        'void ligar(const char* dev);',
        'void desligar(const char* dev);',
        'void alerta(const char* dev, const char* msg);',
        'void alerta_var(const char* dev, const char* msg, int var);',
        '',
        'int main() {'
    ]
    # inicializa observations
    for obs in observation_list:
        header.append(f'    int {obs} = 0;')
    header.append('')

    body = ['    ' + stmt for stmt in c_statements]
    footer = [
        '',
        '    return 0;',
        '}',
        '',
        '// implementações das funções',
        'void ligar(const char* dev) { printf("%s ligado !\\n", dev); }',
        'void desligar(const char* dev) { printf("%s desligado !\\n", dev); }',
        'void alerta(const char* dev, const char* msg) {',
        '    printf("%s recebeu o alerta :\\n", dev);',
        '    printf("%s\\n", msg);',
        '}',
        'void alerta_var(const char* dev, const char* msg, int var) {',
        '    printf("%s recebeu o alerta :\\n", dev);',
        '    printf("%s %d\\n", msg, var);',
        '}',
    ]

    p[0] = '\n'.join(header + body + footer)

# --- DEV_SEC: dispositivos : DEV_LIST fimdispositivos ---
def p_dev_sec(p):
    'dev_sec : DISPOSITIVOS COLON dev_list FIMDISPOSITIVOS'
    pass

def p_dev_list_multiple(p):
    'dev_list : dev_ice dev_list'
    pass

def p_dev_list_single(p):
    'dev_list : dev_ice'
    pass

def p_dev_ice_simple(p):
    'dev_ice : ID_DEV_ICE'
    device_list.append(p[1])

def p_dev_ice_obs(p):
    '''dev_ice : ID_DEV_ICE LBRACKET ID_OBS RBRACKET
               | ID_DEV_ICE LBRACKET ID_DEV_ICE RBRACKET'''
    device_list.append(p[1])
    observation_list.append(p[3])

# --- CMD_SEC: CMD_LIST ---
def p_cmd_sec(p):
    'cmd_sec : cmd_list'
    pass

def p_cmd_list_multiple(p):
    'cmd_list : cmd SEMICOLON cmd_list'
    pass

def p_cmd_list_single(p):
    'cmd_list : cmd SEMICOLON'
    pass

def p_cmd(p):
    '''cmd : attrib
           | obsact
           | act'''
    if p[1]:
        c_statements.append(p[1])

# --- ATTRIB: def ID_OBS = VAL ---
def p_attrib(p):
    '''attrib : DEF ID_OBS EQUAL val
              | DEF ID_DEV_ICE EQUAL val'''
    if p[2] not in observation_list:
        observation_list.append(p[2])
    p[0] = f'{p[2]} = {p[4]};'

# --- VAL: NUM | BOOL ---
def p_val_number(p):
    'val : NUMBER'
    p[0] = str(p[1])

def p_val_bool(p):
    'val : BOOL'
    p[0] = '1' if p[1] else '0'

# --- OBSACT: quando OBS : ACT [senao ACT] ---
def p_obsact_simple(p):
    'obsact : QUANDO obs COLON act'
    cond = p[2]
    then_code = p[4]
    p[0] = f'if ({cond}) {{ {then_code} }}'

def p_obsact_senao(p):
    'obsact : QUANDO obs COLON act SENAO act'
    cond = p[2]
    then_code = p[4]
    else_code = p[6]
    p[0] = f'if ({cond}) {{ {then_code} }} else {{ {else_code} }}'

# --- OBS: ID_OBS OPLOGIC VAL [AND OBS] ---
def p_obs_simple(p):
    '''obs : ID_OBS OPLOGIC val
           | ID_DEV_ICE OPLOGIC val'''
    p[0] = f'{p[1]} {p[2]} {p[3]}'

def p_obs_and(p):
    '''obs : ID_OBS OPLOGIC val AND obs
           | ID_DEV_ICE OPLOGIC val AND obs'''
    p[0] = f'({p[1]} {p[2]} {p[3]}) && ({p[5]})'

# --- ACT: várias formas ---

# execute ACTION em ID_DEV_ICE
def p_act_execute(p):
    'act : EXECUTE action EM ID_DEV_ICE'
    action_func = p[2]
    device = p[4]
    p[0] = action_func(device)

def p_action_ligar(p):
    'action : LIGAR'
    p[0] = lambda dev: f'ligar("{dev}");'

def p_action_desligar(p):
    'action : DESLIGAR'
    p[0] = lambda dev: f'desligar("{dev}");'

# alerta para ID_DEV_ICE : MSG
def p_act_alerta(p):
    'act : ALERTA PARA ID_DEV_ICE COLON MSG'
    device = p[3]
    msg = p[5]
    p[0] = f'alerta("{device}", "{msg}");'

# alerta para ID_DEV_ICE : MSG , ID_OBS
def p_act_alerta_var(p):
    '''act : ALERTA PARA ID_DEV_ICE COLON MSG COMMA ID_OBS
           | ALERTA PARA ID_DEV_ICE COLON MSG COMMA ID_DEV_ICE'''
    device = p[3]
    msg = p[5]
    var = p[7]
    p[0] = f'alerta_var("{device}", "{msg}", {var});'

# difundir : MSG -> [ DEV_LIST_N ]
def p_act_difundir(p):
    'act : DIFUNDIR COLON MSG ARROW LBRACKET dev_list_n RBRACKET'
    msg = p[3]
    devices = p[6]
    alerts = ' '.join([f'alerta("{dev}", "{msg}");' for dev in devices])
    p[0] = alerts

# difundir : MSG ID_OBS -> [ DEV_LIST_N ]
def p_act_difundir_var(p):
    '''act : DIFUNDIR COLON MSG ID_OBS ARROW LBRACKET dev_list_n RBRACKET
           | DIFUNDIR COLON MSG ID_DEV_ICE ARROW LBRACKET dev_list_n RBRACKET'''
    msg = p[3]
    var = p[4]
    devices = p[7]
    alerts = ' '.join([f'alerta_var("{dev}", "{msg}", {var});' for dev in devices])
    p[0] = alerts

# --- DEV_LIST_N: ID_DEV_ICE [, DEV_LIST_N] ---
def p_dev_list_n_single(p):
    'dev_list_n : ID_DEV_ICE'
    p[0] = [p[1]]

def p_dev_list_n_multiple(p):
    'dev_list_n : ID_DEV_ICE COMMA dev_list_n'
    p[0] = [p[1]] + p[3]

# erro de sintaxe
def p_error(p):
    if p:
        print(f"Syntax error detectado perto de {p.value!r} (tipo: {p.type}, linha: {p.lineno})")
        print(f"Verifique a sintaxe do arquivo ObsAct")
    else:
        print("Syntax error no fim de arquivo (verifique se há ponto-e-vírgula faltando)")

parser = yacc.yacc()
