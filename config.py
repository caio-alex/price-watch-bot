"""
Configuração central do projeto.

Carrega variáveis de ambiente (.env) e define a lista de "alvos" que serão
monitorados. Cada alvo é um dicionário com:
    - id: identificador único (usado para salvar o estado no storage)
    - url: endereço da página a ser verificada
    - selector: seletor CSS usado para extrair o valor desejado
    - label: nome amigável exibido nas notificações

Edite TARGETS abaixo para monitorar o que quiser (preço de produto, título
de vaga, disponibilidade, etc).
"""

import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "30"))

STORAGE_FILE = "state.json"
LOG_FILE = "monitor.log"

# ---------------------------------------------------------------------------
# Exemplo de configuração de alvos. Substitua pela URL e seletor CSS reais
# do site que você quer monitorar. Use as ferramentas de desenvolvedor do
# navegador (Inspecionar elemento) para descobrir o seletor certo.
# ---------------------------------------------------------------------------
TARGETS = [
    # Exemplo para produto do Mercado Livre. Troque a URL pela do produto
    # que você quer monitorar. O tipo "meli_price" já sabe juntar a parte
    # inteira do preço (fraction) com os centavos (cents) corretamente.
    {
        "id": "gta_vi_ps5_kabum",
        "label": "GTA VI (PS5) - KaBuM",
        "js": True,
        "url": "https://www.kabum.com.br/produto/1051619/jogo-grand-theft-auto-gta-vi-6-ps5-tt000272ps5",
        "selector": ".text-2xl.leading-tight",
    },
    # Adicione mais alvos aqui, cada um com id único.
    # {
    #     "id": "vaga_exemplo",
    #     "label": "Vaga de Dev Junior",
    #     "url": "https://exemplo.com/vagas/dev-junior",
    #     "selector": ".status-vaga",
    # },
]
