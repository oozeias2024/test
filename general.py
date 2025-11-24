import time
from typing import Callable, Any
from src.config.constants import logger


def _retry_request(func: Callable, *args, retries: int = 3, delay: int = 1, **kwargs) -> Any:
    """Tenta executar uma função com retries."""
    for attempt in range(1, retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == retries:
                logger.error(f"Falha após {retries} tentativas: {e}")
                raise
            logger.warning(f"Tentativa {attempt}/{retries} falhou: {e}")
            time.sleep(delay)
    return None
