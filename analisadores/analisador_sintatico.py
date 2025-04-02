class AnalisadorSintatico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicao = 0
        self.token_atual = self.tokens[self.posicao] if self.tokens else None
        self.funcao_exige_retorno = False
        self.retorno_presente = False

    def avancar(self):
        """Avança para o próximo token."""
        self.posicao += 1
        if self.posicao < len(self.tokens):
            self.token_atual = self.tokens[self.posicao]
        else:
            self.token_atual = None

    def erro(self, mensagem):
        """Levanta erro sintático."""
        raise SyntaxError(f"Erro sintático na linha {self.token_atual.linha}: {mensagem} (Token: {self.token_atual.valor})")

    def validar(self, tipo_esperado, valor_esperado=None):
        """Verifica se o token atual é do tipo e valor esperados e avança."""
        if self.token_atual:
            if self.token_atual.tipo == tipo_esperado and (valor_esperado is None or self.token_atual.valor == valor_esperado):
                self.avancar()
            else:
                self.erro(f"Token esperado: {valor_esperado} (Tipo: {tipo_esperado}), encontrado: {self.token_atual.valor} (Tipo: {self.token_atual.tipo})")
        else:
            self.erro("Fim do arquivo inesperado.")

    def programa(self):
        """<programa> ::= 'programa' <bloco> ."""
        self.validar("PALAVRA_CHAVE", "programa")
        self.validar("IDENTIFICADOR")
        self.validar("DELIMITADOR", ";")
        self.bloco()
        self.validar("DELIMITADOR", ".")
        print("Análise Sintática concluída com sucesso!")

    def bloco(self):
        """<bloco> ::= '{' <declaracoes> <comandos> '}'"""
        self.validar("DELIMITADOR", "{")
        self.declaracoes_opicionais()
        self.comandos()
        self.validar("DELIMITADOR", "}")
    
    def declaracoes_opicionais(self):
        """<declaracoes_opcionais> ::= <declaracao> (";" <declaracao>)*"""
        while self.token_atual and self.token_atual.valor == "var" or self.token_atual.valor == "funcao":
            self.declaracao()
    
    def declaracao(self):
        """<declaracao> ::= <declaracao_variaveis> | <declaracao_funcao>"""
        if self.token_atual.tipo == "PALAVRA_CHAVE" and self.token_atual.valor == "var":
            self.declaracao_variavel()
            self.validar("DELIMITADOR", ";")
        elif self.token_atual.tipo == "PALAVRA_CHAVE" and self.token_atual.valor == "funcao":
            self.declaracao_funcao()
    
    def declaracao_variavel(self):
        """<declaracao_variaveis> ::= "var" <identificador> ":" <tipo>"""
        self.validar("PALAVRA_CHAVE", "var")
        self.validar("IDENTIFICADOR")
        self.validar("DELIMITADOR", ":")
        self.validar("TIPO")

    def declaracao_funcao(self):
        """<declaracao_funcao> ::= "funcao" <identificador> "(" <parametros_opcionais> ")" [ ":" <tipo> ] <bloco>"""
        self.validar("PALAVRA_CHAVE", "funcao")
        self.validar("IDENTIFICADOR")
        self.validar("DELIMITADOR", "(")
        self.parametros_opcionais()
        self.validar("DELIMITADOR", ")")
        
        self.funcao_exige_retorno = False
        if self.token_atual and self.token_atual.valor == ":":
            self.validar("DELIMITADOR", ":")
            self.tipo()
            self.funcao_exige_retorno = True 
        
        self.retorno_presente = False
        self.bloco()
        
        if self.funcao_exige_retorno and not self.retorno_presente:
            self.erro("Função declarada com tipo de retorno deve ter pelo menos um 'retorno'")


    def parametros_opcionais(self):
        """<parametros_opcionais> ::= <parametros> | """
        if self.token_atual and self.token_atual.tipo == "IDENTIFICADOR":
            self.parametros()
        
    def parametros(self):
        """<parametros> ::= <parametro> ("," <parametro>)*"""
        self.parametro()
        while self.token_atual and self.token_atual.tipo == "DELIMITADOR" and self.token_atual.valor == ",":
            self.avancar()
            self.parametro()

    def parametro(self):
        """<parametro> ::= <identificador> ":" <tipo>"""
        self.validar("IDENTIFICADOR")
        self.validar("DELIMITADOR", ":")
        self.tipo()

    def tipo(self):
        """<tipo> ::= "inteiro" | "booleano"""
        if self.token_atual.tipo == "TIPO":
            self.avancar()
        else:
            raise SyntaxError(f"Erro sintático: Esperado tipo, encontrado {self.token_atual.tipo} na linha {self.token_atual.linha}")
    
    def comandos(self):
        """<comandos> ::= <comando> (";" <comando>)*"""
        while self.token_atual and self.token_atual.tipo in ["IDENTIFICADOR", "PALAVRA_CHAVE", "CONDICIONAL"]:
            self.comando()

    
    def comando(self):
        """<comando> ::= <atribuicao> | <chamada_funcao> | <se> | <enquanto> | <comando_retorno> | <comando_desvio> | <comando_impressao>"""
        if self.token_atual.tipo == "IDENTIFICADOR":
            # Lookahead para diferenciar atribuição vs chamada
            if self.tokens[self.posicao + 1].valor == "(":
                self.chamada_funcao()
                self.validar("DELIMITADOR", ";")
            else:
                self.atribuicao()
        
        elif self.token_atual.valor == "se":
            self.se()
        
        elif self.token_atual.valor == "enquanto":
            self.enquanto()
        
        elif self.token_atual.valor == "retorno":
            self.retorno()
        
        elif self.token_atual.valor in ("break", "continue"):
            self.desvio()
        
        elif self.token_atual.valor == "print":
            self.imprimir()
        
        else:
            self.erro("Comando inválido")
    
    def atribuicao(self):
        """<atribuicao> ::= <identificador> "=" <expressao> ;"""
        self.validar("IDENTIFICADOR")
        self.validar("OPERADOR_ARITMETICO", "=")
        self.expressao()
        self.validar("DELIMITADOR", ";")

    def expressao(self):
        """<expressao> ::= <termo> <expressao_rec>"""
        self.termo()
        self.expressao_rec()

    def termo(self):
        """<termo> ::= <fator> <termo_rec>"""
        self.fator()
        self.termo_rec()

    def fator(self):
        """<fator> ::= <identificador> [ "(" <argumentos_opcionais> ")" ] | <numero> | "(" <expressao> ")" | <valor_booleano>"""
        if self.token_atual.tipo == "IDENTIFICADOR":
            self.avancar()
            if self.token_atual and self.token_atual.valor == "(":
                self.chamada_funcao()
        
        elif self.token_atual.tipo == "NUMERO":
            self.avancar()
        
        elif self.token_atual.tipo == "BOOLEANO":
            self.avancar()
        
        elif self.token_atual.valor == "(":
            self.avancar()
            self.expressao()
            self.validar("DELIMITADOR", ")")
        
        else:
            self.erro("Fator inválido")

    def termo_rec(self):
        """<termo_rec> ::= ("*" | "/") <fator> <termo_rec> | """
        if self.token_atual and self.token_atual.tipo == "OPERADOR_ARITMETICO" and self.token_atual.valor in ["*", "/"]:
            self.avancar()
            self.fator()
            self.termo_rec()

    def expressao_rec(self):
        """<expressao_rec> ::= ("+" | "-") <termo> <expressao_rec> | """
        if self.token_atual and self.token_atual.tipo == "OPERADOR_ARITMETICO" and self.token_atual.valor in ["+", "-"]:
            self.avancar()
            self.termo()
            self.expressao_rec()
    
    def chamada_funcao(self):
        """<chamada_funcao> ::= <identificador> "(" <argumentos_opcionais> ")"""     
        self.validar("DELIMITADOR", "(")
        self.argumentos_opcionais()  # Alterado para usar argumentos_opcionais
        self.validar("DELIMITADOR", ")")

    # FALTA ADICIONAR O PROCEDIMENTO(FUNÇÃO SEM RETORNO)

    def argumentos_opcionais(self):
        """<argumentos_opcionais> ::= <argumentos> | """
        # Verifica se há pelo menos um token que pode iniciar uma expressão
        if self.token_atual and self.token_atual.tipo in ["IDENTIFICADOR", "NUMERO", "DELIMITADOR", "BOOLEANO"]:
            if self.token_atual.tipo == "DELIMITADOR" and self.token_atual.valor != "(":
                return
            self.argumentos()
    
    def argumentos(self):
        """<argumentos> ::= <expressao> ("," <expressao>)*"""
        self.expressao()
        while self.token_atual and self.token_atual.tipo == "DELIMITADOR" and self.token_atual.valor == ",":
            self.avancar()
            self.expressao()

    def se(self):
        """<se> ::= "se" "(" <expressao_booleana> ")" <bloco> <senao_opcional>"""
        self.validar("CONDICIONAL", "se")
        self.validar("DELIMITADOR", "(")
        self.expressao_booleana()
        self.validar("DELIMITADOR", ")")
        self.bloco()
        self.senao_opcional()

    def expressao_booleana(self):
        """<expressao_booleana> ::= <expressao> <operador_relacional> <expressao> | <booleano>."""
        if self.token_atual.tipo == "BOOLEANO":
            self.avancar()
        else:
            self.expressao()
            if self.token_atual and self.token_atual.tipo == "OPERADOR_RELACIONAL":
                self.avancar()
                self.expressao()
        
        if self.token_atual and self.token_atual.valor == "(":
            self.argumentos()

    def senao_opcional(self):
        """<senao_opcional> ::= "senao" <bloco> | """
        if self.token_atual and self.token_atual.tipo == "CONDICIONAL" and self.token_atual.valor == "senao":
            self.avancar()
            self.bloco()

    def enquanto(self):
        """<enquanto> ::= "enquanto" "(" <expressao_booleana> ")" <bloco>"""
        self.validar("CONDICIONAL", "enquanto")
        self.validar("DELIMITADOR", "(")
        self.expressao_booleana()
        self.validar("DELIMITADOR", ")")
        self.bloco()

    def retorno(self):
        """<comando_retorno> ::= "retorno" <expressao_opcional> ;"""
        self.validar("PALAVRA_CHAVE", "retorno")
        self.expressao_opcional()
        self.validar("DELIMITADOR", ";")
        self.retorno_presente = True


    def expressao_opcional(self):
        """<expressao_opcional> ::= <expressao> | """
        if self.token_atual and self.token_atual.tipo in ["IDENTIFICADOR", "NUMERO", "DELIMITADOR", "BOOLEANO"]:
            self.expressao()

    def desvio(self):
        """<comando_desvio> ::= "break" | "continue"""
        if self.token_atual.valor == "continue":
            self.avancar()
            self.validar("DELIMITADOR", ";")
        elif self.token_atual.valor == "break":
            self.avancar()
            self.validar("DELIMITADOR", ";")

    def imprimir(self):
        """<comando_impressao> ::= "print" "(" <expressao> ")" """
        self.validar("PALAVRA_CHAVE", "print")
        self.validar("DELIMITADOR", "(")
        self.expressao()
        self.validar("DELIMITADOR", ")")
        self.validar("DELIMITADOR", ";")