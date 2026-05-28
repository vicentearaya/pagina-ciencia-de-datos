const assessmentForm = document.getElementById("assessmentForm");
const statusMessage = document.getElementById("statusMessage");

const CLASS_MESSAGES = {
  0: 'Clasificacion 1: "Jugador sin indicadores relevantes de trastorno"',
  1: 'Clasificacion 2: "Jugador en riesgo de desarrollar problemas por gaming"',
  2: 'Clasificacion 3: "Jugador con alta probabilidad de trastorno por gaming"',
};

assessmentForm?.addEventListener("submit", (event) => {
  event.preventDefault();

  const formData = new FormData(assessmentForm);
  const answers = Object.fromEntries(
    Array.from(formData.entries()).map(([key, value]) => [key, Number(value)])
  );

  statusMessage.textContent = "Calculando clasificacion...";

  fetch("http://127.0.0.1:8000/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(answers),
  })
    .then(async (response) => {
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "No se pudo clasificar");
      }
      return response.json();
    })
    .then((data) => {
      const classId = data.predicted_class;
      const classText = CLASS_MESSAGES[classId] ?? data.predicted_label;
      statusMessage.textContent = `${classText}. Respuestas afirmativas: ${data.positive_answers} de 9.`;
    })
    .catch((error) => {
      statusMessage.textContent = `No fue posible clasificar. ${error.message}`;
      console.error(error);
    });
});
