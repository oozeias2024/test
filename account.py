from typing import List, Dict, Any
from avantis_trader_sdk import TraderClient
from src.config.constants import logger


async def get_open_positions(trader_client: TraderClient) -> List[Dict[str, Any]]:
    """
    Obtém todas as posições abertas da conta.
    
    Args:
        trader_client: Cliente Avantis
        
    Returns:
        Lista de posições abertas
    """
    trader = trader_client.get_signer().get_ethereum_address()
    
    try:
        # Tentar obter trades - se falhar, retornar lista vazia (sem erro visual)
        try:
            trades, pending_orders = await trader_client.trade.get_trades(trader)
        except Exception as parse_error:
            # Erro de parsing é comum quando não há posições
            logger.debug(f"Nenhuma posição encontrada (parsing error ignorado)")
            return []
        
        positions = []
        for trade in trades:
            try:
                positions.append({
                    "pair_index": trade.trade.pair_index,
                    "trade_index": trade.trade.trade_index,
                    "collateral": trade.trade.open_collateral,
                    "is_long": trade.trade.is_long,
                    "leverage": trade.trade.leverage,
                    "open_price": trade.trade.open_price,
                    "tp": trade.trade.tp,
                    "sl": trade.trade.sl,
                    "liquidation_price": trade.liquidation_price,
                    "margin_fee": trade.margin_fee
                })
            except AttributeError as ae:
                logger.debug(f"Ignorando trade com estrutura inválida: {ae}")
                continue
        
        return positions
        
    except Exception as e:
        logger.warning(f"Erro ao buscar posições (retornando vazio): {e}")
        return []


async def get_usdc_balance(trader_client: TraderClient) -> float:
    """
    Obtém o saldo USDC da conta.
    
    Args:
        trader_client: Cliente Avantis
        
    Returns:
        Saldo em USDC
    """
    trader = trader_client.get_signer().get_ethereum_address()
    
    try:
        balance = await trader_client.get_usdc_balance(trader)
        return balance
    except Exception as e:
        logger.error(f"Erro ao buscar saldo: {e}")
        return 0.0
