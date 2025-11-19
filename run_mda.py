import datetime
import configparser
import csv
import math
import ast
import multiprocessing as mp
import numpy as np
import os

from graph import Graph
from aux_functions import node_classification, route, validate_viability
from mda import run_MDA
from topsis import TOPSIS

SAVE_FILE_ALL_PATHS = True
FILE_ALL_PATHS_NAME= 'all_paths.csv'
RUN_MDA = True


def callable(source, target, amt, G):
    print(f"Processing MDA for {source} -> {target} amount {amt} with file {str(os.getpid())}")
    name = str(os.getpid())
    #name= '101600'
    return run_MDA(source, target, amt, G, process=name)

startTime = datetime.datetime.now()

config = configparser.ConfigParser()
config.read('config.ini')

graph = Graph(config)

graph.make_graph()

graph_balances = './sampling/channel_balances.csv'
file_include = 'LN_snapshot_results.csv' # results from original run
saida = 'LN_results_mda_final_all_algoritms.csv'  # output file path

graph.load_balances(graph_balances)

G = graph.G
node_classification(G)
        
if __name__ == '__main__': 

    payments = []
    with open(file_include, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            payments.append(row)
    payments.pop(0)  # Remove header

    if RUN_MDA:
        work = [] 
        results_MDA_par = []
        for i in payments:        
            sender = i[0]
            target = i[1]
            amount = int(i[2])

            work.append((sender, target, amount, G))

            ##result = mda.run(sender, target, amount, G)
            ##results_MDA.append(result)
        
        pool = mp.Pool(processes=7)
        a = pool.starmap(callable, work)
        results_MDA_par.append(a)

        pool.close()

        results_MDA = results_MDA_par[0]

        if SAVE_FILE_ALL_PATHS:
            with open(FILE_ALL_PATHS_NAME, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(results_MDA)
    else:  # IF YOU WANT TO LOAD PREVIOUS RESULTS
        results_MDA = []
        with open(FILE_ALL_PATHS_NAME, encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                print(row)
                if row[2] == '':
                    paths = None
                else:
                    paths = ast.literal_eval(row[2])
                results_MDA.append([row[0], row[1], paths, int(row[3])])
    result = {}
    
    #weights = [ 0.1, 0.03, 0.45, 0.02, 0.4 ]  ->original

    weights_low = [ 0.03, 0.02, 0.45, 0.1, 0.4 ]
    weights_medium = [ 0.0, 0.0, 0.9, 0.0, 0.1 ]
    weights_high = [ 0.0, 0.0, 0.9, 0.0, 0.1 ]
    cost_ben = ["c", "c", "c", "c", "c"]
    criteria = ["fee", "fee_rate", "prob", "hop", "length"]

    for r in results_MDA:
        print("Processing payment from ", r[0], " to ", r[1])
        paths = r[2]
        source = r[0]
        target = r[1]
        amount_send = r[3]

        if paths is None or paths == [] or len(paths) == 0:
                result[str(source)+','+str(target)] = ''
                continue
        
        cust_topsis = []
        for p in paths:
            if p is None:
                continue
            path = p[1]
            cust = p[0]
            if not validate_viability(G, path, amount_send):
                continue
            
            #print(path)
            cust_topsis.append([cust[0], cust[1], cust[2], cust[3], len(path)]) 

        
        if len(cust_topsis) == 0:
            continue
        
        if amount_send <= 10000:
            weights = weights_low
        elif amount_send <= 1000000:
            weights = weights_medium
        else:
            weights = weights_high

        #print(cust_topsis)
        tp = TOPSIS(np.array(cust_topsis), cost_ben,weights=weights, crit_col_names=criteria, alt_col_name="alternative")
        tp.get_closeness_coefficient(verbose=False)


        #tp.plot_ranking()
        best_coe_index = np.argmax(tp.clos_coefficient)
        #print("Best path index: ", best_coe_index)

        sucess, u, v, rout_res = route(G, paths[best_coe_index][1], int(source), int(target),amount_send)
        
        ### split
        # sort_arg = np.argsort(tp.clos_coefficient)
        # if sort_arg.size > 1:
        #     half = int(amount_send/2)
        #     sucess_1, u, v, rout_res_1 = route(G, paths[best_coe_index][1], int(source), int(target),half)
        #     second_coe_index = sort_arg[-2]
        #     sucess_2, u, v, rout_res_2 = route(G, paths[second_coe_index][1], int(source), int(target),amount_send-half)

        #     if sucess_1 and sucess_2:
        #         rout_res = rout_res_1
        #     elif sucess_1:
        #         rout_res = rout_res_2
        #     else:
        #         rout_res = rout_res_1
        # else:
        #    sucess, u, v, rout_res = route(G, paths[best_coe_index][1], int(source), int(target),amount_send)

        ### retry
        # if not sucess:
        #     sort_arg = np.argsort(tp.clos_coefficient)
        #     if sort_arg.size > 1:
        #         second_coe_index = sort_arg[-2]
        #         sucess, u, v, rout_res = route(G, paths[second_coe_index][1], int(source), int(target),amount_send)
                # if not sucess:
                #     if sort_arg.size > 2:
                #         second_coe_index = sort_arg[-3]
                #         sucess, u, v, rout_res = route(G, paths[second_coe_index][1], int(source), int(target),1000)
        
        result[str(source)+','+str(target)] = rout_res

final = []

for i in payments:
    source = i[0]
    target = i[1]
    check = str(source)+','+str(target)
    if check in result:
        i.append(str(result[check]))
    else:
        i.append('')

    # if check in result_menor:
    #     i.append(str(result_menor[check]))
    # else: 
    #     i.append('') 

    final.append(i)

with open(saida, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Source','Target','Amount','LND1','LND2: c/300000.0','LND2: c/10.0','LND3','CLN','LDK1','LDK2','Eclair1','Eclair2','Eclair3','MDA1'])  # Write header
    writer.writerows(final)


endTime = datetime.datetime.now()
print(endTime - startTime)