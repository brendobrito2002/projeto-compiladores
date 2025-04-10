from analisadores.analisador_lexico import AnalisadorLexico
from analisadores.analisador_semantico import AnalisadorSemantico
from analisadores.analisador_sintatico import AnalisadorSintatico

def main():
    with open("testes/Final.txt", "r") as f:
        codigo_fonte = f.read()

    print("\nExecutando Analisador Léxico...")
    lexico = AnalisadorLexico(codigo_fonte)
    tokens = lexico.analisar()
    lexico.salvar_tokens_em_arquivo("lista_tokens.txt")
    print("Análise Léxica concluída com sucesso!")
    print("Lista de Tokens salvos em ./analisadores/arquivos_gerados/lista_tokens.txt")

    print("\nExecutando Analisador Sintático...")
    sintatico = AnalisadorSintatico(tokens)
    sintatico.programa()
    sintatico.tabela_simbolos.gerar_relatorio("analisadores/arquivos_gerados/tabela_simbolos.txt")
    print("Análise Sintática concluída com sucesso!")
    print("Tabela de Símbolos gerada em 'analisadores/arquivos_gerados/'!")

    print("\nExecutando Analisador Semântico...")
    sintatico.semantico.analisar()
    if sintatico.semantico.erros:
        print("\n=== Erros Semânticos ===")
        for erro in sintatico.semantico.erros:
            print(erro)
    else:
        print("Análise Semântica concluída com sucesso!")

    print("\nCódigo intermediário salvo em 'analisadores/arquivos_gerados/codigo_intermediario.txt'")

if __name__ == "__main__":
    main()