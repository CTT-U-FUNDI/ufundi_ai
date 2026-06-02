import secrets
from Crypto.Cipher import AES
from Crypto.Util import Counter

class Chiffrement:
    @staticmethod
    def generer_cle():
        return secrets.token_bytes(32)

    @staticmethod
    def chiffrer(data_bytes, cle_bytes):
        nonce = secrets.token_bytes(8)
        ctr = Counter.new(64, prefix=nonce)
        cipher = AES.new(cle_bytes, AES.MODE_CTR, counter=ctr)
        return nonce + cipher.encrypt(data_bytes)

    @staticmethod
    def dechiffrer(data_chiffree, cle_bytes):
        nonce = data_chiffree[:8]
        ctr = Counter.new(64, prefix=nonce)
        cipher = AES.new(cle_bytes, AES.MODE_CTR, counter=ctr)
        return cipher.decrypt(data_chiffree[8:])
