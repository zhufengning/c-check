from Crypto.Cipher import AES
import base64
import binascii
import os
from Crypto.Random import get_random_bytes

class MData():
    def __init__(self, data=b"", characterSet='utf-8'):
        self.data = data
        self.characterSet = characterSet

    def fromString(self, data):
        self.data = data.encode(self.characterSet) # String -> bytes
        return self.data

    def fromBase64(self, data):
        self.data = base64.b64decode(data.encode(self.characterSet)) # Base64 -> bytes
        return self.data

    def fromHexStr(self, data):
        self.data = binascii.a2b_hex(data) # Hex string -> bytes
        return self.data

    def toString(self):
        return self.data.decode(self.characterSet)

    def toBase64(self):
        return base64.b64encode(self.data).decode(self.characterSet)

    def toHexStr(self):
        return binascii.b2a_hex(self.data).decode(self.characterSet)

    def str(self, data):
        try:
            if isinstance(data, bytes):
                self.data = data
                return self.data
            elif isinstance(data, str):
                return self.fromString(data)
            else:
                return str(data)
        except Exception as e:
            return f"Error converting to bytes: {e}"

    def saveData(self, filename):
        with open(filename, 'wb') as f:
            f.write(self.data)


class AEScryptor():
    def __init__(self, key, mode, iv = None, paddingMode = 'ZeroPadding', characterSet="utf-8"):
        self.key = key
        self.mode = mode
        self.iv = iv
        self.paddingMode = paddingMode
        self.characterSet = characterSet

    def ZeroPadding(self, data):
        data += b'\x00'
        while len(data) % 16 != 0:
            data += b'\x00'
        return data

    def StripZeroPadding(self, data):
        return data.rstrip(b'\x00')

    def PKCS5_7Padding(self, data):
        padding_len = 16 - len(data) % 16
        padding = bytes([padding_len]) * padding_len
        return data + padding

    def StripPKCS5_7Padding(self, data):
        padding_len = data[-1]
        return data[:-padding_len]

    def paddingData(self, data):
        if self.paddingMode == "NoPadding":
            if len(data) % 16 != 0:
                raise ValueError("Data length must be a multiple of 16 for NoPadding mode")
            return data
        elif self.paddingMode == "ZeroPadding":
            return self.ZeroPadding(data)
        elif self.paddingMode in ["PKCS5Padding", "PKCS7Padding"]:
            return self.PKCS5_7Padding(data)
        else:
            raise ValueError("Unsupported padding mode")

    def stripPaddingData(self, data):
        if self.paddingMode in ["NoPadding", "ZeroPadding"]:
            return self.StripZeroPadding(data)
        elif self.paddingMode in ["PKCS5Padding", "PKCS7Padding"]:
            return self.StripPKCS5_7Padding(data)
        else:
            raise ValueError("Unsupported padding mode")

    def encrypt(self, data):
        data = self.paddingData(data)
        if self.mode == AES.MODE_CBC:
            cipher = AES.new(self.key, self.mode, self.iv)
        else:
            cipher = AES.new(self.key, self.mode)
        encrypted = cipher.encrypt(data)
        return encrypted

    def decrypt(self, data):
        if self.mode == AES.MODE_CBC:
            cipher = AES.new(self.key, self.mode, self.iv)
        else:
            cipher = AES.new(self.key, self.mode)
        decrypted = cipher.decrypt(data)
        return self.stripPaddingData(decrypted)

    @staticmethod
    def pad_key( key):
        if isinstance(key, str):
            key = key.encode('utf-8')
        if len(key) not in [16, 24, 32]:
            if len(key) < 16:
                key = key.ljust(16, b'\0')
            elif 16 < len(key) < 24:
                key = key.ljust(24, b'\0')
            elif 24 < len(key) < 32:
                key = key.ljust(32, b'\0')
        return key
