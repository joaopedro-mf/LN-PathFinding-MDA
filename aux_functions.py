import math


def route(G, path, source, target,amt):
        try:
            amt_list = []
            total_fee = 0
            total_delay = 0
            path_length = len(path)
            for i in range(path_length-1):
                v = path[i]
                u = path[i+1]
                if v == target:
                    amt_list.append(amt)
                fee = G.edges[u,v]["BaseFee"] + amt_list[-1]*G.edges[u,v]["FeeRate"]
                if u==source:
                    fee = 0
                fee = round(fee, 5)
                a = round(amt_list[-1] + fee, 5)
                amt_list.append(a)
                total_fee +=  fee
                total_delay += G.edges[u,v]["Delay"]
            path = path[::-1]
            amt_list = amt_list[::-1]
            amount = amt_list[0]
            for i in range(path_length-1):
                u = path[i]
                v = path[i+1]
                fee = G.edges[u,v]["BaseFee"] + amt_list[i+1]*G.edges[u,v]["FeeRate"]
                if u==source:
                    fee = 0
                fee = round(fee, 5)
                if amount > G.edges[u,v]["Balance"] or amount<=0:
                    # G.edges[u,v]["LastFailure"] = 0
                    # if amount < G.edges[u,v]["UpperBound"]:
                    #     G.edges[u,v]["UpperBound"] = amount #new
                    # j = i-1
                    # release_locked(j, path)
                    return False,u,v,[path, total_fee, total_delay, path_length, 'Failure']
                # else:
                    # G.edges[u,v]["Balance"] -= amount
                    # G.edges[u,v]["Locked"] = amount  
                    # G.edges[u,v]["LastFailure"] = 100
                    # if G.edges[u,v]["LowerBound"] < amount:
                    #     G.edges[u,v]["LowerBound"] = amount #new
                amount = round(amount - fee, 5)
                if v == target and amount!=amt:
                    return False,u,v,[path, total_fee, total_delay, path_length, 'Failure']
          
            # release_locked(i-1, path)
            return True,u,v,[path, total_fee, total_delay, path_length, 'Success']
        except Exception as e:
            print(e)
            return "Routing Failed due to the above error"


def validate_viability(G, path, amount = 1000):    
    v = path[0]
    u = path[1]

    bal = G.edges[u,v]['Balance']

    return (bal > amount or len(path) <= 10)


def exp_safe(value):
    try:
        result = math.exp(value)
    except :
        result = 999999 # A large number to represent infinity
    return result

def primitive(c, x, lnd_scale=1000):
    # if datasample == 'uniform':
    #     s = 3e5 #fine tune 's' for improved performance
    # else:
    #     s = c/10
    #global lnd_scale
    #test_scales = config['LND']['test_scales']
    #if test_scales == 'True':
    #    s = c/lnd_scale
    #else:
    s = c/lnd_scale
    #if lnd_scale == 3e5:
    #    s = 3e5
    ecs = exp_safe(-c/s)
    exs = exp_safe(-x/s)
    excs = exp_safe((x-c)/s)
    norm = -2*ecs + 2
    if norm == 0:
        return 0
    return (excs - exs)/norm


def integral(cap, lower, upper):
    return primitive(cap, upper) - primitive(cap, lower)


def bimodal(cap, a_f, a_s, a):
    prob = integral(cap, a, a_f)
    if math.isnan(prob):
        return 0
    
    reNorm = integral(cap, a_s, a_f)
    
    if math.isnan(reNorm) or reNorm == 0:
        return 0
    prob /= reNorm
    if prob>1:
        return 1
    if prob<0:
        return 0
    return prob


def node_classification(G):
    for i in G.edges:
        u = i[0]
        sum_edges = 0
        cnt_edges = 0
        for edges in G.out_edges(u):
                cnt_edges += 1
                sum_edges += G.edges[edges]['Balance']

        G.nodes[u]['TotalOutBalance'] = sum_edges
        G.nodes[u]['CntOutEdges'] = cnt_edges

        if sum_edges >= 10**6 and cnt_edges>5:
                G.nodes[u]['Width'] = 1
        elif sum_edges > 10**2 and sum_edges < 10**6 and cnt_edges>5:
            G.nodes[u]['Width'] = 0.9
        elif cnt_edges<=5:
            G.nodes[u]['Width'] = 0.7
        else:
            G.nodes[u]['Width'] = 0.8