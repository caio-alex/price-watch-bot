"""
Persistência simples em JSON.

Guarda o último valor coletado para cada alvo, permitindo comparar a leitura
atual com a anterior e detectar mudanças.
"""

import json
import os
from config import STORAGE_FILE


def load_state() -> dict:
    """Carrega o estado salvo em disco. Retorna dict vazio se não existir."""
    if not os.path.exists(STORAGE_FILE):
        return {}
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_state(state: dict) -> None:
    """Salva o estado atual em disco."""
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_last_value(state: dict, target_id: str):
    return state.get(target_id, {}).get("value")


def set_value(state: dict, target_id: str, value: str) -> None:
    state[target_id] = {"value": value}
