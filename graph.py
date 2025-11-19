
from datetime import datetime
import networkx as nx
import random as rn
import pandas as pd
import re
from ordered_set import OrderedSet
import numpy as np
import matplotlib.pyplot as plt

class Graph:
    def __init__(self, config):
        self.datasampling = config['General']['datasampling']
        self.y = []
        self.G = nx.DiGraph()

    def make_graph(self):
        G = self.G
        df = pd.read_csv('LN_snapshot.csv')
        is_multi = df["short_channel_id"].value_counts() > 1
        df = df[df["short_channel_id"].isin(is_multi[is_multi].index)]
        node_num = {}
        nodes_pubkey = list(OrderedSet(list(df['source']) + list(df['destination'])))
        for i in range(len(nodes_pubkey)):
            G.add_node(i)
            pubkey = nodes_pubkey[i]
            G.nodes[i]['pubkey'] = pubkey
            node_num[pubkey] = i
        for i in df.index:
            node_src = df['source'][i]
            node_dest = df['destination'][i]
            u = node_num[node_src]
            v = node_num[node_dest]
            G.add_edge(u,v)
            channel_id = df['short_channel_id'][i]
            block_height = int(channel_id.split('x')[0])
            G.edges[u,v]['id'] = channel_id
            G.edges[u,v]['capacity'] = int(df['satoshis'][i])#uncomment
            # G.edges[u,v]['capacity'] = 10**8 #new
            G.edges[u,v]['UpperBound'] = int(df['satoshis'][i])
            # G.edges[u,v]['UpperBound'] = 10**8 #new
            G.edges[u,v]['LowerBound'] = 0
            G.edges[u,v]['Age'] = block_height 
            G.edges[u,v]['BaseFee'] = df['base_fee_millisatoshi'][i]/1000
            G.edges[u,v]['FeeRate'] = df['fee_per_millionth'][i]/1000000
            G.edges[u,v]['Delay'] = df['delay'][i]
            G.edges[u,v]['htlc_min'] = int(re.split(r'(\d+)', df['htlc_minimum_msat'][i])[1])/1000
            G.edges[u,v]['htlc_max'] = int(re.split(r'(\d+)', df['htlc_maximum_msat'][i])[1])/1000
            G.edges[u,v]['LastFailure'] = 100

      
    def assign_balances_all_nodes(self):
        G= self.G
        for i in G.edges:
            if 'Balance' not in G.edges[i]:
                cap = G.edges[i]['capacity']
                
                x = self.get_random_balance(cap, i)
                (u,v) = i
                G.edges[(u,v)]['Balance'] = x
                G.edges[(v,u)]['Balance'] = cap - x
                
                self.y.append(x)
                self.y.append(cap-x)
                
                self.validate_balances(u, v,i, cap)
    
    def assign_balances(self, i):
        #Sample balance from bimodal or uniform distribution
        G= self.G
        (u,v) = i
        cap = G.edges[u,v]['capacity']
         
        x = self.get_random_balance(cap, i)
        G.edges[(u,v)]['Balance'] = x
        G.edges[(v,u)]['Balance'] = cap - x
        
        self.y.append(x)
        self.y.append(cap-x)

        self.validate_balances(u, v, cap)
                
                
                
    def validate_balances(self, u,v,i, cap):
        G= self.G
        
        if G.edges[v,u]['Balance'] < 0 or G.edges[v,u]['Balance'] > G.edges[i]['capacity']:
            print( i,'Balance error at', (v,u))
            raise ValueError
            
        if G.edges[u,v]['Balance'] < 0 or G.edges[u,v]['Balance'] > G.edges[i]['capacity']:
            print('Balance error at', (u,v))
            raise ValueError
            
        if G.edges[(v,u)]['Balance'] + G.edges[(u,v)]['Balance'] != cap:
            print('Balance error at', (v,u))
            raise ValueError


    def get_random_balance(self, cap, i):
        if self.datasampling == 'bimodal':
            rng = np.linspace(0, cap, 10000)
            s = cap/10
            P = np.exp(-rng/s) + np.exp((rng - cap)/s)
            P /= np.sum(P)            
            return  int(np.random.choice(rng, p=P))
        
        return int(rn.uniform(0, self.G.edges[i]['capacity']))
    

    def save_balances(self, filename= './sampling/channel_balances.csv'):
        balance_data = []
        for u, v in self.G.edges():
            balance_data.append({
                'channel_id': self.G.edges[u,v]['id'],
                'node1': self.G.nodes[u]['pubkey'],
                'node2': self.G.nodes[v]['pubkey'],
                'capacity': self.G.edges[u,v]['capacity'],
                'balance1': self.G.edges[u,v]['Balance'],
                'balance2': self.G.edges[v,u]['Balance']
            })
        
        df = pd.DataFrame(balance_data)
        df.to_csv(filename, index=False)
        print(f"Balances saved to {filename}")

    def load_balances(self, filename='./sampling/channel_balances.csv'):
        try:
            df = pd.read_csv(filename)
            node_pubkey_to_id = {self.G.nodes[n]['pubkey']: n for n in self.G.nodes()}
            
            for _, row in df.iterrows():
                node1_id = node_pubkey_to_id[row['node1']]
                node2_id = node_pubkey_to_id[row['node2']]
                
                # Verifica se a capacidade do canal é a mesma
                if self.G.edges[node1_id, node2_id]['capacity'] != row['capacity']:
                    print(f"Warning: Channel capacity mismatch for {row['channel_id']}")
                    continue
                    
                # Atualiza os balances
                self.G.edges[node1_id, node2_id]['Balance'] = row['balance1']
                self.G.edges[node2_id, node1_id]['Balance'] = row['balance2']
                
                # Atualiza lista de balances para plotagem
                self.y.append(row['balance1'])
                self.y.append(row['balance2'])
                
            print(f"Balances loaded from {filename}")
        except FileNotFoundError:
            print(f"Error: File {filename} not found")
        except Exception as e:
            print(f"Error loading balances: {e}")

    def plot_balance_distribution(self):
        plt.hist(self.y)
        plt.show()