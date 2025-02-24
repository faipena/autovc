import { io } from "/static/socket.io/4.8.1/socket.io.esm.min.js";

const socket = io("127.0.0.1:18889");
const MONITOR_DEVICE = "default";
const DEBUG = true;
let log = DEBUG ? ((...what) => console.log("[AUTOVC]", ...what)) : ((...what) => { });

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

function simulateReactSetInputValue(input, value) {
  const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
    window.HTMLInputElement.prototype,
    'value').set;
  nativeInputValueSetter.call(input, value);
  input.dispatchEvent(new Event('input', { bubbles: true, cancelable: true }));
}

function setTune(tuneSlider, value) {
  if ((tuneSlider !== undefined) &&
    (!isNaN(value)) &&
    (tuneSlider.max === undefined || tuneSlider.max >= +value) &&
    (tuneSlider.min === undefined || tuneSlider.min <= +value)) {
    log(`Setting tune value to: ${value}`)
    simulateReactSetInputValue(tuneSlider, value);
  }
}

export function init() {
  // Skip donate nagscreen
  setTimeout(() => {
    const buttons = Array.from(document.querySelectorAll("div.body-button"));
    const startButton = buttons.filter((el) => el.textContent == "start")[0];
    if (startButton !== undefined) {
      log("Clicking start button");
      simulateReactClick(startButton);
    }
  }, 750);
  // Register socketio events

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
    const monitorSelect = Array.from(document.querySelectorAll("div.config-sub-area-control-field"))
      .find((el) => el.parentNode.textContent.startsWith("monitor"))
      .firstChild;
    if (monitorSelect === undefined) {
      log("Cannot find monitor input");
      return;
    }
    log(monitorSelect.value);
    if (monitorSelect.value != "none") {
      monitorSelect.value = "none";
    } else {
      monitorSelect.value = MONITOR_DEVICE;
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

  socket.on("vc tune slide", (direction) => {
    log("vc tune slide", direction);
    const tuneSlider = Array.from(document.querySelectorAll("span.character-area-slider-control-slider input"))
      .find((el) => el.parentNode.parentNode.parentNode.parentNode.textContent.startsWith("TUNE"));
    if (tuneSlider === undefined) {
      log("Cannot find tune slider input element");
      return;
    }
    let newValue = (direction === "down") ? +tuneSlider.value - 1 : +tuneSlider.value + 1;
    setTune(tuneSlider, newValue);
  });

  socket.on("vc tune set", (level) => {
    log("vc tune set", +level);
    const tuneSlider = Array.from(document.querySelectorAll("span.character-area-slider-control-slider input"))
      .find((el) => el.parentNode.parentNode.parentNode.parentNode.textContent.startsWith("TUNE"));
    setTune(tuneSlider, +level);
  });
}