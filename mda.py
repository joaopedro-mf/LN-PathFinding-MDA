import ast
import copy
import math
import subprocess
import csv

from aux_functions import bimodal

SAVE_FILE_GRAPH = True

def run_cpp(executavel, sender, target, output_file):
    try:
        # Construir o comando completo
        comando = [executavel] + [output_file, sender, target]

        # Executar o programa
        resultado = subprocess.run(comando,
                                capture_output=True,
                                text=True,
                                check=True)

        return {
            'sucesso': True,
            'saida': resultado.stdout,
            'codigo_retorno': resultado.returncode
        }

    except subprocess.CalledProcessError as e:
        return {
            'sucesso': False,
            'erro': e.stderr,
            'codigo_retorno': e.returncode
        }

def save_file_to_run_mda(output_file, G):
    mult_dim_data = []
    mult_dim_data.append(['p','sp', 13129, 115546]) # TODO: ajustar para numero de nodes e edges

    for i in G.edges:
        (u,v) = i
        baseFee = G.edges[i]["BaseFee"]
        feeRate = G.edges[i]["FeeRate"]
        delay = G.edges[i]['Delay']
        prob = G.edges[i]['SuccessProb']
        mult_dim_data.append(['a',u,v,int(baseFee),int(feeRate), int(prob),int(delay)])

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter =' ')
        writer.writerows(mult_dim_data)

def implement_contrains_in_graph(G, amnt_send= 1000):
    g_constrains = copy.deepcopy(G)
    
    for i in G.edges:
        (u,v) = i
        cap = G.edges[i]['capacity']

        prob_cal = ((int(cap) - amnt_send )/ int(cap) ) #* G.nodes[u]['Width'] * G.nodes[v]['Width']
        #prob_cal = bimodal(cap, G.edges[i]['UpperBound'], G.edges[i]['LowerBound'], amnt_send) 
        #print(prob_cal)
        #prob_cal= 1/G.edges[i]['capacity']

        if prob_cal > 0.0001:
            # aumentar casas decimais do log para melhorar a precisao
            prob = 100*float((float(math.log(prob_cal)*-1)))
        else: 
            prob = 10000

        if prob > 10000:
            prob = 10000

        g_constrains.edges[i]['SuccessProb'] = prob
        
        baseFee = G.edges[i]["BaseFee"]*100
        if baseFee < 1:
            baseFee = 0
        elif baseFee > 1000:
            baseFee = 1000
        
        g_constrains.edges[i]['BaseFee'] = baseFee

        feeRate = G.edges[i]["FeeRate"]*100000
        if feeRate < 1:
            feeRate = 1
        elif feeRate > 1000:
            feeRate = 1000

        g_constrains.edges[i]['FeeRate'] = math.log(feeRate)

    return g_constrains

def convert_path_output(path_str):
    path_arr_string = path_str.split(';')

    if len(path_arr_string) < 2 :
        return None

    widths = ast.literal_eval(path_arr_string[0])
    path = ast.literal_eval(path_arr_string[1])

    return (widths, path)

def run_MDA(sender, target, amount, G, process ='teste'):

    
    output_file = './multiobjectiveDijkstra/instances/' + process + '.gr'
    #if self.last_amount_process < amount: # 50 sats de margem para nao refazer o grafo e acelerar teste
    if SAVE_FILE_GRAPH:
        G_const = implement_contrains_in_graph(G, amnt_send= amount)

        save_file_to_run_mda(output_file,G_const)

    result= run_cpp('./multiobjectiveDijkstra/build/labelSettingMosp.o', sender, target, output_file)
    if result['sucesso'] and result['saida'] != "":

        if result['saida'] == "":
            return [sender, target, None, amount]
                        
        paths = result['saida'].strip().split('?')
        if len(paths) > 0 and paths[-1] == '':
            paths = paths[:-1]

        paths_result = []
        for p in paths:
            converted_path = convert_path_output(p)
            paths_result.append(converted_path)

        return [sender, target, paths_result, amount]

    else:
        #print("Erro na execução:")
        return [sender, target, None, amount]
        