"""
UFUNDI OIGNON - Routage Anonyme Intégré
Chaque requête passe par 3 couches de chiffrement
"""
import secrets
import hashlib
import threading
import time
import json

class UfundiOignon:
    def __init__(self):
        self.couches = 3
        self.cles = [secrets.token_bytes(32) for _ in range(self.couches)]
        self.relais_actifs = []
        self._demarrer_relais()
    
    def _demarrer_relais(self):
        """Simule des relais oignon en mémoire"""
        for i in range(self.couches):
            relais = {
                "id": secrets.token_hex(8),
                "cle": self.cles[i],
                "actif": True,
                "paquets_relayes": 0
            }
            self.relais_actifs.append(relais)
    
    def chiffrer_oignon(self, donnees):
        """
        Chiffre les données en 3 couches (oignon)
        Couche 3 (interne) → Couche 2 → Couche 1 (externe)
        """
        data = donnees.encode() if isinstance(donnees, str) else donnees
        
        # Couche 3 - la plus profonde
        c3 = bytes([d ^ self.cles[2][i % 32] for i, d in enumerate(data)])
        # Couche 2
        c2 = bytes([d ^ self.cles[1][i % 32] for i, d in enumerate(c3)])
        # Couche 1 - externe
        c1 = bytes([d ^ self.cles[0][i % 32] for i, d in enumerate(c2)])
        
        return c1.hex()
    
    def dechiffrer_oignon(self, data_hex):
        """
        Déchiffre les 3 couches
        Couche 1 (externe) → Couche 2 → Couche 3 (interne)
        """
        c1 = bytes.fromhex(data_hex)
        
        # Couche 1
        d1 = bytes([d ^ self.cles[0][i % 32] for i, d in enumerate(c1)])
        # Couche 2
        d2 = bytes([d ^ self.cles[1][i % 32] for i, d in enumerate(d1)])
        # Couche 3
        d3 = bytes([d ^ self.cles[2][i % 32] for i, d in enumerate(d2)])
        
        return d3.decode()
    
    def rotation_cles(self):
        """Change les clés toutes les 60 secondes"""
        while True:
            time.sleep(60)
            self.cles = [secrets.token_bytes(32) for _ in range(self.couches)]
            print("[OIGNON] Clés renouvelées")
    
    def get_stats(self):
        return {
            "couches": self.couches,
            "relais": len(self.relais_actifs),
            "paquets": sum(r["paquets_relayes"] for r in self.relais_actifs)
        }


# ============================================
# TEST
# ============================================
if __name__ == "__main__":
    oignon = UfundiOignon()
    
    message = "UFUNDI - Connexion Sécurisée"
    chiffre = oignon.chiffrer_oignon(message)
    dechiffre = oignon.dechiffrer_oignon(chiffre)
    
    print("=" * 50)
    print("🧅 UFUNDI OIGNON - Test")
    print("=" * 50)
    print(f"Original  : {message}")
    print(f"Chiffré   : {chiffre[:40]}...")
    print(f"Déchiffré : {dechiffre}")
    print(f"OK        : {message == dechiffre}")
    print(f"Stats     : {oignon.get_stats()}")
    print("=" * 50)
