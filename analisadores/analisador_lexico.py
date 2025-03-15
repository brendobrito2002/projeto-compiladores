import re
import json
import os
from tokens.token_model import Token
from tokens.token_regex import REGEX_TOKENS

# O arquivo implementa a classe AnalisadorLexico, que realiza a análise léxica (tokenização) do código-fonte.
class AnalisadorLexico:

    # Recebe o código-fonte como entrada. 
    # Inicializa: 
    # self.codigo: O código-fonte. 
    # self.tokens: Lista que armazenará os tokens identificados. 
    # self.linha_atual: Contador de linhas (inicialmente 1).
    def __init__(self, codigo):
        self.codigo = codigo
        self.tokens = []
        self.linha_atual = 1

    # É o método principal que analisa o código-fonte e retorna uma lista de tokens.
    def analisar(self):

        # Indica a posição atual no código-fonte.
        i = 0

        # O loop percorre o código-fonte caractere por caractere até o final.
        while i < len(self.codigo):
            token_encontrado = False

            # Esse loop verifica cada tipo de token.
            for tipo, regex in REGEX_TOKENS:
                # Compila a expressão regular.
                padrao = re.compile(regex)
                # Tenta casar o padrão a partir da posição atual (i).
                match = padrao.match(self.codigo, i)

                # Se encontrar um token:
                if match:
                    # Captura o valor literal do token no código.
                    valor = match.group(0)

                    # Ignora "ESPACO" e "NOVA_LINHA"
                    if tipo != "ESPACO" and tipo != "NOVA_LINHA":
                        # Adiciona outros tokens na lista.
                        self.tokens.append(Token(tipo, valor, self.linha_atual))
                    # Incrementa linha_atual quando encontra "NOVA_LINHA".
                    elif tipo == "NOVA_LINHA":
                        self.linha_atual += 1

                    # Avança i: Move a posição atual no código pelo comprimento do token encontrado.
                    i += len(valor)
                    token_encontrado = True
                    break

            # Se não encontrar um token válido, lança um erro léxico.
            if not token_encontrado:
                raise ValueError(f"Erro léxico: Caractere inválido '{self.codigo[i]}' na linha {self.linha_atual}")
        
        # Após processar o código-fonte, a lista self.tokens contém todos os tokens identificados.
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