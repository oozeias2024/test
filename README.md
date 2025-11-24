# Avantis Delta Neutral Bot

Bot automatizado para operações delta neutro na plataforma Avantis (Base Network).

## 🎯 O que o bot faz?

- **Opera em UMA ÚNICA conta** na Avantis (ao contrário do bot Paradex que usa 2 contas)
- **Abre posições long + short simultaneamente** no mesmo ativo para hedging
- **Monitora automaticamente** as posições por duração configurável
- **Fecha automaticamente** as posições ao fim do ciclo
- **Repete o processo** continuamente com intervalos configuráveis

## 📋 Diferenças principais do bot Paradex

| Aspecto | Paradex Bot | Avantis Bot |
|---------|-------------|-------------|
| **Contas** | 2 contas diferentes | 1 conta única |
| **Network** | Starknet (Paradex) | Base (Ethereum L2) |
| **Hedging** | 1 long em conta A, 1 short em conta B | Long + short na mesma conta |
| **Trade Index** | N/A | 0 para long, 1 para short |
| **SDK** | starknet_py + custom | avantis-trader-sdk |
| **Autenticação** | JWT tokens | Private key Ethereum |

## 🚀 Setup

### Opção 1: Com Docker (Recomendado)

```bash
# 1. Build da imagem
docker build -t avantis-bot .

# 2. Executar o bot
docker run --rm -it -v "${PWD}:/app" avantis-bot
```

### Opção 2: Instalação Local

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar o bot
python main.py
```

## ⚙️ Configuração

### 1. Arquivo `data/accounts.xlsx`

Configure sua conta Avantis (apenas UMA conta necessária):

| private_key | address | is_active |
|-------------|---------|-----------|
| 0xSUA_PRIVATE_KEY | 0xSEU_ENDERECO | True |

**⚠️ IMPORTANTE:** 
- Use sua private key completa (com 0x no início)
- Certifique-se de ter USDC suficiente na Base Network
- Aprove USDC para o contrato Avantis (o bot faz isso automaticamente na primeira vez)

### 2. Arquivo `data/active_pairs.xlsx`

Escolha os pares de trading:

| symbol | active |
|--------|--------|
| ETH/USD | True |
| BTC/USD | True |
| SOL/USD | False |

### 3. Arquivo `data/config.json`

Configure os parâmetros de trading:

```json
{
  "order_value_usd": {
    "min": 100,
    "max": 300
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
  "max_leverage": 10,
  "orders_distribution_noise": 0,
  "retries": 3,
  "debug_level": "INFO"
}
```

**Parâmetros explicados:**

- **order_value_usd**: Valor total da posição (será dividido entre long/short)
- **order_duration_min**: Quanto tempo as posições ficam abertas
- **delay_between_trading_cycles_min**: Intervalo entre ciclos
- **ltv_checks_sec**: Frequência de checagem das posições
- **max_leverage**: Alavancagem máxima permitida
- **orders_distribution_noise**: Variação no tamanho das ordens (0 = igual)
- **retries**: Tentativas em caso de falha

## 🎮 Modos de Operação

Ao executar `python main.py`, você pode escolher:

**1. Iniciar Trading (Delta Neutro)**
- Inicia o loop automático de trading
- Abre long+short simultaneamente
- Monitora e fecha ao final do ciclo
- Repete indefinidamente

**2. Fechar Todas as Posições**
- Fecha todas as posições abertas imediatamente
- Útil para emergências

**3. Ver Status**
- Mostra saldo USDC
- Lista todas as posições abertas
- Informações detalhadas de cada posição

## 📊 Como funciona o Delta Neutro

```
Exemplo com $200 USD:

1. Bot seleciona ETH/USD
2. Abre 2 posições simultâneas:
   - LONG  $100 @ 10x (trade_index=0)
   - SHORT $100 @ 10x (trade_index=1)
3. Monitora por X minutos
4. Fecha ambas as posições
5. Aguarda intervalo
6. Repete com outro ativo
```

**Resultado:** Exposição delta neutra (hedge perfeito)

## 🔧 Estrutura do Projeto

```
bot_avantis/
├── main.py                    # Ponto de entrada
├── requirements.txt           # Dependências Python
├── Dockerfile                 # Container Docker
├── README.md                  # Este arquivo
│
├── src/
│   ├── position_manager.py   # Lógica principal de trading
│   ├── avantis/              # Módulo Avantis
│   │   ├── auth.py           # Autenticação
│   │   ├── trade.py          # Abrir/fechar posições
│   │   ├── account.py        # Informações da conta
│   │   └── market.py         # Dados de mercado
│   └── config/               # Configurações
│       ├── constants.py      # Constantes
│       ├── paths.py          # Caminhos de arquivos
│       └── configure_logger.py
│
├── utils/                     # Utilitários
│   ├── data.py               # Gerenciamento de estado
│   ├── calc.py               # Cálculos
│   └── general.py            # Funções gerais
│
├── data/                      # Dados do bot
│   ├── accounts.xlsx         # Conta Avantis
│   ├── active_pairs.xlsx     # Pares ativos
│   ├── config.json           # Configurações
│   └── state.json            # Estado do bot (auto-gerado)
│
└── logs/                      # Logs do bot
    └── bot.log               # Log detalhado
```

## 🛡️ Segurança

- **NUNCA** compartilhe seu arquivo `accounts.xlsx` ou private key
- Use `.gitignore` para evitar commit acidental
- Considere usar variáveis de ambiente para dados sensíveis
- Teste primeiro com valores pequenos

## 📝 Logs

Os logs são salvos em:
- **Console**: Logs INFO e superiores
- **Arquivo**: `logs/bot.log` (DEBUG e superiores)

## ⚠️ Avisos Importantes

1. **Aprovação USDC**: Na primeira execução, o bot aprovará USDC para o contrato Avantis
2. **Gas fees**: Todas as transações na Base Network requerem ETH para gas
3. **Saldo mínimo**: Mantenha saldo suficiente para cobrir as posições + fees
4. **Monitoramento**: Acompanhe os logs para detectar erros
5. **Liquidação**: Configure max_leverage adequadamente para evitar liquidações

## 🔗 Links Úteis

- [Avantis SDK Documentation](https://sdk.avantisfi.com/)
- [Avantis Platform](https://avantisfi.com/)
- [Base Network](https://base.org/)
- [Base RPC Endpoints](https://chainlist.org/chain/8453)

## 🆘 Troubleshooting

### Erro: "Insufficient USDC balance"
- Verifique seu saldo USDC na Base Network
- Transfira USDC para sua conta

### Erro: "Insufficient ETH for gas"
- Você precisa de ETH na Base Network para pagar gas
- Faça bridge de ETH para Base

### Erro: "Allowance too low"
- O bot deve aprovar automaticamente
- Se persistir, execute a opção 3 (Ver Status) primeiro

### Posições não fecham
- Verifique os logs em `logs/bot.log`
- Execute manualmente a opção 2 (Fechar Todas)

## 📈 Melhorias Futuras

- [ ] Implementar TP/SL automático
- [ ] Adicionar estratégias de rebalanceamento
- [ ] Interface web para monitoramento
- [ ] Integração com Telegram para alertas
- [ ] Backtesting de estratégias

## 📄 Licença

Uso livre para fins educacionais. Use por sua conta e risco.

## 🙏 Créditos

Baseado no bot Paradex Delta Neutro original, adaptado para Avantis.
