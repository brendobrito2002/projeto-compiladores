# A classe Token é um modelo de dados que representa os tokens gerados durante a análise léxica.
class Token:
    
    # __init__ é o método construtor da classe Token. Ele define os atributos de um token: tipo, valor, linha
    def __init__(self, tipo, valor, linha):
        self.tipo = tipo
        self.valor = valor
        self.linha = linha

    # __repr__ é um método que retorna uma representação textual legível do objeto.
    def __repr__(self):
        return f"Token({self.tipo}, {self.valor}, Linha: {self.linha})"