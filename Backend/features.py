"""
Mapeo de respuestas del formulario a variables del modelo generic_hybrid.

Las fórmulas derivadas replican scripts/preprocess_real_dataset.py del repo de
modelado (build_generic_contextual_dataframe).
"""

GAMING_HOURS_GROUP = {
    "menos_1h": 0,
    "entre_1_3h": 1,
    "mas_3h": 2,
}

GAMING_HOURS_DAILY = {
    "menos_1h": 0.0,
    "entre_1_3h": 2.0,
    "mas_3h": 4.0,
}

SOCIAL_HOURS_GROUP = {
    "0_2h": 0,
    "3_4h": 1,
    "mas_4h": 2,
}

SOCIAL_HOURS_DAILY = {
    "0_2h": 1.0,
    "3_4h": 3.5,
    "mas_4h": 6.0,
}

USAGE_CAUSE_MAP = {
    "videojuegos": "video games",
    "estudiar": "studying",
    "trabajo": "others",
    "redes_sociales": "social media",
    "mas_de_uno": "more than one reason",
    "otro": "others",
}

SLEEP_QUAL_MAP = {
    "muy_buena": "goodsleep",
    "bastante_buena": "goodsleep",
    "bastante_mala": "poorsleep",
    "muy_mala": "poorsleep",
}

# Minutos hasta dormirse (psqi2 en el dataset jordano)
SLEEP_LATENCY_MINUTES = {
    "menos_15": 10.0,
    "15_30": 30.0,
    "31_60": 45.0,
    "mas_60": 60.0,
}

# Horas de sueño por noche (psqi4 en el dataset jordano)
SLEEP_DURATION_HOURS = {
    "menos_5": 4.5,
    "5_6": 5.5,
    "6_7": 6.5,
    "7_8": 7.5,
    "mas_8": 9.0,
}

PSQI_FREQUENCY = {
    "nunca": 0,
    "menos_1_semana": 1,
    "1_2_semana": 2,
    "3_mas_semana": 3,
}

# Componente PSQI de calidad global (psqi9); se infiere de la misma pregunta de calidad
SLEEP_QUALITY_PSQI9 = {
    "muy_buena": 0,
    "bastante_buena": 1,
    "bastante_mala": 2,
    "muy_mala": 3,
}

# Medias de globalscorepsqi en dataset_preprocesado_jordan_generic_hybrid.csv
_GLOBAL_SCORE_TABLE = {
    ("goodsleep", 0): 2.23,
    ("goodsleep", 1): 3.28,
    ("goodsleep", 2): 3.90,
    ("goodsleep", 3): 4.22,
    ("goodsleep", 4): 4.48,
    ("goodsleep", 5): 4.82,
    ("goodsleep", 6): 4.86,
    ("goodsleep", 7): 5.00,
    ("poorsleep", 0): 6.78,
    ("poorsleep", 1): 6.84,
    ("poorsleep", 2): 7.38,
    ("poorsleep", 3): 7.64,
    ("poorsleep", 4): 8.18,
    ("poorsleep", 5): 8.69,
    ("poorsleep", 6): 9.46,
    ("poorsleep", 7): 10.02,
    ("poorsleep", 8): 11.40,
    ("poorsleep", 9): 12.10,
    ("poorsleep", 10): 12.80,
    ("poorsleep", 11): 16.00,
}


def _estimate_globalscorepsqi(sleepqual: str, sleep_problem_burden: int) -> float:
    burden = min(int(sleep_problem_burden), 11)
    return _GLOBAL_SCORE_TABLE.get((sleepqual, burden), 7.0)


def _apply_derived_features(row: dict) -> dict:
    """Mismas transformaciones que build_generic_contextual_dataframe."""
    row["digital_exposure_total"] = (
        row["gameinghourspermonth"] + row["hoursonsocialmedia"]
    )
    row["gaming_minus_social"] = (
        row["gameinghourspermonth"] - row["hoursonsocialmedia"]
    )
    row["gaming_to_social_ratio"] = row["gameinghourspermonth"] / (
        row["hoursonsocialmedia"] + 1.0
    )
    row["sleep_deficit_hours"] = max(0.0, 8.0 - row["psqi4"])
    row["long_sleep_latency"] = 1.0 if row["psqi2"] >= 30 else 0.0
    row["sleep_problem_burden"] = (
        row["psqi6"] + row["psqi7"] + row["psqi8"] + row["psqi9"]
    )
    row["gaming_sleep_risk_interaction"] = row["gameinghourspermonth"] * (
        row["globalscorepsqi"] + 1.0
    )
    return row


def build_model_row(payload: dict) -> dict:
    """Convierte respuestas del formulario al DataFrame esperado por el pipeline."""
    gaming_key = payload["gaming_hours_daily"]
    social_key = payload["social_media_hours"]
    sleep_quality_key = payload["sleep_quality"]

    psqi6 = PSQI_FREQUENCY[payload["sleep_medication_freq"]]
    psqi7 = PSQI_FREQUENCY[payload["daytime_sleepiness_freq"]]
    psqi8 = PSQI_FREQUENCY[payload["enthusiasm_freq"]]
    psqi9 = SLEEP_QUALITY_PSQI9[sleep_quality_key]

    sleepqual = SLEEP_QUAL_MAP[sleep_quality_key]
    sleep_problem_burden = psqi6 + psqi7 + psqi8 + psqi9

    row = {
        "usagecause": USAGE_CAUSE_MAP[payload["internet_main_reason"]],
        "sleepqual": sleepqual,
        "gamingshgroupsnew": GAMING_HOURS_GROUP[gaming_key],
        "newshgroups": SOCIAL_HOURS_GROUP[social_key],
        "psqi6": psqi6,
        "psqi7": psqi7,
        "psqi8": psqi8,
        "psqi9": psqi9,
        "gameinghourspermonth": GAMING_HOURS_DAILY[gaming_key],
        "hoursonsocialmedia": SOCIAL_HOURS_DAILY[social_key],
        "psqi2": SLEEP_LATENCY_MINUTES[payload["sleep_latency"]],
        "psqi4": SLEEP_DURATION_HOURS[payload["sleep_duration"]],
        "globalscorepsqi": _estimate_globalscorepsqi(sleepqual, sleep_problem_burden),
    }

    for i in range(1, 10):
        row[f"igd{i}"] = int(payload[f"igd{i}"])

    return _apply_derived_features(row)
