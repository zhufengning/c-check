import hashlib
import sys

import os
sys.path.append(os.path.dirname(__file__))
from AES_cryptor import AEScryptor, MData
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

basedir = os.path.join(os.path.dirname(__file__), "db")


def encrypt_data(
    folder_path, file_name, key, data, mode=AES.MODE_CBC, padding_mode="ZeroPadding"
):
    key = hashlib.sha256(key.encode()).digest()
    folder_path = os.path.join(basedir, folder_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    mdata = MData()
    mdata.str(data)

    iv = b"\xc7\xab\xd2\xda\xa0J\xf7\xe9\x11\x16\xd3\xb7\xd2\xe4\t\x89"

    # 使用CBC模式加密数据
    aes_data = AEScryptor(key, mode, iv, padding_mode)
    encrypted_data = aes_data.encrypt(mdata.data)

    # 创建加密文件路径
    encrypted_filename = aes_data.encrypt(file_name.encode()).hex()
    file_path = os.path.join(folder_path, encrypted_filename)

    with open(file_path, "wb") as f:
        # 写入加密的元数据头部信息
        f.write(b"MY_ENCRYPTED_FILE\n")

        # 写入加密的数据
        f.write(encrypted_data)
