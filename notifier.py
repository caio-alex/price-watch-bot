"""
Módulo de notificação via Telegram.

Usa a API HTTP do Telegram Bot diretamente (sem dependências extras).
Para configurar:
  1. Fale com @BotFather no Telegram e crie um bot (/newbot).
  2. Copie o token gerado para TELEGRAM_BOT_TOKEN no .env.
  3. Envie qualquer mensagem para o seu bot.
  4. Acesse https://api.telegram.org/bot<TOKEN>/getUpdates para descobrir
     seu chat_id e coloque em TELEGRAM_CHAT_ID no .env.
"""

import logging
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"


def send_message(text: str) -> bool:
    """Envia uma mensagem para o chat configurado. Retorna True se sucesso."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning(
            "TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID não configurados. "
            "Mensagem não enviada:\n%s",
            text,
        )
        return False

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.RequestException as exc:
        logger.error("Erro ao enviar mensagem no Telegram: %s", exc)
        return False
