from analisadores.tabela.tabela_simbolos import TabelaDeSimbolos

class AnalisadorSintatico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicao = 0
        self.token_atual = self.tokens[self.posicao] if self.tokens else None
        self.em_procedimento = False
        self.tabela_simbolos = TabelaDeSimbolos()

    def avancar(self):
        self.posicao += 1
        if self.posicao < len(self.tokens):
            self.token_atual = self.tokens[self.posicao]
        else:
            self.token_atual = None

    def erro(self, mensagem):
        raise SyntaxError(f"Erro sintático na linha {self.token_atual.linha}: {mensagem} (Token: {self.token_atual.valor})")

    def validar(self, tipo_esperado, valor_esperado=None):
        if self.token_atual:
            if self.token_atual.tipo == tipo_esperado and (valor_esperado is None or self.token_atual.valor == valor_esperado):
                self.avancar()
            else:
                self.erro(f"Esperado: {valor_esperado} ({tipo_esperado}), encontrado: {self.token_atual.valor}")
        else:
            self.erro("Fim do arquivo inesperado")

    def programa(self):
        self.validar("PALAVRA_CHAVE", "programa")
        self.validar("IDENTIFICADOR")
        self.validar("DELIMITADOR", ";")
        self.bloco(is_global=True)
        self.validar("DELIMITADOR", ".")
        print("Análise Sintática concluída com sucesso!")
        self.tabela_simbolos.gerar_relatorio("analisadores/arquivos_gerados/tabela_simbolos.txt")

    def bloco(self, is_global=False):
        if not is_global:
            self.tabela_simbolos.entrar_escopo()
        self.validar("DELIMITADOR", "{")
        self.declaracoes_opcionais()
        while self.token_atual and self.token_atual.tipo in ["IDENTIFICADOR", "PALAVRA_CHAVE", "CONDICIONAL"]:
            self.comando()
            if self.token_atual and self.token_atual.valor == ";":
                self.avancar()
        self.validar("DELIMITADOR", "}")
        if not is_global:
            self.tabela_simbolos.sair_escopo()

    def declaracoes_opcionais(self):
        while self.token_atual and self.token_atual.valor in ["var", "funcao", "procedimento"]:
            self.declaracao()
            if self.token_atual and self.token_atual.valor == ";":
                self.avancar()

    def declaracao(self):
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
        self.validar("PALAVRA_CHAVE", "var")
        nome = self.token_atual.valor
        self.validar("IDENTIFICADOR")
        self.validar("DELIMITADOR", ":")
        tipo = self.token_atual.valor
        self.validar("TIPO")
        self.tabela_simbolos.adicionar(nome=nome, tipo=tipo, categoria='variavel')

    def declaracao_funcao(self):
        self.validar("PALAVRA_CHAVE", "funcao")
        nome_funcao = self.token_atual.valor
        self.validar("IDENTIFICADOR")

        # Parâmetros
        self.validar("DELIMITADOR", "(")
        parametros = []
        if self.token_atual.valor != ")":
            self.tabela_simbolos.entrar_escopo()
            while self.token_atual.valor != ")":
                param_nome = self.token_atual.valor
                self.validar("IDENTIFICADOR")
                self.validar("DELIMITADOR", ":")
                param_tipo = self.token_atual.valor
                self.validar("TIPO")
                self.tabela_simbolos.adicionar(nome=param_nome, tipo=param_tipo, categoria='parametro')
                parametros.append({'nome': param_nome, 'tipo': param_tipo})
                if self.token_atual.valor == ",":
                    self.avancar()
            self.tabela_simbolos.sair_escopo()
        self.validar("DELIMITADOR", ")")

        # Tipo de retorno
        tipo_retorno = 'void'
        if self.token_atual.valor == ":":
            self.avancar()
            tipo_retorno = self.token_atual.valor
            self.validar("TIPO")

        self.tabela_simbolos.adicionar(
            nome=nome_funcao,
            tipo=tipo_retorno,
            categoria='funcao',
            parametros=parametros
        )

        self.tabela_simbolos.entrar_escopo()
        self.bloco()
        self.tabela_simbolos.sair_escopo()

    def declaracao_procedimento(self):
        self.validar("PALAVRA_CHAVE", "procedimento")
        nome_procedimento = self.token_atual.valor
        self.validar("IDENTIFICADOR")

        # Parâmetros
        self.validar("DELIMITADOR", "(")
        parametros = []
        if self.token_atual.valor != ")":
            self.tabela_simbolos.entrar_escopo()
            while self.token_atual.valor != ")":
                param_nome = self.token_atual.valor
                self.validar("IDENTIFICADOR")
                self.validar("DELIMITADOR", ":")
                param_tipo = self.token_atual.valor
                self.validar("TIPO")
                self.tabela_simbolos.adicionar(nome=param_nome, tipo=param_tipo, categoria='parametro')
                parametros.append({'nome': param_nome, 'tipo': param_tipo})
                if self.token_atual.valor == ",":
                    self.avancar()
            self.tabela_simbolos.sair_escopo()
        self.validar("DELIMITADOR", ")")

        self.tabela_simbolos.adicionar(
            nome=nome_procedimento,
            tipo='void',
            categoria='procedimento',
            parametros=parametros
        )

        self.tabela_simbolos.entrar_escopo()
        self.em_procedimento = True
        self.bloco()
        self.em_procedimento = False
        self.tabela_simbolos.sair_escopo()

    def comando(self):
        if self.token_atual.tipo == "IDENTIFICADOR":
            if self.tokens[self.posicao + 1].valor == "(":
                self.chamada_funcao()
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
        if self.token_atual and self.token_atual.valor == ";":
            self.avancar()

    def atribuicao(self):
        self.validar("IDENTIFICADOR")
        self.validar("OPERADOR_ARITMETICO", "=")
        self.expressao()
        self.validar("DELIMITADOR", ";")

    def expressao(self):
        self.termo()
        self.expressao_rec()

    def termo(self):
        self.fator()
        self.termo_rec()

    def fator(self):
        if self.token_atual.tipo == "IDENTIFICADOR":
            if self.posicao + 1 < len(self.tokens) and self.tokens[self.posicao + 1].valor == "(":
                self.chamada_funcao()
            else:
                self.avancar()
        elif self.token_atual.tipo in ["NUMERO", "BOOLEANO"]:
            self.avancar()
        elif self.token_atual.valor == "(":
            self.avancar()
            self.expressao()
            self.validar("DELIMITADOR", ")")
        else:
            self.erro("Fator inválido")

    def termo_rec(self):
        if self.token_atual and self.token_atual.tipo == "OPERADOR_ARITMETICO" and self.token_atual.valor in ["*", "/"]:
            self.avancar()
            self.fator()
            self.termo_rec()

    def expressao_rec(self):
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
        if self.token_atual and self.token_atual.valor != ")":
            self.argumentos()

    def argumentos(self):
        self.expressao()
        while self.token_atual and self.token_atual.valor == ",":
            self.avancar()
            self.expressao()

    def se(self):
        self.validar("CONDICIONAL", "se")
        self.validar("DELIMITADOR", "(")
        self.expressao_booleana()
        self.validar("DELIMITADOR", ")")
        self.bloco()
        if self.token_atual and self.token_atual.valor == "senao":
            self.avancar()
            self.bloco()

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
                self.erro("Expressão booleana inválida. Esperado valor booleano, chamada de função ou operação relacional.")

    def enquanto(self):
        self.validar("CONDICIONAL", "enquanto")
        self.validar("DELIMITADOR", "(")
        self.expressao_booleana()
        self.validar("DELIMITADOR", ")")
        self.bloco()

    def retorno(self):
        self.validar("PALAVRA_CHAVE", "retorno")
        self.expressao_opcional()
        self.validar("DELIMITADOR", ";")

    def expressao_opcional(self):
        if self.token_atual and self.token_atual.valor != ";":
            self.expressao()

    def desvio(self):
        if self.token_atual.valor in ("break", "continue"):
            self.avancar()
            self.validar("DELIMITADOR", ";")

    def imprimir(self):
        self.validar("PALAVRA_CHAVE", "print")
        self.validar("DELIMITADOR", "(")
        self.expressao()
        self.validar("DELIMITADOR", ")")
        self.validar("DELIMITADOR", ";")