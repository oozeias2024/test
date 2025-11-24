import random
import time
import pandas as pd
import asyncio
from typing import List, Dict, Any, Optional

from src.config.constants import logger
from src.config.paths import DATA_DIR
from src.avantis.auth import get_trader_client
from src.avantis.trade import open_position, close_position, open_position_direct
from src.avantis.account import get_open_positions, get_usdc_balance
from src.avantis.market import get_pair_index
from utils.data import update_state, get_user_state, USER_CONFIG, force_close_state
from utils.calc import calc_value_distribution


class TradingManager:
    def __init__(self) -> None:
        self.config: Dict[str, Any] = USER_CONFIG
        self.retries = self.config.get("retries", 3)
        self.trader_client = None
        self.private_key = None
        self.trader_address = None
        self._trading_lock = asyncio.Lock()  # Prevenir execuções simultâneas
        self._positions_open = False  # Flag de controle
        self._consecutive_failures = 0  # Contador de falhas consecutivas
        self._max_consecutive_failures = 3  # Parar após 3 falhas

    def get_random_from_range(self, key: str) -> int:
        if key in self.config and isinstance(self.config[key], dict):
            min_val = self.config[key].get("min", 0)
            max_val = self.config[key].get("max", 0)
            return random.randint(min_val, max_val)
        raise ValueError(f"Invalid or missing config range for '{key}'")

    async def initialize_client(self) -> None:
        """Inicializa o cliente Avantis com a private key."""
        df_accounts = pd.read_excel(DATA_DIR / "accounts.xlsx")
        active_account = df_accounts[df_accounts["is_active"] == True].iloc[0]
        
        self.private_key = active_account["private_key"]
        self.trader_client = get_trader_client(self.private_key)
        self.trader_address = self.trader_client.get_signer().get_ethereum_address()
        
        logger.info(f"✅ Cliente inicializado: {self.trader_address}")

    async def select_market_data(self, df_markets: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Seleciona um mercado aleatório da lista."""
        for _ in range(len(df_markets)):
            market = df_markets.sample().iloc[0]
            try:
                pair_index = await get_pair_index(self.trader_client, market["symbol"])
                if pair_index is not None:
                    logger.info(f"Mercado selecionado: {market['symbol']} (index: {pair_index})")
                    return {
                        "symbol": market["symbol"],
                        "pair_index": pair_index
                    }
            except Exception as e:
                logger.warning(f"Erro ao selecionar mercado {market['symbol']}: {e}")
        
        logger.error("Nenhum mercado válido encontrado")
        return None
    
    def debug_config(self):
        """Mostra a configuração carregada para debug."""
        logger.info("=" * 60)
        logger.info("🔍 DEBUG - Configuração Carregada:")
        logger.info(f"   order_value_usd: ${self.config['order_value_usd']['min']}-${self.config['order_value_usd']['max']}")
        logger.info(f"   max_leverage: {self.config['max_leverage']}x")
        logger.info(f"   order_duration_min: {self.config['order_duration_min']['min']}-{self.config['order_duration_min']['max']} min")
        logger.info("=" * 60)

    async def get_max_order_value(self) -> float:
        """Calcula o valor máximo de ordem baseado no saldo e alavancagem."""
        max_order_value = float(self.config["order_value_usd"]["max"])
        max_leverage = float(self.config["max_leverage"])
        
        usdc_balance = await get_usdc_balance(self.trader_client)
        
        # Verificar se há posições abertas
        positions = await get_open_positions(self.trader_client)
        if positions:
            logger.warning(f"Existem {len(positions)} posições abertas. Aguardando fechamento...")
            return 0
        
        # Calcular valor máximo baseado no saldo
        leverage_check = max_order_value / usdc_balance
        if leverage_check > max_leverage:
            max_corrected = usdc_balance * max_leverage
            logger.debug(f"Valor ajustado por alavancagem: ${max_corrected:.2f}")
            return max_corrected
        
        return max_order_value

    async def start_trading(self) -> None:
        """Loop principal de trading."""
        await self.initialize_client()
        
        # Mostrar configuração para debug
        self.debug_config()
        
        cycle_number = 0
        
        while True:
            cycle_number += 1
            logger.info("=" * 70)
            logger.info(f"🔄 CICLO #{cycle_number} - Verificando posições abertas...")
            logger.info("=" * 70)
            
            # CRÍTICO: Verificar posições abertas ANTES de continuar
            positions = await get_open_positions(self.trader_client)
            
            if positions:
                long_count = sum(1 for p in positions if p["is_long"])
                short_count = sum(1 for p in positions if not p["is_long"])
                
                logger.warning(f"⚠️ POSIÇÕES ABERTAS ENCONTRADAS!")
                logger.warning(f"   Total: {len(positions)} | Long: {long_count} | Short: {short_count}")
                
                # Listar todas as posições
                for i, pos in enumerate(positions, 1):
                    side = "LONG" if pos["is_long"] else "SHORT"
                    logger.warning(f"   {i}. {side} | Colateral: ${pos['collateral']:.2f} | Index: {pos['trade_index']}")
                
                logger.warning("🔧 FECHANDO TODAS antes de novo ciclo...")
                await self.close_all_positions()
                force_close_state()
                
                # Aguardar 5s e verificar novamente
                await asyncio.sleep(5)
                positions_check = await get_open_positions(self.trader_client)
                
                if positions_check:
                    logger.error(f"🚨 AINDA HÁ {len(positions_check)} POSIÇÕES ABERTAS!")
                    logger.error("🚨 TENTANDO FECHAR NOVAMENTE...")
                    await self.close_all_positions()
                    await asyncio.sleep(5)
                
                continue
            
            # Carregar mercados
            df_markets = pd.read_excel(DATA_DIR / "active_pairs.xlsx")
            if df_markets.empty:
                logger.warning("Nenhum mercado encontrado. Parando loop.")
                break
            
            # Selecionar mercado
            market_data = await self.select_market_data(df_markets)
            if not market_data:
                logger.error("Falha ao selecionar mercado. Aguardando...")
                await asyncio.sleep(60)
                continue
            
            # Calcular valores
            max_value = await self.get_max_order_value()
            if max_value == 0:
                logger.warning("Valor máximo de ordem é 0. Pulando ciclo...")
                await asyncio.sleep(60)
                continue
            
            raw_order_value = self.get_random_from_range("order_value_usd")
            order_value = min(raw_order_value, max_value)
            order_duration = self.get_random_from_range("order_duration_min")
            
            logger.debug(f"📊 Valores calculados: raw={raw_order_value}, max={max_value}, final={order_value}")
            
            # Calcular distribuição (sempre 1 long + 1 short)
            long_dist, short_dist = calc_value_distribution(
                order_value, 1, 1,
                market_data["symbol"].split("/")[0],
                0,  # price não usado
                self.config.get("orders_distribution_noise", 0)
            )
            
            # Validar valor mínimo da Avantis (reduzido para $10)
            AVANTIS_MIN_POSITION = 10.0  # Mínimo $10 por posição
            if long_dist[0] < AVANTIS_MIN_POSITION or short_dist[0] < AVANTIS_MIN_POSITION:
                logger.error(
                    f"❌ Valores muito pequenos! Long: ${long_dist[0]:.2f}, Short: ${short_dist[0]:.2f}\n"
                    f"   Avantis requer mínimo ~${AVANTIS_MIN_POSITION} por posição.\n"
                    f"   Configure order_value_usd mínimo de ${AVANTIS_MIN_POSITION * 2} em data/config.json"
                )
                await asyncio.sleep(60)
                continue
            
            logger.info(
                f"Iniciando trade | Mercado: {market_data['symbol']} | "
                f"Long: ${long_dist[0]:.2f} | Short: ${short_dist[0]:.2f} | "
                f"Duração: {order_duration} min"
            )
            
            # CRÍTICO: Lock para prevenir múltiplas execuções
            async with self._trading_lock:
                if self._positions_open:
                    logger.error("🚨 ERRO: Já há posições abertas! Pulando ciclo...")
                    await asyncio.sleep(30)
                    continue
                
                try:
                    success = await self.open_delta_neutral_positions(
                        market_data["pair_index"],
                        long_dist[0],
                        short_dist[0]
                    )
                    
                    # Se não conseguiu abrir ambas, pular para próximo ciclo
                    if not success:
                        self._consecutive_failures += 1
                        logger.error(f"❌ Falha {self._consecutive_failures}/{self._max_consecutive_failures}")
                        
                        if self._consecutive_failures >= self._max_consecutive_failures:
                            logger.error("🚨 MUITAS FALHAS CONSECUTIVAS - PARANDO BOT!")
                            logger.error("🚨 Verifique:")
                            logger.error("   1. Saldo USDC suficiente")
                            logger.error("   2. Posições órfãs abertas")
                            logger.error("   3. Logs de erro acima")
                            break
                        
                        logger.warning("🔄 Pulando para próximo ciclo...")
                        delay = self.get_random_from_range("delay_between_trading_cycles_min")
                        await asyncio.sleep(delay * 60)
                        continue
                    
                    # Marcar que posições estão abertas
                    self._positions_open = True
                        
                except Exception as e:
                    logger.error(f"Erro ao abrir posições: {e}")
                    await asyncio.sleep(60)
                    continue
            
            # VALIDAÇÃO EXTRA: Verificar que realmente há APENAS 2 posições
            await asyncio.sleep(2)
            verify_positions = await get_open_positions(self.trader_client)
            
            if len(verify_positions) != 2:
                logger.error(f"🚨 ERRO CRÍTICO: Esperava 2 posições, encontrou {len(verify_positions)}!")
                logger.error("🔧 FECHANDO TODAS E ABORTANDO CICLO...")
                await self.close_all_positions()
                self._positions_open = False
                await asyncio.sleep(5)
                continue
            
            long_verify = sum(1 for p in verify_positions if p["is_long"])
            short_verify = sum(1 for p in verify_positions if not p["is_long"])
            
            if long_verify != 1 or short_verify != 1:
                logger.error(f"🚨 DELTA NEUTRO PERDIDO! Long={long_verify}, Short={short_verify}")
                logger.error("🔧 FECHANDO TODAS E ABORTANDO CICLO...")
                await self.close_all_positions()
                self._positions_open = False
                await asyncio.sleep(5)
                continue
            
            logger.success(f"✅ VALIDADO: {long_verify} LONG + {short_verify} SHORT (Delta Neutro OK!)")
            
            # Resetar contador de falhas (sucesso!)
            self._consecutive_failures = 0
            
            logger.info(f"📡 Monitorando por {order_duration} minutos com Watchdog a cada 5s...")
            
            # Usar watchdog para monitorar
            from src.watchdog import PositionWatchdog
            watchdog = PositionWatchdog(self.trader_client, expected_positions=2)
            
            monitor_ok = await watchdog.start_monitoring(order_duration * 60)
            
            if not monitor_ok:
                logger.error("🚨 Watchdog detectou anomalia - fechando tudo!")
                await self.close_all_positions()
                self._positions_open = False
                continue
            
            logger.info("⏳ Encerrando ciclo — fechando todas as posições.")
            await self.close_all_positions()
            force_close_state()
            self._positions_open = False  # Resetar flag
            
            delay = self.get_random_from_range("delay_between_trading_cycles_min")
            logger.info(f"Aguardando {delay} minutos antes do próximo ciclo...")
            await asyncio.sleep(delay * 60)

    async def open_delta_neutral_positions(
        self,
        pair_index: int,
        long_value: float,
        short_value: float
    ) -> bool:
        """
        Abre delta neutro BASEADO NO EXEMPLO OFICIAL DA AVANTIS.
        Simplificado: SDK gerencia nonce automaticamente.
        """
        leverage = self.config.get("max_leverage", 10)
        trader = self.trader_client.get_signer().get_ethereum_address()
        
        # PRÉ-VALIDAÇÃO: Verificar posições e encontrar índices livres
        existing_positions = await get_open_positions(self.trader_client)
        
        if existing_positions:
            logger.error(f"🚨 Já existem {len(existing_positions)} posições!")
            for pos in existing_positions:
                side = "LONG" if pos["is_long"] else "SHORT"
                logger.error(f"   {side} | Index: {pos['trade_index']}")
            return False
        
        # Encontrar índices livres (começar de 0 e 1)
        used_indices = [p["trade_index"] for p in existing_positions] if existing_positions else []
        
        # Encontrar primeiro índice livre para long
        long_index = 0
        while long_index in used_indices:
            long_index += 1
        
        # Encontrar segundo índice livre para short
        short_index = long_index + 1
        while short_index in used_indices:
            short_index += 1
        
        logger.info(f"📍 Usando índices: LONG={long_index}, SHORT={short_index}")
        
        # VERIFICAR E APROVAR ALLOWANCE UMA VEZ (como no exemplo oficial)
        total_collateral = long_value + short_value
        allowance = await self.trader_client.get_usdc_allowance_for_trading(trader)
        
        if allowance < total_collateral:
            logger.info(f"💰 Aprovando {total_collateral * 3:.0f} USDC...")
            await self.trader_client.approve_usdc_for_trading(total_collateral * 3)
            logger.info("✅ Aprovação concluída")
            # CRÍTICO: Approval também usa nonce! Aguardar atualizar
            logger.info("⏳ Aguardando 3s após approval...")
            await asyncio.sleep(3.0)
        
        logger.info("🔄 Abrindo delta neutro...")
        
        import time as time_module
        start_time = time_module.time()
        
        # ABRIR LONG
        logger.info(f"1️⃣ Abrindo LONG (index={long_index})...")
        long_success = await open_position_direct(
            self.trader_client,
            pair_index=pair_index,
            collateral=long_value,
            is_long=True,
            leverage=leverage,
            trade_index=long_index
        )
        
        if not long_success:
            logger.error("❌ LONG falhou")
            return False
        
        # CRÍTICO: Aguardar nonce atualizar no node (FIXO em 3s)
        # Node RPC precisa de tempo para atualizar cache de nonce
        delay = 3.0  # FIXO: 3 segundos (mais seguro que 2s)
        logger.info(f"⏳ Aguardando {delay}s para nonce atualizar...")
        await asyncio.sleep(delay)
        
        # ABRIR SHORT (SDK gerencia nonce)
        logger.info(f"2️⃣ Abrindo SHORT (index={short_index})...")
        short_success = await open_position_direct(
            self.trader_client,
            pair_index=pair_index,
            collateral=short_value,
            is_long=False,
            leverage=leverage,
            trade_index=short_index
        )
        
        total_time = time_module.time() - start_time
        logger.info(f"📊 LONG={'✅' if long_success else '❌'} | SHORT={'✅' if short_success else '❌'} | {total_time:.1f}s")
        
        # VERIFICAR ATOMICIDADE
        if long_success and short_success:
            # Aguardar posições serem registradas (até 20s)
            from src.watchdog import wait_for_positions_registered
            
            registered = await wait_for_positions_registered(self.trader_client, expected_count=2, max_wait=20)
            
            if registered:
                logger.success("🎯 DELTA NEUTRO CONFIRMADO - Ambas registradas!")
                return True
            else:
                logger.error("❌ Posições NÃO foram registradas corretamente")
                logger.warning("🔧 Tentando fechar tudo...")
                await asyncio.sleep(5)
                await self.close_all_positions()
                return False
        else:
            logger.error("❌ SHORT falhou - fechando LONG...")
            await asyncio.sleep(5)
            await self.close_all_positions()
            return False

    async def close_all_positions(self) -> None:
        """Fecha todas as posições abertas."""
        logger.info("⚡ Iniciando fechamento de posições...")
        
        positions = await get_open_positions(self.trader_client)
        
        if not positions:
            logger.info("Nenhuma posição aberta para fechar.")
            return
        
        # Fechar todas as posições em paralelo
        tasks = []
        for pos in positions:
            tasks.append(
                close_position(
                    self.trader_client,
                    pair_index=pos["pair_index"],
                    trade_index=pos["trade_index"],
                    collateral_to_close=pos["collateral"]
                )
            )
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success_count = sum(1 for r in results if r is True)
        
        logger.info(f"✅ {success_count}/{len(positions)} posições fechadas com sucesso")

    async def monitor_positions(self, duration_min: int) -> None:
        """
        Monitora as posições durante o período especificado.
        IMPORTANTE: Respeita EXATAMENTE o tempo configurado.
        
        Args:
            duration_min: Duração EXATA em minutos
        """
        duration_seconds = duration_min * 60
        end_time = time.time() + duration_seconds
        
        logger.info(f"📡 Monitoramento iniciado por EXATOS {duration_min} minuto(s) ({duration_seconds}s)")
        logger.info(f"⏰ Término previsto: {time.strftime('%H:%M:%S', time.localtime(end_time))}")
        
        check_interval = 10  # Checar a cada 10 segundos
        last_log_time = time.time()
        
        while time.time() < end_time:
            try:
                # Log de progresso a cada 30 segundos
                if time.time() - last_log_time > 30:
                    remaining = int(end_time - time.time())
                    logger.info(f"⏳ Tempo restante: {remaining}s ({remaining//60}min {remaining%60}s)")
                    last_log_time = time.time()
                
                # Verificar posições
                positions = await get_open_positions(self.trader_client)
                
                if not positions:
                    logger.warning("⚠️ Nenhuma posição aberta durante monitoramento!")
                    break
                
                # Contar long e short
                long_count = sum(1 for p in positions if p["is_long"])
                short_count = sum(1 for p in positions if not p["is_long"])
                
                # CRÍTICO: Se não tiver 1 long + 1 short, algo está errado
                if long_count != 1 or short_count != 1:
                    logger.error(f"❌ DELTA NEUTRO PERDIDO! Long={long_count}, Short={short_count}")
                    logger.error("🚨 FECHANDO TODAS IMEDIATAMENTE!")
                    await self.close_all_positions()
                    break
                
            except Exception as e:
                logger.warning(f"Erro no monitoramento: {e}")
            
            await asyncio.sleep(check_interval)
        
        # Calcular tempo real decorrido
        elapsed = int(time.time() - (end_time - duration_seconds))
        logger.info(f"⏱️ Monitoramento finalizado após {elapsed}s ({elapsed//60}min {elapsed%60}s)")


def run_trading_manager():
    """Wrapper para executar o TradingManager de forma assíncrona."""
    manager = TradingManager()
    asyncio.run(manager.start_trading())
