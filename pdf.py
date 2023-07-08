from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


class CreatePDF():
    def __init__(self, filename, names, **kwargs):
        self.filename = filename
        self.kwargs = kwargs
        self.names = names
        self.data = [["S/N", "REG NO"]] + [[str(i + 1), name] for i, name in enumerate(self.names)]
        self.table_style = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 14),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ])
        self.table = Table(self.data)
        self.table.setStyle(self.table_style)
        self.elements = [self.table]
       

    def create_pdf(self):
        self.pdf = SimpleDocTemplate(self.filename, pagesize=letter)
        self.pdf.build(self.elements)

