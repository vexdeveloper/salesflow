import pandas as pd

from src.salesflow.processor import parse_money, process_sales


def test_parse_money_brazilian_and_international():
    assert parse_money("R$ 1.234,56") == 1234.56
    assert parse_money("1234.56") == 1234.56
    assert parse_money("25,90") == 25.90
    assert parse_money("inválido") is None


def test_process_sales_removes_duplicates_and_rejects_invalid(tmp_path):
    csv_file = tmp_path / "vendas.csv"
    csv_file.write_text(
        "id_venda;data;cliente;produto;quantidade;preco_unitario\n"
        "A1;20/10/2026;Ana;Teclado;2;100,00\n"
        "A1;20/10/2026;Ana;Teclado;2;100,00\n"
        "A2;data-errada;Bruno;Mouse;1;50,00\n"
        "A3;21/10/2026;Carla;Monitor;0;700,00\n",
        encoding="utf-8"
    )

    valid, rejected, summary = process_sales(csv_file)

    assert len(valid) == 1
    assert valid.iloc[0]["total"] == 200.00
    assert len(rejected) == 3
    assert summary["linhas_recebidas"] == 4
    assert summary["vendas_validas"] == 1
    assert summary["faturamento_total"] == 200.00
