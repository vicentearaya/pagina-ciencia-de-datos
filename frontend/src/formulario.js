const assessmentForm = document.getElementById("assessmentForm");
const resultCard = document.getElementById("resultCard");
const resultIdle = document.getElementById("resultIdle");
const resultLoading = document.getElementById("resultLoading");
const resultSuccess = document.getElementById("resultSuccess");
const resultError = document.getElementById("resultError");
const resultBadge = document.getElementById("resultBadge");
const resultTitle = document.getElementById("resultTitle");
const resultDescription = document.getElementById("resultDescription");
const resultTip = document.getElementById("resultTip");
const resultErrorMessage = document.getElementById("resultErrorMessage");

const IGD_FIELDS = Array.from({ length: 9 }, (_, i) => `igd${i + 1}`);

const BLOCK2_FIELDS = [
  "gaming_hours_daily",
  "social_media_hours",
  "internet_main_reason",
  "sleep_latency",
  "sleep_duration",
  "sleep_quality",
  "sleep_medication_freq",
  "daytime_sleepiness_freq",
  "enthusiasm_freq",
];

const RESULT_COPY = {
  0: {
    badge: "Bajo riesgo",
    title: "Tu perfil se ve equilibrado",
    description:
      "Por ahora no aparecen señales fuertes de un problema con el gaming. Sigue cuidando el equilibrio entre jugar, descansar y otras actividades que disfrutas.",
    tip: "Un buen hábito es revisar de vez en cuando cuánto tiempo pasas jugando y cómo te sientes después.",
  },
  1: {
    badge: "Riesgo moderado",
    title: "Conviene estar atento",
    description:
      "Hay algunas señales que vale la pena vigilar: tu tiempo de juego, el sueño o cómo te afecta el día a día. Pequeños ajustes ahora pueden ayudar mucho.",
    tip: "Prueba fijar horarios de juego, hacer pausas y reservar tiempo para dormir y para otras cosas que te importen.",
  },
  2: {
    badge: "Riesgo elevado",
    title: "Tu patrón merece atención",
    description:
      "Tus respuestas sugieren un vínculo con el gaming que podría estar afectándote. No estás solo: hablar con alguien de confianza o buscar orientación profesional puede marcar la diferencia.",
    tip: "Pedir ayuda no es debilidad. Un psicólogo o un servicio de salud pueden orientarte con herramientas concretas.",
  },
};

function parseFormPayload(formData) {
  const payload = Object.fromEntries(formData.entries());

  for (const field of IGD_FIELDS) {
    payload[field] = Number(payload[field]);
  }

  for (const field of BLOCK2_FIELDS) {
    if (!payload[field]) {
      throw new Error("Faltan respuestas en el formulario. Revisa que todo esté marcado.");
    }
  }

  return payload;
}

function formatApiError(detail) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || JSON.stringify(item)).join(" ");
  }
  return "Ocurrió un error inesperado. Intenta de nuevo en unos momentos.";
}

function showResultState(state) {
  resultIdle.classList.toggle("is-hidden", state !== "idle");
  resultLoading.classList.toggle("is-hidden", state !== "loading");
  resultSuccess.classList.toggle("is-hidden", state !== "success");
  resultError.classList.toggle("is-hidden", state !== "error");

  resultCard.classList.remove("result-card--low", "result-card--mid", "result-card--high");
  if (state === "success") {
    resultCard.dataset.state = "success";
  } else if (state === "error") {
    resultCard.dataset.state = "error";
  } else {
    resultCard.dataset.state = state;
  }
}

function showSuccess(classId, fallbackLabel) {
  const copy = RESULT_COPY[classId] ?? {
    badge: "Resultado",
    title: "Tu lectura está lista",
    description: fallbackLabel ?? "Gracias por completar el cuestionario.",
    tip: "Si tienes dudas sobre tus hábitos, conversar con un profesional puede ayudarte.",
  };

  resultBadge.textContent = copy.badge;
  resultTitle.textContent = copy.title;
  resultDescription.textContent = copy.description;
  resultTip.textContent = copy.tip;

  const levelClass =
    classId === 0 ? "result-card--low" : classId === 1 ? "result-card--mid" : "result-card--high";
  resultCard.classList.add(levelClass);
  resultBadge.className = `result-badge result-badge--level-${classId}`;

  showResultState("success");
  resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function showError(message) {
  resultErrorMessage.textContent =
    message.includes("fetch") || message.includes("Failed")
      ? "Parece que no hay conexión con el servicio. Asegúrate de que la aplicación esté en marcha e inténtalo otra vez."
      : message;
  showResultState("error");
  resultCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

assessmentForm?.addEventListener("submit", (event) => {
  event.preventDefault();

  let answers;
  try {
    const formData = new FormData(assessmentForm);
    answers = parseFormPayload(formData);
  } catch (error) {
    showError(error.message);
    return;
  }

  showResultState("loading");

  fetch("http://127.0.0.1:8000/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(answers),
  })
    .then(async (response) => {
      const data = await response.json();
      if (!response.ok) {
        throw new Error(formatApiError(data.detail));
      }
      return data;
    })
    .then((data) => {
      showSuccess(data.predicted_class, data.predicted_label);
    })
    .catch((error) => {
      showError(error.message);
      console.error(error);
    });
});
