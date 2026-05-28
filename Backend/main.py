from pathlib import Path
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from features import build_model_row

app = FastAPI(
    title="Gaming Classification API",
    description="API para clasificar riesgo de trastorno por gaming.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = (
    Path(__file__).resolve().parent
    / "gradient_boosting_jordan_generic_hybrid_multiclass.pkl"
)
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

    gaming_hours_daily: Literal["menos_1h", "entre_1_3h", "mas_3h"]
    social_media_hours: Literal["0_2h", "3_4h", "mas_4h"]
    internet_main_reason: Literal[
        "videojuegos",
        "estudiar",
        "trabajo",
        "redes_sociales",
        "mas_de_uno",
        "otro",
    ]
    sleep_latency: Literal["menos_15", "15_30", "31_60", "mas_60"]
    sleep_duration: Literal["menos_5", "5_6", "6_7", "7_8", "mas_8"]
    sleep_quality: Literal["muy_buena", "bastante_buena", "bastante_mala", "muy_mala"]
    sleep_medication_freq: Literal[
        "nunca", "menos_1_semana", "1_2_semana", "3_mas_semana"
    ]
    daytime_sleepiness_freq: Literal[
        "nunca", "menos_1_semana", "1_2_semana", "3_mas_semana"
    ]
    enthusiasm_freq: Literal[
        "nunca", "menos_1_semana", "1_2_semana", "3_mas_semana"
    ]


@app.get("/health")
async def health_check():
    model_loaded = MODEL_PATH.exists()
    return {
        "status": "ok",
        "model_found": model_loaded,
        "model_file": MODEL_PATH.name,
    }


@app.post("/predict")
async def predict(payload: AssessmentPayload):
    answers = payload.model_dump()
    positive_answers = sum(answers[f"igd{i}"] for i in range(1, 10))

    try:
        model = get_model()
        feature_row = build_model_row(answers)
        columns = list(model.feature_names_in_)
        input_df = pd.DataFrame([feature_row], columns=columns)
        prediction = int(model.predict(input_df)[0])
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Valor de formulario no reconocido: {exc}",
        ) from exc
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
