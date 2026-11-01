from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Iterable

import pandas as pd

COLUMN_ALIASES = {
    "id_venda": {"id_venda", "sale_id", "id", "pedido", "order_id", "numero_pedido"},
    "data": {"data", "data_venda", "sale_date", "date", "data_do_pedido"},
    "cliente": {"cliente", "customer", "nome_cliente", "customer_name"},
    "produto": {"produto", "product", "item", "nome_produto"},
    "quantidade": {"quantidade", "qtd", "quantity", "qty"},
    "preco_unitario": {"preco_unitario", "valor_unitario", "unit_price", "preco", "price"},
}

REQUIRED = list(COLUMN_ALIASES)


def _normalize_header(value: object) -> str:
    text = str(value).strip().lower()
    text = (text.replace("ç", "c").replace("ã", "a").replace("á", "a")
                .replace("à", "a").replace("é", "e").replace("ê", "e")
                .replace("í", "i").replace("ó", "o").replace("ô", "o")
                .replace("ú", "u"))
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    for canonical, aliases in COLUMN_ALIASES.items():
        if text in aliases:
            return canonical
    return text


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    if path.suffix.lower() != ".csv":
        raise ValueError("O arquivo de entrada precisa ter extensão .csv")

    last_error = None
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            with path.open("r", encoding=encoding, newline="") as file:
                sample = file.read(4096)
                file.seek(0)
                try:
                    delimiter = csv.Sniffer().sniff(sample, delimiters=";,").delimiter
                except csv.Error:
                    delimiter = ";"
                return pd.read_csv(file, sep=delimiter, dtype=str, keep_default_na=False)
        except UnicodeDecodeError as exc:
            last_error = exc
    raise ValueError(f"Não foi possível identificar a codificação do CSV: {last_error}")


def parse_money(value: object) -> float | None:
    """Converte valores como 'R$ 1.234,56' ou '1234.56' em float."""
    if value is None:
        return None
    text = str(value).strip().replace("R$", "").replace("$", "").replace(" ", "")
    if not text:
        return None

    if "," in text and "." in text:
        # O último separador é tratado como separador decimal.
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        text = text.replace(".", "").replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def process_sales(path: str | Path) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    raw = _read_csv(Path(path))
    raw.columns = [_normalize_header(column) for column in raw.columns]

    # Evita colunas repetidas após padronização.
    if raw.columns.duplicated().any():
        raise ValueError("Existem colunas duplicadas após a padronização dos nomes.")

    missing = [column for column in REQUIRED if column not in raw.columns]
    if missing:
        raise ValueError("Colunas obrigatórias ausentes: " + ", ".join(missing))

    df = raw[REQUIRED].copy()
    for column in ("id_venda", "cliente", "produto"):
        df[column] = df[column].astype(str).str.strip()

    df["data"] = pd.to_datetime(df["data"].astype(str).str.strip(),
                                dayfirst=True, errors="coerce")
    df["quantidade"] = pd.to_numeric(
        df["quantidade"].astype(str).str.strip().str.replace(",", ".", regex=False),
        errors="coerce"
    )
    df["preco_unitario"] = df["preco_unitario"].map(parse_money)

    reasons: list[list[str]] = [[] for _ in range(len(df))]
    for index, row in enumerate(df.itertuples(index=False, name=None)):
        sale_id, date, customer, product, quantity, price = row
        checks = [
            (not sale_id, "ID da venda ausente"),
            (pd.isna(date), "Data inválida ou ausente"),
            (not customer, "Cliente ausente"),
            (not product, "Produto ausente"),
            (pd.isna(quantity) or quantity <= 0 or float(quantity) % 1 != 0,
             "Quantidade deve ser um inteiro positivo"),
            (price is None or pd.isna(price) or price < 0,
             "Preço unitário inválido"),
        ]
        reasons[index].extend(message for failed, message in checks if failed)

    df["motivo_rejeicao"] = ["; ".join(items) for items in reasons]
    rejected = df[df["motivo_rejeicao"] != ""].copy()
    valid = df[df["motivo_rejeicao"] == ""].drop(columns=["motivo_rejeicao"]).copy()

    duplicate_mask = valid.duplicated(subset=["id_venda"], keep="first")
    duplicates = valid[duplicate_mask].copy()
    if not duplicates.empty:
        duplicates["motivo_rejeicao"] = "ID de venda duplicado"
        rejected = pd.concat([rejected, duplicates], ignore_index=True)
    valid = valid[~duplicate_mask].copy()

    valid["quantidade"] = valid["quantidade"].astype(int)
    valid["preco_unitario"] = valid["preco_unitario"].astype(float).round(2)
    valid["total"] = (valid["quantidade"] * valid["preco_unitario"]).round(2)
    valid["data"] = valid["data"].dt.strftime("%Y-%m-%d")

    summary = {
        "linhas_recebidas": int(len(raw)),
        "vendas_validas": int(len(valid)),
        "registros_rejeitados": int(len(rejected)),
        "faturamento_total": round(float(valid["total"].sum()), 2),
        "ticket_medio": round(float(valid["total"].mean()), 2) if len(valid) else 0.0,
        "quantidade_itens": int(valid["quantidade"].sum()) if len(valid) else 0,
        "produtos_unicos": int(valid["produto"].nunique()) if len(valid) else 0,
    }
    return valid, rejected, summary
