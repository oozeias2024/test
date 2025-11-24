# 💰 Valores Mínimos e Recomendados

## ⚠️ Erro: BELOW_MIN_POS

**Sintoma:**
```
ERROR | Erro ao abrir LONG: execution reverted: BELOW_MIN_POS
```

**Causa:** Avantis requer um valor mínimo por posição (~$20 USD).

---

## 📊 Valores da Avantis

### Mínimos Absolutos:
- **Por posição (long ou short):** ~$20 USD
- **Total por ciclo:** ~$40 USD ($20 long + $20 short)

### Valores Recomendados:

| Finalidade | order_value_usd | Por posição | Total necessário* |
|------------|-----------------|-------------|-------------------|
| **Teste mínimo** | $40-$60 | $20-$30 | $150+ USDC |
| **Teste normal** | $100-$200 | $50-$100 | $400+ USDC |
| **Produção** | $200-$500 | $100-$250 | $1000+ USDC |
| **Alto volume** | $500+ | $250+ | $2000+ USDC |

*Inclui margem para fees, slippage e segurança (3-4x o valor da posição)

---

## ⚙️ Configuração Recomendada

### Para Teste (Mínimo Funcional):
```json
{
  "order_value_usd": {
    "min": 40,
    "max": 60
  },
  "max_leverage": 5
}
```

**Saldo necessário:** ~$200 USDC + ETH para gas

---

### Para Produção (Estável):
```json
{
  "order_value_usd": {
    "min": 100,
    "max": 200
  },
  "max_leverage": 10
}
```

**Saldo necessário:** ~$600 USDC + ETH para gas

---

## 🧮 Como Calcular

### Fórmula:
```
order_value_usd ÷ 2 = Valor por posição

Exemplo:
- Config: order_value_usd = $40
- Long: $40 ÷ 2 = $20 ✅ (acima do mínimo)
- Short: $40 ÷ 2 = $20 ✅ (acima do mínimo)

- Config: order_value_usd = $30 ❌
- Long: $30 ÷ 2 = $15 ❌ (abaixo do mínimo de $20)
- Short: $30 ÷ 2 = $15 ❌ (abaixo do mínimo de $20)
```

### Saldo Total Necessário:
```
Saldo USDC = (order_value_usd × 3) + margem de segurança

Exemplo para $100 order_value:
- Posições: $100 ($50 long + $50 short)
- Margem: $100 (para alavancagem)
- Fees: ~$10 (estimativa)
- Segurança: $50 (buffer)
Total: ~$260 USDC mínimo
```

---

## 🚨 Erros Comuns

### 1. "BELOW_MIN_POS"
**Problema:** Valor de posição < $20

**Solução:**
```json
// ❌ Errado (muito pequeno)
{
  "order_value_usd": {
    "min": 10,
    "max": 20
  }
}

// ✅ Correto
{
  "order_value_usd": {
    "min": 40,
    "max": 100
  }
}
```

### 2. "transfer amount exceeds balance"
**Problema:** Saldo USDC insuficiente

**Solução:**
1. Verifique saldo: Execute opção 3 no bot
2. Adicione USDC via bridge: https://bridge.base.org/
3. OU reduza order_value_usd para valores que você tem

### 3. "Insufficient funds for gas"
**Problema:** Sem ETH para gas fees

**Solução:**
1. Adicione ETH na Base Network
2. Mínimo recomendado: 0.01 ETH

---

## 💡 Dicas

### Para Começar:
1. **Comece com valores seguros:**
   ```json
   {
     "order_value_usd": {"min": 50, "max": 100}
   }
   ```

2. **Verifique saldo antes:**
   ```bash
   python main.py
   # Escolha opção 3 (Ver Status)
   ```

3. **Teste 1-2 ciclos primeiro:**
   - Monitore logs
   - Confirme que abre 2 posições
   - Verifique que fecha corretamente

### Para Escalar:
1. Aumente gradualmente:
   ```
   $50 → $100 → $200 → $500
   ```

2. Mantenha saldo 3-4x maior que order_value_usd

3. Monitore via logs: `tail -f logs/bot.log`

---

## 📋 Checklist Antes de Executar

- [ ] Config.json tem order_value_usd ≥ $40
- [ ] Saldo USDC ≥ 3× order_value_usd
- [ ] Saldo ETH ≥ 0.01 (para gas)
- [ ] Rebuild Docker após mudanças
- [ ] Primeira execução: monitore logs

---

## 🔍 Verificar Valores Atuais

O bot agora mostra ao iniciar:

```
🔍 DEBUG - Configuração Carregada:
   order_value_usd: $40-$100       ← Seu config
   max_leverage: 5x

Iniciando trade | Mercado: BTC/USD | 
Long: $20.00 | Short: $20.00       ← Cada posição
```

Se ver valores < $20, aumente no config.json!

---

## ⚙️ Config Padrão Atualizado

O arquivo `data/config.json` já vem com valores seguros:

```json
{
  "order_value_usd": {
    "min": 40,    // Mínimo seguro
    "max": 100    // Máximo para teste
  },
  "max_leverage": 5,
  "_comment": "Avantis requer ~$20 por posição"
}
```

**Não precisa editar se quiser começar com valores seguros!**

---

## 📞 Suporte

Se ainda tiver problemas:

1. **Verifique logs:** `tail -50 logs/bot.log`
2. **Execute diagnóstico:** `python test_setup.py`
3. **Consulte:** `TROUBLESHOOTING.md`

---

**Versão:** v1.0.3  
**Atualizado:** Com validação de valores mínimos
