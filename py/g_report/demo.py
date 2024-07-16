from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

data = [
    ["Name", "Age", "Country"],
    ["Alice", "24", "USA"],
    ["Bob", "30", "Canada"],
    ["Eve", "29", "UK"],
     ["Eve", "29", "UK"]
]

c = canvas.Canvas("table_example.pdf", pagesize=letter)
table = Table(data)

# 添加表格样式
style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ])
table.setStyle(style)

# 绘制表格
table.wrapOn(c, 200, 400)
table.drawOn(c, 100, 400)
c.save()
