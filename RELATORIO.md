# Relatório do Trabalho - Compilador ObsAct

## 0. Integrantes do trabalho
1. Julia Kymie - 2421312
2. Gabriel Emile - 2220498

## 1. Descrição do Trabalho

Este trabalho implementa um compilador completo para a linguagem ObsAct. O compilador é composto por três componentes principais:

1. **Analisador Léxico (Lexer)** - `lexer.py`
2. **Analisador Sintático (Parser)** - `parser.py`
3. **Gerador de Código C** - `gera_cod.py`

O programa principal `main.py` integra esses componentes, lendo arquivos `.obsact`, realizando a análise léxica e sintática, e gerando código C executável.

## 2. Implementação de cada componente

### 2.1 Analisador Léxico (`lexer.py`)

Implementado utilizando PLY (Python Lex-Yacc), o lexer reconhece os seguintes tokens:

**Palavras-chave:**
- `def`, `quando`, `senao`
- `dispositivos`, `fimdispositivos`
- `execute`, `em`, `alerta`, `para`, `difundir`
- `ligar`, `desligar`
- `true`, `false`
- `AND`

**Tokens especiais:**
- `ID_DEV`: Identificadores de dispositivos
- `ID_OBS`: Identificadores de observáveis
- `NUM`: Números inteiros
- `MSG`: Strings entre aspas duplas
- `OP_LOGIC`: Operadores de comparação (`==`, `!=`, `>=`, `<=`, `>`, `<`)
- `EQ`: Operador de atribuição (`=`)
- Símbolos: `,`, `:`, `->`, `;`, `[`, `]`
- **Operadores aritméticos:** `+`, `-`, `*`, `/`
- **Parênteses:** `(`, `)`

### 2.2 Analisador Sintático (`parser.py`)

Implementado com PLY-Yacc, o parser constrói uma Árvore Sintática Abstrata (AST) representada por dicionários e tuplas Python.

**Estrutura da AST:**
```python
{
    'devices': [(id_dev, id_obs), ...],
    'cmds': {
        'defs': [(id_obs, val), ...],
        'cmds': [comando, ...]
    }
}
```

**Tipos de comandos na AST:**
- `('def', id_obs, val)` - Atribuição
- `('quando', obs, act, else_act)` - Comando condicional
- `('execute', action, dev)` - Ação direta
- `('alerta', dev, msg, obs)` - Alerta
- `('difundir', msg, devs)` - Difusão de mensagem

### 2.3 Gerador de Código C (`gera_cod.py`)

Gera código C completo e executável a partir da AST. 

**Funcionalidades implementadas:**
- Declaração de variáveis inteiras para todos os observáveis criados
- Inicialização de variáveis simples e expressões complexas no início do `main()`
- Geração de funções auxiliares obrigatórias para ações (ligar, desligar, alerta)
- Tradução de expressões lógicas com operadores `AND`
- **Criação de expressões aritméticas (+, -, *, /) com precedência correta**
- **Uso de parênteses para garantir precedência**

**Funções C geradas:**
```c
void ligar(char* dev);
void desligar(char* dev);
void alerta(char* dev, char* msg);
void alerta_obs(char* dev, char* msg, int obs_val);
```

## 3. Gramática Final

### 3.1 Gramática Implementada

```
PROGRAM → DEV_SEC CMD_SEC
DEV_SEC → dispositivos : DEV_LIST fimdispositivos
DEV_LIST → DEV_ITEM | DEV_LIST DEV_ITEM
DEV_ITEM → ID_DEV | ID_DEV [ ID_OBS ]
CMD_SEC → ε | CMD_LIST
CMD_LIST → CMD ; | CMD_LIST CMD ;
CMD → ATTR | OBSACT | ACT
ATTR → def ID_OBS = VAL
OBSACT → quando OBS : ACT | quando OBS : ACT senao ACT
OBS → SIMPLE_OBS | SIMPLE_OBS AND OBS
SIMPLE_OBS → EXPR OP_LOGIC EXPR
VAL → EXPR
EXPR → EXPR + TERM | EXPR - TERM | TERM
TERM → TERM * FACTOR | TERM / FACTOR | FACTOR
FACTOR → NUM | BOOL | ID_OBS | ( EXPR )
ACT → execute ACTION em ID_DEV | alerta para ID_DEV : MSG | alerta para ID_DEV : MSG , ID_OBS | difundir : MSG -> [ DEV_LIST_N ] | difundir : MSG ID_OBS -> [ DEV_LIST_N ]
ACTION → ligar | desligar
DEV_LIST_N → ID_DEV | DEV_LIST_N , ID_DEV
```

### 3.2 Alterações em Relação à Gramática Original

#### **Mudanças de nomenclatura:**
- `ID_DEVICE` → `ID_DEV` (simplificação)
- `DEVICE` → `DEV_ITEM` (clareza semântica)

#### **Regras adicionadas:**

1. **CMD_SEC → ε (vazio)**
   - Permite programas sem comandos (apenas declaração de dispositivos)
   - Aumenta a flexibilidade da linguagem

2. **DEV_LIST_N recursão à esquerda**
   - Alterada de `ID_DEV | ID_DEV , DEV_LIST_N` 
   - Para: `ID_DEV | DEV_LIST_N , ID_DEV`
   - Melhora a construção da lista na pilha do parser

3. **SIMPLE_OBS → EXPR OP_LOGIC EXPR**
   - Alterada de `ID_OBS OP_LOGIC VAL`
   - Permite expressões aritméticas em ambos os lados da comparação
   - Exemplos: `temperatura + 5 > 30`, `(x + y) * 2 == z`

4. **VAL → EXPR**
   - Alterada de `VAL → NUM | BOOL`
   - Permite atribuições com expressões complexas
   - Exemplo: `def limite = temperatura + adicional;`

5. **Novas regras para expressões aritméticas:**
   ```
   EXPR → EXPR + TERM | EXPR - TERM | TERM
   TERM → TERM * FACTOR | TERM / FACTOR | FACTOR
   FACTOR → NUM | BOOL | ID_OBS | ( EXPR )
   ```
   - Implementa precedência de operadores (multiplicação/divisão antes de soma/subtração)
   - Suporta parênteses para alterar precedência
   - Permite referências a variáveis em expressões: `temperatura + 10`
   - Suporta números literais e booleanos como fatores

## 4. Testes Realizados

### 4.1 Testes usados

- Foram utilizados **18 exemplos** de teste (`ex1.obsact` a `ex16.obsact` + exemplos de aritmética) cobrindo:
- A pasta Exemplos possui no total 24 testes, entre eles:
    1. Entre 1 a 8: Testes apresentadas no enunciado
    2. Entre 9 a 16: Testes criados por nós
    3. Entre 17 a 24: Testes criados para nova funcionalidade (Expressões aritméticas)

### 4.2 Como testamos

1. **Análise Léxica:** Executar `python lexer.py` para validar o lexer
2. **Análise Sintática:** Executar `python parser.py` para validar o parser
3. **Geração de Código:** Executar `python main.py exemplos/exN.obsact` para criar código em C
4. **Compilação:** Executar `gcc -Wall -o exN exemplos/exN.c` e `./exN` para verificar o código em C criado

### 4.3 Resultados

**100% de sucesso em todos os testes!**
- 18/18 arquivos parseados corretamente
- 18/18 códigos C gerados sem erros
- 18/18 compilações bem-sucedidas (sem warnings)
- 18/18 execuções completadas sem erros de runtime

## 5. Funcionalidades adicionais

1. **Modo de teste automático:**
   - `python lexer.py` testa todos os exemplos automaticamente
   - `python parser.py` testa todos os exemplos automaticamente
   - Relatórios formatados com ✓/✗ para cada teste

2. **Suporte completo a expressões aritméticas:**
   - Operadores: `+`, `-`, `*`, `/`
   - Precedência de operadores respeitada (*, / antes de +, -)
   - Parênteses para controle de precedência
   - Expressões podem ser usadas em:
     - Atribuições: `def x = a + b * c;`
     - Condições: `quando (temperatura + 5) * 2 > limite`
     - Referências a variáveis: `def resultado = x + y - z;`
   - Geração otimizada de código C com parênteses para garantir precedência

3. **Gerenciamento de variáveis:**
   - Variáveis com valores constantes são declaradas globalmente
   - Variáveis com expressões complexas são declaradas globalmente e inicializadas no `main()`
   - Variáveis não definidas mas usadas são automaticamente inicializadas com 0

## 8. Como Executar

```bash
# Gerar código C
python main.py exemplos/ex1.obsact

# Compilar e executar
gcc -o ex1 exemplos/ex1.c
./ex1
```

### 9. Estrutura de Arquivos

```
INF1022/
├── lexer.py          # Analisador léxico
├── parser.py         # Analisador sintático
├── gera_cod.py       # Gerador de código C
├── main.py           # Programa principal
├── README.md         # Documentação da gramática
└── exemplos/         # Arquivos de teste
    ├── ex1.obsact
    ├── ex2.obsact
    └── ...
```
