from analisadores.tabela.tabela_simbolos import TabelaDeSimbolos

class AnalisadorSemantico:
    def __init__(self, tabela_simbolos):
        self.tabela = tabela_simbolos
        self.nivel_loop = 0
        self.erros = []
        self.usos_variaveis = []
        self.chamadas_funcoes = []
        self.retornos = {}
        self.expressoes_relacionais = []
        self.atribuicoes = []
        self.operacoes_aritmeticas = []

    def analisar(self):
        self._verificar_funcoes()
        self._verificar_variaveis_nao_declaradas()
        self._verificar_usos_variaveis()
        self._verificar_chamadas_funcoes()
        self._verificar_retornos()
        self._verificar_expressoes_relacionais()
        self._verificar_atribuicoes()
        self._verificar_operacoes_aritmeticas()

    def entrar_loop(self):
        self.nivel_loop += 1

    def sair_loop(self):
        if self.nivel_loop > 0:
            self.nivel_loop -= 1

    def adicionar_erro(self, mensagem, linha):
        self.erros.append(f"Erro semântico na linha {linha}: {mensagem}")

    def registrar_uso_variavel(self, nome, linha):
        self.usos_variaveis.append({'nome': nome, 'linha': linha})

    def registrar_atribuicao(self, nome_variavel, tipo_expressao, linha):
        self.atribuicoes.append({
            'variavel': nome_variavel,
            'tipo_expressao': tipo_expressao,
            'linha': linha
        })

    def registrar_operacao_aritmetica(self, operador, tipo_esquerdo, tipo_direito, linha):
        self.operacoes_aritmeticas.append({
            'operador': operador,
            'tipo_esquerdo': tipo_esquerdo,
            'tipo_direito': tipo_direito,
            'linha': linha
        })

    def registrar_expressao_relacional(self, operador, tipo_esquerdo, tipo_direito, linha):
        self.expressoes_relacionais.append({
            'operador': operador,
            'tipo_esquerdo': tipo_esquerdo,
            'tipo_direito': tipo_direito,
            'linha': linha
        })

    def registrar_chamada_funcao(self, nome, tipos_argumentos, linha):
        self.chamadas_funcoes.append({
            'nome': nome,
            'argumentos': tipos_argumentos,
            'linha': linha
        })

    def registrar_retorno(self, nome_funcao, tipo_expressao, linha):
        if not nome_funcao:
            self.adicionar_erro("Comando 'retorno' fora de uma função ou procedimento", linha)
            return
            
        if nome_funcao not in self.retornos:
            self.retornos[nome_funcao] = []
        self.retornos[nome_funcao].append({'tipo': tipo_expressao, 'linha': linha})

    def _verificar_funcoes(self):
        for escopo in self.tabela.historico_escopos:
            for nome, info in escopo.items():
                if info['categoria'] in ['funcao', 'procedimento']:
                    self._validar_funcao(info, nome)

    def _validar_funcao(self, funcao, nome):
        parametros = funcao.get('parametros', [])
        nomes = [p['nome'] for p in parametros]
        if len(nomes) != len(set(nomes)):
            duplicados = {n for n in nomes if nomes.count(n) > 1}
            for duplicado in duplicados:
                linha = next(p['linha'] for p in parametros if p['nome'] == duplicado)
                self.adicionar_erro(f"Parâmetro duplicado '{duplicado}' na função '{nome}'", linha)

    def _verificar_variaveis_nao_declaradas(self):
        declaradas = []
        for escopo in self.tabela.historico_escopos:
            for nome, info in escopo.items():
                if info['categoria'] == 'variavel':
                    declaradas.append((nome, info['linha']))
        
        usadas = set(uso['nome'] for uso in self.usos_variaveis)
        
        for nome, linha in declaradas:
            if nome not in usadas:
                self.adicionar_erro(f"Variável '{nome}' declarada mas não utilizada", linha)

    def _verificar_usos_variaveis(self):
        for uso in self.usos_variaveis:
            nome = uso['nome']
            linha = uso['linha']
            if not self.tabela.buscar(nome):
                self.adicionar_erro(f"Variável '{nome}' não declarada antes do uso", linha)

    def _verificar_chamadas_funcoes(self):
        for chamada in self.chamadas_funcoes:
            nome = chamada['nome']
            tipos_argumentos = chamada['argumentos']
            linha = chamada['linha']
            func_info = self.tabela.buscar(nome)
            
            if not func_info or func_info['categoria'] not in ['funcao', 'procedimento']:
                self.adicionar_erro(f"Função ou procedimento '{nome}' não declarado", linha)
                continue
                
            tipos_params = [p['tipo'] for p in func_info.get('parametros', [])]
            
            if len(tipos_argumentos) != len(tipos_params):
                self.adicionar_erro(f"Chamada de '{nome}' com número incorreto de argumentos: esperado {len(tipos_params)}, recebido {len(tipos_argumentos)}", linha)
                continue
                
            for i, (tipo_arg, tipo_param) in enumerate(zip(tipos_argumentos, tipos_params)):
                if tipo_arg != tipo_param:
                    self.adicionar_erro(f"Argumento {i+1} na chamada de '{nome}' tem tipo incompatível: esperado '{tipo_param}', recebido '{tipo_arg}'", linha)

    def _verificar_retornos(self):
        for escopo in self.tabela.historico_escopos:
            for nome, info in escopo.items():
                if info['categoria'] == 'funcao':
                    retornos = self.retornos.get(nome, [])
                    if not retornos:
                        self.adicionar_erro(f"Função '{nome}' do tipo '{info['tipo']}' não possui retorno", info['linha'])
                    else:
                        for retorno in retornos:
                            tipo_retorno = retorno['tipo']
                            linha = retorno['linha']
                            if tipo_retorno is None:
                                self.adicionar_erro(f"Função '{nome}' deve retornar um valor do tipo '{info['tipo']}'", linha)
                            elif tipo_retorno != info['tipo']:
                                self.adicionar_erro(f"Tipo de retorno incompatível na função '{nome}': esperado '{info['tipo']}', mas encontrado '{tipo_retorno}'", linha)
                elif info['categoria'] == 'procedimento':
                    for retorno in self.retornos.get(nome, []):
                        if retorno['tipo'] is not None:
                            self.adicionar_erro(f"Procedimento '{nome}' não pode retornar um valor (encontrado tipo '{retorno['tipo']}')", retorno['linha'])

    def _verificar_atribuicoes(self):
        for atrib in self.atribuicoes:
            var_info = self.tabela.buscar(atrib['variavel'])
            if not var_info:
                continue
            if atrib['tipo_expressao'] != var_info['tipo']:
                self.adicionar_erro(f"Atribuição inválida: variável '{atrib['variavel']}' é do tipo '{var_info['tipo']}', recebeu '{atrib['tipo_expressao']}'", atrib['linha'])

    def _verificar_operacoes_aritmeticas(self):
        for op in self.operacoes_aritmeticas:
            if op['tipo_esquerdo'] != "inteiro" or op['tipo_direito'] != "inteiro":
                self.adicionar_erro(f"Operação aritmética inválida: '{op['operador']}' entre '{op['tipo_esquerdo']}' e '{op['tipo_direito']}'", op['linha'])

    def _verificar_expressoes_relacionais(self):
        for expr in self.expressoes_relacionais:
            if expr['tipo_esquerdo'] != 'inteiro' or expr['tipo_direito'] != 'inteiro':
                self.adicionar_erro(f"Operador relacional '{expr['operador']}' requer operandos do tipo 'inteiro', mas recebeu '{expr['tipo_esquerdo']}' e '{expr['tipo_direito']}'", expr['linha'])