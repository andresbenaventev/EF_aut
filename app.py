%%writefile app.py
import streamlit as st
import pandas as pd
import torch
from transformers import pipeline, BitsAndBytesConfig
from engine.search import SearchEngine
from engine.extractors import NameExtractor, FinancialExtractor
from engine.gatekeepers import Gatekeeper
from engine.estimator import Estimator

# --- CONFIGURACIÓN VISUAL ---
st.set_page_config(
    page_title="Motor Financiero V7",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Motor de Inteligencia Comercial V7")
st.markdown("""
Esta herramienta busca, valida y estima la solvencia de empresas chilenas en tiempo real.
**Enfoque:** Financial-First (Ventas & CxC).
""")

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuración")
    sector = st.text_input("Sector a Investigar", value="Proveedores Minería")
    umbral = st.slider("Ventas Mínimas (MM USD)", 10, 100, 30)
    st.divider()
    st.info("💡 Tip: Sé específico (ej: 'Empresas de Transporte de Carga').")

# --- CARGA DEL CEREBRO (CACHEADA) ---
@st.cache_resource
def load_model():
    # NOTA: Para Hugging Face Free Tier (CPU), usamos el modelo 1.5B.
    # Es rápido, ligero y no se cae por memoria.
    print("⚙️ Cargando Modelo IA...")
    try:
        # Intento GPU (Si pagas el Space)
        bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)
        return pipeline("text-generation", model="Qwen/Qwen2.5-1.5B-Instruct", model_kwargs={"quantization_config": bnb}, device_map="auto")
    except:
        # Fallback CPU (Gratis)
        return pipeline("text-generation", model="Qwen/Qwen2.5-1.5B-Instruct", device_map="cpu")

# --- LÓGICA PRINCIPAL ---
def run_analysis():
    # 1. Cargar Motores
    with st.spinner("🧠 Inicializando neuronas..."):
        pipe = load_model()
        search = SearchEngine()
        name_ext = NameExtractor(pipe)
        fin_ext = FinancialExtractor()
        gate = Gatekeeper()
        estimator = Estimator()

    # 2. Discovery
    st.subheader(f"1. Exploración: {sector}")
    query = search.generar_query_discovery(sector)
    
    with st.status("🕵️ Buscando candidatos...", expanded=True) as status:
        st.write(f"Query: `{query}`")
        raw_text = search.buscar(query)
        candidatos = name_ext.extraer_nombres(raw_text)
        
        if not candidatos:
            status.update(label="❌ No se encontraron nombres.", state="error")
            st.stop()
            
        st.write(f"--> Detectados: {len(candidatos)} empresas preliminares.")
        status.update(label="✅ Fase 1 Completada", state="complete", expanded=False)

    # 3. Validación y Finanzas
    st.subheader("2. Auditoría Financiera y Validación")
    
    resultados = []
    eliminados = []
    
    barra = st.progress(0)
    log_box = st.empty() # Para mostrar qué está analizando en tiempo real

    for i, cand in enumerate(candidatos):
        log_box.caption(f"Analizando: **{cand}**...")
        
        # A. Gatekeeper
        es_valido, razon = gate.validar(cand)
        if not es_valido:
            eliminados.append({"Empresa": cand, "Motivo": razon})
            barra.progress((i + 1) / len(candidatos))
            continue

        # B. Evidence Hunt
        query_fin = search.generar_query_evidence(cand)
        txt_fin = search.buscar(query_fin)
        cifra, _ = fin_ext.extraer_cifra_explicita(txt_fin)
        usd = fin_ext.normalizar_monto_a_usd(cifra)

        # C. Estimación
        v, cxc, met, conf = estimator.estimar(cand, sector, usd, "RANKING")

        # D. Filtro de Umbral
        if v >= umbral:
            resultados.append({
                "Empresa": cand,
                "Ventas (MM USD)": v,
                "CxC Est. (MM USD)": cxc,
                "Confianza": conf,
                "Fuente": "E1 (Real)" if usd else "E2 (Heurística)"
            })
        else:
            eliminados.append({"Empresa": cand, "Motivo": f"Bajo Umbral ({v}M < {umbral}M)"})
        
        barra.progress((i + 1) / len(candidatos))

    log_box.empty() # Limpiar mensaje

    # --- RESULTADOS FINALES ---
    st.divider()
    
    col1, col2 = st.columns(2)
    col1.metric("Targets Calificados", len(resultados))
    col2.metric("Descartados", len(eliminados))

    if resultados:
        df = pd.DataFrame(resultados)
        st.dataframe(
            df.style.highlight_max(axis=0, subset=["Ventas (MM USD)", "CxC Est. (MM USD)"]),
            use_container_width=True
        )
        
        # Botón descarga
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Reporte CSV", csv, "prospectos_v7.csv", "text/csv")
    else:
        st.warning("Ninguna empresa superó los filtros estrictos.")

    with st.expander("🗑️ Ver Bitácora de Descartes"):
        if eliminados:
            st.dataframe(pd.DataFrame(eliminados), use_container_width=True)
        else:
            st.write("No hubo descartes.")

# --- BOTÓN DE ACCIÓN ---
if st.sidebar.button("🚀 EJECUTAR ANÁLISIS", type="primary"):
    run_analysis()
else:
    st.info("👈 Configura el sector a la izquierda y presiona EJECUTAR.")
