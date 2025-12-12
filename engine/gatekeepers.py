import re
import unicodedata
import os

def normalizar_texto(texto):
    """Normalización agresiva para comparación de identidad."""
    if not isinstance(texto, str): return ""
    n = ''.join(c for c in unicodedata.normalize('NFD', texto.lower()) if unicodedata.category(c) != 'Mn')
    n = n.replace(".", "").replace(",", "").replace("-", " ")
    # Sufijos legales a eliminar para comparar
    sufijos = [" spa", " sa", " s a", " ltda", " limitada", " gmbh", " llc", " inc", " corp", " holding"]
    for s in sufijos:
        if n.endswith(s): n = n[:-len(s)]; break
    return n.strip()

class Gatekeeper:
    def __init__(self):
        # 1. KILLWORDS INSTITUCIONALES (Estado, Gremio, Educación Pública)
        self.kw_inst = {
            "ministerio", "subsecretaria", "gobierno", "municipalidad", "hospital", 
            "servicio de salud", "red hospitalaria", "clinico regional", "cochilco", 
            "sernagesomin", "enami", "codelco", "corfo", "corporacion", "fundacion", 
            "mutual", "achs", "gremio", "asociacion", "camara", "sindicato", 
            "universidad estatal", "liceo", "escuela", "juzgado"
        }
        
        # 2. KILLWORDS INTANGIBLES / NO-FINANCIABLES (Business Logic V6.5)
        self.kw_intangible = {
            "certificacio", "benchmark", "ranking", "rating", "indice", "índice",
            "place to live", "place to work", "consultoria", "consultoría", "research", 
            "intelligence", "estudio de mercado", "medicion", "satisfaccion", 
            "percepcion", "insight", "analytic", "premio", "award", "merco", "monitor"
        }

        # 3. LISTAS NEGRAS (MOCK O REAL)
        self.cmf_set = set()
        self.multinacionales = {
            "google", "microsoft", "amazon", "aws", "enel", "engie", "colbun", 
            "walmart", "falabella", "cencosud", "latam", "bayer", "nestle", 
            "unilever", "coca cola", "pepsico", "procter", "bhp", "anglo american"
        }
        self.financieras = {
            "banco", "bank", "inversiones", "rentas", "capital", "partners", 
            "seguros", "financial", "factoring", "leasing", "corredora"
        }
        self._cargar_cmf_mock() # En prod usaría archivo real

    def _cargar_cmf_mock(self):
        # Mock de empresas públicas chilenas
        mock = [
            "CODELCO", "ENAP", "COLBUN", "FALABELLA", "CENCOSUD", "LATAM", 
            "SOCOVESA", "BESALCO", "PAZ CORP", "SMU", "CCU", "EMBOTELLADORA ANDINA",
            "SALFACORP", "ECHEVERRÍA IZQUIERDO", "CAP", "VAPORES"
        ]
        for m in mock: self.cmf_set.add(normalizar_texto(m))

    def validar(self, nombre):
        """Retorna (Es_Valido: bool, Razon: str)"""
        n_clean = nombre.strip()
        n_norm = normalizar_texto(n_clean)
        n_low = n_clean.lower()

        # Check 1: Institucional
        for k in self.kw_inst:
            if k in n_low: return False, f"Institucional ({k})"

        # Check 2: Intangible (Negocio)
        for k in self.kw_intangible:
            if k in n_low: return False, f"Intangible/No-Factoring ({k})"

        # Check 3: Identidad (CMF / Multi / Fin)
        if n_norm in self.cmf_set: return False, "Listada CMF (Pública)"
        if any(m in n_norm for m in self.multinacionales): return False, "Multinacional"
        if any(f in n_norm for f in self.financieras): return False, "Financiera/Holding Pasivo"

        return True, "OK"
