import argparse
import logging
from pathlib import Path

from .database import save_sales
from .processor import process_sales
from .reporting import export_reports


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="SalesFlow - automação e relatório de vendas com Python."
    )
    parser.add_argument("--input", required=True, help="Caminho do CSV de vendas.")
    parser.add_argument("--output-dir", default="output", help="Pasta dos relatórios.")
    parser.add_argument("--database", default=None, help="Caminho do banco SQLite.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=output_dir / "salesflow.log",
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        encoding="utf-8",
    )
    try:
        logging.info("Iniciando processamento: %s", args.input)
        valid, rejected, summary = process_sales(args.input)
        excel_path, json_path = export_reports(valid, rejected, summary, output_dir)

        database = args.database or str(output_dir / "salesflow.db")
        inserted = save_sales(valid, database)

        print("\n=== SALESFLOW | RESULTADO ===")
        for key, value in summary.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        print(f"Novas vendas gravadas no SQLite: {inserted}")
        print(f"Relatório Excel: {excel_path}")
        print(f"Resumo JSON: {json_path}")
        logging.info("Processamento concluído: %s", summary)
        return 0
    except Exception as exc:
        logging.exception("Falha no processamento")
        print(f"Erro: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
