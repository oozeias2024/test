import random
from typing import List, Tuple
import numpy as np


def calc_value_distribution(
    total_value: float,
    n_long: int,
    n_short: int,
    token: str,
    current_price: float,
    noise: float = 0
) -> Tuple[List[float], List[float]]:
    """
    Calcula a distribuição de valores para posições long e short.
    Para Avantis, sempre será 1 long e 1 short com valores iguais.
    
    Args:
        total_value: Valor total em USD
        n_long: Número de posições long (sempre 1)
        n_short: Número de posições short (sempre 1)
        token: Token do par
        current_price: Preço atual
        noise: Ruído na distribuição (0-1)
        
    Returns:
        (lista de valores long, lista de valores short)
    """
    # Para Avantis, dividimos o valor igualmente entre long e short
    value_per_position = total_value / 2
    
    # Aplicar noise se configurado
    if noise > 0:
        variation = value_per_position * noise * random.uniform(-1, 1)
        long_value = value_per_position + variation
        short_value = total_value - long_value
    else:
        long_value = value_per_position
        short_value = value_per_position
    
    # IMPORTANTE: Não forçar mínimo de $10 se config está menor
    # Mínimo será apenas $1 para permitir testes
    min_value = 1.0
    long_value = max(long_value, min_value)
    short_value = max(short_value, min_value)
    
    return [long_value], [short_value]
