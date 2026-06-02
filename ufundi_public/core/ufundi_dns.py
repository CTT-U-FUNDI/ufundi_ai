"""
UFUNDI DNS – Système de Nom de Domaine Indépendant
Sans serveur, sans registre, sans ICANN
Chaque nœud UFUNDI = un serveur DNS
"""
import socket
import threading
import time
import json
import hashlib
import secrets

class UfundiDNS:
    """
    DNS Décentralisé UFUNDI
    - Pas de serveur central
    - Pas de registre ICANN
    - Résolution P2P
    - Domaine .ufundi natif
    """
    
    def __init__(self, port=5353):
        self.port = port
        self.registre = {}  # {nom.ufundi: ip}
        self.cache = {}     # Cache temporaire
        self._running = False
        self.noeud_id = secrets.token_hex(8)
    
    def enregistrer(self, nom, ip):
        """
        Enregistre un nom de domaine .ufundi
        Exemple : alice.ufundi → 10.14.218.187
        """
        nom_complet = f"{nom}.ufundi"
        self.registre[nom_complet] = ip
        print(f"[UFUNDI DNS] ✅ {nom_complet} → {ip}")
        return True
    
    def resoudre(self, nom):
        """
        Résout un nom .ufundi en adresse IP
        Cherche d'abord dans le cache, puis dans le registre local
        """
        # Cache local
        if nom in self.cache:
            if time.time() - self.cache[nom]["time"] < 300:  # 5 min
                return self.cache[nom]["ip"]
        
        # Registre local
        if nom in self.registre:
            self.cache[nom] = {"ip": self.registre[nom], "time": time.time()}
            return self.registre[nom]
        
        # Résolution P2P (broadcast aux autres nœuds)
        return self._resoudre_p2p(nom)
    
    def _resoudre_p2p(self, nom):
        """
        Demande aux autres nœuds UFUNDI
        Broadcast UDP sur le réseau local
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(2)
            
            requete = {
                "type": "dns_query",
                "nom": nom,
                "noeud": self.noeud_id
            }
            
            sock.sendto(json.dumps(requete).encode(), ("255.255.255.255", self.port))
            
            # Attendre les réponses
            debut = time.time()
            while time.time() - debut < 2:
                try:
                    data, addr = sock.recvfrom(1024)
                    reponse = json.loads(data.decode())
                    if reponse.get("type") == "dns_response" and reponse.get("nom") == nom:
                        ip = reponse.get("ip")
                        self.cache[nom] = {"ip": ip, "time": time.time()}
                        sock.close()
                        return ip
                except socket.timeout:
                    break
            
            sock.close()
        except:
            pass
        
        return None
    
    def demarrer_serveur_dns(self):
        """
        Démarre le serveur DNS UFUNDI
        Écoute les requêtes des autres nœuds
        """
        self._running = True
        
        def ecouter():
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("0.0.0.0", self.port))
            sock.settimeout(1)
            
            print(f"[UFUNDI DNS] Serveur DNS sur port {self.port}")
            
            while self._running:
                try:
                    data, addr = sock.recvfrom(1024)
                    requete = json.loads(data.decode())
                    
                    if requete.get("type") == "dns_query":
                        nom = requete.get("nom")
                        if nom in self.registre:
                            reponse = {
                                "type": "dns_response",
                                "nom": nom,
                                "ip": self.registre[nom],
                                "noeud": self.noeud_id
                            }
                            sock.sendto(json.dumps(reponse).encode(), addr)
                except socket.timeout:
                    continue
                except:
                    break
            
            sock.close()
        
        threading.Thread(target=ecouter, daemon=True).start()
    
    def arreter(self):
        self._running = False
    
    def liste_domaines(self):
        """Liste tous les domaines .ufundi connus"""
        return list(self.registre.keys())
    
    def statistiques(self):
        return {
            "domaines_enregistres": len(self.registre),
            "cache_actif": len(self.cache),
            "noeud_id": self.noeud_id[:8]
        }


# ============================================
# TEST
# ============================================
if __name__ == "__main__":
    dns = UfundiDNS()
    dns.demarrer_serveur_dns()
    
    # Enregistrer des domaines
    dns.enregistrer("alice", "10.14.218.187")
    dns.enregistrer("bob", "192.168.1.42")
    dns.enregistrer("charlie", "172.16.0.99")
    
    print("\n" + "=" * 50)
    print("🔮 UFUNDI DNS - Test")
    print("=" * 50)
    
    # Résoudre
    for nom in ["alice.ufundi", "bob.ufundi", "inconnu.ufundi"]:
        ip = dns.resoudre(nom)
        print(f"   {nom} → {ip or 'Non trouvé'}")
    
    print(f"\n📊 Domaines : {dns.liste_domaines()}")
    print(f"📊 Stats    : {dns.statistiques()}")
    
    print("=" * 50)
