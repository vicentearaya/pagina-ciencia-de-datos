const startBtn = document.getElementById("startBtn");
const wallpaperScene = document.getElementById("wallpaperScene");
const captionScene = document.getElementById("captionScene");
const infoScene = document.getElementById("infoScene");
const finalScene = document.getElementById("finalScene");
const fadeLayer = document.getElementById("fadeLayer");
const replayBtn = document.getElementById("replayBtn");

/** Tiempo en pantalla negra al cambiar de escena */
const FADE_MS = 1200;
/** Segundos para leer cada escena (después del fade) */
const CAPTION_READ_MS = 5000;
const INFO_READ_MS = 7000;

function hideAllScenes() {
  document.querySelectorAll(".scene").forEach((scene) => {
    scene.classList.remove("active");
  });
}

function transitionTo(nextScene, delay = FADE_MS) {
  fadeLayer.classList.add("show");
  setTimeout(() => {
    hideAllScenes();
    nextScene.classList.add("active");
    setTimeout(() => {
      fadeLayer.classList.remove("show");
    }, 100);
  }, delay);
}

startBtn.addEventListener("click", () => {
  transitionTo(captionScene);
  setTimeout(() => {
    transitionTo(infoScene);
    setTimeout(() => {
      transitionTo(finalScene);
    }, FADE_MS + INFO_READ_MS);
  }, FADE_MS + CAPTION_READ_MS);
});

replayBtn.addEventListener("click", () => {
  transitionTo(wallpaperScene);
});
