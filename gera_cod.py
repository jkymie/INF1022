# gerar código C a partir da representação interna do programa
def gen_val(v):
    t = v[0]
    if t == 'num':
        return str(v[1])
    if t == 'bool':
        return '1' if v[1] else '0'
    if t == 'id':
        return v[1]
    if t == 'binop':
        op = v[1]
        left = gen_val(v[2])
        right = gen_val(v[3])
        return f'({left} {op} {right})'
    raise ValueError('VAL inválido')

# retorna expressão C (string)
def gen_obs(obs):
    
    typ = obs[0]
    if typ == 'cmp':
        _, left, op, right = obs
        left_c = gen_val(left)
        right_c = gen_val(right)
        return f'{left_c} {op} {right_c}'
    if typ == 'and':
        left = gen_obs(obs[1])
        right = gen_obs(obs[2])
        return f'({left} && {right})'
    raise ValueError('OBS inválido')

# coleta todos os ID_OBS usados no programa
def collect_obs_ids(program):
    obs_ids = set()
    
    def collect_from_val(val):
        if val[0] == 'id':
            obs_ids.add(val[1])
        elif val[0] == 'binop':
            collect_from_val(val[2])
            collect_from_val(val[3])
    
    def collect_from_obs(obs):
        if obs[0] == 'cmp':
            collect_from_val(obs[1])  # left side
            collect_from_val(obs[3])  # right side
        elif obs[0] == 'and':
            collect_from_obs(obs[1])
            collect_from_obs(obs[2])
    
    def collect_from_act(act):
        if act[0] == 'alerta' and act[3]:
            obs_ids.add(act[3])
        elif act[0] == 'difundir' and isinstance(act[1], tuple):
            # difundir com ID_OBS: ('difundir', (msg, id_obs), devs)
            obs_ids.add(act[1][1])
    
    cmds = program['cmds'].get('cmds', []) if isinstance(program.get('cmds'), dict) else program.get('cmds', [])
    
    for cmd in cmds:
        if cmd[0] == 'quando':
            collect_from_obs(cmd[1])
            collect_from_act(cmd[2])
            if cmd[3]:
                collect_from_act(cmd[3])
        else:
            collect_from_act(cmd)
    
    # também coletar das definições
    defs = program['cmds'].get('defs', []) if isinstance(program.get('cmds'), dict) else []
    for name, val in defs:
        collect_from_val(val)
    
    return obs_ids

# gerar código C para o programa inteiro
def gerar_c(program):
    header = r'''#include <stdio.h>
#include <string.h>

void ligar(char* dev) { printf("%s ligado!\n", dev); }
void desligar(char* dev) { printf("%s desligado!\n", dev); }
void alerta(char* dev, char* msg) { printf("%s recebeu o alerta: %s\n", dev, msg); }
void alerta_obs(char* dev, char* msg, int obs_val) { printf("%s recebeu o alerta:\n", dev); printf("%s %d\n", msg, obs_val); }

'''
    # declarar variáveis (defs)
    vars_code = ''
    for name, val in program['cmds'] is None and [] or program.get('defs', []):
        pass

    defs = program['cmds'].get('defs', []) if isinstance(program.get('cmds'), dict) else []
    cmds = program['cmds'].get('cmds', []) if isinstance(program.get('cmds'), dict) else program.get('cmds', [])

    # coletar todos os ID_OBS usados
    all_obs_ids = collect_obs_ids(program)
    defined_obs_ids = {name for name, _ in defs}
    undefined_obs_ids = all_obs_ids - defined_obs_ids

    # separar definições simples (constantes) de expressões complexas
    simple_defs = []
    complex_defs = []
    for name, val in defs:
        if val[0] in ('num', 'bool'):
            simple_defs.append((name, val))
        else:
            complex_defs.append((name, val))
    
    # declarar variáveis simples com valores iniciais
    for name, val in simple_defs:
        cval = gen_val(val)
        vars_code += f'int {name} = {cval};\n'
    
    # declarar variáveis complexas sem inicialização (serão inicializadas no main)
    for name, _ in complex_defs:
        vars_code += f'int {name};\n'
    
    # declarar variáveis não definidas com valor 0
    for name in sorted(undefined_obs_ids):
        vars_code += f'int {name} = 0;\n'

    # gerar código principal
    main_code = ''
    
    # inicializar variáveis complexas no início do main
    for name, val in complex_defs:
        cval = gen_val(val)
        main_code += f'    {name} = {cval};\n'
    
    if complex_defs:
        main_code += '\n'
    
    for cmd in cmds:
        if cmd[0] == 'quando':
            obs = cmd[1]
            act = cmd[2]
            else_act = cmd[3]
            cond = gen_obs(obs)
            main_code += f'    if ({cond}) {{\n'
            main_code += '        ' + gen_act(act) + '\n'
            main_code += '    }'
            if else_act:
                main_code += f' else {{\n        {gen_act(else_act)}\n    }}'
            main_code += '\n\n'
        elif cmd[0] == 'execute':
            main_code += '    ' + gen_act(cmd) + '\n'
        elif cmd[0] == 'alerta':
            main_code += '    ' + gen_act(cmd) + '\n'
        elif cmd[0] == 'difundir':
            main_code += '    ' + gen_act(cmd) + '\n'

    full = header + '// Variáveis (defs)\n' + vars_code + '\nint main() {\n' + main_code + '    return 0;\n}\n'
    return full

# gerar código C para uma ação
def gen_act(act):
    t = act[0]
    if t == 'execute':
        action = act[1]
        dev = act[2]
        if action == 'ligar':
            return f'ligar("{dev}");'
        else:
            return f'desligar("{dev}");'
    if t == 'alerta':
        dev = act[1]
        msg = act[2]
        obs = act[3]
        if obs:
            return f'alerta_obs("{dev}", "{msg}", {obs});'
        else:
            return f'alerta("{dev}", "{msg}");'
    if t == 'difundir':
        msg = act[1]
        devs = act[2]
        code = ''
        for d in devs:
            code += f'alerta("{d}", "{msg}"); '
        return code
    raise ValueError('Ação inválida')