"""
Gerador de código C a partir da AST do ObsAct
"""
import os
from parser.obsact_parser import (
    Program, DeviceSection, Device, CommandList, 
    Assignment, ObsAction, Condition, ExecuteAction, 
    AlertAction, BroadcastAction
)

class CCodeGenerator:
    def __init__(self):
        self.variables = {}  # Armazena variáveis definidas
        self.indent_level = 0
        
    def indent(self):
        """Retorna a indentação atual"""
        return "    " * self.indent_level
    
    def generate(self, ast):
        """Gera código C a partir da AST"""
        if not isinstance(ast, Program):
            raise ValueError("AST deve ser um Program")
        
        # Processa dispositivos
        devices = self.process_devices(ast.dev_sec)
        
        # Processa comandos
        main_code = self.process_commands(ast.cmd_sec)
        
        # Gera variáveis globais
        variables_code = self.generate_variables()
        
        # Carrega template
        template_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 'templates', 'template.c'
        )
        with open(template_path, 'r') as f:
            template = f.read()
        
        # Substitui placeholders
        code = template.replace('{VARIABLES}', variables_code)
        code = code.replace('{MAIN_CODE}', main_code)
        
        return code
    
    def process_devices(self, dev_sec):
        """Processa a seção de dispositivos"""
        devices = []
        for dev in dev_sec.dev_list:
            if dev.sensor:
                # Dispositivo com sensor: registra a variável do sensor
                self.variables[dev.sensor] = 0
            devices.append(dev.name)
        return devices
    
    def generate_variables(self):
        """Gera declarações de variáveis globais"""
        if not self.variables:
            return "// Nenhuma variável declarada"
        
        lines = []
        for var_name in self.variables:
            lines.append(f"int {var_name} = 0;")
        return "\n".join(lines)
    
    def process_commands(self, cmd_sec):
        """Processa a lista de comandos"""
        lines = []
        self.indent_level = 1  # Dentro do main
        
        for cmd in cmd_sec.commands:
            code = self.process_command(cmd)
            if code:
                lines.append(code)
        
        return "\n".join(lines)
    
    def process_command(self, cmd):
        """Processa um comando individual"""
        if isinstance(cmd, Assignment):
            return self.generate_assignment(cmd)
        elif isinstance(cmd, ObsAction):
            return self.generate_obsaction(cmd)
        elif isinstance(cmd, ExecuteAction):
            return self.generate_execute(cmd)
        elif isinstance(cmd, AlertAction):
            return self.generate_alert(cmd)
        elif isinstance(cmd, BroadcastAction):
            return self.generate_broadcast(cmd)
        else:
            return f"{self.indent()}// Comando não reconhecido"
    
    def generate_assignment(self, assign):
        """Gera código para atribuição"""
        var_name = assign.var_name
        value = assign.value
        
        # Registra variável
        self.variables[var_name] = value
        
        return f"{self.indent()}{var_name} = {self.format_value(value)};"
    
    def format_value(self, value):
        """Formata um valor (número ou booleano)"""
        if isinstance(value, bool):
            return "1" if value else "0"
        return str(value)
    
    def generate_obsaction(self, obsact):
        """Gera código para quando...senao"""
        lines = []
        
        # Gera condição
        condition = self.generate_condition(obsact.condition)
        lines.append(f"{self.indent()}if ({condition}) {{")
        
        # Gera ação then
        self.indent_level += 1
        action_code = self.process_command(obsact.action)
        lines.append(action_code)
        self.indent_level -= 1
        
        # Gera ação else (se existir)
        if obsact.else_action:
            lines.append(f"{self.indent()}}} else {{")
            self.indent_level += 1
            else_code = self.process_command(obsact.else_action)
            lines.append(else_code)
            self.indent_level -= 1
        
        lines.append(f"{self.indent()}}}")
        
        return "\n".join(lines)
    
    def generate_condition(self, cond):
        """Gera código para condição lógica"""
        if not isinstance(cond, Condition):
            return "1"  # true
        
        # Condição simples
        left = cond.var_name
        op = self.convert_operator(cond.operator)
        right = self.format_value(cond.value)
        
        result = f"{left} {op} {right}"
        
        # Se tem próxima condição (AND)
        if cond.next_cond:
            next_cond = self.generate_condition(cond.next_cond)
            result = f"({result}) && ({next_cond})"
        
        return result
    
    def convert_operator(self, op):
        """Converte operador ObsAct para C"""
        return op  # Os operadores são os mesmos
    
    def generate_execute(self, exec_action):
        """Gera código para execute ligar/desligar"""
        action = exec_action.action_type.lower()
        device = exec_action.device
        
        return f'{self.indent()}{action}("{device}");'
    
    def generate_alert(self, alert_action):
        """Gera código para alerta"""
        device = alert_action.device
        msg = alert_action.message
        var_name = alert_action.var_name
        
        if var_name:
            # alerta com variável
            return f'{self.indent()}alerta_com_var("{device}", "{msg}", {var_name});'
        else:
            # alerta simples
            return f'{self.indent()}alerta("{device}", "{msg}");'
    
    def generate_broadcast(self, broadcast_action):
        """Gera código para difundir"""
        lines = []
        msg = broadcast_action.message
        var_name = broadcast_action.var_name
        devices = broadcast_action.device_list
        
        # Para cada dispositivo na lista
        for device in devices:
            if var_name:
                lines.append(
                    f'{self.indent()}alerta_com_var("{device}", "{msg}", {var_name});'
                )
            else:
                lines.append(
                    f'{self.indent()}alerta("{device}", "{msg}");'
                )
        
        return "\n".join(lines)

def generate_c_code(ast):
    """Função auxiliar para gerar código C"""
    generator = CCodeGenerator()
    return generator.generate(ast)

if __name__ == '__main__':
    # Teste básico
    from parser.obsact_parser import parse_program
    
    test_code = '''
    dispositivos:
        Lampada
        Sensor[temperatura]
    fimdispositivos
    
    def temperatura = 25;
    quando temperatura > 30: execute ligar em Lampada;
    '''
    
    ast = parse_program(test_code)
    if ast:
        c_code = generate_c_code(ast)
        print("=== CÓDIGO C GERADO ===")
        print(c_code)
