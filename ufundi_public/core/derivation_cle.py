"""
UFUNDI - Dérivation de Clé Sécurisée
Remplace le XOR par Argon2id (standard militaire)
"""
import hashlib
import secrets
from argon2.low_level import hash_secret_raw, Type

class DerivationCle:
    @staticmethod
    def generer_cle_maitresse(mots_de_passe: list, sel: bytes = None) -> bytes:
        """
        Combine 6 mots de passe avec Argon2id
        Résistant aux attaques GPU/ASIC
        """
        if sel is None:
            sel = secrets.token_bytes(32)
        
        # Concaténer tous les MDP avec le sel
        donnees = b"|".join(mdp.encode() for mdp in mots_de_passe)
        
        # Argon2id : 64 MB mémoire, 3 itérations, 1 thread
        cle = hash_secret_raw(
            secret=donnees,
            salt=sel,
            time_cost=3,
            memory_cost=65536,  # 64 MB
            parallelism=1,
            hash_len=32,
            type=Type.ID
        )
        
        return cle
    
    @staticmethod
    def generer_hash_mdp(mot_de_passe: str) -> bytes:
        """Hash individuel d'un MDP avec SHA512"""
        return hashlib.sha512(mot_de_passe.encode()).digest()

# Test
if __name__ == "__main__":
    mdps = ["Azerty1!", "Qwerty2@", "MdpTest3#", "Secure4$", "Passwd5%", "Ufundi6&"]
    cle = DerivationCle.generer_cle_maitresse(mdps)
    print(f"Clé maîtresse Argon2id : {cle.hex()}")
