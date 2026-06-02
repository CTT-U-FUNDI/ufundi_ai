from .chiffrement import Chiffrement

class Reassembleur:
    @staticmethod
    def reassembler(fragments, cle_bytes):
        """
        Réassemble des fragments bytes (pas des dicts)
        Les fragments sont dans l'ordre (pas mélangés par Fragmenteur)
        """
        data = b""
        for frag in fragments:
            # frag est un bytes, pas un dict
            data += Chiffrement.dechiffrer(frag, cle_bytes)
        return data
