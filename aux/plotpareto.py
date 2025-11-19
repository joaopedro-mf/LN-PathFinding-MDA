import ast
import csv
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import argparse

dim_names = ['Dim 1', 'Dim 2', 'Dim 3', 'Dim 4']

# Criar DataFrame

# Configurar estilo
#plt.style.use('dark_background')

def plot_radar(points):
    df = pd.DataFrame(points, columns=dim_names, index=range(len(points)))
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='polar')
    
    # Normalizar dados (0-100)
    max_vals = df.max()
    df_norm = (df / max_vals) * 100
    
    # Ângulos para cada dimensão
    angles = np.linspace(0, 2 * np.pi, len(dim_names), endpoint=False).tolist()
    angles += angles[:1]  # Fechar o círculo
    
    # Plotar cada ponto
    for idx, (label, row) in enumerate(df_norm.iterrows()):
        values = row.tolist()
        values += values[:1]  # Fechar o círculo
        ax.plot(angles, values, 'o-', linewidth=2, label=label)
        ax.fill(angles, values, alpha=0.15)
    
    # Configurar eixos
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dim_names, size=12)
    ax.set_ylim(0, 100)
    ax.set_title('Radar Chart - Fronteira de Pareto', size=16, pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    ax.grid(True)
    
    plt.tight_layout()
    #plt.savefig('1_radar_chart.png', dpi=300, bbox_inches='tight')
    plt.show()


def plot_parallel_coordinates(points):
    df = pd.DataFrame(points, columns=dim_names, index=range(len(points)))
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Normalizar para escala similar
    #df_norm = (df - df.min()) / (df.max() - df.min())
    
    # Plotar linhas
    for idx, (label, row) in enumerate(df.iterrows()):
        ax.plot(range(len(dim_names)), row, marker='o', linewidth=2.5, 
                label=label, markersize=10)
    
    ax.set_xticks(range(len(dim_names)))
    ax.set_xticklabels(dim_names, size=12)
    ax.set_ylabel('Valor Normalizado', size=12)
    ax.set_title('Coordenadas Paralelas', size=16)
    #ax.legend(loc='best', fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    #plt.savefig('2_parallel_coordinates.png', dpi=300, bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Amostra aleatória de linhas de um CSV.")
    parser.add_argument("--sender", help="sender")
    parser.add_argument("--target", help="target")
    parser.add_argument("--tipo", type=str, default="paralelas")

    args = parser.parse_args()

    fileinclude = '../all_paths.csv'
    paths = ""
    with open(fileinclude, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0] == args.sender and row[1] == args.target:
                paths = ast.literal_eval(row[2])
                break
    

    if(paths == ""):        
        print("No paths found for the given sender and target.")
        raise SystemExit
    
    points = []
    for p in paths:
        points.append([p[0][0],p[0][1],p[0][2],p[0][3]])  # Ajuste conforme necessário para extrair os dados corretos

    print(points)

    if args.tipo == "radar":
        plot_radar(points)
    else:
        plot_parallel_coordinates(points)

#python plotpareto.py --sender=4768 --target=7665