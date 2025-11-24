#!/usr/bin/env python3
"""
Script de verificação rápida da instalação.
Execute este script para garantir que todas as dependências estão instaladas corretamente.
"""

import sys

def verify_imports():
    """Verifica se todas as dependências necessárias podem ser importadas."""
    print("🔍 Verificando dependências...\n")
    
    errors = []
    warnings = []
    
    # 1. Verificar avantis-trader-sdk
    print("1. Verificando avantis-trader-sdk...")
    try:
        from avantis_trader_sdk import TraderClient
        from avantis_trader_sdk.types import TradeInput, TradeInputOrderType, MarginUpdateType
        print("   ✅ avantis-trader-sdk OK")
    except ImportError as e:
        errors.append(f"   ❌ Erro ao importar avantis-trader-sdk: {e}")
    
    # 2. Verificar web3
    print("2. Verificando web3...")
    try:
        import web3
        print("   ✅ web3 OK")
    except ImportError as e:
        errors.append(f"   ❌ Erro ao importar web3: {e}")
    
    # 3. Verificar pandas
    print("3. Verificando pandas...")
    try:
        import pandas
        print("   ✅ pandas OK")
    except ImportError as e:
        errors.append(f"   ❌ Erro ao importar pandas: {e}")
    
    # 4. Verificar openpyxl
    print("4. Verificando openpyxl...")
    try:
        import openpyxl
        print("   ✅ openpyxl OK")
    except ImportError as e:
        errors.append(f"   ❌ Erro ao importar openpyxl: {e}")
    
    # 5. Verificar loguru
    print("5. Verificando loguru...")
    try:
        from loguru import logger
        print("   ✅ loguru OK")
    except ImportError as e:
        errors.append(f"   ❌ Erro ao importar loguru: {e}")
    
    # 6. Verificar aiohttp
    print("6. Verificando aiohttp...")
    try:
        import aiohttp
        print("   ✅ aiohttp OK")
    except ImportError as e:
        errors.append(f"   ❌ Erro ao importar aiohttp: {e}")
    
    # 7. Verificar numpy
    print("7. Verificando numpy...")
    try:
        import numpy
        print("   ✅ numpy OK")
    except ImportError as e:
        errors.append(f"   ❌ Erro ao importar numpy: {e}")
    
    # 8. Verificar módulos internos
    print("\n8. Verificando módulos internos...")
    try:
        sys.path.insert(0, '.')
        from src.position_manager import TradingManager
        from src.avantis.auth import get_trader_client
        from src.avantis.trade import open_position, close_position
        from src.avantis.account import get_open_positions, get_usdc_balance
        from src.config.constants import logger
        print("   ✅ Módulos internos OK")
    except ImportError as e:
        errors.append(f"   ❌ Erro ao importar módulos internos: {e}")
    
    # 9. Verificar arquivos de dados
    print("\n9. Verificando arquivos de dados...")
    from pathlib import Path
    data_dir = Path("data")
    
    required_files = ["accounts.xlsx", "active_pairs.xlsx", "config.json"]
    for file in required_files:
        if (data_dir / file).exists():
            print(f"   ✅ {file} encontrado")
        else:
            warnings.append(f"   ⚠️  {file} não encontrado")
    
    # Resumo
    print("\n" + "=" * 60)
    print("📋 RESUMO DA VERIFICAÇÃO")
    print("=" * 60)
    
    if errors:
        print("\n❌ ERROS ENCONTRADOS:")
        for error in errors:
            print(error)
        print("\n💡 Solução: Execute 'pip install -r requirements.txt'")
        return False
    
    if warnings:
        print("\n⚠️  AVISOS:")
        for warning in warnings:
            print(warning)
        print("\n💡 Configure os arquivos em data/ antes de executar o bot.")
    
    if not errors:
        print("\n✅ TODAS AS DEPENDÊNCIAS INSTALADAS CORRETAMENTE!")
        print("\n🚀 Próximos passos:")
        print("   1. Configure data/accounts.xlsx com sua private key")
        print("   2. Execute: python test_setup.py")
        print("   3. Execute: python main.py")
        return True
    
    return False


if __name__ == "__main__":
    try:
        success = verify_imports()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
