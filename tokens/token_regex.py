REGEX_TOKENS = [
    ("TIPO", r'\b(inteiro|booleano)\b'),
    ("PALAVRA_CHAVE", r'\b(programa|var|funcao|print|retorno|break|continue)\b'),
    ("CONDICIONAL", r'\b(se|senao|enquanto)\b'),
    ("IDENTIFICADOR", r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
    ("OPERADOR_RELACIONAL", r'(==|!=|>=|<=|>|<)'),
    ("OPERADOR_ARITMETICO", r'[+\-*/=]'),
    ("DELIMITADOR", r'[;:{}().,]'),
    ("NUMERO", r'\b\d+\b'),
    ("ESPACO", r'[ \t]+'),
    ("NOVA_LINHA", r'\n'),
]