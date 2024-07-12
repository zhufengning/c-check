import hashlib
import sys
import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from AES_cryptor import AEScryptor, MData

basedir = os.path.join(os.path.dirname(__file__), "db")

def decrypt_data(folder_path, file_name, key, mode=AES.MODE_CBC, padding_mode="ZeroPadding"):
    key = hashlib.sha256(key.encode()).digest()
    folder_path = os.path.join(basedir, folder_path)

    # 使用相同的 IV（初始化向量）
    iv = b'\xc7\xab\xd2\xda\xa0J\xf7\xe9\x11\x16\xd3\xb7\xd2\xe4\t\x89'

    # 创建AEScryptor对象用于文件名解密
    aes_filename = AEScryptor(key, mode, iv, padding_mode)
    encrypted_filename = aes_filename.encrypt(file_name.encode()).hex()
    file_path = os.path.join(folder_path, encrypted_filename)

    # 读取加密文件的数据
    with open(file_path, "rb") as f:
        header = f.readline()  # 读取文件头部
        if header.strip() != b"MY_ENCRYPTED_FILE":
            raise ValueError("Invalid encrypted file format")

        encrypted_data = f.read()  # 读取加密的数据

    # 创建AEScryptor对象用于数据解密
    aes_data = AEScryptor(key, mode, iv, padding_mode)
    decrypted_data = aes_data.decrypt(encrypted_data)

    # 处理解密后的数据
    mdata = MData()
    mdata.data = decrypted_data
    original_data = mdata.toString()

    return original_data
