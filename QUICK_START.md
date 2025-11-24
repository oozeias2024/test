# 🚀 Guia Rápido de Início

## Passo 1: Configure sua conta

Edite o arquivo `data/accounts.xlsx`:

```
private_key          | address                                    | is_active
0xSUA_PRIVATE_KEY   | 0xSEU_ENDERECO_ETHEREUM                   | True
```

**Como obter:**
- **Private Key**: Exporte do MetaMask ou outra wallet
- **Address**: Seu endereço público Ethereum
- **is_active**: Sempre True (já que é apenas 1 conta)

## Passo 2: Verifique seu saldo

Certifique-se de ter na **Base Network**:
- ✅ USDC suficiente (para as posições)
- ✅ ETH suficiente (para gas fees)

**Valores mínimos recomendados:**
- USDC: $500+ 
- ETH: 0.01+ (para gas)

## Passo 3: Configure os pares

Edite `data/active_pairs.xlsx` para escolher quais ativos quer operar:

```
symbol    | active
ETH/USD   | True
BTC/USD   | True
SOL/USD   | False
```

## Passo 4: Ajuste as configurações

Edite `data/config.json` se quiser mudar:
- Valores das ordens
- Duração das posições
- Alavancagem máxima
- Intervalos entre ciclos

**Configuração conservadora (recomendada para início):**
```json
{
  "order_value_usd": {"min": 50, "max": 100},
  "order_duration_min": {"min": 1, "max": 2},
  "max_leverage": 5
}
```

## Passo 5: Execute o bot

### Usando Docker:
```bash
docker build -t avantis-bot .
docker run --rm -it -v "${PWD}:/app" avantis-bot
```

### Sem Docker:
```bash
python main.py
```

## Passo 6: Escolha o modo

Quando o bot iniciar, escolha:

**1** = Iniciar Trading (automático)
**2** = Fechar todas as posições
**3** = Ver status da conta

## 📊 O que vai acontecer (Modo 1):

```
1. Bot carrega suas configurações
2. Conecta à sua conta Avantis
3. Seleciona um par aleatório (ex: ETH/USD)
4. Calcula quanto alocar (ex: $100)
5. Abre SIMULTANEAMENTE:
   - LONG  $50 @ 5x (trade_index=0)
   - SHORT $50 @ 5x (trade_index=1)
6. Monitora as posições por X minutos
7. Fecha ambas as posições
8. Aguarda intervalo
9. Repete do passo 3
```

## ⚠️ Checklist Antes de Começar

- [ ] Private key configurada corretamente
- [ ] Saldo USDC suficiente na Base Network
- [ ] Saldo ETH para gas fees
- [ ] Aprovação USDC (bot faz automaticamente na 1ª vez)
- [ ] Pares de trading selecionados
- [ ] Configurações revisadas

## 🎯 Primeira Execução - Modo Teste

**Recomendação:** Teste primeiro com valores pequenos!

1. Configure `order_value_usd` para valores baixos (ex: $20-50)
2. Execute o bot
3. Observe 1-2 ciclos completos
4. Verifique os logs em `logs/bot.log`
5. Se tudo funcionar bem, aumente os valores

## 📝 Monitoramento

Durante a execução, você verá logs como:

```
15:30:45 | INFO     | ✅ Cliente inicializado: 0x742d35C...
15:30:47 | INFO     | Mercado selecionado: ETH/USD (index: 0)
15:30:49 | SUCCESS  | [0x742d35C] LONG 50.0 USDC @ 5x - Ordem enviada
15:30:51 | SUCCESS  | [0x742d35C] SHORT 50.0 USDC @ 5x - Ordem enviada
15:30:52 | INFO     | ✅ 2/2 posições abertas com sucesso
15:30:52 | INFO     | Posições abertas. Monitorando por 1 minutos...
```

## 🛑 Como Parar o Bot

1. **Gracefully**: Pressione `Ctrl+C` uma vez
2. **Force**: Pressione `Ctrl+C` duas vezes
3. **Emergência**: Execute novamente e escolha opção 2 (Fechar tudo)

## 💡 Dicas

1. **Comece devagar**: Use valores pequenos até entender o funcionamento
2. **Monitore logs**: Fique atento aos logs por possíveis erros
3. **Saldo seguro**: Mantenha sempre saldo extra para imprevistos
4. **Alavancagem**: Comece com alavancagem baixa (3-5x)
5. **Teste horários**: Teste em horários de baixa volatilidade primeiro

## ❓ FAQ Rápido

**Q: Quantas contas preciso?**
A: Apenas UMA conta Avantis.

**Q: Preciso de duas wallets?**
A: Não! Diferente do Paradex, uma conta única basta.

**Q: O bot opera 24/7?**
A: Sim, se você deixá-lo rodando. Ele abre e fecha posições continuamente.

**Q: É seguro?**
A: O bot executa operações delta neutro (hedge), mas sempre há riscos. Use valores que você pode perder.

**Q: Posso modificar a estratégia?**
A: Sim! Edite o arquivo `src/position_manager.py` para implementar sua própria lógica.

## 🆘 Problemas Comuns

| Problema | Solução |
|----------|---------|
| "Module not found" | Execute `pip install -r requirements.txt` |
| "Insufficient balance" | Adicione USDC na Base Network |
| "Gas estimation failed" | Adicione ETH para gas |
| "Allowance error" | O bot deve aprovar automaticamente |
| Posições não abrem | Verifique logs em `logs/bot.log` |

## 📞 Próximos Passos

Depois que estiver confortável:

1. Aumente os valores das ordens
2. Ajuste a alavancagem
3. Adicione mais pares de trading
4. Customize a estratégia
5. Implemente TP/SL automático

---

**Pronto para começar?** Execute `python main.py` e escolha opção 1! 🚀
