const assessmentForm = document.getElementById("assessmentForm");
const statusMessage = document.getElementById("statusMessage");

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

const CLASS_MESSAGES = {
  0: 'Clasificacion 1: "Jugador sin indicadores relevantes de trastorno"',
  1: 'Clasificacion 2: "Jugador en riesgo de desarrollar problemas por gaming"',
  2: 'Clasificacion 3: "Jugador con alta probabilidad de trastorno por gaming"',
};

function parseFormPayload(formData) {
  const payload = Object.fromEntries(formData.entries());

  for (const field of IGD_FIELDS) {
    payload[field] = Number(payload[field]);
  }

  for (const field of BLOCK2_FIELDS) {
    if (!payload[field]) {
      throw new Error(`Falta responder: ${field}`);
    }
  }

  return payload;
}

function formatApiError(detail) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || JSON.stringify(item)).join(" ");
  }
  return "No se pudo clasificar";
}

assessmentForm?.addEventListener("submit", (event) => {
  event.preventDefault();

  const formData = new FormData(assessmentForm);
  const answers = parseFormPayload(formData);

  statusMessage.textContent = "Calculando clasificacion...";

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
      const classId = data.predicted_class;
      const classText = CLASS_MESSAGES[classId] ?? data.predicted_label;
      statusMessage.textContent = `${classText} (sintomas IGD afirmativos: ${data.positive_answers} de 9).`;
    })
    .catch((error) => {
      statusMessage.textContent = `No fue posible clasificar. ${error.message}`;
      console.error(error);
    });
});
