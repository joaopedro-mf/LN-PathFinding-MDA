

import ast
import csv

import numpy as np

from aux_functions import validate_viability
from topsis import TOPSIS


fileinclude = '../all_paths.csv'
paths = []
with open(fileinclude, encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        paths.append(ast.literal_eval(row[2]))

result = {}
    
weights = [ 0.2, 0.1, 0.35, 0.05, 0.3 ]
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

saidda = 'results_MDA_validate_topsis.csv'
with open(saidda, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Source','Target','Amount','LND1','LND2: c/300000.0','LND2: c/10.0','LND3','CLN','LDK1','LDK2','Eclair1','Eclair2','Eclair3','MDA1'])  # Write header
    writer.writerows(final)


