import re
from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
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

asts = {}


@app.get("/")
def read_root():
    return {"Hello": "World"}

class ReadItem(BaseModel):
    filepath: str
    cwd: str = ""

@app.post("/parse/")
def read_file(item: ReadItem):
    with open(os.path.join(item.cwd, item.filepath), "r") as file:
        text = file.read()
    return text

def parse_c_file(filepath):
    global asts
    from c_parser import Cparser
    from c_parser.ply import yacc
    from c_parser import TreePrinter

    cparser = Cparser()
    parser = yacc.yacc(module=cparser)
    with open(filepath, "r") as file:
        text = file.read()
        ast = parser.parse(
            text,
            lexer=cparser.scanner,
        )
    asts[filepath] = ast
    return text


c_files = set()


def parse_headers(filename, base):
    global c_files
    pattern = r'#include\s+"([^"]+)"'
    with open(filename, "r") as file:
        text = file.read()

    # 使用 re.findall 提取所有匹配的文件名
    included_headers = re.findall(pattern, text)
    for i in range(len(included_headers)):
        if included_headers[i].endswith(".h"):
            included_headers[i] = included_headers[i][:-2] + ".c"
        included_headers[i] = os.path.realpath(os.path.join(base, included_headers[i]))
    c_files.update(included_headers)
    # print(included_headers)

    return included_headers


def check(file_path):
    # print(file_path)
    if file_path in c_files:
        parse_c_file(file_path)
        parse_headers(file_path, os.path.dirname(file_path))
        return True
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
def scan(item:ScanItem):
    global c_files
    filename = item.filename
    c_files.clear()
    c_files.add(filename)
    folder = os.path.dirname(filename)
    parse_headers(filename, folder)
    tree_dict = directory_to_tree_dict(folder)
    return tree_dict
