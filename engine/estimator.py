import random

class Estimator:
    def __init__(self):
        # Tabla DSO (Días Calle) Estimada por Sector
        self.sector_dso = {
            "Minería": 0.25,      # 90 días
            "Construcción": 0.30, # 108 días (lento)
            "Salud": 0.28,        # Isapres/Fonasa lento
            "Agro": 0.20,         # Estacional
            "Logística": 0.15,    # 54 días
            "Default": 0.18
        }
    
    def _get_dso(self, sector):
        for k, v in self.sector_dso.items():
            if k in sector: return v
        return self.sector_dso["Default"]

    def estimar(self, empresa, sector, evidencia_financiera_raw, tipo_origen):
        """
        Lógica Híbrida V7:
        E1: Si hay evidencia financiera -> Úsala.
        E2: Si no -> Imputa por heurística sectorial (Fallback).
        """
        dso_factor = self._get_dso(sector)
        
        # --- E1: CAMINO DE EVIDENCIA (GOLD) ---
        if evidencia_financiera_raw:
            # Aquí asumimos que el extractor ya convirtió a MM USD en un paso previo
            # o lo hacemos aquí. Para simplificar, asumimos que entra el valor numérico.
            ventas = evidencia_financiera_raw 
            cxc = round(ventas * dso_factor, 2)
            metodo = "E1 (Evidencia Explícita)"
            confianza = "Alta"
            return ventas, cxc, metodo, confianza

        # --- E2: CAMINO HEURÍSTICO (SILVER/FALLBACK) ---
        # Base según de dónde salió el nombre
        if tipo_origen == "RANKING":
            base = 45 # Estar en un ranking implica tamaño
            confianza = "Media (Ranking)"
        elif tipo_origen == "LICITACION":
            base = 50 # Ganar licitación pública implica espalda
            confianza = "Media (Licitación)"
        elif tipo_origen == "CONTRATO":
            base = 30 
            confianza = "Baja (Contrato)"
        else:
            base = 10
            confianza = "Baja (Mención)"

        # Variación estocástica controlada (para no ver números planos)
        ventas_est = int(base * random.uniform(0.9, 1.2))
        cxc_est = round(ventas_est * dso_factor, 2)
        
        return ventas_est, cxc_est, "E2 (Heurística)", confianza
