# Este arquivo define uma lista chamada REGEX_TOKENS, que contém as regras para identificar os diferentes tipos de tokens no código-fonte.
REGEX_TOKENS = [ 
    
    # Cada elemento da lista é uma tupla com: tipo, regex(uma expressão regular que identifica os padrões válidos para aquele tipo de token).
    ("TIPO", r'\b(inteiro|booleano)\b'),
    ("PALAVRA_CHAVE", r'\b(programa|var|funcao|print|retorno|break|continue)\b'),
    ("CONDICIONAL", r'\b(se|senao|enquanto)\b'),
    ("BOOLEANO", r'\b(true|false)\b'),
    ("IDENTIFICADOR", r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
    ("OPERADOR_RELACIONAL", r'(==|!=|>=|<=|>|<)'),
    ("OPERADOR_ARITMETICO", r'[+\-*/=]'),
    ("DELIMITADOR", r'[;:{}().,]'),
    ("NUMERO", r'\b\d+\b'),
    ("ESPACO", r'[ \t]+'),
    ("NOVA_LINHA", r'\n'),
]