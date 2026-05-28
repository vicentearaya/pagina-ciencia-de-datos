from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Gaming Classification API",
    description="API para clasificar riesgo de trastorno por gaming.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = Path(__file__).resolve().parent / "random_forest_jordan_multiclass.pkl"
FEATURE_ORDER = [f"igd{i}" for i in range(1, 10)]
CLASS_LABELS = {
    0: "Jugador sin indicadores relevantes de trastorno",
    1: "Jugador en riesgo de desarrollar problemas por gaming",
    2: "Jugador con alta probabilidad de trastorno por gaming",
}

_model = None


def get_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"No se encontro el modelo en: {MODEL_PATH}")
        try:
            _model = joblib.load(MODEL_PATH)
        except Exception as exc:
            raise RuntimeError(
                f"No se pudo cargar el modelo en '{MODEL_PATH.name}': {exc}"
            ) from exc
    return _model


class AssessmentPayload(BaseModel):
    igd1: int = Field(ge=0, le=1)
    igd2: int = Field(ge=0, le=1)
    igd3: int = Field(ge=0, le=1)
    igd4: int = Field(ge=0, le=1)
    igd5: int = Field(ge=0, le=1)
    igd6: int = Field(ge=0, le=1)
    igd7: int = Field(ge=0, le=1)
    igd8: int = Field(ge=0, le=1)
    igd9: int = Field(ge=0, le=1)


@app.get("/health")
async def health_check():
    model_loaded = MODEL_PATH.exists()
    return {"status": "ok", "model_found": model_loaded}


@app.post("/predict")
async def predict(payload: AssessmentPayload):
    answers = payload.model_dump()
    ordered_answers = {feature: answers[feature] for feature in FEATURE_ORDER}
    input_df = pd.DataFrame([ordered_answers], columns=FEATURE_ORDER)
    positive_answers = int(sum(ordered_answers.values()))

    try:
        model = get_model()
        prediction = int(model.predict(input_df)[0])
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error ejecutando prediccion del modelo: {exc}",
        ) from exc

    predicted_label = CLASS_LABELS.get(prediction, "Clasificacion no reconocida")

    return {
        "predicted_class": prediction,
        "predicted_label": predicted_label,
        "positive_answers": positive_answers,
        "input": answers,
    }
