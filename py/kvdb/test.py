import json
from decrypt_data import decrypt_data
from encrypt_data import encrypt_data

mp = {}

mp["gets"] = {"level":0,"描述":"使用 fgets（buf, size, stdin）。这几乎总是一个大问题！"}
mp["aaa"] = {"level":0}
mp["ccc"] = {"level":0}




encrypt_data("usera","函数表", "哈哈", json.dumps(mp))

print(json.loads(decrypt_data("usera","函数表", "哈哈")))


