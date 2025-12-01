# ObsActTranspiler

ObsActTranspiler is a command-line tool that parses programs written in the ObsAct domain-specific language and translates them into equivalent C code. It implements a lexer and parser using PLY (Python Lex-Yacc) following the official grammar specification from the INF1022 course assignment.

## Objective

The objective of this project is to demonstrate the implementation of a compiler front-end for the ObsAct DSL. Key goals include:

* Implementing the official ObsAct grammar as specified in the course assignment
* Building a lexer and LALR(1) parser with PLY
* Generating readable, idiomatic C code that reflects ObsAct semantics
* Supporting all 8 mandatory examples from the specification
* Proper handling of device declarations, observations, conditions, and actions

## Prerequisites

* Python 3.6 or higher
* [PLY library](https://www.dabeaz.com/ply/) version 3.11+

Install dependencies:

```bash
pip install -r req.txt
```

## Usage Tutorial

1. **Install dependencies**

   ```bash
   pip install ply
   ```

2. **Run the transpiler**

   ```bash
   python main.py <input_file.obsact> <output_file.c>
   ```

   - `<input_file.obsact>`: path to your ObsAct source file  
   - `<output_file.c>`: target C file to generate

   **Example:**

   ```bash
   python main.py tests/exemplo1_oficial.obsact saida_exemplo1.c
   ```

3. **Compile and execute the generated C code**

   ```bash
   gcc saida_exemplo1.c -o exemplo1
   ./exemplo1
   ```

## Grammar Specification

The ObsAct grammar follows the official specification from INF1022 2025.2:

```
PROGRAM → DEV_SEC CMD_SEC

DEV_SEC → dispositivos : DEV_LIST fimdispositivos

DEV_LIST → DEV_ICE DEV_LIST 
         | DEV_ICE

DEV_ICE → ID_DEV_ICE 
        | ID_DEV_ICE [ ID_OBS ]

CMD_SEC → CMD_LIST

CMD_LIST → CMD ; CMD_LIST 
         | CMD ;

CMD → ATTRIB 
    | OBSACT 
    | ACT

ATTRIB → def ID_OBS = VAL

OBSACT → quando OBS : ACT
       | quando OBS : ACT senao ACT

OBS → ID_OBS OPLOGIC VAL
    | ID_OBS OPLOGIC VAL AND OBS

VAL → NUM 
    | BOOL

ACT → execute ACTION em ID_DEV_ICE
    | alerta para ID_DEV_ICE : MSG
    | alerta para ID_DEV_ICE : MSG , ID_OBS
    | difundir : MSG -> [ DEV_LIST_N ]
    | difundir : MSG ID_OBS -> [ DEV_LIST_N ]

ACTION → ligar 
       | desligar

DEV_LIST_N → ID_DEV_ICE 
           | ID_DEV_ICE , DEV_LIST_N
```

### Terminals:
- **NUM**: Non-negative integers `[0-9]+`
- **BOOL**: `TRUE` or `FALSE` (uppercase)
- **ID_OBS**: Alphanumeric identifiers starting with a letter `[A-Za-z][A-Za-z0-9]*`
- **ID_DEV_ICE**: Alphabetic-only identifiers `[A-Za-z]+`
- **MSG**: String literals up to 100 characters `"[^"]{0,100}"`
- **OPLOGIC**: Comparison operators `>`, `<`, `>=`, `<=`, `==`, `!=`
- **AND**: Logical AND operator (keyword)
- **Keywords**: `dispositivos`, `fimdispositivos`, `def`, `quando`, `senao`, `execute`, `ligar`, `desligar`, `alerta`, `para`, `difundir`, `em`
- **Symbols**: `:`, `;`, `,`, `[`, `]`, `->`, `=`

## Mandatory Test Cases

The parser correctly accepts all 8 mandatory examples from the specification:

### Example 1: Basic conditional with execute
```obsact
dispositivos:
Termometro[temperatura]
Ventilador[potencia]
fimdispositivos
def temperatura = 40;
def potencia = 90;
quando temperatura > 30 : execute ligar em Ventilador;
```

### Example 2: Broadcast with variable
```obsact
dispositivos:
Monitor
Celular
Termometro[temperatura]
fimdispositivos
quando temperatura > 30 :
difundir: "Temperatura em " temperatura -> [Monitor , Celular];
```

### Example 3: Multiple conditions with senao
```obsact
dispositivos:
Monitor
Celular[movimento]
Higrometro[umidade]
Lampada[potencia]
fimdispositivos
def potencia = 100 ;
quando umidade < 40 : alerta para Monitor: "Ar seco detectado" ;
quando movimento == TRUE : execute ligar em Lampada senao execute desligar em Lampada ;
```

### Example 4: Simple alert
```obsact
dispositivos:
Monitor
Higrometro[umidade]
fimdispositivos
quando umidade < 40 : alerta para Monitor: "Ar seco detectado" ;
```

### Example 5: Direct action with assignment
```obsact
dispositivos:
Lampada[potencia]
fimdispositivos
def potencia = 100;
execute ligar em Lampada;
```

### Example 6: Direct desligar action
```obsact
dispositivos:
Ventilador
fimdispositivos
execute desligar em Ventilador ;
```

### Example 7: Simple alert without condition
```obsact
dispositivos:
Celular
fimdispositivos
alerta para Celular: "Hora de acordar !" ;
```

### Example 8: Alert with variable concatenation
```obsact
dispositivos:
Termometro[temperatura]
fimdispositivos
alerta para Termometro: "Temperatura esta em", temperatura ;
```

## Generated C Runtime

The compiler generates C code with the following runtime functions:

```c
void ligar(const char* dev) { 
    printf("%s ligado !\n", dev); 
}

void desligar(const char* dev) { 
    printf("%s desligado !\n", dev); 
}

void alerta(const char* dev, const char* msg) {
    printf("%s recebeu o alerta :\n", dev);
    printf("%s\n", msg);
}

void alerta_var(const char* dev, const char* msg, int var) {
    printf("%s recebeu o alerta :\n", dev);
    printf("%s %d\n", msg, var);
}
```

### Semantic Rules:
1. All numeric variables are non-negative integers
2. Undefined observations default to value 0
3. Message concatenation: `MSG + space + variable_value`
4. Boolean `TRUE` = 1, `FALSE` = 0 in generated C code

## Project Structure

```
ObsActTranspiler/
├── main.py                           # Entry point and CLI
├── lexico/
│   └── obsact_lexer.py              # Lexical analyzer (tokenizer)
├── parser/
│   └── obsact_parser.py             # Syntax analyzer and code generator
├── tests/
│   ├── exemplo1_oficial.obsact      # Mandatory example 1
│   ├── exemplo2_oficial.obsact      # Mandatory example 2
│   ├── exemplo3_oficial.obsact      # Mandatory example 3
│   ├── exemplo4_oficial.obsact      # Mandatory example 4
│   ├── exemplo5_oficial.obsact      # Mandatory example 5
│   ├── exemplo6_oficial.obsact      # Mandatory example 6
│   ├── exemplo7_oficial.obsact      # Mandatory example 7
│   └── exemplo8_oficial.obsact      # Mandatory example 8
├── req.txt                          # Python dependencies
└── README.md                        # This file
```

## Implementation Notes

### Lexer (`obsact_lexer.py`)
- Implements all terminals from the official grammar
- Validates message length (max 100 characters)
- Distinguishes between ID_DEV_ICE (letters only) and ID_OBS (alphanumeric)
- Recognizes all keywords and operators

### Parser (`obsact_parser.py`)
- LALR(1) parser generated by PLY
- Implements the complete official grammar
- Generates structured C code with proper indentation
- Handles all command types: assignments, conditionals, actions, broadcasts
- Supports nested conditions with AND operator
- Implements proper variable scoping and initialization

### Code Generation
- Variables declared at start of main() and initialized to 0
- Conditional logic translated to C if/else statements
- Actions translated to function calls
- Broadcasts expanded to multiple function calls
- Proper string escaping and formatting

## Testing

Run all mandatory examples:

```bash
# Test all 8 examples
python main.py tests/exemplo1_oficial.obsact saida_exemplo1.c
python main.py tests/exemplo2_oficial.obsact saida_exemplo2.c
python main.py tests/exemplo3_oficial.obsact saida_exemplo3.c
python main.py tests/exemplo4_oficial.obsact saida_exemplo4.c
python main.py tests/exemplo5_oficial.obsact saida_exemplo5.c
python main.py tests/exemplo6_oficial.obsact saida_exemplo6.c
python main.py tests/exemplo7_oficial.obsact saida_exemplo7.c
python main.py tests/exemplo8_oficial.obsact saida_exemplo8.c

# Validate with simulation script
python teste_validacao.py
```
