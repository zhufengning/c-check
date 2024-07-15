import os,json ,sys,re
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from kvdb import decrypt_data,encrypt_data



def add_function(folder_path, file_name, key,fun_name,fun_level,fun_solution)->bool:
    """向风险函数库中添加一条函数信息,成功返回true,失败返回false

    :param folder_path: 路径
    :param file_name: 文件名
    :param key: 密钥
    :param fun_name: 函数名
    :param fun_level: 风险等级
    :param fun_solution: 解决方案
    """
    try:
        functions:list=json.loads(decrypt_data(folder_path,file_name,key))
        
    except FileNotFoundError:
        functions=[]
    finally:
        if any(entry['fun_name']==fun_name for entry in functions):
            print("该函数已存在")
            return False
        functions.append({"fun_name":fun_name,"fun_level":fun_level,"fun_solution":fun_solution})
        encrypt_data(folder_path,file_name,key,json.dumps(functions))
        return True

def del_function(folder_path, file_name, key,fun_name)->bool:
    """删除一条危险函数，成功返回true,失败返回false

    :param folder_path: _description_
    :param file_name: _description_
    :param key: _description_
    :param fun_name: 函数名
    """
    try:
        functions:list=json.loads(decrypt_data(folder_path,file_name,key))
        for entry in functions[:]:  # 使用切片复制列表，以便在迭代过程中安全删除
            if entry['fun_name'] == fun_name:
                functions.remove(entry)
                print("已删除")
                encrypt_data(folder_path,file_name,key,json.dumps(functions))
                return True
        print("函数不存在")
        return False
    except FileNotFoundError:
        print("文件不存在")
        return False
    

def find_function(folder_path, file_name, key,fun_name)->dict:
    """在文件中查找函数，返回一条危险函数信息,找到这条则返回该函数信息,否则返回None

    :param folder_path: _description_
    :param file_name: _description_
    :param key: _description_
    :param fun_name: _description_
    """
    try:
        functions:list=json.loads(decrypt_data(folder_path,file_name,key))
        for entry in functions[:]:  # 使用切片复制列表，以便在迭代过程中安全删除
            if entry['fun_name'] == fun_name:
                return entry
        
        print("函数不存在")
        return None

    except FileNotFoundError:
        print("文件不存在")
        return None
def find_function_from_list(functions:list,fun_name:str)->dict:
    """在列表中查找函数

    :param functions: _description_
    :param fun_name: _description_
    :return: _description_
    """
    for entry in functions:
        if entry["fun_name"] == fun_name:
            return entry
    return None        
def show_functions(folder_path, file_name, key)->list:
    """展示文件中的所有函数信息，文件不存在则返回None

    :param folder_path: _description_
    :param file_name: _description_
    :param key: _description_
    :return: _description_
    """
    try:
        functions:list=json.loads(decrypt_data(folder_path,file_name,key))
        return functions

    except FileNotFoundError:
        print("文件不存在")
        return None
    
def filter_by_level(functions:list,level:str)->list:
    """根据风险等级过滤函数信息，返回过滤后的函数信息列表

    :param functions: _description_
    :param level: _description_
    :return: _description_
    """
    return [entry for entry in functions if entry['fun_level'] == level]

def search_by_name_regex(functions:list,regex_pattern:str)->list:
    """根据函数名正则表达式过滤函数信息，返回过滤后的函数信息列表

    :param functions: _description_
    :param regex_pattern: _description_
    """
    matched_functions = [function for function in functions if re.search(regex_pattern, function['fun_name'])]
    # for func in matched_functions:
    #     print(func)
    return matched_functions
if __name__ == "__main__":
    # print(add_function("usera","函数表", "key","gets","最危险","使用 fgets（buf, size, stdin）。这几乎总是一个大问题！"))
    # add_function("usera","函数表", "key","strcpy","很危险","改为使用 strncpy。")
    # add_function("usera","函数表", "key","function1","很危险","改为使用 strncpy。")
    add_function("usera","函数表", "key","f","很危险","不能使用。")
    # del_function("usera","函数表", "key","get")
    # print(json.loads(decrypt_data("usera","函数表", "key")))
    # print(find_function("usera","函数表", "key","strcpy"))
    # add_function("usera","函数表", "key","1111","很危险","改为使用 strncpy。")
    print(show_functions("usera","函数表", "key"))
    # print(filter_by_level(show_functions("usera","函数表", "key"),"很危险"))
    # print(search_by_name_regex(show_functions("usera","函数表", "key"),'\w*ets'))

