# API Banxico: Tasa Real Ex-Ante

Este proyecto obtiene y visualiza la **tasa de interés real ex-ante** usando datos públicos de Banxico a través de su API. Incluye:

- Script en Python (`code/exante_real_rate.py`)
- Aplicación interactiva con Streamlit (`code/app.py`)
- Botón para descarga en CSV
- Cálculo de reducción esperada por junta

---

## 📦 Requisitos

- Python 3.11
- Cuenta en [https://streamlit.io](https://streamlit.io)

---

## 🔧 Cómo usar localmente (con Conda)

```bash
conda env create -f environment.yml
conda activate banxico
streamlit run code/app.py

