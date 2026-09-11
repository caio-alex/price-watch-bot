# Monitor de Preços/Vagas com Notificação via Telegram

Automação que verifica periodicamente páginas web (preço de produto, status
de vaga, disponibilidade de item, etc.) e envia uma notificação no Telegram
sempre que o valor monitorado mudar.

## Como funciona

1. `scraper.py` baixa a página e extrai o valor usando um seletor CSS.
2. `storage.py` compara o valor atual com o último salvo (`state.json`).
3. Se houve mudança, `notifier.py` envia uma mensagem via Telegram Bot API.
4. `main.py` orquestra tudo e pode rodar uma vez ou em loop contínuo.

## Setup

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Criar o bot do Telegram

1. No Telegram, converse com **@BotFather** e envie `/newbot`.
2. Siga as instruções e copie o **token** gerado.
3. Envie qualquer mensagem para o seu bot recém-criado (ex: "oi").
4. Acesse no navegador:
   `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`
5. Procure o campo `"chat":{"id": ...}` — esse número é o seu `chat_id`.

### 3. Configurar variáveis de ambiente

Copie o arquivo de exemplo e preencha com seus dados:

```bash
cp .env.example .env
```

Edite `.env`:
```
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui
CHECK_INTERVAL_MINUTES=30
```

### 4. Configurar os alvos monitorados

Edite `config.py` e ajuste a lista `TARGETS`. Para descobrir o seletor CSS
correto de um site:

1. Abra a página no navegador.
2. Clique com o botão direito no elemento (ex: o preço) → **Inspecionar**.
3. Copie um seletor CSS único (classe ou id) que aponte para aquele elemento.

Exemplo:
```python
TARGETS = [
    {
        "id": "notebook_dell",
        "label": "Notebook Dell G15",
        "url": "https://www.exemplo.com/produto/notebook-dell-g15",
        "selector": ".price-value",
    },
]
```

> **Atenção:** se o site carregar o preço via JavaScript (conteúdo não
> aparece no "Ver código-fonte da página"), o `requests` simples não vai
> funcionar. Nesse caso, é necessário trocar `fetch_html` em `scraper.py`
> para usar **Playwright** (renderiza a página como um navegador real).

## Uso

**Verificação única** (bom para testar):
```bash
python main.py
```

**Rodando continuamente** (verifica a cada `CHECK_INTERVAL_MINUTES`):
```bash
python main.py --loop
```

## Estrutura do projeto

```
price-monitor-bot/
├── main.py           # orquestração principal
├── scraper.py         # extração de dados via requests + BeautifulSoup
├── notifier.py         # envio de notificações via Telegram
├── storage.py          # persistência do último estado (state.json)
├── config.py            # configurações e lista de alvos monitorados
├── requirements.txt
├── .env.example
└── README.md
```

## Ideias de expansão (para diferenciar o projeto)

- **Múltiplos canais de notificação**: adicionar e-mail (SMTP) ou Discord
  webhook como alternativa ao Telegram.
- **Dashboard web**: pequena API em FastAPI/Flask exibindo o histórico de
  valores coletados (gráfico de preço ao longo do tempo).
- **Histórico completo**: em vez de salvar só o último valor, guardar todas
  as leituras em SQLite com timestamp, permitindo análises de tendência.
- **Suporte a JS-heavy sites**: trocar `requests`/`BeautifulSoup` por
  `Playwright` para sites que renderizam conteúdo via JavaScript.
- **Deploy**: rodar em um VPS barato, Railway, Render, ou até um Raspberry
  Pi com `cron` chamando `python main.py` periodicamente.
- **Dockerfile**: containerizar a aplicação para facilitar o deploy.

## Observações importantes

- Respeite o `robots.txt` e os termos de uso dos sites monitorados.
- Adicione atrasos (`time.sleep`) entre requisições se monitorar múltiplos
  alvos no mesmo site, para não sobrecarregar o servidor.
- Alguns sites bloqueiam scraping por User-Agent — o `HEADERS` em
  `scraper.py` já simula um navegador comum, mas pode ser necessário ajustar.
