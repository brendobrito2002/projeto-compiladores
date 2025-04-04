class AnalisadorSintatico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicao = 0
        self.token_atual = self.tokens[self.posicao] if self.tokens else None
        self.funcao_exige_retorno = False
        self.retorno_presente = False
        self.em_procedimento = False
        self.retorno_valido_encontrado = False

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
        self.validar("DELIMITADOR", "{")
        self.declaracoes_opcionais()
        garante_retorno = False
        while self.token_atual and self.token_atual.tipo in ["IDENTIFICADOR", "PALAVRA_CHAVE", "CONDICIONAL"]:
            garante_retorno = self.comando()
            if garante_retorno:
                break
            if self.token_atual and self.token_atual.valor == ";":
                self.avancar()
        self.validar("DELIMITADOR", "}")
        return garante_retorno
    
    def declaracoes_opcionais(self):
        """<declaracoes_opcionais> ::= (<declaracao> ";")*"""
        while self.token_atual and self.token_atual.valor in ["var", "funcao", "procedimento"]:
            self.declaracao()
            if self.token_atual and self.token_atual.valor == ";":
                self.avancar()

    def declaracao(self):
        """<declaracao> ::= <declaracao_variaveis> | <declaracao_funcao> | <declaracao_procedimento>"""
        if self.token_atual.valor == "var":
            self.declaracao_variavel()
            self.validar("DELIMITADOR", ";")
        elif self.token_atual.valor == "funcao":
            self.declaracao_funcao()
        elif self.token_atual.valor == "procedimento":
            self.declaracao_procedimento()
        else:
            self.erro("Declaração inválida")

    def declaracao_variavel(self):
        """<declaracao_variaveis> ::= "var" <identificador> ":" <tipo>"""
        self.validar("PALAVRA_CHAVE", "var")
        self.validar("IDENTIFICADOR")
        self.validar("DELIMITADOR", ":")
        self.validar("TIPO")

    def declaracao_funcao(self):
        self.validar("PALAVRA_CHAVE", "funcao")
        self.validar("IDENTIFICADOR")
        self.validar("DELIMITADOR", "(")
        self.parametros_opcionais()
        self.validar("DELIMITADOR", ")")
        
        tem_retorno = False
        if self.token_atual and self.token_atual.valor == ":":
            self.avancar()
            self.tipo()
            tem_retorno = True
        
        garante_retorno = self.bloco()
        
        if tem_retorno and not garante_retorno:
            self.erro("Função deve garantir retorno em todos os caminhos")

    def declaracao_procedimento(self):
        """<declaracao_procedimento> ::= "procedimento" <identificador> "(" <parametros_opcionais> ")" <bloco>"""
        self.validar("PALAVRA_CHAVE", "procedimento")
        self.validar("IDENTIFICADOR")
        self.validar("DELIMITADOR", "(")
        self.parametros_opcionais()
        self.validar("DELIMITADOR", ")")
        
        self.em_procedimento = True
        self.bloco()
        self.em_procedimento = False

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
        while self.token_atual and self.token_atual.tipo in ["IDENTIFICADOR", "PALAVRA_CHAVE", "CONDICIONAL"]:
            self.comando()
            if self.token_atual and self.token_atual.valor == ";":
                self.avancar()
    
    def comando(self):
        if self.token_atual.tipo == "IDENTIFICADOR":
            if self.tokens[self.posicao + 1].valor == "(":
                self.chamada_funcao()
                self.validar("DELIMITADOR", ";")
                return False
            else:
                self.atribuicao()
                return False
        elif self.token_atual.valor == "se":
            return self.se()
        elif self.token_atual.valor == "enquanto":
            self.enquanto()
            return False
        elif self.token_atual.valor == "retorno":
            self.retorno()
            return True
        elif self.token_atual.valor in ("break", "continue"):
            self.desvio()
            return False
        elif self.token_atual.valor == "print":
            self.imprimir()
            return False 
        else:
            self.erro("Comando inválido")
            return False
    
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
        if self.token_atual.tipo == "IDENTIFICADOR":
            if self.posicao + 1 < len(self.tokens) and self.tokens[self.posicao + 1].valor == "(":
                self.chamada_funcao()
            else:
                self.avancar() 
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
        self.validar("IDENTIFICADOR")
        self.validar("DELIMITADOR", "(")
        self.argumentos_opcionais()
        self.validar("DELIMITADOR", ")")


    def argumentos_opcionais(self):
        """<argumentos_opcionais> ::= <argumentos> | """
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
        self.validar("CONDICIONAL", "se")
        self.validar("DELIMITADOR", "(")
        self.expressao_booleana()
        self.validar("DELIMITADOR", ")")
        retorno_se = self.bloco()
        if self.token_atual and self.token_atual.valor == "senao":
            self.avancar()
            retorno_senao = self.bloco() 
            return retorno_se and retorno_senao 
        return False

    def expressao_booleana(self):
        if self.token_atual.tipo == "BOOLEANO":
            self.avancar()
        elif (self.token_atual.tipo == "IDENTIFICADOR" and 
            self.posicao + 1 < len(self.tokens) and 
            self.tokens[self.posicao + 1].valor == "("):
            self.chamada_funcao()
        else:
            self.expressao()
            if self.token_atual and self.token_atual.tipo == "OPERADOR_RELACIONAL":
                self.avancar()
                self.expressao()
            else:
                self.erro("Esperada uma expressão booleana válida")

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
        
        if self.token_atual.tipo not in ["DELIMITADOR", "PALAVRA_CHAVE"]:
            if self.em_procedimento:
                self.erro("Procedimento não pode ter retorno com valor")
            else:
                self.retorno_valido_encontrado = True
        elif not self.em_procedimento:
            self.erro("Função deve retornar um valor")
        
        self.expressao_opcional()
        self.validar("DELIMITADOR", ";")

    def verificar_sem_retorno(self):
        """Verifica se procedimentos não contêm retornos com valor"""
        if self.bloco_tem_retorno_com_valor():
            self.erro("Procedimento não pode conter 'retorno' com valor")


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