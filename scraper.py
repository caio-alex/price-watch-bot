"""
Módulo de scraping.

Responsável por baixar a página de um alvo e extrair o valor desejado usando
o seletor CSS configurado.

Duas estratégias de download disponíveis:
  - fetch_html: usa requests puro (rápido, mas não executa JavaScript).
  - fetch_html_js: usa Playwright, que renderiza a página como um navegador
    de verdade (necessário para sites como Mercado Livre, que carregam o
    preço via JavaScript).
"""

import logging
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

stealth = Stealth(
    navigator_languages_override=("pt-BR", "pt"),
    navigator_platform_override="Win32",
)


def fetch_html(url: str, timeout: int = 15) -> str | None:
    """Baixa o HTML da página via requests puro (não executa JavaScript)."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as exc:
        logger.error("Erro ao acessar %s: %s", url, exc)
        return None


def fetch_html_js(url: str, timeout: int = 30, wait_selector: str | None = None) -> str | None:
    """
    Baixa o HTML da página usando Playwright (navegador real headless) com
    playwright-stealth aplicado, para reduzir sinais de automação que sites
    como o Mercado Livre usam para bloquear scrapers.

    Necessário para sites que carregam conteúdo via JavaScript. Se
    `wait_selector` for informado, espera esse elemento aparecer na página
    antes de capturar o HTML (mais confiável que só esperar o carregamento
    da página).
    """
    try:
        with stealth.use_sync(sync_playwright()) as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=HEADERS["User-Agent"],
                locale="pt-BR",
                viewport={"width": 1366, "height": 768},
            )
            page = context.new_page()
            page.goto(url, timeout=timeout * 1000, wait_until="domcontentloaded")

            if wait_selector:
                try:
                    page.wait_for_selector(wait_selector, timeout=timeout * 1000)
                except Exception:
                    logger.warning(
                        "Elemento '%s' não apareceu em %ds (site pode ter mudado ou bloqueado).",
                        wait_selector, timeout,
                    )

            html = page.content()
            browser.close()
            return html
    except Exception as exc:
        logger.error("Erro ao acessar %s via Playwright: %s", url, exc)
        return None


def extract_value(html: str, selector: str) -> str | None:
    """Extrai o texto do primeiro elemento que casa com o seletor CSS."""
    soup = BeautifulSoup(html, "lxml")
    element = soup.select_one(selector)
    if element is None:
        logger.warning("Seletor '%s' não encontrou nenhum elemento.", selector)
        return None
    return element.get_text(strip=True)


def extract_meli_price(html: str, fraction_selector: str, cents_selector: str | None = None) -> str | None:
    """
    Extrai preços no formato do Mercado Livre, que separa a parte inteira
    (ex: '1.790') dos centavos (ex: '90') em dois elementos distintos.

    Se cents_selector não for encontrado, assume ',00' (preço redondo).
    """
    soup = BeautifulSoup(html, "lxml")

    fraction_el = soup.select_one(fraction_selector)
    if fraction_el is None:
        logger.warning("Seletor de preço '%s' não encontrou nenhum elemento.", fraction_selector)
        return None
    fraction = fraction_el.get_text(strip=True)

    cents = "00"
    if cents_selector:
        cents_el = soup.select_one(cents_selector)
        if cents_el is not None:
            cents = cents_el.get_text(strip=True)

    return f"R$ {fraction},{cents}"


def check_target(target: dict) -> str | None:
    """
    Executa o fluxo completo para um alvo: baixa a página e extrai o valor.

    Se o alvo tiver "js": true, usa Playwright para renderizar a página
    (necessário para sites como Mercado Livre). Caso contrário, usa
    requests puro (mais rápido).

    Se o alvo tiver "type": "meli_price", usa a extração especial de preço
    do Mercado Livre (parte inteira + centavos). Caso contrário, usa o
    seletor CSS simples.
    """
    if target.get("js"):
        wait_selector = target.get("selector")
        html = fetch_html_js(target["url"], wait_selector=wait_selector)
    else:
        html = fetch_html(target["url"])

    if html is None:
        return None

    if target.get("type") == "meli_price":
        return extract_meli_price(
            html,
            fraction_selector=target["selector"],
            cents_selector=target.get("cents_selector"),
        )

    return extract_value(html, target["selector"])
