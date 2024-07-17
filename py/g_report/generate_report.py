import os,sys,tempfile,io

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate,Image,Table,TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics import renderPM
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.renderPDF import drawToString
from PIL import Image as PILImage
from c_parser.DFSVisitor import DFSVisitor
import c_parser.ply.yacc as yacc
from c_parser import AST, cparser
from f_management import function_management
import matplotlib.pyplot as plt


class Risk_fun_Visitor(DFSVisitor):
    def __init__(self,risk_funs:list):
        super().__init__()
        self.risk_fun_nodes = []
        self.risk_fun_infos=[]
        self.risk_funcions=risk_funs[:]

    def get_result(self):
        """得到检测结果

        :return: _description_
        """
        return self.risk_fun_nodes,self.risk_fun_infos

    def fn(self, node):
        if type(node) is AST.FunctionCall:
            entry=function_management.find_function_from_list(self.risk_funcions,node.id)
            if entry:
                self.risk_fun_nodes.append(node)
                self.risk_fun_infos.append({"position":node.pos,"fun_name":entry["fun_name"],"fun_level":entry["fun_level"],"fun_solution":entry["fun_solution"]})

def generate_risk_fun_pie_chart(risk_fun_infos:list,level_nums:dict):
    """生成风险函数饼图
    Args:
        risk_fun_infos (list): 风险函数信息列表
    """
     # 提取标签和大小
    labels = list(level_nums.keys())
    sizes = list(level_nums.values())
    if all(size == 0 for size in sizes):
        # 如果所有的值都是零，可以选择返回空字符串或者其他提示信息
        print("无有效数据生成饼图。")
        return ""
    # 设置中文显示
    plt.rcParams['font.sans-serif'] = 'SimHei'

    # 创建画布
    plt.figure(figsize=(8, 6))

    # 绘制饼图
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title('风险函数分布饼图', fontsize=16)

    # 添加图例
    plt.legend(labels, loc="best", fontsize=10)

    # 保持图像比例一致
    plt.axis('equal')

    # 保存饼图到临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        chart_filename = temp_file.name
        # chart_filename="py\g_report\图片"
        plt.savefig(chart_filename)

    plt.close()
    print(chart_filename)
    return chart_filename
def generate_risk_fun_table(risk_fun_infos:list,table_name:str)->tuple[Table,Paragraph]:
    """返回生成的表格和表格名

    :param risk_fun_infos: _description_
    """
    # 数据表格
    table_data = [
        ['Position', 'Function Name', 'Function Level', 'Function Solution']
    ]

    for entry in risk_fun_infos:
        position = '{} x {}'.format(entry['position'][0], entry['position'][1])
        fun_name = entry['fun_name']
        fun_level = entry['fun_level']
        fun_solution = entry['fun_solution']
        table_data.append([position, fun_name, fun_level, fun_solution])

    # 创建表格对象
    table = Table(table_data, colWidths=[80, 80, 80, 200])
    # 设定表格样式
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),  # 设置表头背景色
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),  # 设置表头文字颜色
        ('FONTNAME', (0, 0), (-1, -1), 'SimSun'),  # 设置整个表格的字体为Simsun
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # 设置所有单元格居中对齐
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),  # 设置表格内部网格线
        ('BOX', (0, 0), (-1, -1), 0.25, colors.black),  # 设置表格外框线
    ]))
    # 添加表名
    table_title_style = ParagraphStyle(
        'TitleStyle',
        fontName='SimSun',
        fontSize=16,
        textColor=colors.black,
        spaceAfter=10,
        alignment=1  # 1代表居中对齐
    )
    table_title = Paragraph(table_name, table_title_style)
    return table,table_title
import os
def generate_report(file_name:str,program:str,risk_fun_infos:list):
    """生成报告

    :param file_name: _description_
    :return: _description_
    """
    folder_path= os.path.join(os.path.dirname(__file__),"..", "reports")
    full_path = os.path.join(folder_path, file_name)
    # 定义要在文档中插入的内容
    # 返回一个字典，包含了多个预定义的样式，例如 'Title'、'Normal'、'Italic' 等。
    pdfmetrics.registerFont(TTFont('SimSun', os.path.join(os.path.dirname(__file__), "SimSun.ttf")))  #注册字体
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(fontName='SimSun', name='Song', leading=20, fontSize=12))  # 自己增加新注册的字体
    styles['Title'].fontName = 'SimSun' #将标题字体更改为'SimSun'
    styles['Heading1'].fontName = 'SimSun'
    # 创建 SimpleDocTemplate 对象时传入完整路径
    pdf = SimpleDocTemplate(full_path, pagesize=letter)
    # 获取当前日期的字符串格式
    current_date_str = datetime.now().strftime('%Y-%m-%d')
    content = [
        Paragraph("审计报告", styles['Title']),
        Paragraph("项目名称："+program,styles['Song']),
        Paragraph("审计日期："+current_date_str,styles['Song']),
        # 可以添加更多的 Paragraph 或者其他 ReportLab 组件
    ]
    level_nums = {
        '最危险': 0,
        '很危险': 0,
        '危险': 0,
        '稍低危险': 0,
        '中等危险': 0,
        '低危险': 0,
        # '无效函数': 0
    }
    for func in risk_fun_infos:
        level = func['fun_level']
        if level in level_nums:
            level_nums[level] += 1
    # 生成饼图
    pie_chart_path = generate_risk_fun_pie_chart(risk_fun_infos,level_nums)
    if pie_chart_path=="":
        content.append(Paragraph("无有效数据生成饼图",styles['Song']))
    else:
        content.append(Image(pie_chart_path, width=400, height=400,hAlign='CENTER', kind='proportional'))
    # 生成表
    table,table_title = generate_risk_fun_table(risk_fun_infos,'扫描到的风险函数表')
    content.append(table_title)
    # 将表格对象添加到内容列表中
    content.append(table)
    pdf.build(content)
    # os.remove(pie_chart_path)


if __name__ == '__main__':

    cparser = cparser.Cparser()
    parser = yacc.yacc(module=cparser)
    source2 = """#include <stdio.h>
    #define a 2
    int f() {
    f();
    return 1;
    }
    int main() {
    int x = 0;
    gets(x);
    int *y = &x;
    int arr[50];
    arr[0] = 1;
    arr[1] = arr[0];
    int a = 0;
    int b;
    b=(a+1)*3;
    printf("%d", a);
    f(a + 2);
    float fuck;
    printf("%lf", fuck);
    while (1) {
    }
    }

    """

    ast = parser.parse(
        source2,
        lexer=cparser.scanner,
    )

    # risk_functions=[{'fun_name': 'gets', 'fun_level': '最危险', 'fun_solution': '使用 fgets（buf, size, stdin）。这几乎总是一个大问题！'},
    #                  {'fun_name': 'strcpy', 'fun_level': '很危险', 'fun_solution': '改为使用 strncpy。'},
    #                  {'fun_name': 'function1', 'fun_level': '很危险', 'fun_solution': '改为使用 strncpy。'},
    #                  {'fun_name': 'f', 'fun_level': '很危险', 'fun_solution': '不能使用。'}]
    risk_functions=[{'fun_name': 'gets', 'fun_level': '最危险', 'fun_solution': '使用 fgets（buf, size, stdin）这几乎总是一个大问题'},
                    {'fun_name': 'strcpy', 'fun_level': '很危险', 'fun_solution': '改为使用 strncpy'},
                    {'fun_name': 'strcat', 'fun_level': '很危险', 'fun_solution': '改为使用 strncat'},
                    {'fun_name': 'sprintf', 'fun_level': '很危险', 'fun_solution': '改为使用 snprintf，或者使用精度说明符'},
                    {'fun_name': 'scanf', 'fun_level': '很危险', 'fun_solution': '使用精度说明符，或自己进行解析'},
                    {'fun_name': 'sscanf', 'fun_level': '很危险', 'fun_solution': '使用精度说明符，或自己进行解析'},
                    {'fun_name': 'vsprintf', 'fun_level': '很危险', 'fun_solution': '改为使用 vsnprintf，或者使用精度说明符'},
                    {'fun_name': 'vscanf', 'fun_level': '很危险', 'fun_solution': '使用精度说明符，或自己进行解析'},
                    {'fun_name': 'vsscanf', 'fun_level': '很危险', 'fun_solution': '使用精度说明符，或自己进行解析'},
                    {'fun_name': 'streadd', 'fun_level': '很危险', 'fun_solution': '确保分配的目的地参数大小是源参数大小的四倍'},
                    {'fun_name': 'strecpy', 'fun_level': '很危险', 'fun_solution': '确保分配的目的地参数大小是源参数大小的四倍'},
                    {'fun_name': 'strtrns', 'fun_level': '危险', 'fun_solution': '手工检查来查看目的地大小是否至少与源字符串相等'},
                    {'fun_name': 'realpath', 'fun_level': '稍低危险', 'fun_solution': '分配缓冲区大小为 MAXPATHLEN。同样，手工检查参数以确保输入参数不超过 MAXPATHLEN'},
                    {'fun_name': 'syslog', 'fun_level': '稍低危险', 'fun_solution': '在将字符串输入传递给该函数之前，将所有字符串输入截成合理的大小'},
                    {'fun_name': 'getopt_long', 'fun_level': '稍低危险', 'fun_solution': '在将字符串输入传递给该函数之前，将所有字符串输入截成合理的大小'},
                    {'fun_name': 'getopt', 'fun_level': '稍低危险', 'fun_solution': '在将字符串输入传递给该函数之前，将所有字符串输入截成合理的大小'},
                    {'fun_name': 'getpass', 'fun_level': '稍低危险', 'fun_solution': '在将字符串输入传递给该函数之前，将所有字符串输入截成合理的大小'},
                    {'fun_name': 'getchar', 'fun_level': '中等危险', 'fun_solution': '如果在循环中使用该函数，确保检查缓冲区边界'},
                    {'fun_name': 'fgetc', 'fun_level': '中等危险', 'fun_solution': '如果在循环 中使用该函数，确保检查缓冲区边界'},
                    {'fun_name': 'getc', 'fun_level': '中等危险', 'fun_solution': '如果在循环中使用该函数，确保检查缓冲区边界'},
                    {'fun_name': 'read', 'fun_level': '中等危险', 'fun_solution': '如果在循环中使用该函数，确保检查缓冲区边界'},
                    {'fun_name': 'bcopy', 'fun_level': '低危险', 'fun_solution': '确保缓冲区大小与它所说的一样大'},
                    {'fun_name': 'fgets', 'fun_level': '低危险', 'fun_solution': '确保缓冲区大小与它所说的一样大'},
                    {'fun_name': 'memcpy', 'fun_level': '低危险', 'fun_solution': '确保缓冲区大小与它所说的一样大'},
                    {'fun_name': 'strccpy', 'fun_level': '低危险', 'fun_solution': '确保缓冲区大小与它所说的一样大'},
                    {'fun_name': 'strncpy', 'fun_level': '低危险', 'fun_solution': '确保缓冲区大小与它所说的一样大'},
                    {'fun_name': 'vsnprintf', 'fun_level': '低危险', 'fun_solution': '确保缓冲区大小与它所说的一样大'}]
    v=Risk_fun_Visitor(risk_functions)
    v.visit(ast)
    print(v.risk_fun_infos)
    for node in v.risk_fun_nodes:
        print(node)
    file_name = "report.pdf"
    generate_report(file_name,"test",v.risk_fun_infos)
