"""
Ponto de entrada do monitor.

Fluxo, para cada alvo configurado em config.TARGETS:
  1. Faz o scraping do valor atual.
  2. Compara com o último valor salvo.
  3. Se mudou (ou é a primeira execução), envia notificação no Telegram
     e atualiza o estado salvo.

Uso:
    python main.py            # roda uma verificação única
    python main.py --loop     # roda continuamente, respeitando o intervalo
                                 configurado em CHECK_INTERVAL_MINUTES
"""

import argparse
import logging
import sys
import time

from apscheduler.schedulers.blocking import BlockingScheduler

from config import TARGETS, CHECK_INTERVAL_MINUTES, LOG_FILE
from scraper import check_target
from storage import load_state, save_state, get_last_value, set_value
from notifier import send_message
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def run_check() -> None:
    """Executa uma rodada de verificação em todos os alvos configurados."""
    logger.info("Iniciando verificação de %d alvo(s)...", len(TARGETS))
    state = load_state()

    for target in TARGETS:
        target_id = target["id"]
        label = target["label"]

        current_value = check_target(target)
        if current_value is None:
            logger.warning("Não foi possível obter valor para '%s'.", label)
            continue

        last_value = get_last_value(state, target_id)

        if last_value is None:
            # Primeira vez que este alvo é verificado.
            logger.info("Primeira leitura de '%s': %s", label, current_value)
            send_message(f"👀 Monitoramento iniciado para <b>{label}</b>\nValor atual: {current_value}")
        elif current_value != last_value:
            logger.info(
                "Mudança detectada em '%s': '%s' -> '%s'",
                label, last_value, current_value,
            )
            send_message(
                f"🔔 <b>{label}</b> mudou!\n"
                f"De: {last_value}\n"
                f"Para: {current_value}"
            )
        else:
            logger.info("Sem mudanças em '%s' (%s).", label, current_value)

        set_value(state, target_id, current_value)

    save_state(state)
    logger.info("Verificação concluída.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Monitor de preços/vagas com notificação via Telegram.")
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Roda continuamente, verificando a cada CHECK_INTERVAL_MINUTES.",
    )
    args = parser.parse_args()

    if not args.loop:
        run_check()
        return

    logger.info(
        "Rodando em loop, verificando a cada %d minuto(s). Ctrl+C para parar.",
        CHECK_INTERVAL_MINUTES,
    )
    scheduler = BlockingScheduler()
    scheduler.add_job(run_check, "interval", minutes=CHECK_INTERVAL_MINUTES, next_run_time=None)
    # Executa uma vez imediatamente antes de entrar no loop agendado.
    run_check()
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Encerrando monitor.")


if __name__ == "__main__":
    main()
