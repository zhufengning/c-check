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
    root, db = getCache()
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
    asts = root.asts
    asts[filepath] = ast
    root.asts = asts
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
