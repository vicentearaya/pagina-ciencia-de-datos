# Backend FastAPI

Base inicial para exponer la clasificacion del formulario con `model.pkl`.

## Ejecutar en local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Endpoints

- `GET /health`: verificacion de servicio.
- `POST /predict`: endpoint placeholder para integrar el modelo.
