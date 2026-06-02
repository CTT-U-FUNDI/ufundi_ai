import time, hashlib

class TempsConstant:
    TEMPS = 0.050  # 50ms

    @staticmethod
    def comparaison(a, b):
        if len(a) != len(b):
            return False
        r = 0
        for x, y in zip(a, b):
            r |= x ^ y
        return r == 0

    @staticmethod
    def attente(duree):
        debut = time.perf_counter()
        while time.perf_counter() - debut < duree:
            pass

    @staticmethod
    def hasher(data):
        return hashlib.sha256(data).hexdigest()
