class TabelaDeSimbolos:
    def __init__(self):
        self.escopos_ativos = [{}]
        self.historico_escopos = [self.escopos_ativos[0]]
        self.nomes_escopos = ["Global"]

    def entrar_escopo(self, nome=None):
        novo_escopo = {}
        self.escopos_ativos.append(novo_escopo)
        self.historico_escopos.append(novo_escopo)
        self.nomes_escopos.append(nome if nome else f"Escopo {len(self.nomes_escopos)}")

    def sair_escopo(self):
        if len(self.escopos_ativos) > 1:
            self.escopos_ativos.pop()

    def adicionar(self, nome, tipo, categoria, **atributos):
        escopo_atual = self.escopos_ativos[-1]
        escopo_atual[nome] = {
            'tipo': tipo,
            'categoria': categoria,
            'linha': atributos.get('linha', 0),
            **atributos
        }

    def buscar(self, nome):
        for escopo in reversed(self.historico_escopos):
            if nome in escopo:
                return escopo[nome]
        return None

    def gerar_relatorio(self, nome_arquivo="tabela_simbolos.txt"):
        with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
            arquivo.write("TABELA DE SÍMBOLOS (Todos os Escopos)\n")
            arquivo.write("=" * 50 + "\n")
            for escopo, nome in zip(self.historico_escopos, self.nomes_escopos):
                arquivo.write(f"\n=== {nome} ===\n")
                if not escopo:
                    arquivo.write("(Escopo vazio)\n")
                    continue
                for nome_simbolo, info in escopo.items():
                    linha_info = f"Nome: {nome_simbolo.ljust(15)} | Tipo: {info['tipo'].ljust(10)} | Categoria: {info['categoria'].ljust(10)} | Linha: {info['linha']}\n"
                    arquivo.write(linha_info)