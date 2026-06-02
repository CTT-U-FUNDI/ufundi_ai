"""
UFUNDI - Chiffrement AES-GCM (Authentifié)
Remplace AES-CTR par AES-GCM pour l'intégrité
"""
import secrets
from Crypto.Cipher import AES

class ChiffrementGCM:
    @staticmethod
    def generer_cle():
        return secrets.token_bytes(32)
    
    @staticmethod
    def chiffrer(data_bytes, cle_bytes):
        """
        AES-GCM : chiffre ET authentifie
        Empêche la modification de bits
        """
        nonce = secrets.token_bytes(12)  # 12 octets pour GCM
        cipher = AES.new(cle_bytes, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(data_bytes)
        # Format : nonce (12) + tag (16) + ciphertext
        return nonce + tag + ciphertext
    
    @staticmethod
    def dechiffrer(data_chiffree, cle_bytes):
        """
        Déchiffre ET vérifie l'intégrité
        Lève une exception si les données ont été modifiées
        """
        nonce = data_chiffree[:12]
        tag = data_chiffree[12:28]
        ciphertext = data_chiffree[28:]
        cipher = AES.new(cle_bytes, AES.MODE_GCM, nonce=nonce)
        try:
            return cipher.decrypt_and_verify(ciphertext, tag)
        except ValueError:
            raise ValueError("FRAGMENT CORROMPU - Intégrité violée !")

# Test
if __name__ == "__main__":
    cle = ChiffrementGCM.generer_cle()
    original = b"Alice|Dupont|alice.dupont@ufundi.ai|1472"
    chiffre = ChiffrementGCM.chiffrer(original, cle)
    dechiffre = ChiffrementGCM.dechiffrer(chiffre, cle)
    print(f"Original  : {original.decode()}")
    print(f"Déchiffré : {dechiffre.decode()}")
    print(f"OK : {original == dechiffre}")
    
    # Test de corruption
    try:
        chiffre_corrompu = bytearray(chiffre)
        chiffre_corrompu[30] ^= 0xFF  # Modifier un bit
        ChiffrementGCM.dechiffrer(bytes(chiffre_corrompu), cle)
        print("ERREUR : Corruption non détectée")
    except ValueError as e:
        print(f"✅ Corruption détectée : {e}")
