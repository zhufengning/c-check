import sys
import os
from AES_cryptor import AEScryptor, MData
from Crypto.Cipher import AES
from binascii import unhexlify

def decrypt_data(folder_path, key, name):
    found = False
    padded_key = AEScryptor.pad_key(key)

    try:
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)

            with open(file_path, 'rb') as f:
                # 读取加密的文件头部信息
                header = f.readline().strip()
                if header != b'MY_ENCRYPTED_FILE':
                    continue

                # 读取加密的元数据
                encrypted_metadata = f.read(256)  # 假设元数据长度为256字节，根据实际情况调整
                aes_metadata = AEScryptor(padded_key, AES.MODE_ECB)
                decrypted_metadata = aes_metadata.decrypt(encrypted_metadata)

                # 解析元数据
                iv = None
                mode = None
                padding_mode = None
                metadata_lines = decrypted_metadata.split(b'\n')
                for line in metadata_lines:
                    if line.startswith(b'IV:'):
                        iv = line[len(b'IV:'):].strip()
                    elif line.startswith(b'MODE:'):
                        mode = int.from_bytes(line[len(b'MODE:'):], byteorder='big')
                    elif line.startswith(b'PADDING:'):
                        padding_mode = line[len(b'PADDING:'):].decode()

                if None in (iv, mode, padding_mode):
                    print(f"解密文件名 {file_path} 失败：缺少必要的加密信息")
                    continue

                # 读取加密的数据（实际上是文件内容）
                encrypted_data = f.read()

                try:
                    aes_filename = AEScryptor(padded_key, mode, iv, padding_mode)
                    decrypted_filename_bytes = unhexlify(file)  # 将十六进制文件名转换为字节串
                    decrypted_filename = aes_filename.decrypt(decrypted_filename_bytes).decode()

                    if name.decode() == decrypted_filename:
                        # print(f"在文件 {file_path} 中找到匹配的文件名。")
                        found = True
                        break

                except Exception as e:
                    print(f"解密文件名 {file_path} 失败：{e}")
                    continue

    except Exception as e:
        print(f"处理文件 {file_path} 时出错：{e}")

    return 1 if found else 0

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("用法: python decrypt_data.py <文件夹路径> <解密密钥> <未加密的文件名>")
        sys.exit(1)

    folder_path = sys.argv[1]
    decryption_key = sys.argv[2].encode()
    unencrypted_file_name = sys.argv[3].encode()

    result = decrypt_data(folder_path, decryption_key, unencrypted_file_name)
    sys.stdout.write(str(result) + "\n")
    sys.exit(0)





import sys
import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from binascii import unhexlify

class AEScryptor:
    def __init__(self, key, mode, iv=None, padding_mode="ZeroPadding"):
        self.key = key
        self.mode = mode
        self.iv = iv
        self.padding_mode = padding_mode

    def encrypt(self, data):
        if self.mode == AES.MODE_CBC:
            cipher = AES.new(self.key, self.mode, self.iv)
        elif self.mode == AES.MODE_ECB:
            cipher = AES.new(self.key, self.mode)

        return cipher.encrypt(data)

    def decrypt(self, encrypted_data):
        if self.mode == AES.MODE_CBC:
            cipher = AES.new(self.key, self.mode, self.iv)
        elif self.mode == AES.MODE_ECB:
            cipher = AES.new(self.key, self.mode)

        return cipher.decrypt(encrypted_data)

    @staticmethod
    def pad_key(key):
        return key.ljust(16, b'\0')  # 假设密钥长度为16字节，根据需要调整


def decrypt_data(folder_path, key, unencrypted_file_name):
    found = False
    padded_key = AEScryptor.pad_key(key)

    try:
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)

            with open(file_path, 'rb') as f:
                header = f.readline().strip()
                if header != b'MY_ENCRYPTED_FILE':
                    continue

                encrypted_metadata = f.read(256)  # 根据实际情况调整元数据长度
                aes_metadata = AEScryptor(padded_key, AES.MODE_ECB)
                decrypted_metadata = aes_metadata.decrypt(encrypted_metadata)

                iv = None
                mode = None
                padding_mode = None
                metadata_lines = decrypted_metadata.split(b'\n')
                for line in metadata_lines:
                    if line.startswith(b'IV:'):
                        iv = line[len(b'IV:'):].strip()
                    elif line.startswith(b'MODE:'):
                        mode = int.from_bytes(line[len(b'MODE:'):], byteorder='big')
                    elif line.startswith(b'PADDING:'):
                        padding_mode = line[len(b'PADDING:'):].decode()

                if None in (iv, mode, padding_mode):
                    print(f"解密文件名 {file_path} 失败：缺少必要的加密信息")
                    continue

                encrypted_data = f.read()

                try:
                    aes_filename = AEScryptor(padded_key, mode, iv, padding_mode)
                    decrypted_filename_bytes = unhexlify(file)
                    decrypted_filename = aes_filename.decrypt(decrypted_filename_bytes).decode()

                    if unencrypted_file_name.decode() == decrypted_filename:
                        print(f"在文件 {file_path} 中找到匹配的文件名: {decrypted_filename}")

                        # 读取文件内容并输出
                        decrypted_data = aes_filename.decrypt(encrypted_data)
                        print("文件内容:")
                        print(decrypted_data.decode())

                        found = True
                        break

                except Exception as e:
                    print(f"解密文件名 {file_path} 失败：{e}")
                    continue

    except Exception as e:
        print(f"处理文件 {file_path} 时出错：{e}")

    return 1 if found else 0


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("用法: python decrypt_data.py <文件夹路径> <解密密钥> <未加密的文件名>")
        sys.exit(1)

    folder_path = sys.argv[1]
    key = sys.argv[2].encode()  # 解密密钥必须是字节
    unencrypted_file_name = sys.argv[3].encode()  # 将未加密的文件名转换为字节串

    result = decrypt_data(folder_path, key, unencrypted_file_name)
    sys.stdout.write(str(result) + "\n")
    sys.exit(0)
