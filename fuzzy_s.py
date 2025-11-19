import numpy as np  # Apenas para operações matemáticas básicas; pode ser substituído por math

def triangular_membership(x, a, b, c):
    """
    Função de pertinência triangular simples.
    x: valor de entrada
    a: ponto esquerdo (início da rampa)
    b: pico
    c: ponto direito (fim da rampa)
    """
    if x <= a or x >= c:
        return max(0, 0)
    elif a < x <= b:
        return (x - a) / (b - a)
    else:  # b < x < c
        return (c - x) / (c - b)

def fuzzify_capacity(capacity, max_cap=1e7):  # max_cap assume canais até 10M sats
    """
    Fuzzificação para capacidade: small (0-0.3), medium (0.2-0.6), large (0.5-1.0)
    """
    norm_cap = capacity / max_cap  # Normaliza para [0,1]
    small = triangular_membership(norm_cap, 0, 0.15, 0.3)
    medium = triangular_membership(norm_cap, 0.2, 0.4, 0.6)
    large = triangular_membership(norm_cap, 0.5, 0.85, 1.0)
    return {'small': small, 'medium': medium, 'large': large}

def fuzzify_node_type(node_type):  # 0: wallet, 1: merchant, 2: routing hub
    """
    Fuzzificação simples para tipo de nó.
    """
    wallet = max(0, 1 - node_type / 2)  # Diminui com tipo maior
    merchant = 0.5 if node_type == 1 else 0
    hub = node_type / 2  # Aumenta com tipo maior
    return {'wallet': wallet, 'merchant': merchant, 'hub': hub}

def fuzzy_inference(capacity_fuzzy, node_fuzzy):
    """
    Inferência: Regras simples para determinar grau de pertinência para s.
    Saída fuzzy para s: very_low, low, medium, high, very_high
    """
    # Regras baseadas em conhecimento de domínio
    very_low = 0  # Para canais pequenos e wallets
    low = 0
    medium = 0
    high = 0
    very_high = 0
    
    # Regra 1: SE capacity small E node wallet → low s (concentrado)
    rule1 = min(capacity_fuzzy['small'], node_fuzzy['wallet'])
    low = max(low, rule1)
    
    # Regra 2: SE capacity medium E node merchant → medium s
    rule2 = min(capacity_fuzzy['medium'], node_fuzzy['merchant'])
    medium = max(medium, rule2)
    
    # Regra 3: SE capacity large E node hub → high s (mais espalhado)
    rule3 = min(capacity_fuzzy['large'], node_fuzzy['hub'])
    high = max(high, rule3)
    
    # Regra 4: SE capacity small E node hub → medium s (hubs gerenciam melhor)
    rule4 = min(capacity_fuzzy['small'], node_fuzzy['hub'])
    medium = max(medium, rule4)
    
    # ... Adicione mais regras conforme necessário
    
    return {'very_low': very_low, 'low': low, 'medium': medium, 'high': high, 'very_high': very_high}

def defuzzify_s(fuzzy_output, s_ranges):
    """
    Defuzzificação por centro de gravidade simples.
    s_ranges: dicionário com centros dos conjuntos (ex: {'low': 1e5, 'medium': 3e5})
    """
    numerator = 0
    denominator = 0
    for label, mu in fuzzy_output.items():
        if mu > 0:
            center = s_ranges[label]
            numerator += mu * center
            denominator += mu
    if denominator == 0:
        return 3e5  # Valor padrão
    return numerator / denominator

# Exemplo de uso
def get_fuzzy_s(capacity, node_type, s_ranges={'very_low': 5, 'low': 10, 'medium': 3e3, 'high': 1e5, 'very_high': 3e5}):
    cap_fuzzy = fuzzify_capacity(capacity)
    node_fuzzy = fuzzify_node_type(node_type)
    inference = fuzzy_inference(cap_fuzzy, node_fuzzy)
    s = defuzzify_s(inference, s_ranges)
    return s

# Teste
print(get_fuzzy_s(100000, 0))  # Canal pequeno, wallet → s baixo (~1e5)
print(get_fuzzy_s(100000, 2))  # Canal grande, hub → s alto (~5e5)