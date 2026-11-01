import json
from pathlib import Path

import pandas as pd


def export_reports(valid: pd.DataFrame, rejected: pd.DataFrame,
                   summary: dict, output_dir: str | Path) -> tuple[Path, Path]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    excel_path = output / "relatorio_vendas.xlsx"
    json_path = output / "resumo_vendas.json"

    summary_df = pd.DataFrame(
        [{"indicador": key, "valor": value} for key, value in summary.items()]
    )
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        valid.to_excel(writer, sheet_name="Vendas", index=False)
        summary_df.to_excel(writer, sheet_name="Resumo", index=False)
        rejected.to_excel(writer, sheet_name="Rejeitados", index=False)

        for worksheet in writer.book.worksheets:
            worksheet.freeze_panes = "A2"
            worksheet.auto_filter.ref = worksheet.dimensions
            for column_cells in worksheet.columns:
                max_length = max(
                    (len(str(cell.value)) if cell.value is not None else 0)
                    for cell in column_cells
                )
                worksheet.column_dimensions[column_cells[0].column_letter].width = min(
                    max(max_length + 2, 12), 42
                )

    json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=4),
        encoding="utf-8"
    )
    return excel_path, json_path
