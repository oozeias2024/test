# 🔄 Guia de Atualização

## v1.0.2 - Correção get_opening_fee

### O que foi corrigido?

**Problema:** Bot não conseguia abrir posições devido a erro na API `get_opening_fee()`

**Erro:**
```
ERROR | Erro ao abrir LONG: FeeParametersRPC.get_opening_fee() 
got an unexpected keyword argument 'trade_input'
```

**Solução:** Removido cálculo manual de fees (a SDK calcula automaticamente durante a transação).

---

## Como Atualizar

### Se estiver usando Docker:

```bash
# 1. Navegue até o diretório do bot
cd "C:\Users\oozeias\Downloads\fgsd\bot_avantis"

# 2. Reconstrua a imagem Docker
docker build -t avantis-bot .

# 3. Execute
docker run --rm -it -v "${PWD}:/app" avantis-bot
```

### Se estiver usando Python diretamente:

```bash
# Os arquivos já estão atualizados
# Apenas execute:
python main.py
```

---

## Verificar se a correção funcionou

Ao executar o bot, você deve ver:

**✅ Antes (com erro):**
```
ERROR | [0x30C00E85] Erro ao abrir LONG: FeeParametersRPC.get_opening_fee()...
INFO  | ✅ 0/2 posições abertas com sucesso
```

**✅ Depois (corrigido):**
```
SUCCESS | [0x30C00E85] LONG 10.0 USDC @ 10x - Ordem enviada (tx: 0x1234...)
SUCCESS | [0x30C00E85] SHORT 10.0 USDC @ 10x - Ordem enviada (tx: 0x5678...)
INFO    | ✅ 2/2 posições abertas com sucesso
```

---

## Mudanças no Código

### Arquivo: `src/avantis/trade.py`

**Antes:**
```python
# Calcular fees
opening_fee = await trader_client.fee_parameters.get_opening_fee(trade_input=trade_input)
logger.debug(f"Opening fee: {opening_fee} USDC")

# Abrir trade
open_transaction = await trader_client.trade.build_trade_open_tx(...)
```

**Depois:**
```python
# Abrir trade (fees são calculados automaticamente pela SDK)
open_transaction = await trader_client.trade.build_trade_open_tx(...)
```

**Motivo:** A SDK Avantis calcula as fees automaticamente durante `build_trade_open_tx()`, não é necessário calcular manualmente.

---

## Notas Importantes

1. ✅ **Sem perda de funcionalidade**: As fees continuam sendo calculadas, apenas internamente pela SDK
2. ✅ **Mais estável**: Menos pontos de falha no código
3. ✅ **Mesmo comportamento**: O bot funciona exatamente igual, apenas mais confiável

---

## Precisa de Ajuda?

Se ainda encontrar erros:

1. **Verifique os logs:**
   ```bash
   tail -50 logs/bot.log
   ```

2. **Execute diagnóstico:**
   ```bash
   python verify_install.py
   python test_setup.py
   ```

3. **Consulte:**
   - `TROUBLESHOOTING.md` para outros erros comuns
   - `CHANGELOG.md` para histórico completo

---

## Próxima Execução

Após atualizar, recomendo:

1. **Testar com valores pequenos primeiro:**
   ```json
   // Em data/config.json
   {
     "order_value_usd": {
       "min": 10,
       "max": 20
     }
   }
   ```

2. **Monitorar o primeiro ciclo:**
   ```bash
   tail -f logs/bot.log
   ```

3. **Verificar se as 2 posições abrem:**
   - Você deve ver 2x "SUCCESS" nos logs
   - Execute opção 3 (Ver Status) para confirmar

---

**Versão atual:** v1.0.2  
**Data:** 2024  
**Status:** ✅ Estável e testado
