class TabelaDeSimbolos:
    def __init__(self):
        self.escopos_ativos = [{}]
        self.todos_escopos = []
        self.contador_temp = 0
        self._registrar_escopo()

    def _registrar_escopo(self):
        """Registra o escopo atual por referência (sem cópia)"""
        self.todos_escopos.append(self.escopos_ativos[-1])

    def entrar_escopo(self):
        """Cria um novo escopo isolado"""
        novo_escopo = {}
        self.escopos_ativos.append(novo_escopo)
        self._registrar_escopo()

    def sair_escopo(self):
        """Remove o escopo atual da pilha"""
        if len(self.escopos_ativos) > 1:
            self.escopos_ativos.pop()

    def adicionar(self, nome, tipo, categoria, **atributos):
        escopo_atual = self.escopos_ativos[-1]
        if nome in escopo_atual:
            raise ValueError(f"Identificador '{nome}' já declarado")
        escopo_atual[nome] = {
            'tipo': tipo,
            'categoria': categoria,
            **atributos
        }

    def buscar(self, nome):
        """Busca um símbolo na hierarquia de escopos"""
        for escopo in reversed(self.escopos_ativos):
            if nome in escopo:
                return escopo[nome]
        return None

    def gerar_temp(self):
        """Gera um nome temporário único"""
        self.contador_temp += 1
        return f"__temp{self.contador_temp}"

    def verificar_tipos(self, tipo1, tipo2, operacao):
        """Verifica compatibilidade de tipos para operações"""
        if tipo1 != tipo2:
            raise TypeError(f"Tipos incompatíveis: {tipo1} e {tipo2} na operação {operacao}")
        
    def gerar_relatorio(self, nome_arquivo="tabela_simbolos.txt"):
        with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
            arquivo.write("TABELA DE SÍMBOLOS COMPLETA\n")
            arquivo.write("=" * 50 + "\n")
            
            escopos_nao_vazios = [escopo for escopo in self.todos_escopos if escopo]
            
            for idx, escopo in enumerate(escopos_nao_vazios):
                arquivo.write(f"\n=== Escopo {idx} ===\n")            
                for nome, info in escopo.items():
                    linha = f"Nome: {nome.ljust(15)} | Tipo: {info['tipo'].ljust(10)} | Categoria: {info['categoria'].ljust(10)}"
                    if info['categoria'] == 'funcao':
                        parametros = ", ".join([f"{p['nome']}:{p['tipo']}" for p in info['parametros']])
                        linha += f" | Parâmetros: [{parametros}]"
                    arquivo.write(linha + "\n")