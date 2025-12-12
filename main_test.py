# main_test.py
import torch
from transformers import pipeline, BitsAndBytesConfig
from engine.search import SearchEngine
from engine.extractors import NameExtractor, FinancialExtractor
from engine.gatekeepers import Gatekeeper
from engine.estimator import Estimator
import pandas as pd

# 1. Configurar LLM (Solo una vez)
print("⚙️ Cargando Motor V7...")
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
)
pipe = pipeline(
    "text-generation",
    model="Qwen/Qwen2.5-7B-Instruct",
    model_kwargs={"quantization_config": bnb_config},
    device_map="auto",
)

# 2. Instanciar Módulos
search = SearchEngine()
name_ext = NameExtractor(pipe)
fin_ext = FinancialExtractor()
gate = Gatekeeper()
estimator = Estimator()

# 3. Flujo de Prueba
sector = "Proveedores Minería"
print(f"\n🔎 Fase 1: Discovery en '{sector}'...")

# A. Buscar Nombres
query_disc = search.generar_query_discovery(sector)
raw_text = search.buscar(query_disc)
nombres_candidatos = name_ext.extraer_nombres(raw_text)
print(f"   Candidatos crudos: {len(nombres_candidatos)}")

prospectos = []

# B. Procesar cada candidato
for cand in nombres_candidatos:
    # 1. Gatekeeper (Identidad & Negocio)
    es_valido, razon = gate.validar(cand)
    if not es_valido:
        print(f"   ❌ {cand} -> {razon}")
        continue
    
    print(f"   ✅ Analizando Target: {cand}...")
    
    # 2. Evidence Hunt (Búsqueda Financiera)
    query_fin = search.generar_query_evidence(cand)
    text_fin = search.buscar(query_fin)
    
    # 3. Extracción Cifra (Regex)
    cifra_str, confianza_cifra = fin_ext.extraer_cifra_explicita(text_fin)
    monto_usd_evidencia = fin_ext.normalizar_monto_a_usd(cifra_str) if cifra_str else None
    
    # 4. Estimación Final
    origen = "RANKING" # Simplificado para el test
    ventas, cxc, metodo, conf = estimator.estimar(cand, sector, monto_usd_evidencia, origen)
    
    print(f"      💰 Ventas: {ventas}M | CxC: {cxc}M | {metodo}")
    
    prospectos.append({
        "Empresa": cand,
        "Ventas": ventas,
        "CxC": cxc,
        "Método": metodo,
        "Evidencia Raw": cifra_str if cifra_str else "-"
    })

# C. Resultado
if prospectos:
    df = pd.DataFrame(prospectos)
    print("\n📊 RESULTADO V7 TEST:")
    print(df)
else:
    print("\n⚠️ No quedaron prospectos válidos.")
