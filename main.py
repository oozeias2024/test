import asyncio
from src.position_manager import TradingManager
from src.config.constants import logger


async def main():
    """
    Ponto de entrada principal do bot Avantis Delta Neutro.
    """
    logger.info("="*60)
    logger.info("🚀 Avantis Delta Neutro Bot v1.0")
    logger.info("="*60)
    
    # Escolha da ação
    print("\nEscolha uma ação:")
    print("1 - Iniciar Trading (Delta Neutro)")
    print("2 - Fechar Todas as Posições")
    print("3 - Ver Status")
    
    action = input("\nDigite o número da ação (ou edite main.py para modo automático): ").strip()
    
    manager = TradingManager()
    
    if action == "1":
        logger.info("Modo: Iniciar Trading")
        await manager.start_trading()
    
    elif action == "2":
        logger.info("Modo: Fechar Todas as Posições")
        await manager.initialize_client()
        await manager.close_all_positions()
        logger.info("✅ Processo concluído")
    
    elif action == "3":
        logger.info("Modo: Ver Status")
        await manager.initialize_client()
        from src.avantis.account import get_open_positions, get_usdc_balance
        
        balance = await get_usdc_balance(manager.trader_client)
        positions = await get_open_positions(manager.trader_client)
        
        print(f"\n💰 Saldo USDC: ${balance:.2f}")
        print(f"📊 Posições abertas: {len(positions)}")
        
        if positions:
            for i, pos in enumerate(positions, 1):
                side = "LONG" if pos["is_long"] else "SHORT"
                print(f"\nPosição {i}:")
                print(f"  Tipo: {side}")
                print(f"  Colateral: ${pos['collateral']:.2f}")
                print(f"  Alavancagem: {pos['leverage']:.1f}x")
                print(f"  Preço Abertura: ${pos['open_price']:.2f}")
                print(f"  Preço Liquidação: ${pos['liquidation_price']:.2f}")
        
        logger.info("✅ Status exibido")
    
    else:
        logger.warning("Ação inválida. Saindo...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n⚠️ Bot interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}", exc_info=True)
