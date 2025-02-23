import { io } from "/static/socket.io/4.8.1/socket.io.esm.min.js";

const socket = io("127.0.0.1:18889");
const MONITOR_DEVICE = "default";
const DEBUG = true;
let log = DEBUG ? ((...what) => console.log("[AUTOVC]", ...what)) : ((...what) => { });

socket.on("vc start", () => {
  log("vc start");
  changeVCState(true);
});

socket.on("vc stop", () => {
  log("vc stop");
  changeVCState(false);
});

socket.on("vc monitor toggle", () => {
  log("vc monitor toggle");
  const monitorSelect = document.querySelectorAll("div.config-sub-area-control-field select")[6];
  if (monitorSelect.value === "none") {
    monitorSelect.value = MONITOR_DEVICE;
  } else {
    monitorSelect.value = "none";
  }
});

socket.on("vc model select", (modelIndex) => {
  log("vc model select", modelIndex);
  // First, sort models by ID
  document.querySelector("div.model-slot-sort-buttons").firstChild.click();
  // Then click nth model
  const model = document.querySelector("div.model-slot-tiles-container").children[modelIndex];
  if (model && !model.classList.contains("model-slot-tile-container-selected")) {
    model.click();
  }
});

socket.on("vc tune", (direction) => {
  log("vc tune", direction);
  const tuneSlider = document.querySelectorAll("span.character-area-slider-control-slider input")[2];

  if (direction === "up") {

  } else if (direction === "down") {

  }
})

function changeVCState(started) {
  const buttonsParent = document.querySelector("div.character-area-control-buttons");
  if (started) {
    buttonsParent.children[0].click();
  } else {
    buttonsParent.children[1].click();
  }
}

function simulateReactClick(element) {
  element.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true }));
  element.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true }));
  element.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
}

export function init() {
  setTimeout(() => {
    const buttons = Array.from(document.querySelectorAll("div.body-button"));
    const startButton = buttons.filter((el) => el.textContent == "start")[0];
    if (startButton !== undefined) {
      log("Clicking start button");
      simulateReactClick(startButton);
    }
  }, 750);
}