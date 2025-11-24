# 🔧 Correção: Valores de Config.json Não Aplicados

## Problema Identificado

**Sintoma:**
```
Config.json está configurado para $1-$1
Mas o bot tenta abrir $10 long + $10 short
```

**Causas:**
1. ❌ Docker estava usando imagem antiga (com config padrão de $100-$300)
2. ❌ Havia um mínimo forçado de $10 no código (utils/calc.py)
3. ❌ Config.json do container não estava sendo sobrescrito pelo volume

## Correções Aplicadas (v1.0.3)

### 1. Removido Mínimo Forçado
**Arquivo:** `utils/calc.py`

**Antes:**
```python
# Garantir valores mínimos
long_value = max(long_value, 10)  # ❌ Forçava $10 mínimo
short_value = max(short_value, 10)
```

**Depois:**
```python
# Mínimo de apenas $1 para permitir testes
min_value = 1.0
long_value = max(long_value, min_value)  # ✅ Permite até $1
short_value = max(short_value, min_value)
```

### 2. Adicionado Debug de Config
**Arquivo:** `src/position_manager.py`

Agora ao iniciar, o bot mostra:
```
🔍 DEBUG - Configuração Carregada:
   order_value_usd: $1-$1
   max_leverage: 5x
   order_duration_min: 1-2 min
```

### 3. Logs Detalhados
Adicionado logs para ver exatamente qual valor está sendo usado:
```python
logger.debug(f"📊 Valores calculados: raw=1, max=..., final=1")
```

## Como Aplicar a Correção

### PowerShell (Windows):
```powershell
# 1. Limpar imagem antiga
docker rmi avantis-bot

# 2. Reconstruir
docker build -t avantis-bot .

# 3. Executar
docker run --rm -it -v "${PWD}:/app" avantis-bot
```

**OU use o script:**
```powershell
.\rebuild.ps1
docker run --rm -it -v "${PWD}:/app" avantis-bot
```

### Bash (Linux/Mac):
```bash
# 1. Limpar imagem antiga
docker rmi avantis-bot

# 2. Reconstruir
docker build -t avantis-bot .

# 3. Executar
docker run --rm -it -v "$(pwd):/app" avantis-bot
```

**OU use o script:**
```bash
chmod +x rebuild.sh
./rebuild.sh
docker run --rm -it -v "$(pwd):/app" avantis-bot
```

## Verificar se Funcionou

Ao executar, você deve ver:

**✅ CORRETO:**
```
🔍 DEBUG - Configuração Carregada:
   order_value_usd: $1-$1         ← Seu config
   max_leverage: 5x
   order_duration_min: 1-2 min

📊 Valores calculados: raw=1, max=..., final=1

Iniciando trade | Mercado: BTC/USD | 
Long: $0.50 | Short: $0.50        ← Correto: $1 dividido em 2
```

**❌ AINDA ERRADO:**
```
Iniciando trade | Mercado: BTC/USD | 
Long: $10.00 | Short: $10.00      ← Ainda usando valores antigos
```

Se ainda estiver errado:
1. Verifique que reconstruiu o Docker
2. Verifique que o config.json está no diretório correto
3. Execute sem Docker: `python main.py`

## Sobre o Erro "transfer amount exceeds balance"

Este erro ocorre quando:
- ✅ Saldo USDC insuficiente
- ✅ Allowance não aprovado

**Solução:**
1. **Verifique saldo:**
   ```bash
   python main.py
   # Escolha opção 3 (Ver Status)
   ```

2. **Valores mínimos recomendados:**
   - Para $1 de posição: tenha pelo menos $5 USDC
   - Para $10 de posição: tenha pelo menos $30 USDC
   - Para $100 de posição: tenha pelo menos $250 USDC
   
   *Nota: Valores maiores devido a fees, slippage e margem de segurança*

3. **Configure valores apropriados:**
   ```json
   {
     "order_value_usd": {
       "min": 20,    // Recomendado: $20+ para evitar erros
       "max": 50
     }
   }
   ```

## Valores Muito Pequenos

**⚠️ AVISO:** Valores muito pequenos ($1-$5) podem:
- Falhar devido a fees serem maiores que o valor
- Não ter liquidez suficiente
- Ser rejeitados pela exchange

**Recomendação:**
- Teste: $20-$50 por posição
- Produção: $100+ por posição

## Resumo das Mudanças

| Item | Antes | Depois |
|------|-------|--------|
| Mínimo forçado | $10 | $1 |
| Debug config | ❌ | ✅ |
| Logs detalhados | ❌ | ✅ |
| Rebuild script | ❌ | ✅ |

## Próximos Passos

1. ✅ Reconstrua Docker com `rebuild.ps1` ou manualmente
2. ✅ Verifique logs de configuração ao iniciar
3. ✅ Confirme valores de long/short estão corretos
4. ✅ Tenha saldo USDC suficiente (3-5x o valor da posição)
5. ✅ Ajuste config.json para valores realistas ($20+)

---

**Versão:** v1.0.3  
**Status:** ✅ Corrigido
