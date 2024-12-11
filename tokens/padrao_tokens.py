REGEX_TOKENS = [
    ("PALAVRA_CHAVE", r'\b(programa|var|inteiro|booleano|funcao|se|senao|enquanto|retorno|break|continue|print)\b'),
    ("IDENTIFICADOR", r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),
    ("NUMERO", r'\b\d+\b'),
    ("OPERADOR", r'[+\-*/]'),
    ("OPERADOR_RELACIONAL", r'(==|!=|>=|<=|>|<)'),
    ("DELIMITADOR", r'[;:{}().,=]'),
    ("ESPACO", r'[ \t]+'),
    ("NOVA_LINHA", r'\n'),
]