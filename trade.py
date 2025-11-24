import asyncio
from typing import Optional
from avantis_trader_sdk import TraderClient
from avantis_trader_sdk.types import TradeInput, TradeInputOrderType
from src.config.constants import logger
from utils.data import update_state


async def open_position_direct(
    trader_client: TraderClient,
    pair_index: int,
    collateral: float,
    is_long: bool,
    leverage: int,
    trade_index: int = 0,
    tp: float = 0,
    sl: float = 0
) -> bool:
    """
    Abre posição DIRETAMENTE baseado no exemplo oficial da Avantis SDK.
    SIMPLIFICADO: Sem complicações de nonce.
    """
    trader = trader_client.get_signer().get_ethereum_address()
    side = "LONG" if is_long else "SHORT"
    
    try:
        # Preparar trade input (EXATAMENTE como no exemplo oficial)
        trade_input = TradeInput(
            trader=trader,
            open_price=None,
            pair_index=pair_index,
            collateral_in_trade=collateral,
            is_long=is_long,
            leverage=leverage,
            index=trade_index,
            tp=tp if tp > 0 else 0,
            sl=sl if sl > 0 else 0,
            timestamp=0
        )
        
        # Build transaction (EXATAMENTE como no exemplo oficial)
        open_transaction = await trader_client.trade.build_trade_open_tx(
            trade_input,
            TradeInputOrderType.MARKET,
            slippage_percentage=1
        )
        
        # Send transaction (EXATAMENTE como no exemplo oficial)
        receipt = await trader_client.sign_and_get_receipt(open_transaction)
        
        if receipt.get('status') == 1:
            tx_hash = receipt['transactionHash'].hex()
            logger.success(f"[{trader[:10]}] {side} {collateral} USDC @ {leverage}x - TX: {tx_hash[:10]}...")
            return True
        else:
            logger.error(f"[{trader[:10]}] {side} falhou - TX status != 1")
            return False
            
    except Exception as e:
        import traceback
        logger.error(f"[{trader[:10]}] Erro ao abrir {side}: {e}")
        logger.error(f"Detalhes: pair_index={pair_index}, collateral={collateral}, leverage={leverage}, trade_index={trade_index}")
        logger.debug(f"Stack trace: {traceback.format_exc()}")
        return False


# Manter a função antiga para compatibilidade
async def open_position(
    trader_client: TraderClient,
    pair_index: int,
    collateral: float,
    is_long: bool,
    leverage: int,
    trade_index: int = 0,
    tp: float = 0,
    sl: float = 0,
    wait_for_confirmation: bool = True
) -> bool:
    """Wrapper para compatibilidade"""
    return await open_position_direct(
        trader_client, pair_index, collateral, is_long, leverage, trade_index, tp, sl
    )


async def close_position(
    trader_client: TraderClient,
    pair_index: int,
    trade_index: int,
    collateral_to_close: float
) -> bool:
    """
    Fecha uma posição na Avantis.
    
    Args:
        trader_client: Cliente Avantis
        pair_index: Índice do par
        trade_index: Índice da trade
        collateral_to_close: Quantidade de colateral para fechar
        
    Returns:
        True se sucesso
    """
    trader = trader_client.get_signer().get_ethereum_address()
    
    try:
        close_transaction = await trader_client.trade.build_trade_close_tx(
            pair_index=pair_index,
            trade_index=trade_index,
            collateral_to_close=collateral_to_close,
            trader=trader
        )
        
        receipt = await trader_client.sign_and_get_receipt(close_transaction)
        
        if receipt.get('status') == 1:
            logger.success(f"[{trader[:10]}] Posição {trade_index} fechada (tx: {receipt['transactionHash'].hex()[:10]}...)")
            return True
        else:
            logger.error(f"[{trader[:10]}] Falha ao fechar posição {trade_index}")
            return False
            
    except Exception as e:
        logger.error(f"[{trader[:10]}] Erro ao fechar posição: {e}")
        return False
