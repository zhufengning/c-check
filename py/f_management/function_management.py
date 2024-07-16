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
def initialize_functions(folder_path, file_name, key):
    """向用户文件添加内置危险函数

    :param folder_path: _description_
    :param file_name: _description_
    :param key: _description_
    """
    functions=[
    {'fun_name': 'gets', 'fun_level': '最危险', 'fun_solution': '使用 fgets（buf, size, stdin）这几乎总是一个大问题'},
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
    {'fun_name': 'fgetc', 'fun_level': '中等危险', 'fun_solution': '如果在循环中使用该函数，确保检查缓冲区边界'},
    {'fun_name': 'getc', 'fun_level': '中等危险', 'fun_solution': '如果在循环中使用该函数，确保检查缓冲区边界'},
    {'fun_name': 'read', 'fun_level': '中等危险', 'fun_solution': '如果在循环中使用该函数，确保检查缓冲区边界'},
    {'fun_name': 'bcopy', 'fun_level': '低危险', 'fun_solution': '确保缓冲区大小与它所说的一样大'},
    {'fun_name': 'fgets', 'fun_level': '低危险', 'fun_solution': '确保缓冲区大小与它所说的一样大'},
    {'fun_name': 'memcpy', 'fun_level': '低危险', 'fun_solution': '确保缓冲区大小与它所说的一样大'},
    {'fun_name': 'strccpy', 'fun_level': '低危险', 'fun_solution': '确保缓冲区大小与它所说的一样大'},
    {'fun_name': 'strncpy', 'fun_level': '低危险', 'fun_solution': '确保缓冲区大小与它所说的一样大'},
    {'fun_name': 'vsnprintf', 'fun_level': '低危险', 'fun_solution': '确保缓冲区大小与它所说的一样大'}
]
    encrypt_data(folder_path,file_name,key,json.dumps(functions))
    
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
    # add_function("usera","函数表", "key","f","很危险","不能使用。")
    # del_function("usera","函数表", "key","get")
    # print(json.loads(decrypt_data("usera","函数表", "key")))
    # print(find_function("usera","函数表", "key","strcpy"))
    # add_function("usera","函数表", "key","1111","很危险","改为使用 strncpy。")
    # print(show_functions("usera","函数表", "key"))
    # print(filter_by_level(show_functions("usera","函数表", "key"),"很危险"))
    # print(search_by_name_regex(show_functions("usera","函数表", "key"),'\w*ets'))
    initialize_functions("usera","初始化表", "key")
    print(show_functions("usera","初始化表", "key"))
    # i=0
    # for entry in show_functions("usera","初始化表", "key"):
    #     i+=1
    #     print(entry)
    # print(i)


