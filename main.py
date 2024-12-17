from analisadores.analisador_lexico import AnalisadorLexico
from analisadores.analisador_sintatico import AnalisadorSintatico

def main():
    with open("testes/funcoes/funcao.txt", "r") as f:
        codigo_fonte = f.read()

    print("\nExecutando Analisador Léxico...")
    lexico = AnalisadorLexico(codigo_fonte)
    tokens = lexico.analisar()
    print("\nTokens gerados:")
    for token in tokens:
        print(token)

    print("\nExecutando Analisador Sintático...")
    sintatico = AnalisadorSintatico(tokens)
    sintatico.programa()

if __name__ == "__main__":
    main()
