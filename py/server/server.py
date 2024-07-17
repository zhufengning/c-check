from collections import defaultdict
import re
from typing import Union
from urllib.parse import parse_qsl
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import transaction
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


def getCache():
    zconfig = "./zodb.config"
    import ZODB.config, ZODB.FileStorage

    db = ZODB.config.databaseFromURL(zconfig)
    connection = db.open()
    root = connection.root
    return (root, db)


app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    root, db = getCache()
    root.c_files = set()
    root.asts = {}
    root.hello = "world"
    transaction.commit()
    db.close()
    return "world"


@app.get("/hello")
def read_root():
    root, db = getCache()
    t = root.hello
    db.close()
    return t


class ReadItem(BaseModel):
    filepath: str
    cwd: str = ""


# 返回文件内容，不是真正的parse
@app.post("/parse/")
def read_file(item: ReadItem):
    with open(os.path.realpath(os.path.join(item.cwd, item.filepath)), "r") as file:
        text = file.read()
    return text


def parse_c_file(filepath):
    print(filepath)
    root, db = getCache()
    asts = root.asts
    if filepath in asts:
        return
    from c_parser import cparser
    from c_parser.ply import yacc
    from c_parser import TreePrinter

    cparser = cparser.Cparser()
    parser = yacc.yacc(module=cparser)
    with open(filepath, "r") as file:
        text = file.read()
        ast = parser.parse(
            text,
            lexer=cparser.scanner,
        )
    # print(ast.printTree(0))
    asts[filepath] = ast
    root.asts = asts

    from astwalk import FunctionVisitor

    vis = FunctionVisitor()
    vis.visit(ast)

    fr = root.functions
    callee = root.callee
    new_callee = vis.callee
    print(callee, new_callee)
    for i in new_callee:
        for j in range(len(new_callee[i])):
            new_callee[i][j]["file"] = filepath
    for i in new_callee:
        if i not in callee:
            callee[i] = []
        callee[i] += new_callee[i]
    functions = vis.functions
    for i in range(len(functions)):
        functions[i]["file"] = filepath

    fr += functions

    ufr = root.used_functions
    ufr += vis.calls

    for i in range(len(fr)):
        if fr[i]["name"] in ufr or fr[i]["name"] == "main":
            fr[i]["used"] = True

    root.functions = fr
    root.used_functions = ufr

    transaction.commit()
    db.close()
    return text


def parse_headers(filename, base):
    root, db = getCache()
    pattern = r'#include\s+"([^"]+)"'
    with open(filename, "r") as file:
        text = file.read()

    # 使用 re.findall 提取所有匹配的文件名
    included_headers = re.findall(pattern, text)
    for i in range(len(included_headers)):
        if included_headers[i].endswith(".h"):
            included_headers[i] = included_headers[i][:-2] + ".c"
        included_headers[i] = os.path.realpath(os.path.join(base, included_headers[i]))
    c_files = root.c_files
    c_files.update(included_headers)
    root.c_files = c_files
    transaction.commit()
    print(included_headers)
    db.close()
    return included_headers


def check(file_path):
    # print(file_path)
    root, db = getCache()
    if file_path in root.c_files:
        parse_c_file(file_path)
        parse_headers(file_path, os.path.dirname(file_path))
        return True
    db.close()
    return False


def directory_to_tree_dict(directory):
    tree_dict = {}

    for root, dirs, files in os.walk(directory):
        # 获取当前目录的相对路径
        relative_path = os.path.relpath(root, directory)

        # 如果相对路径是'.'，则直接在最外层添加文件
        if relative_path == ".":
            current_dict = tree_dict
        else:
            # 将路径分割成各级目录
            path_parts = relative_path.split(os.sep)
            # 在字典中定位到当前目录的位置
            current_dict = tree_dict
            for part in path_parts:
                if part not in current_dict:
                    current_dict[part] = {}
                current_dict = current_dict[part]

        # 将符合条件的文件添加到字典中
        for file in files:
            file_path = os.path.join(root, file)
            if check(file_path):
                current_dict[file] = None

    return clean_empty_directories(tree_dict)


def clean_empty_directories(tree_dict):
    # 递归清理子字典
    keys_to_delete = []
    for key, value in tree_dict.items():
        if isinstance(value, dict):
            cleaned_subdict = clean_empty_directories(value)
            if not cleaned_subdict:  # 如果子字典为空，则记录该键以便删除
                keys_to_delete.append(key)
            else:
                tree_dict[key] = cleaned_subdict

    # 删除所有空的子字典
    for key in keys_to_delete:
        del tree_dict[key]

    return tree_dict


class ScanItem(BaseModel):
    filename: str


@app.post("/scan/")
def scan(item: ScanItem):
    root, db = getCache()
    filename = item.filename
    c_files = root.c_files
    c_files.clear()
    c_files.add(filename)
    root.c_files = c_files
    root.asts = {}
    root.functions = []
    root.used_functions = ["main"]
    root.callee = {}
    transaction.commit()
    db.close()
    folder = os.path.dirname(filename)
    parse_c_file(filename)
    parse_headers(filename, folder)
    tree_dict = directory_to_tree_dict(folder)
    return tree_dict


import astwalk


@app.get("/debug")
def debug():
    root, db = getCache()
    print(root.asts)

    for i in root.c_files:
        print(i)
    db.close()


@app.get("/test")
def test():
    root, db = getCache()
    asts = root.asts
    db.close()
    for ast in asts.values():
        astwalk.getVars(ast)
    return "?"


class User(BaseModel):
    user: str
    passwd: str


@app.post("/check_user")
def check_user(user: User):
    from user import user_check

    return user_check(user.user, user.passwd)


@app.post("/create_user")
def check_user(user: User):
    from user import user_create

    return user_create(user.user, user.passwd)


@app.post("/delete_user")
def check_user(user: User):
    from user import user_delete

    return user_delete(user.user, user.passwd)


@app.post("/vars")
def vars(item: ReadItem):
    f = os.path.realpath(os.path.join(item.cwd, item.filepath))
    root, db = getCache()

    # parse_c_file(f)
    r = astwalk.getVars(root.asts[f])
    db.close()
    return r


class VarItem(ReadItem):
    var: str
    fun: str


@app.post("/var_pos")
def var_pos(item: VarItem):
    f = os.path.realpath(os.path.join(item.cwd, item.filepath))
    var = item.var
    fun = item.fun
    root, db = getCache()
    r = astwalk.findVar(root.asts[f], var, fun)
    db.close()
    return r


@app.get("/functions")
def functions():
    root, db = getCache()
    r = root.functions
    db.close()
    return r


@app.get("/callee")
def callee():
    root, db = getCache()
    r = root.callee
    db.close()
    return r


@app.post("/mem")
def mem(item: ReadItem):
    file = os.path.realpath(os.path.join(item.cwd, item.filepath))
    root, db = getCache()
    ast = root.asts[file]
    db.close()
    vis = astwalk.MallocVisitor()
    vis.visit(ast)
    print(vis.malloced, list(vis.freed))
    s = [
        x
        for x in vis.malloced
        if len(
            list(filter(lambda y: x["fun"] == y[1] and x["name"] == y[0], vis.freed))
        )
        == 0
    ]

    return s

@app.post("/graph")
def graph(item: ReadItem):
    file = os.path.realpath(os.path.join(item.cwd, item.filepath))
    root, db = getCache()
    ast = root.asts[file]

    from vgraphtest import gen_graph

    gen_graph(ast)
    db.close()
    return "OK"

@app.post("/risk")
def risk(user: User):
    root, db = getCache()

    from f_management.function_management import show_functions
    from g_report.generate_report import generate_report, Risk_fun_Visitor
    from g_report.complexity_analysis import ComplexityAnalyzer

    userbase = os.path.join("users", user.user)
    rules = show_functions(userbase, "risk_fun", user.passwd)
    #print(rules)

    al = []
    av = []
    ac = []

    for f in root.asts:
        print(f)
        ast = root.asts[f]
        vis = Risk_fun_Visitor(rules, f)
        vis.visit(ast)
        al += vis.risk_fun_infos
        var_vis = astwalk.getVars2(ast)
        all_vars = var_vis.globalv + var_vis.localv
        unused_vars = [x for x in all_vars if x["used"] == False]
        for i in range(len(unused_vars)):
            unused_vars[i]["File Path"] = f
        av += unused_vars

        ca = ComplexityAnalyzer(ast, f)
        ac.append(ca.analyze())

    af = [x for x in root.functions if x["used"]==False]
    for i in range(len(af)):
        af[i].pop("used")
        av[i].pop("used")

    print(av)
    generate_report(os.path.join(os.path.dirname(__file__),"..", "reports","report.pdf"),"Program", av,al,af,ac)

    db.close()
    return "ok"

@app.post("/rules")
def rules(user: User):
    root, db = getCache()

    from f_management.function_management import show_functions

    userbase = os.path.join("users", user.user)
    rules = show_functions(userbase, "risk_fun", user.passwd)
    db.close()
    return rules


class UpdateRulesItem(BaseModel):
    user: str
    passwd: str
    rules: list[dict]
@app.post("/update_rules")
def update_rules(item: UpdateRulesItem):

    from f_management.function_management import set_function_list

    userbase = os.path.join("users", item.user)
    set_function_list(userbase, "risk_fun", item.passwd, item.rules)
    return "ok"


@app.post("/init_rules")
def init_rules(user: User):

    from f_management.function_management import initialize_functions

    userbase = os.path.join("users", user.user)
    initialize_functions(userbase, "risk_fun", user.passwd)
    return "ok"
