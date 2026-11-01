from pathlib import Path
import sqlite3
import pandas as pd


def save_sales(df: pd.DataFrame, database: str | Path) -> int:
    """Salva vendas válidas. O ID da venda impede duplicação no banco."""
    db_path = Path(database)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS vendas (
                id_venda TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                cliente TEXT NOT NULL,
                produto TEXT NOT NULL,
                quantidade INTEGER NOT NULL,
                preco_unitario REAL NOT NULL,
                total REAL NOT NULL
            )
        """)
        if df.empty:
            return 0

        records = df[[
            "id_venda", "data", "cliente", "produto",
            "quantidade", "preco_unitario", "total"
        ]].itertuples(index=False, name=None)

        before = connection.total_changes
        connection.executemany("""
            INSERT OR IGNORE INTO vendas
            (id_venda, data, cliente, produto, quantidade, preco_unitario, total)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, records)
        return connection.total_changes - before
