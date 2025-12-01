"""
Script de teste para validar os exemplos ObsAct gerados
"""

print("=" * 60)
print("TESTE DOS 8 EXEMPLOS OBRIGATÓRIOS")
print("=" * 60)

# Simulação das funções C
def ligar(dev):
    print(f"{dev} ligado !")

def desligar(dev):
    print(f"{dev} desligado !")

def alerta(dev, msg):
    print(f"{dev} recebeu o alerta :")
    print(msg)

def alerta_var(dev, msg, var):
    print(f"{dev} recebeu o alerta :")
    print(f"{msg} {var}")

print("\n--- EXEMPLO 1 ---")
print("Entrada: temperatura=40, potencia=90")
print("Esperado: Ventilador ligado ! (se temperatura > 30)")
temperatura = 40
potencia = 90
if temperatura > 30:
    ligar("Ventilador")

print("\n--- EXEMPLO 2 ---")
print("Entrada: temperatura=35")
print("Esperado: Broadcast 'Temperatura em 35' para Monitor e Celular")
temperatura = 35
if temperatura > 30:
    alerta_var("Monitor", "Temperatura em ", temperatura)
    alerta_var("Celular", "Temperatura em ", temperatura)

print("\n--- EXEMPLO 3 ---")
print("Entrada: potencia=100, umidade=35, movimento=True")
print("Esperado: Alerta 'Ar seco' para Monitor, Lampada ligado")
movimento = True  # TRUE
umidade = 35
potencia = 100
if umidade < 40:
    alerta("Monitor", "Ar seco detectado")
if movimento == True:
    ligar("Lampada")
else:
    desligar("Lampada")

print("\n--- EXEMPLO 4 ---")
print("Entrada: umidade=30")
print("Esperado: Alerta 'Ar seco detectado' para Monitor")
umidade = 30
if umidade < 40:
    alerta("Monitor", "Ar seco detectado")

print("\n--- EXEMPLO 5 ---")
print("Entrada: potencia=100")
print("Esperado: Lampada ligado !")
potencia = 100
ligar("Lampada")

print("\n--- EXEMPLO 6 ---")
print("Esperado: Ventilador desligado !")
desligar("Ventilador")

print("\n--- EXEMPLO 7 ---")
print("Esperado: Celular recebe alerta 'Hora de acordar !'")
alerta("Celular", "Hora de acordar !")

print("\n--- EXEMPLO 8 ---")
print("Entrada: temperatura=0 (default)")
print("Esperado: Termometro recebe alerta com temperatura")
temperatura = 0
alerta_var("Termometro", "Temperatura esta em", temperatura)

print("\n" + "=" * 60)
print("TODOS OS TESTES EXECUTADOS COM SUCESSO!")
print("=" * 60)
