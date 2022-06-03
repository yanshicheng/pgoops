import base64
import simplejson

from Crypto.Cipher import AES
from common.config_dispose import ConfigDispose


def encrypt_base64_aes(data):
    try:
        data = simplejson.dumps(data)
        key = bytes(ConfigDispose.get_default('secret_key'), encoding='utf-8')
        cipher = AES.new(key, AES.MODE_CBC, key)
        bytes_data = bytearray(data, encoding='utf-8')
        v1 = len(bytes_data)
        v2 = v1 % 16
        if v2 == 0:
            v3 = 16
        else:
            v3 = 16 - v2
        for i in range(v3):
            bytes_data.append(v3)
        msg = cipher.encrypt(bytes_data)
        en_text = base64.encodebytes(msg)
        en_text = en_text.decode('utf8')
        return en_text, True

    except Exception as e:
        return str(e), False


def decrypt_base64_aes(data):
    try:
        text = data.encode(encoding='utf-8')  # 需要解密的文本
        ecrypted_base64 = base64.decodebytes(text)  # base64解码成字节流
        key = bytes(ConfigDispose.get_default('secret_key'), encoding='utf-8')
        cipher = AES.new(key, AES.MODE_CBC, key)
        result = cipher.decrypt(ecrypted_base64)
        bytes_data = result[0:-result[-1]]
        str_data = str(bytes_data, encoding='utf-8')
        dic_data = simplejson.loads(str_data)
        return dic_data, True
    except Exception as e:
        return str(e), False
