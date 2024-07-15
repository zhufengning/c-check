import os,sys,tempfile,io

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate,Image
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
        
def generate_report(file_name:str,program:str,risk_fun_infos:list)->str:
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
    styles['Title'].fontName = 'SimSun' #将标题字体更改为'SimSun'
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
    # level_nums = {
    #     '最危险': 0,
    #     '很危险': 0,
    #     '危险': 0,
    #     '稍低危险': 0,
    #     '中等危险': 0,
    #     '低危险': 0,
    #     # '无效函数': 0
    # }
    # for func in risk_fun_infos:
    #     level = func['fun_level']
    #     if level in level_nums:
    #         level_nums[level] += 1
    level_nums = {
        '最危险': 1,
        '很危险': 2,
        '危险': 3,
        '稍低危险': 4,
        '中等危险': 5,
        '低危险': 6,
        # '无效函数': 0
    }
    pie_chart_path = generate_risk_fun_pie_chart(risk_fun_infos,level_nums)
    content.append(Image(pie_chart_path, width=400, height=400,hAlign='CENTER', kind='proportional'))
    # 将内容添加到文档中
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
                     {'fun_name': 'f', 'fun_level': '很危险', 'fun_solution': '不能使用。'}]
    v=Risk_fun_Visitor(risk_functions)
    v.visit(ast)
    print(v.risk_fun_infos)
    for node in v.risk_fun_nodes:
        print(node)
    file_name = "report.pdf"
    generate_report(file_name,"test",v.risk_fun_infos)