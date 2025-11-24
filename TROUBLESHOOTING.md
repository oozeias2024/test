# 🔧 Guia de Solução de Problemas

## Erros Comuns e Soluções

### 1. FeeParametersRPC.get_opening_fee() got an unexpected keyword argument

**Erro completo:**
```
ERROR | [0x30C00E85] Erro ao abrir LONG: FeeParametersRPC.get_opening_fee() got an unexpected keyword argument 'trade_input'
```

**Causa:** API da SDK mudou.

**Solução:** ✅ Corrigido na v1.0.2 (cálculo de fees removido - SDK calcula automaticamente)

**Status:** ✅ Corrigido na v1.0.2

---

### 2. ImportError: cannot import name 'TradeInput'

**Erro completo:**
```
ImportError: cannot import name 'TradeInput' from 'avantis_trader_sdk'
```

**Causa:** Versão desatualizada ou imports incorretos.

**Solução:**
```bash
# Reinstalar a SDK
pip uninstall avantis-trader-sdk -y
pip install avantis-trader-sdk --upgrade

# Verificar instalação
python verify_install.py
```

**Status:** ✅ Corrigido na v1.0.1

---

### 2. ModuleNotFoundError: No module named 'avantis_trader_sdk'

**Causa:** SDK não instalada.

**Solução:**
```bash
pip install -r requirements.txt
```

---

### 3. FileNotFoundError: accounts.xlsx não encontrado

**Causa:** Arquivo de configuração faltando.

**Solução:**
```bash
# Verificar se existe
ls -la data/

# Se não existir, o arquivo está no diretório data/
cd data/
ls -la
```

O arquivo deve estar em `data/accounts.xlsx`, não na raiz.

---

### 4. Erro ao conectar com Base Network

**Erro:**
```
Error: Could not connect to RPC endpoint
```

**Soluções:**

1. **Verificar RPC URL:**
   ```python
   # Em src/config/constants.py
   BASE_RPC_URL = "https://mainnet.base.org"
   ```

2. **Testar RPC manualmente:**
   ```bash
   curl -X POST https://mainnet.base.org \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
   ```

3. **Usar RPC alternativo:**
   - Alchemy: `https://base-mainnet.g.alchemy.com/v2/YOUR_KEY`
   - Infura: `https://base-mainnet.infura.io/v3/YOUR_KEY`

---

### 5. Private key inválida

**Erro:**
```
ValueError: Invalid private key format
```

**Soluções:**

1. **Formato correto:**
   ```
   0x1234567890abcdef...  (deve começar com 0x)
   ```

2. **Verificar no Excel:**
   - Abra `data/accounts.xlsx`
   - Coluna `private_key` deve ter o formato completo
   - Não deve haver espaços extras

3. **Testar private key:**
   ```python
   from web3 import Web3
   w3 = Web3()
   account = w3.eth.account.from_key('0xSUA_PRIVATE_KEY')
   print(account.address)
   ```

---

### 6. Insufficient USDC balance

**Erro:**
```
Error: Insufficient USDC balance for trade
```

**Soluções:**

1. **Verificar saldo:**
   ```bash
   python main.py
   # Escolha opção 3 (Ver Status)
   ```

2. **Adicionar USDC:**
   - Bridge para Base Network: https://bridge.base.org/
   - Ou compre diretamente na Base

3. **Ajustar valores:**
   Edite `data/config.json`:
   ```json
   {
     "order_value_usd": {
       "min": 20,  // Reduza para testar
       "max": 50
     }
   }
   ```

---

### 7. Insufficient ETH for gas

**Erro:**
```
Error: Insufficient funds for gas
```

**Solução:**
1. Você precisa de ETH na Base Network para gas fees
2. Bridge ETH: https://bridge.base.org/
3. Valor mínimo recomendado: 0.01 ETH

---

### 8. Docker não encontra o bot

**Erro:**
```
docker: Error response from daemon: No such container
```

**Solução:**

1. **Build primeiro:**
   ```bash
   docker build -t avantis-bot .
   ```

2. **Executar:**
   ```bash
   # Windows PowerShell
   docker run --rm -it -v "${PWD}:/app" avantis-bot

   # Linux/Mac
   docker run --rm -it -v "$(pwd):/app" avantis-bot
   ```

---

### 9. Posições não abrem

**Possíveis causas:**

1. **Saldo insuficiente** - Verifique USDC + ETH
2. **Allowance não aprovado** - Bot deve aprovar automaticamente na 1ª vez
3. **Pair index inválido** - Par não disponível na Avantis
4. **Alavancagem muito alta** - Reduza `max_leverage` no config.json

**Debug:**
```bash
# Ver logs detalhados
tail -f logs/bot.log

# Executar teste
python test_setup.py
```

---

### 10. Posições não fecham

**Soluções:**

1. **Fechamento manual:**
   ```bash
   python main.py
   # Escolha opção 2 (Fechar Todas)
   ```

2. **Verificar logs:**
   ```bash
   tail -100 logs/bot.log | grep -i "fechar\|close"
   ```

3. **Verificar se existem:**
   ```bash
   python main.py
   # Escolha opção 3 (Ver Status)
   ```

---

## Comandos Úteis de Debug

### Verificar instalação completa
```bash
python verify_install.py
```

### Testar configuração
```bash
python test_setup.py
```

### Ver logs em tempo real
```bash
tail -f logs/bot.log
```

### Ver últimos erros
```bash
tail -50 logs/bot.log | grep -i "error\|exception"
```

### Verificar processos Docker
```bash
docker ps -a
docker logs <container_id>
```

### Limpar e reconstruir Docker
```bash
docker system prune -a
docker build -t avantis-bot .
```

---

## Checklist de Debug

Quando algo não funcionar, siga esta ordem:

- [ ] 1. Execute `python verify_install.py`
- [ ] 2. Verifique `data/accounts.xlsx` está configurado
- [ ] 3. Confirme saldo USDC + ETH na Base
- [ ] 4. Execute `python test_setup.py`
- [ ] 5. Verifique logs em `logs/bot.log`
- [ ] 6. Teste com valores mínimos (order_value_usd = 10-20)
- [ ] 7. Verifique RPC está respondendo
- [ ] 8. Confirme private key está correta

---

## Logs Importantes

### Log de sucesso (esperado):
```
15:30:45 | INFO     | ✅ Cliente inicializado: 0x742d35C...
15:30:47 | INFO     | Mercado selecionado: ETH/USD (index: 0)
15:30:49 | SUCCESS  | [0x742d35C] LONG 50.0 USDC @ 5x - Ordem enviada
15:30:51 | SUCCESS  | [0x742d35C] SHORT 50.0 USDC @ 5x - Ordem enviada
15:30:52 | INFO     | ✅ 2/2 posições abertas com sucesso
```

### Log de erro (requer atenção):
```
15:30:45 | ERROR    | ❌ Erro ao conectar com Avantis: ...
15:30:47 | ERROR    | Insufficient USDC balance
15:30:49 | ERROR    | Failed to open position: ...
```

---

## Contato e Suporte

Se o problema persistir:

1. Verifique os logs: `logs/bot.log`
2. Execute diagnóstico: `python test_setup.py`
3. Consulte documentação Avantis: https://sdk.avantisfi.com/
4. Revise o código em `src/` para entender o fluxo

---

## Versão Atual

**Bot:** v1.0.1  
**SDK:** avantis-trader-sdk >= 0.1.0  
**Python:** 3.10+

---

**Última atualização:** Correção de imports TradeInput/TradeInputOrderType
