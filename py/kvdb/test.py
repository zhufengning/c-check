import json
from decrypt_data import decrypt_data
from encrypt_data import encrypt_data

mp = {}

mp["kkk"] = {"level":0}
mp["aaa"] = {"level":0}
mp["ccc"] = {"level":0}




encrypt_data("usera","函数表", "哈哈", json.dumps(mp))

print(json.loads(decrypt_data("usera","函数表", "哈哈")))


