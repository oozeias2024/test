# 📋 Explicação Completa do config.json

## Configuração Atual vs Recomendada

### ⚠️ Sua Configuração Atual:

```json
{
  "order_value_usd": {
    "min": 1,
    "max": 1
  },
  "order_duration_min": {
    "min": 1,
    "max": 2
  },
  "delay_between_trading_cycles_min": {
    "min": 0,
    "max": 1
  },
  "ltv_checks_sec": {
    "min": 30,
    "max": 60
  },
  "price_checks_sec": {
    "min": 5,
    "max": 10
  },
  "max_leverage": 5,
  "orders_distribution_noise": 0,
  "retries": 3,
  "debug_level": "INFO"
}
```

---

## 📖 Explicação Campo por Campo

### 1. `order_value_usd`
```json
"order_value_usd": {
  "min": 1,    // ❌ MUITO BAIXO!
  "max": 1     // ❌ MUITO BAIXO!
}
```

**O que faz:**
- Define o valor TOTAL em USD que será dividido entre long e short
- `min`: Valor mínimo da ordem
- `max`: Valor máximo da ordem
- Bot escolhe aleatoriamente entre min e max

**Seu caso:**
- Total: $1
- Long: $1 ÷ 2 = $0.50
- Short: $1 ÷ 2 = $0.50

**❌ PROBLEMA:**
- Avantis requer mínimo ~$10 por posição
- Você está usando $0.50 por posição
- **ERRO GARANTIDO:** "BELOW_MIN_POS"

**✅ RECOMENDAÇÃO:**
```json
"order_value_usd": {
  "min": 20,   // $10 long + $10 short
  "max": 100   // $50 long + $50 short
}
```

**Por quê diferentes?**
- `min != max` → Bot varia o tamanho das ordens (mais natural)
- `min == max` → Bot sempre usa mesmo valor (previsível)

---

### 2. `order_duration_min`
```json
"order_duration_min": {
  "min": 1,    // ✅ OK - 1 minuto mínimo
  "max": 2     // ✅ OK - 2 minutos máximo
}
```

**O que faz:**
- Define quanto tempo as posições ficam abertas (em minutos)
- Bot escolhe aleatoriamente entre min e max
- Após esse tempo, fecha AMBAS as posições

**Seu caso:**
- Bot escolhe: 1 ou 2 minutos aleatoriamente
- Se escolher 2 min → Fecha EXATAMENTE após 120 segundos

**✅ Está BOM!** Mas considere:

**Para testes rápidos:**
```json
"order_duration_min": {
  "min": 1,
  "max": 2
}
```

**Para operação normal:**
```json
"order_duration_min": {
  "min": 5,
  "max": 15
}
```

**Para longo prazo:**
```json
"order_duration_min": {
  "min": 30,
  "max": 60
}
```

---

### 3. `delay_between_trading_cycles_min`
```json
"delay_between_trading_cycles_min": {
  "min": 0,    // ⚠️ MUITO RÁPIDO!
  "max": 1     // ⚠️ MUITO RÁPIDO!
}
```

**O que faz:**
- Tempo de ESPERA entre um ciclo e outro (em minutos)
- Após fechar posições, aguarda esse tempo antes de abrir novas

**Seu caso:**
- Bot aguarda 0-1 minuto entre ciclos
- **Ciclo completo:** 1-2 min (posições) + 0-1 min (espera) = 1-3 min

**⚠️ PROBLEMA:**
- Muito rápido pode causar:
  - Muitas transações (gas caro)
  - Parecer "spam" para a exchange
  - Não dar tempo de confirmar fechamento

**✅ RECOMENDAÇÃO:**
```json
"delay_between_trading_cycles_min": {
  "min": 2,    // Mínimo 2 minutos
  "max": 5     // Máximo 5 minutos
}
```

**Frequência resultante:**
- Ciclo: 1-2 min + Espera: 2-5 min = **Total: 3-7 min por ciclo**
- **~10-20 ciclos por hora**

---

### 4. `ltv_checks_sec`
```json
"ltv_checks_sec": {
  "min": 30,   // ✅ OK
  "max": 60    // ✅ OK
}
```

**O que faz:**
- Intervalo de checagem durante monitoramento (em segundos)
- Bot verifica posições a cada X segundos
- **Atualmente NÃO USADO** (código usa 10s fixo)

**✅ Pode REMOVER** ou atualizar código para usar

---

### 5. `price_checks_sec`
```json
"price_checks_sec": {
  "min": 5,    // Não usado
  "max": 10    // Não usado
}
```

**O que faz:**
- Deveria definir frequência de checagem de preço
- **Atualmente NÃO USADO** no código

**✅ Pode REMOVER**

---

### 6. `max_leverage`
```json
"max_leverage": 5   // ✅ CONSERVADOR (BOM!)
```

**O que faz:**
- Define a alavancagem máxima das posições
- Maior alavancagem = Maior risco de liquidação

**Seu caso:**
- 5x leverage é **conservador**

**Opções:**

**Ultra-conservador (iniciante):**
```json
"max_leverage": 2
```

**Conservador (recomendado):**
```json
"max_leverage": 5   // ✅ Você está aqui
```

**Moderado:**
```json
"max_leverage": 10
```

**Agressivo (risco alto):**
```json
"max_leverage": 20  // ⚠️ Cuidado!
```

**✅ SEU VALOR ESTÁ ÓTIMO!**

---

### 7. `orders_distribution_noise`
```json
"orders_distribution_noise": 0   // ✅ OK
```

**O que faz:**
- Adiciona variação aleatória no tamanho long vs short
- `0` = Perfeitamente igual (50/50)
- `0.1` = Até 10% de variação

**Exemplo com noise=0.1:**
- Total: $100
- Long: $55 (50 + 10% variação)
- Short: $45 (50 - 10% variação)

**Seu caso:**
- `0` = Sempre 50/50 exato
- **✅ PERFEITO para delta neutro!**

**Não mude!** Mantenha em 0.

---

### 8. `retries`
```json
"retries": 3   // ✅ OK
```

**O que faz:**
- Número de tentativas em caso de falha
- **Atualmente pouco usado** no código

**✅ Pode manter ou remover**

---

### 9. `debug_level`
```json
"debug_level": "INFO"   // ✅ OK
```

**O que faz:**
- Define nível de logs
- Opções: "DEBUG", "INFO", "WARNING", "ERROR"

**Seu caso:**
- `INFO` = Logs normais (recomendado)

**Para mais detalhes:**
```json
"debug_level": "DEBUG"
```

**Para menos logs:**
```json
"debug_level": "WARNING"
```

**✅ ESTÁ BOM!**

---

### 10. **FALTANDO:** `nonce_delay_seconds`

**Você NÃO TEM esse campo!** Mas ele é importante:

```json
"nonce_delay_seconds": 0.3
```

**O que faz:**
- Tempo entre abertura de long e short (em segundos)
- Previne conflito de nonce
- 0.3s = 300ms (quase instantâneo)

**✅ ADICIONE ESSE CAMPO!**

---

## 🎯 Configuração Recomendada COMPLETA

### Para TESTES (valores baixos):
```json
{
  "order_value_usd": {
    "min": 20,     // $10 long + $10 short (mínimo funcional)
    "max": 40      // $20 long + $20 short
  },
  "order_duration_min": {
    "min": 1,      // 1 minuto mínimo
    "max": 2       // 2 minutos máximo
  },
  "delay_between_trading_cycles_min": {
    "min": 1,      // 1 minuto entre ciclos
    "max": 2       // 2 minutos máximo
  },
  "max_leverage": 5,             // Conservador
  "nonce_delay_seconds": 0.3,    // 300ms entre long/short
  "orders_distribution_noise": 0, // Sempre 50/50
  "debug_level": "INFO",
  
  "_comment_1": "Valores para TESTE - Mínimo funcional na Avantis",
  "_comment_2": "order_value_usd: mínimo $20 = $10 cada posição",
  "_comment_3": "nonce_delay_seconds: 0.3s recomendado (pode usar 0.2-0.5)",
  "_comment_4": "Ciclo total: ~3-4 min (1-2min posições + 1-2min espera)"
}
```

### Para PRODUÇÃO (valores normais):
```json
{
  "order_value_usd": {
    "min": 100,    // $50 long + $50 short
    "max": 300     // $150 long + $150 short
  },
  "order_duration_min": {
    "min": 5,      // 5 minutos mínimo
    "max": 15      // 15 minutos máximo
  },
  "delay_between_trading_cycles_min": {
    "min": 3,      // 3 minutos entre ciclos
    "max": 10      // 10 minutos máximo
  },
  "max_leverage": 10,            // Moderado
  "nonce_delay_seconds": 0.3,    // 300ms entre long/short
  "orders_distribution_noise": 0, // Sempre 50/50
  "debug_level": "INFO",
  
  "_comment_1": "Valores para PRODUÇÃO",
  "_comment_2": "Saldo recomendado: $1500+ USDC",
  "_comment_3": "Ciclo total: ~15-25 min"
}
```

---

## 📊 Comparação: Seu Config vs Recomendado

| Campo | Seu Valor | Recomendado | Status |
|-------|-----------|-------------|--------|
| order_value min | $1 | $20-$100 | ❌ Muito baixo |
| order_value max | $1 | $40-$300 | ❌ Muito baixo |
| duration min | 1 min | 1-5 min | ✅ OK |
| duration max | 2 min | 2-15 min | ✅ OK |
| delay min | 0 min | 1-3 min | ⚠️ Muito rápido |
| delay max | 1 min | 2-10 min | ⚠️ Muito rápido |
| leverage | 5x | 5-10x | ✅ Ótimo |
| noise | 0 | 0 | ✅ Perfeito |
| nonce_delay | ❌ Falta | 0.3s | ❌ Adicionar |

---

## 🔧 Campos a REMOVER (não usados):

```json
// REMOVER estes:
"ltv_checks_sec": {...},    // Não usado
"price_checks_sec": {...},  // Não usado
"retries": 3                // Pouco usado
```

---

## ✅ Configuração FINAL Recomendada

```json
{
  "order_value_usd": {
    "min": 20,
    "max": 100,
    "_comment": "Valor total dividido em 2 (long + short). Min $20 = $10 cada"
  },
  "order_duration_min": {
    "min": 2,
    "max": 5,
    "_comment": "Quanto tempo posições ficam abertas (minutos)"
  },
  "delay_between_trading_cycles_min": {
    "min": 2,
    "max": 5,
    "_comment": "Tempo de espera entre ciclos (minutos)"
  },
  "max_leverage": 5,
  "nonce_delay_seconds": 0.3,
  "orders_distribution_noise": 0,
  "debug_level": "INFO",
  
  "_info_1": "=== DELTA NEUTRO CONFIG ===",
  "_info_2": "Mínimos Avantis: ~$10 por posição",
  "_info_3": "Saldo recomendado: 3-4x order_value_usd",
  "_info_4": "Exemplo: order_value=$100 → Tenha $300-400 USDC",
  "_info_5": "nonce_delay: 0.2s (rápido) | 0.3s (padrão) | 0.5s (seguro)",
  "_info_6": "Ciclo completo: ~4-10 min (2-5min trade + 2-5min delay)"
}
```

---

## 🎯 Resumo de Mudanças Necessárias

### ❌ Críticas (OBRIGATÓRIAS):

1. **order_value_usd:**
   - Atual: $1 → $0.50 cada (❌ abaixo do mínimo)
   - Mudar para: $20 mínimo → $10 cada (✅)

2. **nonce_delay_seconds:**
   - Atual: ❌ Não existe
   - Adicionar: 0.3 (✅)

### ⚠️ Recomendadas:

3. **delay_between_cycles:**
   - Atual: 0-1 min (muito rápido)
   - Mudar para: 2-5 min (melhor)

4. **Remover campos não usados:**
   - ltv_checks_sec
   - price_checks_sec
   - retries

---

## 💡 Sugestões por Caso de Uso

### 🧪 TESTE RÁPIDO (primeiros usos):
```json
{
  "order_value_usd": {"min": 20, "max": 40},
  "order_duration_min": {"min": 1, "max": 2},
  "delay_between_trading_cycles_min": {"min": 1, "max": 2},
  "max_leverage": 2,
  "nonce_delay_seconds": 0.3
}
```
**Ciclos/hora:** ~20  
**Saldo necessário:** $150 USDC

### ⚖️ OPERAÇÃO NORMAL:
```json
{
  "order_value_usd": {"min": 50, "max": 150},
  "order_duration_min": {"min": 3, "max": 10},
  "delay_between_trading_cycles_min": {"min": 2, "max": 5},
  "max_leverage": 5,
  "nonce_delay_seconds": 0.3
}
```
**Ciclos/hora:** ~6-8  
**Saldo necessário:** $500 USDC

### 🏢 PRODUÇÃO:
```json
{
  "order_value_usd": {"min": 100, "max": 500},
  "order_duration_min": {"min": 10, "max": 30},
  "delay_between_trading_cycles_min": {"min": 5, "max": 15},
  "max_leverage": 10,
  "nonce_delay_seconds": 0.3
}
```
**Ciclos/hora:** ~2-3  
**Saldo necessário:** $2000 USDC

---

**Precisa de ajuda para escolher? Diga seu objetivo e saldo disponível!**
