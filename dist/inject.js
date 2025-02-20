const DEBUG = false;
let log = DEBUG ? ((...what) => console.log("[AUTOVC]", ...what)) : ((...what) => { });

function inject() {
  const buttonsParent = document.querySelector("div.character-area-control-buttons");
  const startButton = buttonsParent.children[0];
  const stopButton = buttonsParent.children[1];

  setInterval(() => {
    const isClientStarted = startButton.classList.contains("character-area-control-button-active");
    fetch("http://127.0.0.1:18889").then(response => response.json())
      .then(data => {
        log(data);
        const isServerStarted = data.started === true;
        if (isClientStarted == isServerStarted) {
          return;
        }
        if (isServerStarted) {
          startButton.click();
        } else {
          stopButton.click();
        }
      })
      .catch(error => log("Cannot fetch autovc request: ", error))
  }, 250);
}

export function init() {
  log("Let go!");
  let timer = setInterval(() => {
    const buttonsParent = document.querySelector("div.character-area-control-buttons");
    if (buttonsParent !== undefined) {
      log("Buttons found, injecting!");
      clearInterval(timer);
      setTimeout(inject, 100);
    }
  }, 500);
}