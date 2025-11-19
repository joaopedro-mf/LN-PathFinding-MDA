import pandas as pd

# Ler o arquivo CSV
df = pd.read_csv('LN_results_bi_combo.csv')

# Ordenar pela coluna 'idade' (assumindo que é um inteiro)
df_ordenado = df.sort_values(by='Amount')

# Salvar o DataFrame ordenado em um novo arquivo CSV
df_ordenado.to_csv('LN_results_bi_combo_order.csv', index=False)

# Exibir o resultado (opcional)
print(df_ordenado)