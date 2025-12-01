# Compilador ObsAct para C

Compilador para a linguagem ObsAct que gera código C.

## Estrutura do Projeto

```
compilador/
├── lexico/              # Analisador Léxico
├── parser/              # Analisador Sintático
├── codegen/             # Gerador de código C
├── templates/           # Template C
├── tests/               # Exemplos de teste
├── main.py              # Compilador principal
└── requirements.txt     # Dependências
```

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

### Compilar um programa ObsAct

```bash
python main.py programa.obsact [-o saida.c]
```

### Compilar e executar

```bash
python main.py programa.obsact -o output.c
gcc output.c -o output
./output
```

### Compilar todos os exemplos

```bash
python compile_all.py
```

## Componentes Implementados

### 1. Analisador Léxico (lexico/obsact_lexer.py)

Implementado usando PLY (Python Lex-Yacc). Reconhece os seguintes tokens:

- **Palavras reservadas**: `dispositivos`, `fimdispositivos`, `def`, `quando`, `senao`, `execute`, `em`, `alerta`, `para`, `difundir`, `ligar`, `desligar`, `TRUE`, `FALSE`, `AND`
- **Identificadores**: 
  - `ID_OBS`: começa com letra, pode conter números
  - `ID_DEV_ICE`: apenas letras
- **Números**: `NUM` (inteiros não negativos)
- **Operadores lógicos**: `>`, `<`, `>=`, `<=`, `==`, `!=`
- **Mensagens**: strings entre aspas duplas (máx 100 caracteres)
- **Símbolos**: `:`, `;`, `,`, `[`, `]`, `=`, `->`
- **Comentários**: `//` (linha única)

### 2. Analisador Sintático (parser/obsact_parser.py)

Implementado usando PLY com método LALR(1). Implementa a gramática completa da linguagem ObsAct:

- Seção de dispositivos
- Definições de variáveis (def)
- Comandos ObsAct (quando...senao)
- Ações: execute, alerta, difundir
- Condições lógicas com operadores e AND
- Valores booleanos e numéricos

### 3. AST (Abstract Syntax Tree)

O parser gera uma árvore sintática abstrata com as seguintes classes:

- `Program`: nó raiz
- `DeviceSection`: seção de dispositivos
- `Device`: dispositivo individual
- `CommandList`: lista de comandos
- `Assignment`: atribuição de variável
- `ObsAction`: comando quando...senao
- `Condition`: condição lógica
- `ExecuteAction`: ação execute
- `AlertAction`: ação alerta
- `BroadcastAction`: ação difundir

## Testes

### Testar o Lexer

```python
from lexico.obsact_lexer import test_lexer

with open('teste_simples.obsact', 'r') as f:
    code = f.read()

test_lexer(code)
```

### Testar o Parser

```python
from parser.obsact_parser import parse_program

with open('teste_simples.obsact', 'r') as f:
    code = f.read()

result = parse_program(code)
if result:
    print("✓ Análise sintática concluída com sucesso!")
```

## Exemplo de Código ObsAct

```obsact
dispositivos:
    Lampada
    Sensor[temperatura]
fimdispositivos

def temperatura = 25;
quando temperatura > 30: execute ligar em Lampada;
```

## Próximos Passos

- [ ] Implementar geração de código C
- [ ] Implementar análise semântica
- [ ] Adicionar mais testes
- [ ] Tratar concatenação de mensagens
- [ ] Implementar difusão de mensagens

## Gramática Implementada

```
PROGRAM     → DEV_SEC CMD_SEC
DEV_SEC     → dispositivos : DEV_LIST fimdispositivos
DEV_LIST    → DEV_ICE DEV_LIST | DEV_ICE
DEV_ICE     → ID_DEV_ICE | ID_DEV_ICE [ID_OBS]
CMD_SEC     → CMD_LIST
CMD_LIST    → CMD; CMD_LIST | CMD;
CMD         → ATTRIB | OBSACT | ACT
ATTRIB      → def ID_OBS = VAL
OBSACT      → quando OBS : ACT | quando OBS : ACT senao ACT
OBS         → ID_OBS OP_LOGIC VAL | ID_OBS OP_LOGIC VAL AND OBS
VAL         → NUM | BOOL
ACT         → execute ACTION em ID_DEV_ICE
            | alerta para ID_DEV_ICE : MSG
            | alerta para ID_DEV_ICE : MSG , ID_OBS
            | difundir : MSG -> [DEV_LIST_N]
            | difundir : MSG ID_OBS -> [DEV_LIST_N]
ACTION      → ligar | desligar
DEV_LIST_N  → ID_DEV_ICE | ID_DEV_ICE , DEV_LIST_N
```
