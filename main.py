from analisadores.analisador_lexico import AnalisadorLexico
from analisadores.analisador_sintatico import AnalisadorSintatico

def main():
    with open("testes/Final.txt", "r") as f:
        codigo_fonte = f.read()

    print("\nExecutando Analisador Léxico...")
    lexico = AnalisadorLexico(codigo_fonte)
    tokens = lexico.analisar()
    lexico.salvar_tokens_em_arquivo("lista_tokens.txt")

    print("\nExecutando Analisador Sintático...")
    sintatico = AnalisadorSintatico(tokens)
    sintatico.programa()

    sintatico.tabela_simbolos.gerar_relatorio("analisadores/arquivos_gerados/tabela_simbolos.txt")
    sintatico.tabela_simbolos.gerar_relatorio_json("analisadores/arquivos_gerados/tabela_simbolos.json")

    print("Tabela de Simbolos gerada em 'analisadores/arquivos_gerados/'!")

if __name__ == "__main__":
    main()