import os

class GeradorCodigo:
    def __init__(self):
        self.instrucoes = []
        self.temp_counter = 0
        self.label_counter = 0

    def nova_temporaria(self):
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def novo_rotulo(self):
        self.label_counter += 1
        return f"L{self.label_counter}"

    def adicionar_instrucao(self, instrucao):
        self.instrucoes.append(instrucao)

    def salvar_codigo_em_arquivo(self, nome_arquivo="codigo_intermediario.txt", caminho_base=None):
        caminho_diretorio = caminho_base if caminho_base else "analisadores/arquivos_gerados"
        os.makedirs(caminho_diretorio, exist_ok=True)
        caminho_arquivo = os.path.join(caminho_diretorio, nome_arquivo)
        
        with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
            for instrucao in self.instrucoes:
                arquivo.write(f"{instrucao}\n")