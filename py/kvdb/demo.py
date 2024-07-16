import json
from decrypt_data import decrypt_data
from encrypt_data import encrypt_data
ls=[]
ls.append({"fun_name":"gets","level":0,"fun_solution":"使用 fgets（buf, size, stdin）。这几乎总是一个大问题！"})
ls.append({"fun_name":"gets","level":0,"fun_solution":"使用 fgets（buf, size, stdin）。这几乎总是一个大问题！"})


encrypt_data("usera","函数表", "哈哈", json.dumps(ls))

print(json.loads(decrypt_data("usera","函数表", "哈哈")))