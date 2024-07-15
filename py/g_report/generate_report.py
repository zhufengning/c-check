import os,sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate,Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from c_parser.DFSVisitor import DFSVisitor
import c_parser.ply.yacc as yacc
from c_parser import AST, cparser
from f_management import function_management


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

def generate_pie_chart()
def generate_report(file_name)->str:
    """生成报告

    :param file_name: _description_
    :return: _description_
    """
    folder_path= "py/reports"
    full_path = os.path.join(folder_path, file_name)

    

    # 定义要在文档中插入的内容
    # 返回一个字典，包含了多个预定义的样式，例如 'Title'、'Normal'、'Italic' 等。
    pdfmetrics.registerFont(TTFont('SimSun', 'py\g_report\SimSun.ttf'))  #注册字体
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(fontName='SimSun', name='Song', leading=20, fontSize=12))  # 自己增加新注册的字体
    # 创建 SimpleDocTemplate 对象时传入完整路径
    pdf = SimpleDocTemplate(full_path, pagesize=letter)
    content = [
        Paragraph("Hello, World!", styles['Title']),
        Paragraph("项目名称",styles['Song']),
        Paragraph("审计日期",styles['Song']),
        Paragraph("This is a simple PDF document generated using ReportLab.", styles['Normal']),
        # 可以添加更多的 Paragraph 或者其他 ReportLab 组件
    ]
    content.append(Image("py\g_report\风险报告.jpg",width=500,height=200))

    # 将内容添加到文档中
    pdf.build(content)


if __name__ == '__main__':
    file_name = "report.pdf"
    generate_report(file_name)
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
    risk_functions=[{'fun_name': 'gets', 'fun_level': '最危险', 'fun_solution': '使用 fgets（buf, size, stdin）。这几乎总是一个大问题！'},
                     {'fun_name': 'strcpy', 'fun_level': '很危险', 'fun_solution': '改为使用 strncpy。'}, 
                     {'fun_name': 'function1', 'fun_level': '很危险', 'fun_solution': '改为使用 strncpy。'}, 
                     {'fun_name': 'f', 'fun_level': '很 危险', 'fun_solution': '不能使用。'}]
    v=Risk_fun_Visitor(risk_functions)
    v.visit(ast)
    print(v.risk_fun_infos)
    for node in v.risk_fun_nodes:
        print(node)