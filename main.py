from analisadores.analisador_lexico import AnalisadorLexico
from analisadores.analisador_sintatico import AnalisadorSintatico

def main():
    with open("testes/final.txt", "r") as f:
        codigo_fonte = f.read()

    print("\nExecutando Analisador Léxico...")
    lexico = AnalisadorLexico(codigo_fonte)
    tokens = lexico.analisar()

    lexico.salvar_tokens_em_arquivo("lista_tokens.txt")

    print("\nExecutando Analisador Sintático...")
    sintatico = AnalisadorSintatico(tokens)
    sintatico.programa()

if __name__ == "__main__":
    main()