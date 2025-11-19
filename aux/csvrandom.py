import argparse
import pandas as pd

def amostrar_csv(input_file, output_file, num_linhas=1000):
    """
    Lê um CSV, amostra linhas aleatórias e escreve em um novo CSV.
    
    Args:
    - input_file: Caminho para o CSV de entrada.
    - output_file: Caminho para o CSV de saída.
    - num_linhas: Número de linhas a amostrar (padrão: 1000).
    """
    # Lê o CSV completo
    df = pd.read_csv(input_file)
    
    # Calcula o tamanho da amostra (não excede o número de linhas disponíveis)
    tamanho_total = len(df)
    tamanho_amostra = min(num_linhas, tamanho_total)
    
    # Amostra aleatória sem reposição
    df_amostra = df.sample(n=tamanho_amostra, random_state=None)  # random_state=None para aleatoriedade
    
    # Escreve o novo CSV, preservando índice se presente
    df_amostra.to_csv(output_file, index=False)
    print(f"Amostra de {tamanho_amostra} linhas salva em {output_file}.")

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Amostra aleatória de linhas de um CSV.")
    # parser.add_argument("input_file", help="Arquivo CSV de entrada")
    # parser.add_argument("output_file", help="Arquivo CSV de saída")
    # parser.add_argument("--linhas", type=int, default=1000, help="Número de linhas a amostrar")
    
    amostrar_csv('LN_results_bi_combo_order.csv', 'LN_results_bi_combo_order_rand.csv', 1000)