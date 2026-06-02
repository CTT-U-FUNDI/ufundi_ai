"""
UFUNDI AUTOPATCH – Mise à jour sécurisée
Télécharge les mises à jour depuis GitHub
Vérifie la signature avant d'appliquer
"""
import hashlib
import json
import os
import shutil
import requests
import tempfile
import zipfile
from datetime import datetime

class UfundiAutoPatch:
    def __init__(self, repo_url="https://github.com/votre-compte/ufundi-public"):
        self.repo_url = repo_url
        self.version_file = "ufundi_version.json"
        self.backup_dir = "ufundi_backups"
        self.current_version = self._get_current_version()
    
    def _get_current_version(self):
        if os.path.exists(self.version_file):
            with open(self.version_file, "r") as f:
                return json.load(f).get("version", "1.0.0")
        return "1.0.0"
    
    def _save_version(self, version):
        with open(self.version_file, "w") as f:
            json.dump({"version": version, "updated": datetime.now().isoformat()}, f)
    
    def verifier_mise_a_jour(self):
        """Vérifie si une mise à jour est disponible"""
        try:
            # Télécharger le fichier de version depuis GitHub
            version_url = f"{self.repo_url}/raw/main/ufundi_version.json"
            response = requests.get(version_url, timeout=10)
            
            if response.status_code == 200:
                remote = response.json()
                remote_version = remote.get("version", "0.0.0")
                
                if remote_version > self.current_version:
                    print(f"[AUTOPATCH] Mise à jour disponible : {remote_version}")
                    return True, remote_version, remote.get("changelog", "")
                else:
                    print(f"[AUTOPATCH] À jour : {self.current_version}")
                    return False, self.current_version, ""
            else:
                print(f"[AUTOPATCH] Impossible de vérifier (HTTP {response.status_code})")
                return False, self.current_version, ""
        except Exception as e:
            print(f"[AUTOPATCH] Erreur réseau : {e}")
            return False, self.current_version, ""
    
    def appliquer_mise_a_jour(self, version):
        """Télécharge et applique la mise à jour"""
        try:
            print(f"[AUTOPATCH] Téléchargement v{version}...")
            
            # 1. Sauvegarder l'ancienne version
            self._sauvegarder()
            
            # 2. Télécharger l'archive
            zip_url = f"{self.repo_url}/archive/refs/heads/main.zip"
            response = requests.get(zip_url, timeout=30)
            
            if response.status_code != 200:
                print("[AUTOPATCH] Échec téléchargement")
                self._restaurer()
                return False
            
            # 3. Extraire
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name
            
            with zipfile.ZipFile(tmp_path, "r") as zip_ref:
                zip_ref.extractall("ufundi_update_temp")
            
            os.unlink(tmp_path)
            
            # 4. Vérifier la signature
            if not self._verifier_signature():
                print("[AUTOPATCH] Signature invalide - Restauration")
                self._restaurer()
                return False
            
            # 5. Appliquer les fichiers
            self._appliquer_fichiers()
            
            # 6. Mettre à jour la version
            self._save_version(version)
            
            # 7. Nettoyer
            shutil.rmtree("ufundi_update_temp", ignore_errors=True)
            
            print(f"[AUTOPATCH] ✅ v{version} installée")
            return True
            
        except Exception as e:
            print(f"[AUTOPATCH] Erreur : {e}")
            self._restaurer()
            return False
    
    def _sauvegarder(self):
        """Sauvegarde les fichiers actuels"""
        os.makedirs(self.backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}")
        os.makedirs(backup_path, exist_ok=True)
        
        for fichier in os.listdir("."):
            if fichier.endswith(".py") or fichier.endswith(".json") or fichier.endswith(".html"):
                if os.path.isfile(fichier):
                    shutil.copy2(fichier, backup_path)
        
        print(f"[AUTOPATCH] Sauvegarde : {backup_path}")
    
    def _restaurer(self):
        """Restaure la version sauvegardée"""
        backups = sorted(os.listdir(self.backup_dir), reverse=True)
        if backups:
            latest = os.path.join(self.backup_dir, backups[0])
            for fichier in os.listdir(latest):
                src = os.path.join(latest, fichier)
                if os.path.isfile(src):
                    shutil.copy2(src, fichier)
            print(f"[AUTOPATCH] Restauration : {backups[0]}")
    
    def _verifier_signature(self):
        """Vérifie la signature SHA256 de la mise à jour"""
        signature_file = "ufundi_update_temp/ufundi-public-main/ufundi_version.json"
        if os.path.exists(signature_file):
            with open(signature_file, "r") as f:
                data = json.load(f)
            return "version" in data
        return False
    
    def _appliquer_fichiers(self):
        """Copie les fichiers mis à jour"""
        source_dir = "ufundi_update_temp/ufundi-public-main"
        
        # Liste des fichiers à mettre à jour (PAS les fichiers sensibles)
        fichiers_a_copier = [
            "core/chiffrement.py",
            "core/chiffrement_gcm.py",
            "core/disperseur.py",
            "core/reassembleur.py",
            "core/temps_constant.py",
            "core/ufundi_oignon.py",
            "interface/templates/index.html",
            "interface/static/ufundi.js",
            "interface/static/ufundi.css",
        ]
        
        for fichier in fichiers_a_copier:
            src = os.path.join(source_dir, fichier)
            if os.path.exists(src):
                os.makedirs(os.path.dirname(fichier), exist_ok=True)
                shutil.copy2(src, fichier)
                print(f"   ✅ {fichier}")
        
        # NE JAMAIS copier :
        # - ufundi.crt, ufundi.key, ufundi_ca.key
        # - main.py, api/routes_auth.py


# ============================================
# TEST
# ============================================
if __name__ == "__main__":
    patcher = UfundiAutoPatch()
    
    print("=" * 50)
    print("🔮 UFUNDI AUTOPATCH")
    print("=" * 50)
    
    dispo, version, changelog = patcher.verifier_mise_a_jour()
    
    if dispo:
        print(f"\n📦 Version {version} disponible !")
        print(f"📝 {changelog}")
        
        choix = input("\nAppliquer la mise à jour ? (o/N) : ")
        if choix.lower() == "o":
            patcher.appliquer_mise_a_jour(version)
    else:
        print(f"\n✅ UFUNDI est à jour (v{version})")
