# Churn D1 — Pipeline & EDA · Etermax

Modelo predictivo de **churn Día 1** para videojuegos móviles.  
Pipeline de feature engineering con [Polars](https://pola.rs/) (lazy evaluation) orientado a entrenamiento con [LightGBM](https://lightgbm.readthedocs.io/).

---

## Requisitos

- Python ≥ 3.10
- Dependencias:

```bash
pip install polars lightgbm matplotlib numpy scikit-learn optuna shap
```

---

## Estructura del proyecto

```
etermax/
├── data/
│   └── dataset_raw.csv              # Dataset crudo (20,000 registros)
├── src/
│   ├── churn_feature_pipeline.py    # Pipeline de preparación de datos
│   ├── eda_churn_bivariado.py       # EDA bivariado (tablas + 7 gráficos)
│   └── train_churn_model.py         # Entrenamiento LightGBM (Optuna + SHAP)
├── plots/                           # Carpeta generada con las visualizaciones (.png)
├── main.py                          # Orquestador del pipeline completo
├── requirements.txt                 # Dependencias del proyecto
├── Dockerfile                       # Configuración para empaquetado Docker
├── walkthrough.md                   # Documentación detallada del proceso
└── README.md                        # Este archivo
```

---

## Ejecución

### Opción 1: Docker (Recomendado para reproducibilidad)

El proyecto está empaquetado en un contenedor Docker que instala todas las dependencias y ejecuta el orquestador (`main.py`).

```bash
# 1. Construir la imagen
docker build -t etermax-churn .

# 2. Ejecutar el contenedor (los resultados se mostrarán por consola)
docker run --rm etermax-churn
```

### Opción 2: Localmente

Si prefieres ejecutarlo localmente, puedes correr el orquestador `main.py` que invocará secuencialmente el pipeline, el EDA y el entrenamiento del modelo.

```bash
# Ejecutar todo el flujo
python -X utf8 main.py
```

Los gráficos se guardarán automáticamente en la carpeta `plots/`.

**Métricas Finales (Test Set):**
- **PR-AUC:** 0.7539
- **ROC-AUC:** 0.7836

---

## Datos clave

| Métrica | Valor |
|---|---|
| Filas originales | 20,000 |
| Filas eliminadas (borde temporal) | 2,308 |
| Filas finales | 17,692 |
| Columnas finales | 30 |
| Tasa de churn global | ~48% |

### Features con mayor poder predictivo (EDA)

| Feature | Señal |
|---|---|
| `total_events` | Relación monotónica inversa: 72.8% churn (0-10 eventos) → 10.1% (+150 eventos) |
| `has_done_event_3` | Δ=36.9pp (20.7% vs 57.6%) con volumetría sólida en ambos grupos |
| `has_done_event_1/2` | Δ≈25pp (46% vs 71%) |

---

## Documentación detallada

Consultá [`walkthrough.md`](walkthrough.md) para el paso a paso completo: fases del pipeline, registros eliminados, variables creadas, correcciones aplicadas y hallazgos del EDA con gráficos embebidos.
