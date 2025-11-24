"""
Watchdog - Monitor contínuo de posições (a cada 5 segundos)
Garante que SEMPRE há 1 long + 1 short ou 0 posições
"""
import asyncio
import time
from src.config.constants import logger
from src.avantis.account import get_open_positions


class PositionWatchdog:
    def __init__(self, trader_client, expected_positions=2):
        self.trader_client = trader_client
        self.expected_positions = expected_positions
        self.is_running = False
        self.last_check = 0
        self.check_interval = 5  # 5 segundos
        
    async def start_monitoring(self, duration_seconds):
        """
        Monitora posições a cada 5 segundos durante duration_seconds.
        Se encontrar anomalia (1 posição, 3+), retorna False.
        """
        self.is_running = True
        end_time = time.time() + duration_seconds
        anomaly_detected = False
        
        logger.info(f"🛡️ Watchdog iniciado - Monitor a cada {self.check_interval}s por {duration_seconds}s")
        
        while time.time() < end_time and not anomaly_detected:
            try:
                positions = await get_open_positions(self.trader_client)
                
                # Contar long e short
                long_count = sum(1 for p in positions if p["is_long"])
                short_count = sum(1 for p in positions if not p["is_long"])
                total = len(positions)
                
                # Log a cada 30s
                if time.time() - self.last_check > 30:
                    logger.info(f"🛡️ Watchdog: {total} posições ({long_count}L + {short_count}S)")
                    self.last_check = time.time()
                
                # VERIFICAR ANOMALIAS
                if total != self.expected_positions:
                    logger.error(f"🚨 ANOMALIA DETECTADA!")
                    logger.error(f"   Esperado: {self.expected_positions} posições")
                    logger.error(f"   Encontrado: {total} posições ({long_count}L + {short_count}S)")
                    
                    if total == 0:
                        logger.error("   Posições foram fechadas prematuramente!")
                    elif total == 1:
                        logger.error("   DELTA NEUTRO PERDIDO - Apenas 1 posição!")
                    else:
                        logger.error("   MÚLTIPLAS POSIÇÕES ABERTAS!")
                    
                    anomaly_detected = True
                    break
                
                # Verificar ratio 1:1
                if total == 2 and (long_count != 1 or short_count != 1):
                    logger.error(f"🚨 RATIO INCORRETO!")
                    logger.error(f"   Esperado: 1L + 1S")
                    logger.error(f"   Encontrado: {long_count}L + {short_count}S")
                    anomaly_detected = True
                    break
                
            except Exception as e:
                logger.warning(f"Watchdog erro: {e}")
            
            await asyncio.sleep(self.check_interval)
        
        self.is_running = False
        
        if anomaly_detected:
            logger.error("🛡️ Watchdog: ANOMALIA - Retornando False")
            return False
        else:
            logger.success("🛡️ Watchdog: OK - Ciclo completo sem anomalias")
            return True


async def wait_for_positions_registered(trader_client, expected_count=2, max_wait=20):
    """
    Aguarda até expected_count posições serem registradas.
    Verifica a cada 2 segundos por até max_wait segundos.
    """
    logger.info(f"⏳ Aguardando {expected_count} posições serem registradas...")
    
    for attempt in range(max_wait // 2):
        await asyncio.sleep(2)
        
        positions = await get_open_positions(trader_client)
        
        if len(positions) == expected_count:
            long_count = sum(1 for p in positions if p["is_long"])
            short_count = sum(1 for p in positions if not p["is_long"])
            
            logger.success(f"✅ {expected_count} posições registradas ({long_count}L + {short_count}S)")
            return True
        else:
            logger.debug(f"   Tentativa {attempt+1}: {len(positions)} posições encontradas")
    
    logger.error(f"❌ Timeout: Esperava {expected_count}, encontrou {len(positions)}")
    return False
