#!/usr/bin/env python3
"""
Script de teste para validar a configuração do bot Avantis.
Execute este script antes de rodar o bot principal.
"""

import asyncio
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.config.constants import logger
from src.avantis.auth import get_trader_client
from src.avantis.account import get_usdc_balance, get_open_positions
from src.avantis.market import get_pair_index
import pandas as pd
from src.config.paths import DATA_DIR


async def test_configuration():
    """Testa a configuração do bot."""
    logger.info("=" * 60)
    logger.info("🔍 Testando Configuração do Bot Avantis")
    logger.info("=" * 60)
    
    errors = []
    warnings = []
    
    # 1. Testar arquivo accounts.xlsx
    logger.info("\n📁 Testando accounts.xlsx...")
    try:
        df_accounts = pd.read_excel(DATA_DIR / "accounts.xlsx")
        active_accounts = df_accounts[df_accounts["is_active"] == True]
        
        if len(active_accounts) == 0:
            errors.append("❌ Nenhuma conta ativa encontrada em accounts.xlsx")
        elif len(active_accounts) > 1:
            warnings.append("⚠️  Múltiplas contas ativas. Bot usará apenas a primeira.")
        else:
            logger.info("✅ Conta ativa encontrada")
            
        account = active_accounts.iloc[0]
        private_key = account["private_key"]
        address = account["address"]
        
        if not private_key or private_key == "0xSUA_PRIVATE_KEY_AQUI":
            errors.append("❌ Private key não configurada em accounts.xlsx")
        else:
            logger.info(f"✅ Private key presente (endereço: {address})")
            
    except FileNotFoundError:
        errors.append("❌ Arquivo accounts.xlsx não encontrado em data/")
    except Exception as e:
        errors.append(f"❌ Erro ao ler accounts.xlsx: {e}")
    
    # 2. Testar arquivo active_pairs.xlsx
    logger.info("\n📁 Testando active_pairs.xlsx...")
    try:
        df_pairs = pd.read_excel(DATA_DIR / "active_pairs.xlsx")
        active_pairs = df_pairs[df_pairs["active"] == True]
        
        if len(active_pairs) == 0:
            errors.append("❌ Nenhum par ativo em active_pairs.xlsx")
        else:
            logger.info(f"✅ {len(active_pairs)} pares ativos: {', '.join(active_pairs['symbol'].tolist())}")
            
    except FileNotFoundError:
        errors.append("❌ Arquivo active_pairs.xlsx não encontrado em data/")
    except Exception as e:
        errors.append(f"❌ Erro ao ler active_pairs.xlsx: {e}")
    
    # 3. Testar arquivo config.json
    logger.info("\n📁 Testando config.json...")
    try:
        import json
        with open(DATA_DIR / "config.json", 'r') as f:
            config = json.load(f)
        
        required_keys = ["order_value_usd", "max_leverage", "order_duration_min"]
        for key in required_keys:
            if key not in config:
                errors.append(f"❌ Chave '{key}' faltando em config.json")
        
        logger.info("✅ config.json válido")
        logger.info(f"   - Valores: ${config['order_value_usd']['min']}-${config['order_value_usd']['max']}")
        logger.info(f"   - Alavancagem: {config['max_leverage']}x")
        
    except FileNotFoundError:
        errors.append("❌ Arquivo config.json não encontrado em data/")
    except Exception as e:
        errors.append(f"❌ Erro ao ler config.json: {e}")
    
    # Se houver erros críticos, parar aqui
    if errors:
        logger.error("\n" + "=" * 60)
        logger.error("❌ ERROS CRÍTICOS ENCONTRADOS:")
        for error in errors:
            logger.error(error)
        logger.error("=" * 60)
        return False
    
    # 4. Testar conexão com Avantis
    logger.info("\n🌐 Testando conexão com Avantis...")
    try:
        trader_client = get_trader_client(private_key)
        trader_address = trader_client.get_signer().get_ethereum_address()
        logger.info(f"✅ Conectado! Endereço: {trader_address}")
        
        # 5. Testar saldo USDC
        logger.info("\n💰 Verificando saldo USDC...")
        balance = await get_usdc_balance(trader_client)
        logger.info(f"✅ Saldo USDC: ${balance:.2f}")
        
        if balance < 100:
            warnings.append(f"⚠️  Saldo USDC baixo: ${balance:.2f}. Recomendado: $500+")
        
        # 6. Verificar posições abertas
        logger.info("\n📊 Verificando posições abertas...")
        positions = await get_open_positions(trader_client)
        
        if positions:
            logger.info(f"⚠️  {len(positions)} posições já abertas:")
            for i, pos in enumerate(positions, 1):
                side = "LONG" if pos["is_long"] else "SHORT"
                logger.info(f"   {i}. {side} - ${pos['collateral']:.2f}")
        else:
            logger.info("✅ Nenhuma posição aberta")
        
        # 7. Testar pares de mercado
        logger.info("\n🔍 Testando pares de mercado...")
        test_pairs = ["ETH/USD", "BTC/USD"]
        
        for pair in test_pairs:
            try:
                pair_index = await get_pair_index(trader_client, pair)
                if pair_index is not None:
                    logger.info(f"✅ {pair} disponível (index: {pair_index})")
                else:
                    warnings.append(f"⚠️  Par {pair} não disponível")
            except Exception as e:
                warnings.append(f"⚠️  Erro ao testar {pair}: {e}")
        
    except Exception as e:
        errors.append(f"❌ Erro ao conectar com Avantis: {e}")
        logger.error(f"Erro: {e}", exc_info=True)
        return False
    
    # Resumo
    logger.info("\n" + "=" * 60)
    logger.info("📋 RESUMO DO TESTE")
    logger.info("=" * 60)
    
    if warnings:
        logger.warning("\n⚠️  AVISOS:")
        for warning in warnings:
            logger.warning(warning)
    
    if not errors:
        logger.info("\n✅ CONFIGURAÇÃO VÁLIDA!")
        logger.info("Você pode executar o bot com: python main.py")
        return True
    else:
        logger.error("\n❌ CONFIGURAÇÃO INVÁLIDA!")
        logger.error("Corrija os erros acima antes de executar o bot.")
        return False


async def main():
    try:
        success = await test_configuration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Teste interrompido")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
