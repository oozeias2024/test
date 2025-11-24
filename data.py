import json
from pathlib import Path
from typing import Dict, Any
from src.config.paths import DATA_DIR
from src.config.constants import logger

STATE_FILE = DATA_DIR / "state.json"
CONFIG_FILE = DATA_DIR / "config.json"

# Carregar configuração do usuário
try:
    with open(CONFIG_FILE, 'r') as f:
        USER_CONFIG = json.load(f)
except FileNotFoundError:
    logger.warning(f"Arquivo {CONFIG_FILE} não encontrado. Usando configurações padrão.")
    USER_CONFIG = {}


def get_user_state() -> Dict[str, Any]:
    """Obtém o estado atual do bot."""
    if not STATE_FILE.exists():
        return {}
    
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao ler state: {e}")
        return {}


def update_state(key: str, field: str, value: Any) -> None:
    """Atualiza um campo no estado."""
    state = get_user_state()
    
    if key not in state:
        state[key] = {}
    
    state[key][field] = value
    
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        logger.error(f"Erro ao salvar state: {e}")


def force_close_state() -> None:
    """Força o fechamento de todas as posições no estado."""
    state = get_user_state()
    
    for key in state:
        if "position" in state[key]:
            state[key]["position"] = "closed"
    
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        logger.info("✅ Estado resetado - todas posições marcadas como fechadas")
    except Exception as e:
        logger.error(f"Erro ao resetar state: {e}")
