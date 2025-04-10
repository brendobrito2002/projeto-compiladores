from analisadores.analisador_semantico import AnalisadorSemantico
from analisadores.gerador.gerador_codigo import GeradorCodigo
from analisadores.tabela.tabela_simbolos import TabelaDeSimbolos

class AnalisadorSintatico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.posicao = 0
        self.token_atual = self.tokens[self.posicao] if self.tokens else None
        self.tabela_simbolos = TabelaDeSimbolos()
        self.semantico = AnalisadorSemantico(self.tabela_simbolos)
        self.gerador = GeradorCodigo()

    def avancar(self):
        self.posicao += 1
        self.token_atual = self.tokens[self.posicao] if self.posicao < len(self.tokens) else None

    def erro(self, mensagem):
        raise SyntaxError(f"Erro sintático na linha {self.token_atual.linha}: {mensagem} (Token: {self.token_atual.valor})")

    def validar(self, tipo, valor=None):
        if not self.token_atual or self.token_atual.tipo != tipo or (valor and self.token_atual.valor != valor):
            raise Exception(f"Erro sintático: esperado {tipo} {valor or ''}, encontrado {self.token_atual}")
        self.avancar()

    def programa(self):
        self.validar("PALAVRA_CHAVE", "programa")
        self.validar("IDENTIFICADOR")
        self.validar("DELIMITADOR", ";")
        self.gerador.adicionar_instrucao("# Início do programa")
        self.bloco()
        self.validar("DELIMITADOR", ".")
        self.gerador.adicionar_instrucao("# Fim do programa")
        self.tabela_simbolos.gerar_relatorio("analisadores/arquivos_gerados/tabela_simbolos.txt")
        self.gerador.salvar_codigo_em_arquivo()

    def bloco(self, nome_funcao=None):
        self.validar("DELIMITADOR", "{")
        while self.token_atual and self.token_atual.valor != "}":
            if self.token_atual.tipo == "PALAVRA_CHAVE" and self.token_atual.valor in ["var", "funcao", "procedimento"]:
                self.declaracao()
            else:
                self.comando(nome_funcao)
        self.validar("DELIMITADOR", "}")

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
        linha = self.token_atual.linha
        self.validar("IDENTIFICADOR")
        self.validar("DELIMITADOR", ":")
        tipo = self.token_atual.valor
        self.validar("TIPO")
        self.tabela_simbolos.adicionar(nome=nome, tipo=tipo, categoria='variavel', linha=linha)

    def declaracao_funcao(self):
        self.validar("PALAVRA_CHAVE", "funcao")
        nome_funcao = self.token_atual.valor
        linha_funcao = self.token_atual.linha
        self.validar("IDENTIFICADOR")
        self.validar("DELIMITADOR", "(")
        parametros = []
        if self.token_atual.valor != ")":
            while self.token_atual.valor != ")":
                param_nome = self.token_atual.valor
                param_linha = self.token_atual.linha
                self.validar("IDENTIFICADOR")
                self.validar("DELIMITADOR", ":")
                param_tipo = self.token_atual.valor
                self.validar("TIPO")
                self.tabela_simbolos.adicionar(nome=param_nome, tipo=param_tipo, categoria='parametro', linha=param_linha)
                parametros.append({'nome': param_nome, 'tipo': param_tipo, 'linha': param_linha})
                if self.token_atual.valor == ",":
                    self.avancar()
        self.validar("DELIMITADOR", ")")
        self.validar("DELIMITADOR", ":")
        tipo_retorno = self.token_atual.valor
        self.validar("TIPO")
        self.tabela_simbolos.adicionar(nome=nome_funcao, tipo=tipo_retorno, categoria='funcao', parametros=parametros, linha=linha_funcao)
        self.tabela_simbolos.entrar_escopo(nome_funcao)
        self.bloco(nome_funcao)
        self.tabela_simbolos.sair_escopo()

    def declaracao_procedimento(self):
        self.validar("PALAVRA_CHAVE", "procedimento")
        nome_procedimento = self.token_atual.valor
        linha_procedimento = self.token_atual.linha
        self.validar("IDENTIFICADOR")
        self.validar("DELIMITADOR", "(")  
        parametros = []
        if self.token_atual.valor != ")":
            self.tabela_simbolos.entrar_escopo()
            while self.token_atual.valor != ")":
                param_nome = self.token_atual.valor
                param_linha = self.token_atual.linha
                self.validar("IDENTIFICADOR")
                self.validar("DELIMITADOR", ":")
                param_tipo = self.token_atual.valor
                self.validar("TIPO")
                self.tabela_simbolos.adicionar(nome=param_nome, tipo=param_tipo, categoria='parametro', linha=param_linha)
                parametros.append({'nome': param_nome, 'tipo': param_tipo, 'linha': param_linha})
                if self.token_atual.valor == ",":
                    self.avancar()
            self.tabela_simbolos.sair_escopo()  
        self.validar("DELIMITADOR", ")")
        self.tabela_simbolos.adicionar(nome=nome_procedimento, tipo='none', categoria='procedimento', parametros=parametros, linha=linha_procedimento)
        self.tabela_simbolos.entrar_escopo(nome_procedimento)
        self.bloco(nome_procedimento)
        self.tabela_simbolos.sair_escopo()

    def comando(self, nome_funcao=None):
        if self.token_atual.tipo == "IDENTIFICADOR":
            nome = self.token_atual.valor
            linha = self.token_atual.linha
            self.avancar()
            if self.token_atual and self.token_atual.valor == "(":
                info = self.tabela_simbolos.buscar(nome)
                if info and info['categoria'] == 'procedimento':
                    self.chamada_procedimento(nome, linha)
                elif info and info['categoria'] == 'funcao':
                    self.chamada_funcao(nome, linha)
                else:
                    self.semantico.adicionar_erro(f"'{nome}' não declarado", linha)
                    self.chamada_funcao(nome, linha)
            else:
                self.atribuicao(nome, linha)
        elif self.token_atual.valor == "se":
            self.se(nome_funcao)
        elif self.token_atual.valor == "enquanto":
            self.enquanto(nome_funcao)
        elif self.token_atual.valor == "retorno":
            self.retorno(nome_funcao)
        elif self.token_atual.valor in ("break", "continue"):
            self.desvio()
        elif self.token_atual.valor == "print":
            self.imprimir()
        else:
            self.erro("Comando inválido")
        if self.token_atual and self.token_atual.valor == ";":
            self.avancar()

    def atribuicao(self, var_nome, var_linha):
        self.semantico.registrar_uso_variavel(var_nome, var_linha)
        self.validar("OPERADOR_ARITMETICO", "=")
        tipo_expressao, resultado_expressao = self.expressao()
        self.semantico.registrar_atribuicao(var_nome, tipo_expressao, var_linha)
        self.gerador.adicionar_instrucao(f"{var_nome} := {resultado_expressao}")
        self.validar("DELIMITADOR", ";")

    def expressao(self):
        tipo_esquerdo, resultado_esquerdo = self.termo()
        while self.token_atual and self.token_atual.tipo == "OPERADOR_ARITMETICO" and self.token_atual.valor in ("+", "-"):
            operador = self.token_atual.valor
            linha = self.token_atual.linha
            self.avancar()
            tipo_direito, resultado_direito = self.termo()
            self.semantico.registrar_operacao_aritmetica(operador, tipo_esquerdo, tipo_direito, linha)
            temp = self.gerador.nova_temporaria()
            self.gerador.adicionar_instrucao(f"{temp} := {resultado_esquerdo} {operador} {resultado_direito}")
            resultado_esquerdo = temp
            tipo_esquerdo = "inteiro"
        return tipo_esquerdo, resultado_esquerdo

    def termo(self):
        tipo_esquerdo, resultado_esquerdo = self.fator()
        while self.token_atual and self.token_atual.tipo == "OPERADOR_ARITMETICO" and self.token_atual.valor in ("*", "/"):
            operador = self.token_atual.valor
            linha = self.token_atual.linha
            self.avancar()
            tipo_direito, resultado_direito = self.fator()
            self.semantico.registrar_operacao_aritmetica(operador, tipo_esquerdo, tipo_direito, linha)
            temp = self.gerador.nova_temporaria()
            self.gerador.adicionar_instrucao(f"{temp} := {resultado_esquerdo} {operador} {resultado_direito}")
            resultado_esquerdo = temp
            tipo_esquerdo = "inteiro"
        return tipo_esquerdo, resultado_esquerdo

    def fator(self):
        if self.token_atual.tipo == "NUMERO":
            valor = self.token_atual.valor
            temp = self.gerador.nova_temporaria()
            self.gerador.adicionar_instrucao(f"{temp} := {valor}")
            self.avancar()
            return "inteiro", temp
        elif self.token_atual.tipo == "BOOLEANO":
            valor = self.token_atual.valor
            temp = self.gerador.nova_temporaria()
            self.gerador.adicionar_instrucao(f"{temp} := {valor}")
            self.avancar()
            return "booleano", temp
        elif self.token_atual.tipo == "IDENTIFICADOR":
            nome = self.token_atual.valor
            linha = self.token_atual.linha
            self.avancar()
            if self.token_atual and self.token_atual.valor == "(":
                func_info = self.tabela_simbolos.buscar(nome)
                if func_info and func_info['categoria'] == 'funcao':
                    resultado = self.chamada_funcao()
                    return func_info['tipo'], resultado
                else:
                    self.semantico.adicionar_erro(f"Função '{nome}' não declarada", linha)
                    self.chamada_funcao()
                    return None, None
            else:
                var_info = self.tabela_simbolos.buscar(nome)
                self.semantico.registrar_uso_variavel(nome, linha)
                tipo = var_info['tipo'] if var_info else None
                return tipo, nome
        elif self.token_atual.valor == "(":
            self.avancar()
            tipo, resultado = self.expressao()
            self.validar("DELIMITADOR", ")")
            return tipo, resultado
        else:
            self.erro("Fator inválido")

    def chamada_funcao(self):
        nome_funcao = self.tokens[self.posicao - 1].valor
        linha = self.token_atual.linha
        self.validar("DELIMITADOR", "(")
        args = []
        if self.token_atual and self.token_atual.valor != ")":
            while True:
                tipo, resultado = self.expressao()
                args.append((tipo, resultado))
                if self.token_atual.valor != ",":
                    break
                self.avancar()
        self.validar("DELIMITADOR", ")")
        for _, resultado in args:
            self.gerador.adicionar_instrucao(f"param {resultado}")
        temp = self.gerador.nova_temporaria()
        self.gerador.adicionar_instrucao(f"{temp} := call {nome_funcao}, {len(args)}")
        tipos_argumentos = [tipo for tipo, _ in args]
        self.semantico.registrar_chamada_funcao(nome_funcao, tipos_argumentos, linha)
        return temp
    
    def chamada_procedimento(self, nome_procedimento, linha):
        self.validar("DELIMITADOR", "(")
        args = []
        if self.token_atual and self.token_atual.valor != ")":
            while True:
                tipo, resultado = self.expressao()
                args.append((tipo, resultado))
                if self.token_atual.valor != ",":
                    break
                self.avancar()
        self.validar("DELIMITADOR", ")")
        for _, resultado in args:
            self.gerador.adicionar_instrucao(f"param {resultado}")
        self.gerador.adicionar_instrucao(f"call {nome_procedimento}, {len(args)}")
        tipos_argumentos = [tipo for tipo, _ in args]
        self.semantico.registrar_chamada_procedimento(nome_procedimento, tipos_argumentos, linha)

    def se(self, nome_funcao=None):
        self.validar("CONDICIONAL", "se")
        self.validar("DELIMITADOR", "(")
        tipo_condicao, resultado_condicao = self.expressao_booleana()
        if tipo_condicao != "booleano":
            self.semantico.adicionar_erro("A condição do 'se' deve ser do tipo 'booleano'", self.token_atual.linha)
        rotulo_else = self.gerador.novo_rotulo()
        rotulo_fim = self.gerador.novo_rotulo()
        self.gerador.adicionar_instrucao(f"if not {resultado_condicao} goto {rotulo_else}")
        self.validar("DELIMITADOR", ")")
        self.bloco(nome_funcao)
        self.gerador.adicionar_instrucao(f"goto {rotulo_fim}")
        self.gerador.adicionar_instrucao(f"{rotulo_else}:")
        if self.token_atual and self.token_atual.valor == "senao":
            self.avancar()
            self.bloco(nome_funcao)
        self.gerador.adicionar_instrucao(f"{rotulo_fim}:")

    def expressao_booleana(self):
        if self.token_atual.tipo == "BOOLEANO":
            valor = self.token_atual.valor
            temp = self.gerador.nova_temporaria()
            self.gerador.adicionar_instrucao(f"{temp} := {valor}")
            self.avancar()
            return "booleano", temp
        elif self.token_atual.tipo == "IDENTIFICADOR" and self.posicao + 1 < len(self.tokens) and self.tokens[self.posicao + 1].valor == "(":
            nome_funcao = self.token_atual.valor
            linha = self.token_atual.linha
            func_info = self.tabela_simbolos.buscar(nome_funcao)
            if func_info is None or func_info['categoria'] != 'funcao':
                self.erro(f"Função '{nome_funcao}' não declarada")
            resultado = self.chamada_funcao()
            return func_info['tipo'], resultado
        elif self.token_atual.valor == "(":
            self.avancar()
            tipo, resultado = self.expressao_booleana()
            self.validar("DELIMITADOR", ")")
            return tipo, resultado
        else:
            tipo_esquerdo, resultado_esquerdo = self.expressao()
            if self.token_atual and (self.token_atual.tipo == "OPERADOR_RELACIONAL" or self.token_atual.valor == "="):
                operador = self.token_atual.valor
                linha = self.token_atual.linha
                self.avancar()
                tipo_direito, resultado_direito = self.expressao()
                self.semantico.registrar_expressao_relacional(operador, tipo_esquerdo, tipo_direito, linha)
                temp = self.gerador.nova_temporaria()
                self.gerador.adicionar_instrucao(f"{temp} := {resultado_esquerdo} {operador} {resultado_direito}")
                return "booleano", temp
            else:
                return tipo_esquerdo, resultado_esquerdo

    def enquanto(self, nome_funcao=None):
        self.validar("CONDICIONAL", "enquanto")
        rotulo_inicio = self.gerador.novo_rotulo()
        rotulo_fim = self.gerador.novo_rotulo()
        self.gerador.adicionar_instrucao(f"{rotulo_inicio}:")
        self.validar("DELIMITADOR", "(")
        tipo_condicao, resultado_condicao = self.expressao_booleana()
        if tipo_condicao != "booleano":
            self.semantico.adicionar_erro("A condição do 'enquanto' deve ser do tipo 'booleano'", self.token_atual.linha)
        self.gerador.adicionar_instrucao(f"if not {resultado_condicao} goto {rotulo_fim}")
        self.validar("DELIMITADOR", ")")
        self.semantico.entrar_loop()
        self.bloco(nome_funcao)
        self.semantico.sair_loop()
        self.gerador.adicionar_instrucao(f"goto {rotulo_inicio}")
        self.gerador.adicionar_instrucao(f"{rotulo_fim}:")

    def retorno(self, nome_funcao=None):
        self.validar("PALAVRA_CHAVE", "retorno")
        linha = self.token_atual.linha
        tipo_expressao = None
        if self.token_atual.valor != ";":
            tipo_expressao, resultado_expressao = self.expressao()
            self.gerador.adicionar_instrucao(f"return {resultado_expressao}")
        else:
            self.gerador.adicionar_instrucao("return")
        self.validar("DELIMITADOR", ";")
        self.semantico.registrar_retorno(nome_funcao, tipo_expressao, linha)

    def desvio(self):
        if self.token_atual.valor == "break":
            self.gerador.adicionar_instrucao("break")
        elif self.token_atual.valor == "continue":
            self.gerador.adicionar_instrucao("continue")
        if self.semantico.nivel_loop == 0:
            self.semantico.adicionar_erro(f"'{self.token_atual.valor}' fora de loop", self.token_atual.linha)
        self.avancar()
        self.validar("DELIMITADOR", ";")

    def imprimir(self):
        self.validar("PALAVRA_CHAVE", "print")
        self.validar("DELIMITADOR", "(")
        _, resultado = self.expressao()
        self.gerador.adicionar_instrucao(f"print {resultado}")
        self.validar("DELIMITADOR", ")")
        self.validar("DELIMITADOR", ";")