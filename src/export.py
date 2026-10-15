from io import BytesIO
from datetime import datetime
import pandas as pd
from fpdf import FPDF


def to_excel_bytes(detail_df: pd.DataFrame, summary_df: pd.DataFrame,
                   summary_title: str) -> bytes:
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        summary_df.to_excel(w, sheet_name=summary_title[:31], index=False)
        detail_df.to_excel(w, sheet_name="Detail", index=False)
    return buf.getvalue()


class ReportPDF(FPDF):
    def __init__(self, period_label: str):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.period_label = period_label
        self.set_auto_page_break(auto=True, margin=18)

    def header(self):
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(30, 41, 59)
        self.cell(0, 10, "Urenrapport", align="L", new_x="LMARGIN", new_y="NEXT")

        self.set_font("Helvetica", "", 11)
        self.set_text_color(100, 116, 139)
        self.cell(0, 6, self.period_label, new_x="LMARGIN", new_y="NEXT")

        self.set_draw_color(203, 213, 225)
        self.set_line_width(0.4)
        self.line(self.l_margin, self.get_y() + 2, 210 - self.r_margin, self.get_y() + 2)
        self.ln(6)
        self.set_text_color(0)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120)
        self.cell(0, 8,
                  f"Gegenereerd op {datetime.now():%d/%m/%Y %H:%M}   -   pagina {self.page_no()}",
                  align="C")


def _table_header(pdf: FPDF, headers, widths):
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(241, 245, 249)
    pdf.set_text_color(30, 41, 59)
    for h, w in zip(headers, widths):
        pdf.cell(w, 8, h, border=0, fill=True, align="L")
    pdf.ln(8)


def _table_row(pdf: FPDF, cells, widths, bold=False, fill=False):
    pdf.set_font("Helvetica", "B" if bold else "", 10)
    if fill:
        pdf.set_fill_color(248, 250, 252)
    for c, w in zip(cells, widths):
        pdf.cell(w, 7, str(c), border=0, fill=fill)
    pdf.ln(7)


def _fmt(minutes: int) -> str:
    m = abs(int(minutes))
    return f"{m // 60}:{m % 60:02d}"


def to_pdf_bytes(period_label: str, summary_title: str,
                 summary_df: pd.DataFrame, detail_df: pd.DataFrame,
                 total_minutes: int) -> bytes:
    pdf = ReportPDF(period_label)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Totaal", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(60, 7, "Totaal uren:")
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, _fmt(total_minutes), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(60, 7, "Aantal shiften:")
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, str(len(detail_df)), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, summary_title, new_x="LMARGIN", new_y="NEXT")
    widths = [80, 40, 40]
    _table_header(pdf, list(summary_df.columns), widths)
    for i, row in summary_df.iterrows():
        _table_row(pdf, list(row), widths, fill=(i % 2 == 1))

    if not detail_df.empty:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Detail per shift", new_x="LMARGIN", new_y="NEXT")
        d_widths = [28, 22, 22, 22, 45, 55]
        _table_header(pdf, list(detail_df.columns), d_widths)
        for i, row in detail_df.iterrows():
            _table_row(pdf, list(row), d_widths, fill=(i % 2 == 1))

    return bytes(pdf.output())
