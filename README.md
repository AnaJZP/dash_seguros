# Dash Seguros 🚗💼

Este proyecto es un **dashboard interactivo** desarrollado con [Streamlit](https://streamlit.io/) para analizar datos de accidentes automovilísticos en México. Proporciona visualizaciones y análisis clave para entender los accidentes según entidades federativas, tipos de vehículos, y otros factores. Además, incluye insights útiles para estrategias comerciales, como frases tractoras para venta de seguros.

---

## 🚀 Características

- **Tendencias nacionales:** Gráficas interactivas que muestran la evolución de los accidentes automovilísticos a lo largo de los años.
- **Análisis por estado:** Identificación de las entidades federativas con mayor número de accidentes.
- **Distribución de causas y tipos:** Visualización detallada de las principales causas y tipos de accidentes.
- **Frases tractoras:** Generación automática de recomendaciones comerciales basadas en los datos.
- **Glosario:** Definiciones claras y útiles sobre conceptos clave.

---

## 📂 Estructura de Archivos

- `streamlit_accidentes.py`: Código principal del dashboard.
- `accidentes_causa_inegi.xlsx`: Base de datos de causas de accidentes.
- `accidentes_clase_inegi.xlsx`: Base de datos de clases de accidentes.
- `accidentes_tipo.xlsx`: Base de datos de tipos de accidentes.
- `victimas_inegi.xlsx`: Base de datos de víctimas de accidentes.
- `vmrc.xlsx`: Base de datos de vehículos involucrados en accidentes.

---

## 🛠️ Requisitos

- Python 3.7 o superior
- Paquetes requeridos:
  - `streamlit`
  - `pandas`
  - `plotly`
  - `openpyxl`

---

## 📦 Instalación

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/AnaJZP/dash_seguros.git
   cd dash_seguros
