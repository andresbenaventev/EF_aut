import re

class FinancialExtractor:
    def __init__(self):
        # Patrones Regex para detectar cifras financieras en texto chileno
        # Captura: "Ventas de MM$ 45.000", "US$ 50 millones", "UF 300.000"
        self.patrones_dinero = [
            r'(?:ventas|ingresos|facturación).{0,40}?((?:US\$|USD|\$|CLP|UF)\s?[\d\.,]+(?:\s?(?:millones|MM|M))?)',
            r'((?:US\$|USD|\$|CLP)\s?[\d\.,]+(?:\s?(?:millones|MM|M))?).{0,20}?(?:ventas|ingresos)',
            r'(?:adjudicó|contrato).{0,30}?((?:US\$|USD|\$|CLP)\s?[\d\.,]+(?:\s?(?:millones|MM|M))?)'
        ]

    def extraer_cifra_explicita(self, texto):
        """
        Busca evidencia dura de dinero en el texto.
        Retorna: (cifra_raw, confianza)
        """
        for patron in self.patrones_dinero:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                return match.group(1), "Alta (Evidencia Explícita)"
        return None, "N/A"

    def normalizar_monto_a_usd(self, cifra_raw):
        """
        Convierte strings como 'MM$ 45.000' a float USD (Estimado).
        Tipo de cambio base: 1 USD = 950 CLP. 1 UF = 38000 CLP.
        """
        if not cifra_raw: return 0.0
        
        c = cifra_raw.lower().replace(",", ".").replace(" ", "")
        monto = 0.0
        
        # Extracción numérica simple
        nums = re.findall(r"[\d\.]+", c)
        if not nums: return 0.0
        # Tomamos el número más largo encontrado (heurística simple)
        valor_num = float(sorted(nums, key=len)[-1])
        
        # Lógica de conversión (Aproximada para V7)
        factor = 1.0
        if "mm" in c or "millones" in c:
            factor = 1_000_000
        
        monto_nominal = valor_num * factor
        
        monto_usd = 0.0
        if "us" in c or "usd" in c:
            monto_usd = monto_nominal
        elif "uf" in c:
            monto_usd = (monto_nominal * 38000) / 950
        else: # Asumimos CLP si no dice nada o dice $
            monto_usd = monto_nominal / 950
            
        return round(monto_usd / 1_000_000, 2) # Retorna en MM USD

class NameExtractor:
    def __init__(self, llm_pipeline):
        self.pipe = llm_pipeline

    def extraer_nombres(self, texto_raw):
        """Usa el LLM solo para recortar, no para pensar."""
        prompt = f"Extrae nombres de empresas del texto: '{texto_raw[:800]}'. Solo lista separada por comas sin explicaciones."
        try:
            msgs = [{"role": "user", "content": prompt}]
            outputs = self.pipe(msgs, max_new_tokens=100, do_sample=True, temperature=0.1)
            raw = outputs[0]["generated_text"][-1]["content"]
            # Limpieza parser V6.4
            raw = raw.replace("```json", "").replace("```", "").replace("\n", ",")
            lista = [x.strip() for x in raw.split(',') if len(x.strip()) > 3]
            return lista
        except:
            return []
