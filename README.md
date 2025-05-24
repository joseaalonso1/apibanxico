# API Banxico: Tasa Real Ex-Ante

Esta aplicación permite visualizar y calcular la **tasa real ex-ante de corto plazo en México** mediante datos públicos de Banxico consumidos vía API. Utiliza una interfaz en **Streamlit**, y permite elegir fechas, observar tasas objetivo vs. expectativas, y descargar los resultados.

APIBANXICO/
├── code/                    # Código fuente principal
│   ├── app.py              # Aplicación Streamlit (interfaz)
│   └── exante_real_rate.py # Script base con lógica y procesamiento
├── data/                   # Carpeta para guardar CSV exportado
├── .env                    # Token de Banxico (ignorado por Git)
├── .gitignore              # Exclusiones de control de versiones
├── environment.local.yml   # Entorno reproducible Conda (uso local)
├── README.md               # Documentación principal del proyecto

## 🔧 Cómo ejecutar localmente

1. Crear el entorno Conda:

```bash
conda env create -f environment.local.yml
conda activate banxico

No se usa requirements.txt: este proyecto está optimizado para entorno local con conda.
No se especifica una versión exacta de matplotlib, pero se recomienda 3.7.x por compatibilidad con entornos donde versiones superiores presentan conflictos.
El archivo .env se excluye automáticamente gracias al .gitignore.
## aplicación WEB
https://apibanxico-exante.streamlit.app