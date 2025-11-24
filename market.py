from typing import Dict, Any, Optional
from avantis_trader_sdk import TraderClient
from src.config.constants import logger
import asyncio


async def get_pair_index(trader_client: TraderClient, pair_symbol: str) -> Optional[int]:
    """
    Obtém o índice de um par de trading.
    
    Args:
        trader_client: Cliente Avantis
        pair_symbol: Símbolo do par (ex: "ETH/USD")
        
    Returns:
        Índice do par ou None
    """
    try:
        pair_index = await trader_client.pairs_cache.get_pair_index(pair_symbol)
        return pair_index
    except Exception as e:
        logger.error(f"Erro ao buscar par {pair_symbol}: {e}")
        return None


async def get_pair_price(trader_client: TraderClient, pair_index: int) -> float:
    """
    Obtém o preço atual de um par.
    
    Args:
        trader_client: Cliente Avantis
        pair_index: Índice do par
        
    Returns:
        Preço atual
    """
    try:
        # A SDK não tem método direto para preço, vamos usar feed client se necessário
        # Por enquanto retornaremos 0 e precisaremos implementar via Pyth
        logger.warning("get_pair_price não implementado completamente")
        return 0.0
    except Exception as e:
        logger.error(f"Erro ao buscar preço: {e}")
        return 0.0
