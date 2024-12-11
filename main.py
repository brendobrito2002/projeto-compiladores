from analisadores.analisador_lexico import AnalisadorLexico

def main():
    # Lê o código do arquivo teste.txt
    with open("teste.txt", "r") as arquivo:
        codigo_fonte = arquivo.read()

    # Executa o analisador léxico
    print("Executando Analisador Léxico...")
    lexico = AnalisadorLexico(codigo_fonte)
    tokens = lexico.analisar()

    # Exibe os tokens gerados
    print("\nTokens gerados:")
    for token in tokens:
        print(token)

if __name__ == "__main__":
    main()
