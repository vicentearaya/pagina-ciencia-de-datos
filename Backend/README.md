# Backend FastAPI

API para clasificar riesgo de trastorno por gaming usando el modelo híbrido
`gradient_boosting_jordan_generic_hybrid_multiclass.pkl`.

## Ejecutar en local

```bash
cd Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Endpoints

- `GET /health`: verificación de servicio y modelo cargado.
- `POST /predict`: recibe respuestas del formulario (Bloque 1 + Bloque 2) y devuelve la clasificación.

## Variables del formulario

**Bloque 1 (Sí/No):** `igd1` … `igd9` (valores `0` o `1`).

**Bloque 2:** `gaming_hours_daily`, `social_media_hours`, `internet_main_reason`,
`sleep_latency`, `sleep_duration`, `sleep_quality`, `sleep_medication_freq`,
`daytime_sleepiness_freq`, `enthusiasm_freq`.

El módulo `features.py` transforma esas respuestas a las variables que espera el pipeline del modelo.
