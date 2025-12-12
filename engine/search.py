from langchain_community.tools import DuckDuckGoSearchRun
import time

class SearchEngine:
    def __init__(self):
        self.ddg = DuckDuckGoSearchRun()

    def buscar(self, query):
        try:
            # Rate limit handling básico
            time.sleep(1) 
            return self.ddg.invoke(query)
        except Exception as e:
            print(f"Error DDG: {e}")
            return ""

    def generar_query_discovery(self, sector):
        """Fase 1: Encontrar nombres"""
        return f"Ranking principales empresas {sector} Chile ventas facturación"

    def generar_query_evidence(self, empresa):
        """Fase 2: Encontrar dinero (V7 Financial First)"""
        return f'"{empresa}" estados financieros memoria anual ventas facturación Chile'
