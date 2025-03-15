import re
import json
import os
from tokens.token_model import Token
from tokens.token_regex import REGEX_TOKENS

class AnalisadorLexico:
    def __init__(self, codigo):
        self.codigo = codigo
        self.tokens = []
        self.linha_atual = 1

    def analisar(self):
        """Analisa o código-fonte e gera uma lista de tokens."""
        i = 0
        while i < len(self.codigo):
            token_encontrado = False
            for tipo, regex in REGEX_TOKENS:
                padrao = re.compile(regex)
                match = padrao.match(self.codigo, i)
                if match:
                    valor = match.group(0)
                    if tipo != "ESPACO" and tipo != "NOVA_LINHA":
                        self.tokens.append(Token(tipo, valor, self.linha_atual))
                    elif tipo == "NOVA_LINHA":
                        self.linha_atual += 1

                    i += len(valor)
                    token_encontrado = True
                    break

            if not token_encontrado:
                raise ValueError(f"Erro léxico: Caractere inválido '{self.codigo[i]}' na linha {self.linha_atual}")
        return self.tokens

    def salvar_tokens_em_arquivo(self, nome_arquivo="tokens.txt"):
        """Salva a lista de tokens em um arquivo de texto."""
        caminho_diretorio = "./analisadores/arquivos_gerados"
        os.makedirs(caminho_diretorio, exist_ok=True)
        caminho_arquivo = os.path.join(caminho_diretorio, nome_arquivo)
        with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
            for token in self.tokens:
                arquivo.write(f"{token}\n")
        print(f"Lista de Tokens salvos em {caminho_arquivo}")

    def salvar_tokens_json(self, nome_arquivo="tokens.json"):
        """Salva a lista de tokens em um arquivo JSON."""
        caminho_diretorio = "./analisadores/arquivos_gerados"
        os.makedirs(caminho_diretorio, exist_ok=True)
        caminho_arquivo = os.path.join(caminho_diretorio, nome_arquivo)
        tokens_dict = [{"tipo": token.tipo, "valor": token.valor, "linha": token.linha} for token in self.tokens]
        with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
            json.dump(tokens_dict, arquivo, indent=4)
        print(f"Lista de Tokens salvos em {caminho_arquivo}")