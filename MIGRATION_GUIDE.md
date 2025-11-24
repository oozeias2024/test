# 📚 Guia de Migração: Paradex → Avantis

## Comparação Lado a Lado

### Arquitetura

| Aspecto | Paradex Bot | Avantis Bot |
|---------|-------------|-------------|
| **Network** | Starknet (Paradex) | Base (Ethereum L2) |
| **Contas necessárias** | 2 contas | 1 conta |
| **Estratégia Delta Neutro** | Long em conta A, Short em conta B | Long + Short na mesma conta |
| **SDK Principal** | starknet_py + custom | avantis-trader-sdk |
| **Linguagem de contratos** | Cairo/Starknet | Solidity/EVM |
| **Autenticação** | JWT Tokens | Private Key Ethereum |
| **RPC** | Paradex custom | Base RPC public/dedicated |

### Estrutura de Arquivos

| Arquivo | Paradex | Avantis | Mudanças |
|---------|---------|---------|----------|
| **accounts.xlsx** | 2+ contas | 1 conta | Simplificado |
| **active_pairs.xlsx** | Igual | Igual | Sem mudanças |
| **config.json** | Igual | Igual | Mesma estrutura |
| **src/paradex/** | ✅ | ❌ | Substituído por src/avantis/ |
| **src/avantis/** | ❌ | ✅ | Novo módulo |
| **requirements.txt** | starknet_py | avantis-trader-sdk | Dependências diferentes |

### Fluxo de Operação

#### Paradex Bot:
```
1. Carregar 2 contas ativas
2. Selecionar 1 conta para long, 1 para short
3. Abrir long na conta A
4. Abrir short na conta B (simultaneamente)
5. Monitorar ambas as contas
6. Fechar posição na conta A
7. Fechar posição na conta B
```

#### Avantis Bot:
```
1. Carregar 1 conta única
2. Selecionar par de trading
3. Abrir long (trade_index=0) na conta
4. Abrir short (trade_index=1) na conta (simultaneamente)
5. Monitorar ambas as posições
6. Fechar posição long (index=0)
7. Fechar posição short (index=1)
```

## Principais Diferenças Técnicas

### 1. Autenticação

**Paradex:**
```python
from starknet_py.net.account.account import Account
account = get_account(address, private_key)
jwt = get_jwt_token(account, proxy_str)
```

**Avantis:**
```python
from avantis_trader_sdk import TraderClient
trader_client = TraderClient(BASE_RPC_URL)
trader_client.set_local_signer(private_key)
```

### 2. Abertura de Posições

**Paradex:**
```python
# Conta A - Long
open_position(account_A, "BUY", "ETH-USD-PERP", size, proxy)

# Conta B - Short
open_position(account_B, "SELL", "ETH-USD-PERP", size, proxy)
```

**Avantis:**
```python
# Mesma conta - Long (index=0)
await open_position(
    trader_client, pair_index, collateral, 
    is_long=True, trade_index=0
)

# Mesma conta - Short (index=1)
await open_position(
    trader_client, pair_index, collateral, 
    is_long=False, trade_index=1
)
```

### 3. Buscar Posições

**Paradex:**
```python
# Para cada conta separadamente
positions_A = get_open_positions(account_A, proxy)
positions_B = get_open_positions(account_B, proxy)
```

**Avantis:**
```python
# Todas as posições da conta única
trades, pending = await trader_client.trade.get_trades(trader)
# Retorna: long (index=0) e short (index=1)
```

### 4. Fechamento

**Paradex:**
```python
# Fechar em cada conta
for account in [account_A, account_B]:
    pos = get_last_position_info(account, proxy)
    close_side = "SELL" if pos["side"] == "LONG" else "BUY"
    open_position(account, close_side, market, size, proxy)
```

**Avantis:**
```python
# Fechar cada posição pelo índice
for position in positions:
    await close_position(
        trader_client,
        pair_index=position["pair_index"],
        trade_index=position["trade_index"],
        collateral_to_close=position["collateral"]
    )
```

## Mudanças no Código

### position_manager.py

**Função `open_positions` - Paradex:**
```python
def open_positions(self, long_dist, short_dist, market):
    # Seleciona 2 contas diferentes
    df_shuffled = df_active.sample(frac=1).iloc[:2]
    
    # Conta 1 = Long
    execute_position(df_shuffled.iloc[0], "BUY", long_dist[0], market)
    
    # Conta 2 = Short
    execute_position(df_shuffled.iloc[1], "SELL", short_dist[0], market)
```

**Função `open_delta_neutral_positions` - Avantis:**
```python
async def open_delta_neutral_positions(self, pair_index, long_value, short_value):
    # Mesma conta, índices diferentes
    tasks = [
        open_position(
            self.trader_client, pair_index, long_value,
            is_long=True, trade_index=0  # Long
        ),
        open_position(
            self.trader_client, pair_index, short_value,
            is_long=False, trade_index=1  # Short
        )
    ]
    
    await asyncio.gather(*tasks)
```

### main.py

**Paradex:**
```python
def main():
    manager = TradingManager()
    manager.start_trading()  # Síncrono
```

**Avantis:**
```python
async def main():
    manager = TradingManager()
    await manager.start_trading()  # Assíncrono

if __name__ == "__main__":
    asyncio.run(main())
```

## Vantagens do Bot Avantis

✅ **Mais simples**: Apenas 1 conta para gerenciar
✅ **Menos complexo**: Não precisa gerenciar múltiplas contas
✅ **Mais eficiente**: Gas fees apenas para 1 conta
✅ **Hedge verdadeiro**: Long+Short na mesma conta (netting)
✅ **Menos erros**: Menos pontos de falha
✅ **SDK oficial**: Suporte da plataforma Avantis

## Desvantagens Potenciais

⚠️ **Dependência de índice**: Precisa gerenciar trade_index manualmente
⚠️ **Margin compartilhada**: Ambas posições usam a mesma margem
⚠️ **Liquidação conjunta**: Se uma liquida, pode afetar a outra

## Checklist de Migração

- [ ] Copiar estrutura de arquivos
- [ ] Adaptar accounts.xlsx (de 2 contas para 1)
- [ ] Manter active_pairs.xlsx igual
- [ ] Manter config.json igual
- [ ] Obter USDC na Base Network
- [ ] Obter ETH para gas na Base
- [ ] Testar com valores pequenos primeiro
- [ ] Validar com `python test_setup.py`
- [ ] Executar modo teste
- [ ] Monitorar logs cuidadosamente
- [ ] Escalar valores gradualmente

## FAQ de Migração

**Q: Posso usar a mesma private key do Paradex?**
A: Não diretamente. Paradex usa Starknet, Avantis usa Ethereum. São wallets diferentes.

**Q: Preciso transferir fundos?**
A: Sim. Você precisa de USDC + ETH na Base Network (não no Starknet).

**Q: O comportamento do bot é igual?**
A: Sim! A estratégia delta neutro é a mesma, apenas a implementação técnica mudou.

**Q: Posso rodar ambos os bots?**
A: Sim! São independentes. Rode em contas/networks diferentes.

**Q: Os pares de trading são os mesmos?**
A: Não necessariamente. Avantis tem sua própria lista de pares. Verifique em active_pairs.xlsx.

**Q: O monitoramento funciona igual?**
A: Sim! LTV checks, TP/SL, logs funcionam da mesma forma.

**Q: Proxies são suportados?**
A: Não implementado no bot Avantis por padrão, mas pode ser adicionado.

## Próximos Passos

1. ✅ Leia este guia completo
2. ✅ Configure accounts.xlsx com 1 conta
3. ✅ Obtenha USDC + ETH na Base
4. ✅ Execute `python test_setup.py`
5. ✅ Leia QUICK_START.md
6. ✅ Execute com valores baixos
7. ✅ Monitore por algumas horas
8. ✅ Escale gradualmente

## Suporte

Se encontrar problemas durante a migração:
1. Verifique os logs em `logs/bot.log`
2. Execute `python test_setup.py` para diagnóstico
3. Revise a documentação da Avantis SDK
4. Compare com o código do bot Paradex original

---

**Boa sorte com a migração!** 🚀
