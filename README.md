# EF_aut

Financial-First Engine (EF_aut) es un motor de inteligencia financiera diseñado para identificar empresas chilenas medianas realmente financiables, priorizando Ventas y Cuentas por Cobrar (CxC) como variables centrales de solvencia.

A diferencia de scrapers genéricos o rankings empresariales, EF_aut opera bajo un enfoque *financial-first*: no busca nombres, busca balances implícitos. El sistema combina búsqueda dirigida, extracción determinística de cifras financieras y múltiples capas de validación para entregar un set limpio y accionable de prospectos.

---

## 🎯 Objetivo del Proyecto

Identificar empresas privadas chilenas:
- Con **ventas relevantes** (≥ umbral configurable).
- Con **CxC estimadas significativas**, útiles para análisis de financiamiento (factoring, confirming, crédito).
- Que **no** sean instituciones públicas, bancos, empresas listadas, multinacionales o modelos de negocio intangibles.

El output final está orientado a **uso financiero real**, no exploratorio.

---

## 🧠 Principios de Diseño

- **Financial-first, no name-first**  
- **Determinismo sobre alucinación** (Regex > LLM para cifras)
- **Filtros estrictos antes de scoring**
- **Velocidad y reproducibilidad**
- **Preparado para despliegue en Hugging Face Spaces**

---

## 🏗️ Arquitectura General

El motor sigue un pipeline secuencial:

1. **Búsqueda dirigida (Discovery & Evidence)**
2. **Extracción de nombres**
3. **Gatekeepers institucionales y de negocio**
4. **Extracción de cifras financieras**
5. **Estimación de Ventas y CxC**
6. **Scoring y reporting final**

La estimación financiera prioriza:
- Evidencia explícita (ventas reales encontradas).
- Fallback heurístico sectorial cuando no hay cifras directas.

---

## 🧱 Capas de Filtro (Gatekeepers)

EF_aut elimina automáticamente:

- Ministerios, servicios públicos, hospitales, universidades.
- Empresas listadas en CMF.
- Bancos, aseguradoras y holdings financieros.
- Rankings, índices, certificadoras y consultoras.
- Modelos de negocio intangibles (ej: *Best Place*, *Great Place*, *Rankings*).
- Multinacionales y entidades extranjeras.

Solo sobreviven empresas **comercialmente financiables**.

---

## 📊 Variables Clave

Cada prospecto válido incluye:

- **Empresa**
- **Sector corregido**
- **Ventas Estimadas (USD)**
- **Cuentas por Cobrar Estimadas (CxC)**
- **Nivel de Confianza**
- **Fuente de evidencia**

CxC se estima usando factores sectoriales (DSO) cuando no existe dato explícito.

---

## 🗂️ Estructura del Repositorio

```text
EF_aut/
│
├── app.py                  # Interfaz Streamlit (HF Spaces)
├── requirements.txt        # Dependencias
│
├── engine/
│   ├── search.py           # Búsqueda dirigida
│   ├── extractors.py       # Parsers y regex financieros
│   ├── gatekeepers.py      # Filtros institucionales y de negocio
│   ├── estimator.py        # Motor de ventas y CxC
│   └── scorer.py           # Scoring heurístico / tabular
│
├── data/
│   ├── cmf_blacklist.txt
│   ├── killwords.json
│   └── sector_dso.csv
│
└── models/
    └── scorer_v1.pkl       # (Opcional / futuro)
