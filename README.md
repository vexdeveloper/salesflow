# Prompt Studio | SalesFlow
### Automação de vendas com Python

Projeto demonstrativo de portfólio que transforma arquivos CSV brutos de vendas em dados limpos, relatórios Excel e um resumo JSON, além de armazenar vendas válidas em SQLite.

> Projeto fictício para demonstração. Utilize somente dados autorizados.

## Funcionalidades

- Leitura de arquivos CSV com detecção de separador (`;` ou `,`) e codificação comum.
- Padronização dos nomes das colunas.
- Normalização de datas e valores monetários brasileiros (`R$ 1.234,56`) e internacionais (`1234.56`).
- Remoção de linhas duplicadas.
- Validação de campos obrigatórios, quantidades e valores.
- Separação de registros válidos e rejeitados, com motivo.
- Relatório Excel com abas `Vendas`, `Resumo` e `Rejeitados`.
- Resumo JSON com indicadores.
- Persistência dos dados válidos em SQLite.
- Logs de execução e testes automatizados.

## Tecnologias

- Python 3.10+
- pandas
- openpyxl
- SQLite
- pytest

## Estrutura

```text
prompt-studio-salesflow/
├── data/
│   └── vendas_exemplo.csv
├── output/
│   └── .gitkeep
├── src/
│   └── salesflow/
│       ├── __init__.py
│       ├── cli.py
│       ├── database.py
│       ├── processor.py
│       └── reporting.py
├── tests/
│   └── test_processor.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Instalação

Recomendado: Python 3.10 ou superior.

### Windows (PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Executar

Na raiz do projeto:

```bash
python -m src.salesflow.cli --input data/vendas_exemplo.csv --output-dir output --database output/salesflow.db
```

Ao terminar, a pasta `output/` conterá:
- `relatorio_vendas.xlsx`
- `resumo_vendas.json`
- `salesflow.db`
- `salesflow.log`

Para usar outro arquivo:

```bash
python -m src.salesflow.cli --input caminho/arquivo.csv --output-dir output
```

## Formato esperado

Os nomes das colunas aceitam variações simples. O arquivo precisa conter:

| Campo | Exemplos de nomes aceitos |
|---|---|
| ID da venda | `id_venda`, `sale_id`, `pedido` |
| Data | `data`, `data_venda`, `sale_date` |
| Cliente | `cliente`, `customer`, `nome_cliente` |
| Produto | `produto`, `product`, `item` |
| Quantidade | `quantidade`, `qtd`, `quantity` |
| Preço unitário | `preco_unitario`, `valor_unitario`, `unit_price` |

O separador pode ser vírgula ou ponto e vírgula. Datas aceitas incluem `2026-10-20` e `20/10/2026`.

## Testes

```bash
pytest -q
```

## Como funciona

1. O processador lê e padroniza o CSV.
2. Registros sem campos essenciais ou com valores inválidos são enviados para rejeitados.
3. Duplicatas são identificadas pelo ID da venda.
4. Os dados válidos alimentam o Excel, JSON e SQLite.

## Melhorias futuras

- Dashboard web com FastAPI.
- Agendamento automático de processamento.
- Envio de relatórios por e-mail mediante autorização.
- Integração com plataformas de e-commerce.
- Configuração de regras de validação por empresa.

## Autor

**Prompt Studio** — Automation & Technology  
Automatizamos o presente. Construímos o futuro.
