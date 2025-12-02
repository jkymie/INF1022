"""
Analisador Sintático para a linguagem ObsAct
Utiliza PLY (Python Lex-Yacc) - LALR(1)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ply.yacc as yacc
from lexico.obsact_lexer import tokens, build_lexer

# Estruturas de dados para a AST (Abstract Syntax Tree)
class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, dev_sec, cmd_sec):
        self.dev_sec = dev_sec
        self.cmd_sec = cmd_sec

class DeviceSection(ASTNode):
    def __init__(self, dev_list):
        self.dev_list = dev_list

class Device(ASTNode):
    def __init__(self, name, sensor=None):
        self.name = name
        self.sensor = sensor

class CommandList(ASTNode):
    def __init__(self, commands):
        self.commands = commands

class Assignment(ASTNode):
    def __init__(self, var_name, value):
        self.var_name = var_name
        self.value = value

class ObsAction(ASTNode):
    def __init__(self, condition, action, else_action=None):
        self.condition = condition
        self.action = action
        self.else_action = else_action

class Condition(ASTNode):
    def __init__(self, var_name, operator, value, next_cond=None):
        self.var_name = var_name
        self.operator = operator
        self.value = value
        self.next_cond = next_cond

class Action(ASTNode):
    pass

class ExecuteAction(Action):
    def __init__(self, action_type, device):
        self.action_type = action_type  # 'ligar' ou 'desligar'
        self.device = device

class AlertAction(Action):
    def __init__(self, device, message, var_name=None):
        self.device = device
        self.message = message
        self.var_name = var_name

class BroadcastAction(Action):
    def __init__(self, message, var_name, device_list):
        self.message = message
        self.var_name = var_name
        self.device_list = device_list

# Precedência e associatividade
precedence = ()

# Regras da gramática

def p_program(p):
    '''program : dev_sec cmd_sec'''
    p[0] = Program(p[1], p[2])

def p_dev_sec(p):
    '''dev_sec : DISPOSITIVOS COLON dev_list FIMDISPOSITIVOS'''
    p[0] = DeviceSection(p[3])

def p_dev_list(p):
    '''dev_list : device dev_list
                | device'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_device_simple(p):
    '''device : id_device'''
    p[0] = Device(p[1])

def p_device_with_sensor(p):
    '''device : id_device LBRACKET ID_OBS RBRACKET'''
    p[0] = Device(p[1], p[3])

def p_id_device(p):
    '''id_device : ID_OBS'''
    # ID_DEV_ICE é representado por ID_OBS que contém apenas letras
    p[0] = p[1]

def p_cmd_sec(p):
    '''cmd_sec : cmd_list'''
    p[0] = CommandList(p[1])

def p_cmd_list(p):
    '''cmd_list : cmd SEMICOLON cmd_list
                | cmd SEMICOLON'''
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = [p[1]]

def p_cmd(p):
    '''cmd : attrib
           | obsact
           | act'''
    p[0] = p[1]

def p_attrib(p):
    '''attrib : DEF ID_OBS EQUALS val'''
    p[0] = Assignment(p[2], p[4])

def p_obsact_simple(p):
    '''obsact : QUANDO obs COLON act'''
    p[0] = ObsAction(p[2], p[4])

def p_obsact_with_else(p):
    '''obsact : QUANDO obs COLON act SENAO act'''
    p[0] = ObsAction(p[2], p[4], p[6])

def p_obs_simple(p):
    '''obs : ID_OBS OP_LOGIC val'''
    p[0] = Condition(p[1], p[2], p[3])

def p_obs_and(p):
    '''obs : ID_OBS OP_LOGIC val AND obs'''
    p[0] = Condition(p[1], p[2], p[3], p[5])

def p_val_num(p):
    '''val : NUM'''
    p[0] = p[1]

def p_val_bool(p):
    '''val : bool'''
    p[0] = p[1]

def p_bool(p):
    '''bool : TRUE
            | FALSE'''
    p[0] = p[1] == 'TRUE'

def p_act_execute(p):
    '''act : EXECUTE action EM id_device'''
    p[0] = ExecuteAction(p[2], p[4])

def p_action(p):
    '''action : LIGAR
              | DESLIGAR'''
    p[0] = p[1]

def p_act_alert_simple(p):
    '''act : ALERTA PARA id_device COLON MSG'''
    p[0] = AlertAction(p[3], p[5])

def p_act_alert_with_var(p):
    '''act : ALERTA PARA id_device COLON MSG COMMA ID_OBS'''
    p[0] = AlertAction(p[3], p[5], p[7])

def p_act_broadcast_simple(p):
    '''act : DIFUNDIR COLON MSG ARROW LBRACKET dev_list_n RBRACKET'''
    p[0] = BroadcastAction(p[3], None, p[6])

def p_act_broadcast_with_var(p):
    '''act : DIFUNDIR COLON MSG ID_OBS ARROW LBRACKET dev_list_n RBRACKET'''
    p[0] = BroadcastAction(p[3], p[4], p[7])

def p_dev_list_n_single(p):
    '''dev_list_n : id_device'''
    p[0] = [p[1]]

def p_dev_list_n_multiple(p):
    '''dev_list_n : id_device COMMA dev_list_n'''
    p[0] = [p[1]] + p[3]

def p_error(p):
    if p:
        print(f"Erro de sintaxe na linha {p.lineno}: token inesperado '{p.value}' (tipo: {p.type})")
    else:
        print("Erro de sintaxe: fim de arquivo inesperado")

# Constrói o parser
def build_parser():
    return yacc.yacc()

# Função para testar o parser
def parse_program(code):
    lexer = build_lexer()
    parser = build_parser()
    result = parser.parse(code, lexer=lexer)
    return result

if __name__ == '__main__':
    # Teste básico
    test_code = '''
    dispositivos:
        Lampada
        Sensor[temperatura]
    fimdispositivos
    
    def temperatura = 25;
    quando temperatura > 30: execute ligar em Lampada;
    '''
    
    result = parse_program(test_code)
    if result:
        print("\n✓ Análise sintática concluída com sucesso!")
        print(f"Programa possui {len(result.dev_sec.dev_list)} dispositivos")
        print(f"Programa possui {len(result.cmd_sec.commands)} comandos")
    else:
        print("\n✗ Erro na análise sintática")
