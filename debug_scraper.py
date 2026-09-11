"""
Script de debug: baixa a página de um alvo e salva o HTML bruto em disco,
além de mostrar informações úteis para diagnosticar por que um seletor
não está encontrando o elemento esperado.

Uso:
    python debug_scraper.py
"""

from config import TARGETS
from scraper import fetch_html, fetch_html_js

TARGET_INDEX = 0  # troque se quiser debugar outro alvo da lista

def main():
    target = TARGETS[TARGET_INDEX]
    use_js = target.get("js", False)
    print(f"Baixando: {target['url']}")
    print(f"Modo: {'Playwright (JS)' if use_js else 'requests (sem JS)'}")

    if use_js:
        html = fetch_html_js_with_screenshot(target["url"])
    else:
        html = fetch_html(target["url"])

    if html is None:
        print("Falha ao baixar a página (erro de rede/conexão). Veja o log acima.")
        return

    output_file = "debug_page.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\nHTML salvo em: {output_file}")
    print(f"Tamanho do HTML baixado: {len(html)} caracteres")

    # Sinais comuns de bloqueio anti-bot / captcha
    lower_html = html.lower()
    warning_signs = ["captcha", "robot", "access denied", "unusual traffic", "blocked", "verifique que você é humano", "não sou um robô"]
    found_signs = [sign for sign in warning_signs if sign in lower_html]
    if found_signs:
        print(f"\n⚠️  Possível bloqueio anti-bot detectado! Termos encontrados: {found_signs}")
    else:
        print("\nNenhum sinal óbvio de bloqueio encontrado no HTML.")

    if target["selector"] in html or target["selector"].lstrip(".") in html:
        print(f"A classe '{target['selector']}' aparece em algum lugar do HTML (bom sinal).")
    else:
        print(f"A classe '{target['selector']}' NÃO aparece em nenhum lugar do HTML baixado.")

    print(f"\nAbra '{output_file}' no navegador ou em um editor de texto para inspecionar manualmente.")
    if use_js:
        print("Screenshot salvo em: debug_screenshot.png -- abra para ver o que o navegador via Playwright realmente carregou.")


def fetch_html_js_with_screenshot(url: str) -> str | None:
    """Versão do fetch_html_js que também salva um screenshot para inspeção visual."""
    from playwright.sync_api import sync_playwright

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)  # espera extra para JS terminar de rodar
            page.screenshot(path="debug_screenshot.png", full_page=True)
            html = page.content()
            browser.close()
            return html
    except Exception as exc:
        print(f"Erro ao acessar {url} via Playwright: {exc}")
        return None


if __name__ == "__main__":
    main()

