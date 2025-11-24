from avantis_trader_sdk import TraderClient
from src.config.constants import BASE_RPC_URL, logger

# Cache global do cliente
_trader_client = None

def get_trader_client(private_key: str) -> TraderClient:
    """
    Inicializa e retorna o TraderClient da Avantis.
    
    Args:
        private_key: Private key da conta Ethereum
        
    Returns:
        TraderClient configurado
    """
    global _trader_client
    
    if _trader_client is None:
        logger.info("Inicializando TraderClient Avantis...")
        _trader_client = TraderClient(BASE_RPC_URL)
        _trader_client.set_local_signer(private_key)
        logger.info(f"Cliente conectado: {_trader_client.get_signer().get_ethereum_address()}")
    
    return _trader_client
