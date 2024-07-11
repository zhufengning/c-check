import sys
import os
from AES_cryptor import AEScryptor, MData
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def encrypt_data(folder_path, name, key, mode, data, padding_mode):
    """_summary_

    :param folder_path:路径
    :param name: 文件名
    :param key: 密码
    :param mode: 模式
    :param data: 需要加密的数据
    :param padding_mode: _description_
    """
    mdata = MData()
    mdata.str(data)

    # 生成随机的IV，仅用于CBC模式
    iv = get_random_bytes(16)

    # 使用CBC模式加密数据
    aes_data = AEScryptor(key, mode, iv, padding_mode)
    encrypted_data = aes_data.encrypt(mdata.data)

    # 使用ECB模式加密元数据
    aes_metadata = AEScryptor(key, AES.MODE_ECB)
    encrypted_metadata = aes_metadata.encrypt(
        b'IV:' + iv + b'\n' +
        b'MODE:' + mode.to_bytes(1, byteorder='big') + b'\n' +
        b'PADDING:' + padding_mode.encode() + b'\n' +
        b'DATA_START\n'
    )

    # 创建加密文件路径
    encrypted_filename = aes_data.encrypt(name.encode()).hex()
    file_path = os.path.join(folder_path, encrypted_filename)

    with open(file_path, 'wb') as f:
        # 写入加密的元数据头部信息
        f.write(b'MY_ENCRYPTED_FILE\n')
        f.write(encrypted_metadata)

        # 写入加密的数据
        f.write(encrypted_data)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("用法: python encrypt_data.py <文件夹路径> <密钥> <文件名>")
        sys.exit(1)

    folder_path = sys.argv[1]
    key = sys.argv[2]
    padded_key = AEScryptor.pad_key(key.encode())
    file_name = sys.argv[3]

    mode = AES.MODE_CBC  # 数据加密模式为CBC
    data = sys.stdin.read()
    padding_mode = "ZeroPadding"

    encrypt_data(folder_path, file_name, padded_key, mode, data.strip(), padding_mode)
